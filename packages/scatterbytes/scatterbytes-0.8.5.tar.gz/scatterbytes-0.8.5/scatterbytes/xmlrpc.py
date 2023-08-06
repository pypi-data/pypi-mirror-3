"""XMLRPC functionality common to both client and storage nodes.

"""

import os
import sys
import time
import types
import base64
import urllib2
import logging
import inspect
import threading
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from M2Crypto import m2
from M2Crypto import m2urllib
from M2Crypto import m2urllib2
from M2Crypto import m2xmlrpclib
from M2Crypto import SSL
from M2Crypto.m2xmlrpclib import SSL_Transport
from . import errors
from . import util
from . import https
from https import build_opener
from https import SBHTTPS
from https import SBHTTPSConnection
from https import SBHTTPSServer
from https import HandlerLoggingMixIn
from https import ThreadedSBHTTPSServer

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 20

fault_codes = {
    'SBError' : 10,
    'RequestExpiredError' : 20,
    'ClientNotFoundError' : 30,
    'CRC32ChecksumError' : 40,
    'MD5ChecksumError' : 50,
    'SHA256ChecksumError' : 60,
    'DuplicateFilenameError' : 70,
    'FileNotFoundError' : 80,
    'FileExistsError' : 90,
    'VolumeNotFoundError' : 100,
    'ChunkError' : 110,
    'ChunkNotFoundError' : 120,
    'EncryptionError' : 130,
    'AuthenticationError' : 140,
    'CertificateError': 150,
    'CertificateRequestError' : 160
}


# The default implementation of xmlrpclib does not support marshalling
# integers > 32 bits.  This will cause all integers up to 64 bit signed to be
# marshalled as int.  Some other implementations use int8, but I think it
# makes better sense to leave it as int and let the unmarshaller figure out
# what platform specific sub-type is required.

MAXINT32 = xmlrpclib.MAXINT
MININT32 = -1 * xmlrpclib.MAXINT
MAXINT64 = 2**63-1
MININT64 = -1 * 2**63

def marshall_int(marshaller, value, write):
    logger.debug('marshalling %s' % value)
    if value > MAXINT64 or value < MININT64:
        raise OverflowError("integer exceeds XML-RPC limits")
    else:
        write("<value><int>")
        write(str(value).rstrip('L'))
        write("</int></value>\n")

xmlrpclib.Marshaller.dispatch[types.IntType] = marshall_int
xmlrpclib.Marshaller.dispatch[types.LongType] = marshall_int


class SB_SSL_Transport(SSL_Transport):
    """SSL Transport that accepts a socket timeout and can bind an address.
    
    This subclass is designed use SSL resume to speed up the SSL handshake and
    to be thread-safe for requests.
    
    """

    def __init__(self, ssl_context, use_datetime=True,
                 timeout=DEFAULT_TIMEOUT, src_ip=None):
        # caching
        ssl_context.set_session_cache_mode(m2.SSL_SESS_CACHE_BOTH)
        self._timeout = timeout
        self._src_ip = src_ip
        self._session = None
        self._ctx_lock = threading.Lock()
        self._sess_lock = threading.Lock()
        SSL_Transport.__init__(self, ssl_context=ssl_context,
                               use_datetime=use_datetime)

    @property
    def ssl_session(self):
        with self._sess_lock:
            return self._session

    @ssl_session.setter
    def ssl_session(self, sess):
        with self._sess_lock:
            self._session = sess

    def request(self, host, handler, request_body, verbose=0):
        # modified from m2 to use timeout and bind src_ip
        # TODO - handle timeouts
        logger.debug('%s, %s, %s' % (host, handler, request_body)) 
        (user_passwd, host_port) = m2urllib.splituser(host)
        (_host, _port) = m2urllib.splitport(host_port)
        h = SBHTTPS(_host, int(_port), timeout=self._timeout,
                     src_ip=self._src_ip, ssl_context=self.ssl_ctx)

        # If a previous session exists, attempt to use it. It must be set
        # before the connection attempt is made.
        if self.ssl_session:
            h.set_session(self.ssl_session)
        # from xmlrpclib
        h.putrequest("POST", handler)
        # required by HTTP/1.1
        h.putheader("Host", _host)
        # required by XML-RPC
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))
        h.endheaders()
        ##logger.debug('finished putting headers')
        # Save the session for reuse.
        ##logger.debug('saving the session')
        session = h.get_session()
        self.ssl_session = session
        # Must add session to context for resume to work.  Another method is
        # to prevent connection from GC.
        with self._ctx_lock:
            self.ssl_ctx.add_session(session)
        # On resume, the master key should match that of the previous session.
        ##logger.debug('sending request body')
        if request_body:
            h.send(request_body)
        ##logger.debug('getting reply')
        errcode, errmsg, headers = h.getreply()
        ##logger.debug('got reply %s, %s, %s' % (errcode, errmsg, headers))
        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler, errcode, errmsg, headers
            )
        self.verbose = verbose
        self.verbose = True
        logger.debug('getting response')
        response = self.parse_response(h.getfile())
        logger.debug('got response')
        # let gc cleanup connection - should be implicit on exit, but let's be
        # explict
        # del h triggers an 'ALERT: write: warning: close notify'
        del h
        return response

    def parse_response(self, f):
        ##logger.debug('getting parser')
        (p, u) = self.getparser()
        ##logger.debug('got parser')
        while 1:
            ##logger.debug('reading response from %s' % str(f))
            ##logger.debug('readable: %s' % f.readable())
            ##logger.debug('should_read: %s' % f.should_read())
            response = f.read(1024)
            ##logger.debug('read: %s' % response)
            if not response:
                break
            ##logger.debug('feeding response')
            p.feed(response)
        ##logger.debug('closing')
        f.close()
        p.close()
        return u.close()


class RPCServerProxy(m2xmlrpclib.Server):

    """ServerProxy base class for xmlrpc proxies.

    This class adds a timeout using a custom transport and should only be used
    directly by RPCProxy.

    """

    def __init__(self, url, transport=None, ssl_context=None, encoding='utf-8',
                 verbose=0, allow_none=1, use_datetime=True, src_ip=None):
        if not (transport or ssl_context):
            raise ValueError('must provide either transport or ssl_context')
        if transport is None:
            transport = SB_SSL_Transport(
                ssl_context=ssl_context, src_ip=src_ip
            )
        m2xmlrpclib.Server.__init__(
            self, url, transport, encoding, verbose, allow_none,
            use_datetime=use_datetime
        )


class RPCProxy(object):

    """Proxy base class to an xmlrpc service.

    This class is insulated from the actual xmlrpc proxy, RPCServerProxy, to
    provide a cleaner namespace.

    """

    def __init__(self, url, ssl_context, src_ip=None):
        logger.debug('created proxy to %s' % url)
        self.url = url
        self.ssl_context = ssl_context
        self.proxy = RPCServerProxy(url, ssl_context=ssl_context,
                                    encoding='utf-8', use_datetime=True,
                                    src_ip=src_ip)

    def make_get_request(self, url):
        """Make a GET request using the exisiting SSL session.

        """
        opener = build_opener(self.ssl_context)
        opener.addheaders = [('Connection', 'close')]
        u = opener.open(url)
        try:
            data = u.read()
        finally:
            u.close()
        return data

    def __getattr__(self, attname):
        def new_func(*args):
            try:
                return getattr(self.proxy, attname)(*args)
            except xmlrpclib.Fault, f:
                raise convert_from_fault(f)
        return new_func


class ControlNodeProxy(RPCProxy):
    """Proxy to the control node.

    configuration based on the client's settings

    """

    def __init__(self, config, src_ip=None):
        address = config.get('control_node_address')
        port = config.get('control_node_port')
        url = "https://%s:%s" % (address, port)
        ctx = config.make_ssl_context()
        self.config = config
        RPCProxy.__init__(self, url, ctx, src_ip=src_ip)

    def get_certificates(self):
        address = self.config.get('control_node_address')
        port = self.config.get('control_node_port')
        url = "https://%s:%s/scatterbytes_certs.zip" % (address, port)
        zipf_data = self.make_get_request(url)
        output_path = os.path.join(
            self.config.get('tls_dir'), 'scatterbytes_certs.zip',
        )
        open(output_path, 'wb').write(zipf_data)
        return output_path


class RPCDispatcher(SimpleXMLRPCDispatcher):

    def __init__(self, allow_none=True, encoding='utf-8'):
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)

    def register_instance(self, instance):
        """register published methods for instance

        methods with "published" attribute will be registered.

        """
        for (member_name, member) in inspect.getmembers(instance):
            if inspect.ismethod(member) and \
                                        getattr(member, 'published', False):
                self.register_function(member, member_name)

    def _marshaled_dispatch(self, data, client_cert_info=None):
        
        try:
            (params, method) = xmlrpclib.loads(data, use_datetime=True)
            # generate response
            if client_cert_info:
                params = [client_cert_info, ] + list(params)
            try:
                response = self._dispatch(method, params)
            except Exception, e:
                # using exc_info in testing causes a delay
                logger.debug(str(e))
                # logger.debug(str(e), exc_info=True)
                fault = convert_to_fault(e)
                raise fault
            # wrap response in a singleton tuple
            response = (response,)
            rpc_response = xmlrpclib.dumps(
                response, methodresponse=1, allow_none=self.allow_none,
                encoding=self.encoding
            )
        except xmlrpclib.Fault, fault:
            logger.debug('fault is: %s' % fault)
            rpc_response = xmlrpclib.dumps(
                fault, allow_none=self.allow_none, encoding=self.encoding
            )
        except Exception, e:
            logger.error(str(Exception), exc_info=True)
            fault = convert_to_fault(e)
            rpc_response = xmlrpclib.dumps(
                fault, allow_none=self.allow_none, encoding=self.encoding
            )
            ##logger.error(str(Exception))
            # The default implementation calls sys.exc_info, but calling
            # sys.exc_info causes a delay in the response. I don't know why -
            # maybe something related to threading or M2Crypto or both.
            # May be related to nose.  It occures when capturing logging, but
            # not with --nologcapture
        return rpc_response


class RPCRequestHandler(SimpleXMLRPCRequestHandler, HandlerLoggingMixIn):

    def log_message(self, *args, **kwargs):
        HandlerLoggingMixIn.log_message(self, *args, **kwargs)

    def do_POST(self):
        ##return SimpleXMLRPCRequestHandler.do_POST(self)
        # shutting down the connection causes a hang
        logger.debug('handling POST')
        # check path
        if self.path not in ('/', '/RPC2'):
            self.report_404()
            return
        try:
            data = self.read_content()
            # connection should make the cert available
            cert_info = self.request.client_cert_info
            response = self.server._marshaled_dispatch(data, cert_info)
            ##logger.debug('marshalled response: %s' % response)
        except Exception, e:
            logger.debug('oops: %s' % str(e))
            self.send_response(500)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/xml")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            self.wfile.flush()
            ##logger.debug('flushed response to buffer')
        ##return SimpleXMLRPCRequestHandler.do_POST(self)

    def read_content(self, size=None):
        max_chunk_size = 5*1024*1024
        size_remaining = int(self.headers['content-length'])
        if size and size < size_remaining:
            size_remaining = size
        L = []
        while size_remaining:
            chunk_size = min(size_remaining, max_chunk_size)
            L.append(self.rfile.read(chunk_size))
            size_remaining -= len(L[-1])
        data = ''.join(L)
        return data


class RPCServer(SBHTTPSServer, RPCDispatcher):
    """XMLRPC Server.

    single-threaded XMLRPC server

    """

    def __init__(self, (ip_address, port), ssl_context,
                 request_handler=RPCRequestHandler, log_requests=True):
        self.logRequests = log_requests
        SBHTTPSServer.__init__(
            self, (ip_address, port), request_handler, ssl_context
        )
        RPCDispatcher.__init__(self)


class ThreadedRPCServer(ThreadedSBHTTPSServer, RPCDispatcher):
    """XMLRPC Server.

    multi-threaded XMLRPC server

    """

    def __init__(self, (ip_address, port), ssl_context,
                 request_handler=RPCRequestHandler, log_requests=True):
        self.logRequests = log_requests
        ThreadedSBHTTPSServer.__init__(
            self, (ip_address, port), request_handler, ssl_context
        )
        RPCDispatcher.__init__(self)


##def reverse_fault(f):
##    """substitute SB specific error for Fault Code
##    
##    This client-side function uses predefined fault codes so the client can
##    translate the error.
##    
##    """
##    def new_func(*args, **kwargs):
##        try:
##            return f(*args, **kwargs)
##        except xmlrpclib.Fault, e:
##            for (key, code) in fault_codes.items():
##                if e.faultCode == code:
##                    E = getattr(errors, key)
##                    raise E(e.faultString)
##            # if nothing matches
##            raise
##    return new_func


class StorageNodeProxy(RPCProxy):

    requires_ssl_context = True

    def __init__(self, url, ssl_context, src_ip=None):
        RPCProxy.__init__(self, url, ssl_context, src_ip)

    def store_chunk(self, sig, sig_ts, expire_time, transfer_name,
                    chunk_name, chunk_hash_salt, chunk_data):

        url = '%s/sbfile/%s' % (self.url, chunk_name)
        logger.debug('storing chunk at %s' % url)
        opener = https.build_opener(self.ssl_context)
        request = m2urllib2.Request(url, data=chunk_data)
        headers = [
            ('x-sb-sig', sig),
            ('x-sb-sig-ts', util.datetime_to_string(sig_ts)),
            ('x-sb-transfer-name', transfer_name),
            ('x-sb-hash-salt', chunk_hash_salt),
            ('x-sb-expire-time', util.datetime_to_string(expire_time)),
        ]
        for (header_name, header) in headers:
            request.add_header(header_name, header)
        request.add_header('Content-Type', 'application/octet-stream')
        # figure out the content length
        if isinstance(chunk_data, file):
            content_length = os.fstat(chunk_data.fileno()).st_size
        else:
            content_length = len(chunk_data)
        request.add_header('Content-Length', content_length)
        request.get_method = lambda: 'PUT'
        logger.debug('opening url')
        f = opener.open(request)
        logger.debug('reading ...')
        response = f.read()
        assert f.code == 201
        logger.debug('chunk stored, response is %s' % str(response))
        return response

    def retrieve_chunk(self, auth, auth_ts, expire_time, chunk_name,
                             byte_start=0, byte_end=0):
        url = '%s/sbfile/%s'
        url = url % (self.url, chunk_name)
        logger.debug('request to %s' % url)
        request = m2urllib2.Request(url)
        headers = [
            ('x-sb-auth', auth),
            ('x-sb-action', 'RETRIEVE_CHUNK'),
            ('x-sb-auth-ts', util.datetime_to_string(auth_ts)),
            ('x-sb-expire-time', util.datetime_to_string(expire_time)),
        ]
        if byte_end > 0:
            # HTTP Spec uses inclusive ranges.
            headers.append(('bytes', '%s-%s' % (byte_start, byte_end - 1)))
        for (header_name, header) in headers:
            request.add_header(header_name, header)
        ##request.add_header('Content-Type', 'application/octet-stream')
        opener = https.build_opener(self.ssl_context)
        f = opener.open(request)
        return f


def gen_storage_node_proxy_creator(config):
    
    def create_storage_node_proxy(url):
        ssl_context = config.make_ssl_context()
        return StorageNodeProxy(url, ssl_context)

    return create_storage_node_proxy

def convert_from_fault(fault):
    e = fault
    for (key, code) in fault_codes.items():
        if e.faultCode == code:
            E = getattr(errors, key)
            raise E(e.faultString)
    raise fault

def convert_to_fault(exception):
    e = exception
    ename = e.__class__.__name__
    logger.debug('converting %s' % ename)
    if ename in fault_codes:
        logger.debug('found matching code')
        msg = 'no error information'
        if e.args:
            msg = str(e.args[0])
        fault = xmlrpclib.Fault(fault_codes[ename], msg)
    else:
        # don't want to send across unhandled exceptions
        logger.debug('did not find matching code')
        fault = xmlrpclib.Fault(1, 'an unexpected exception occurred')
    return fault

        

def check_fault(f):
    """substitute xmlrpc Fault Codes for Exceptions
    
    Uses predefined fault codes so the client can translate the error.
    
    """
    def new_func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            logger.error(str(e), exc_info=True)
            ename = e.__class__.__name__
            if ename in fault_codes:
                msg = 'no error information'
                if e.args:
                    msg = str(e.args[0])
                fault = xmlrpclib.Fault(fault_codes[ename], msg)
                raise fault
            else:
                # don't want to send across unhandled exceptions
                fault = xmlrpclib.Fault(1, 'an unexpected exception occurred')
                raise fault
    return new_func

if __name__ == '__main__':
    url = 'https://net1.realcloudstorage.net:8888/wsgi_test'
    proxy = SBProxy(url)
    print proxy.echo('hello you')
