"""HTTPS functionality

"""

import os
import sys
import types
import socket
import urllib2
import logging
import urlparse
import threading
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
from M2Crypto import m2
from M2Crypto import SSL
from M2Crypto import m2urllib2
from M2Crypto.SSL import SSLError
from M2Crypto import httpslib
from M2Crypto.httpslib import HTTPS
from M2Crypto.httpslib import HTTPSConnection
from M2Crypto.SSL.Checker import Checker

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 20

def make_context(ca_cert_path, cert_path, key_path, mode='client'):
    logger.debug('making context')
    logger.debug('ca_cert_path: %s' % ca_cert_path)
    logger.debug('cert_path: %s' % cert_path)
    logger.debug('key_path: %s' % key_path)
    logger.debug('mode: %s' % mode)
    ctx = SSL.Context('tlsv1')
    if mode != 'init':
        ctx.load_cert_chain(cert_path, key_path)
    ctx.load_verify_locations(ca_cert_path)
    if mode == 'init':
        ctx.set_verify(SSL.verify_peer, 2)
    else:
        ctx.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, 2)
    ctx.set_session_id_ctx('ScatterBytes')
    if mode != 'init':
        ctx.load_client_ca(ca_cert_path)
    if mode == 'server':
        ctx.set_session_cache_mode(m2.SSL_SESS_CACHE_SERVER)
    else:
        ctx.set_session_cache_mode(m2.SSL_SESS_CACHE_CLIENT)
    ##ctx.set_info_callback()
    return ctx


class SBHTTPSHandler(m2urllib2.HTTPSHandler):
    
    def __init__(self, ssl_context=None):
        m2urllib2.HTTPSHandler.__init__(self, ssl_context)

    def https_open(self, req):
        # modified to use SBHTTPSConnection
        logger.debug('opening request %s' % req)
        host = req.get_host()
        if not host:
            raise urllib2.URLError('no host given')

        # Our change: Check to see if we're using a proxy.
        # Then create an appropriate ssl-aware connection.
        full_url = req.get_full_url() 
        target_host = urlparse.urlparse(full_url)[1]

        if (target_host != host):
            h = httpslib.ProxyHTTPSConnection(host=host, ssl_context=self.ctx)
        else:
            h = SBHTTPSConnection(host=host, ssl_context=self.ctx)
        # End our change
        h.set_debuglevel(self._debuglevel)

        headers = dict(req.headers)
        headers.update(req.unredirected_hdrs)
        # We want to make an HTTP/1.1 request, but the addinfourl
        # class isn't prepared to deal with a persistent connection.
        # It will try to read all remaining data from the socket,
        # which will block while the server waits for the next request.
        # So make sure the connection gets closed after the (only)
        # request.
        headers["Connection"] = "close"
        try:
            h.request(req.get_method(), req.get_selector(), req.data, headers)
            r = h.getresponse()
        except socket.error, err: # XXX what error?
            raise m2urllib2.URLError(err)

        # Pick apart the HTTPResponse object to get the addinfourl
        # object initialized properly.

        # Wrap the HTTPResponse object in socket's file object adapter
        # for Windows.  That adapter calls recv(), so delegate recv()
        # to read().  This weird wrapping allows the returned object to
        # have readline() and readlines() methods.

        # XXX It might be better to extract the read buffering code
        # out of socket._fileobject() and into a base class.

        r.recv = r.read
        fp = m2urllib2._closing_fileobject(r)

        resp = m2urllib2.addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        return resp

        
    https_request = m2urllib2.AbstractHTTPHandler.do_request_


def build_opener(ssl_context):
    opener = urllib2.OpenerDirector()
    opener.add_handler(SBHTTPSHandler(ssl_context))
    return opener


class ClientSideChecker(Checker):

    def __call__(self, peerCert, host=None):
        # do not check host
        return Checker.__call__(self, peerCert, None)


class SBHTTPSConnection(HTTPSConnection):
    """SSL connection with a timeout and bindable address."""

    def __init__(self, host, port=None, strict=None, timeout=DEFAULT_TIMEOUT,
                 src_ip=None, **ssl):
        if not isinstance(timeout, (types.NoneType, int)):
            raise TypeError('timeout should be an int')
        self._src_ip = src_ip
        self._timeout = SSL.timeout(timeout)
        assert ssl['ssl_context']
        HTTPSConnection.__init__(self, host, port, strict, **ssl)

    def connect(self):
        sock = SSL.Connection(self.ssl_ctx)
        sock.set_post_connection_check_callback(ClientSideChecker())
        self.sock = sock
        if self.session:
            sock.set_session(self.session)
        if self._src_ip:
            # bind it
            sock.bind((self._src_ip, 0))
        sock.set_socket_read_timeout(self._timeout)
        sock.set_socket_write_timeout(self._timeout)
        # While using an unreliable connection, I've seen it fail with
        # unexpected eof. Possibly check for SSLError and retry.
        # First attempt at this resulted in Transport endpoint is already
        # connected errors.
        sock.connect((self.host, self.port))


class SBHTTPS(HTTPS):
    """HTTPS class that accepts socket timeout and bind address.
    
    xmlrpclib Transport uses a HTTP compatability class that doesn't accept a
    socket timeout, so this class adds that functionality.
    
    """

    def __init__(self, host='', port=None, strict=None,
                 timeout=DEFAULT_TIMEOUT, src_ip=None, **ssl):
        # Don't init superclass because it doesn't pass timeout and src_ip to
        # our connection class.
        if port == 0:
            port = None
        con = SBHTTPSConnection(host, port, strict, timeout=timeout,
                                src_ip=src_ip, **ssl)
        ssl_ctx = ssl['ssl_context']
        self._setup(con)
        assert isinstance(self._conn, SBHTTPSConnection)
        self.ssl_ctx = ssl_ctx
        self._conn.ssl_ctx = ssl_ctx

    def get_session(self):
        return self._conn.get_session()

    def set_session(self, sess):
        return self._conn.set_session(sess)


class HandlerLoggingMixIn(object):

    def build_request_logger(self):

        # format
        fmt = '%(asctime)s: %(message)s'

        logger = logging.Logger('scatterbytes_https_server')
        formatter = logging.Formatter(fmt=fmt)
        file_path = getattr(self.server, 'requests_log_path', None)
        if file_path is None:
            # stdout handler
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.RotatingFileHandler(file_path, maxBytes=2**20)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.request_logger = logger

    def log_message(self, format, *args):
        if not hasattr(self, 'request_logger'):
            self.build_request_logger()
        msg = "%s - - [%s] %s\n" % (self.address_string(),
                                    self.log_date_time_string(),
                                    format % args)
        self.request_logger.info(msg)


class SBHTTPSServer(SSL.SSLServer):
    """HTTPS Server

    By default, it listens on all interfaces.

    """

    def __init__(self, server_address, request_handler_class, ssl_context):
        ssl_context.set_session_cache_mode(m2.SSL_SESS_CACHE_BOTH)
        SSL.SSLServer.__init__(self, server_address,
            request_handler_class, ssl_context
        )

    def _handle_request_noblock(self):
        """Handle a request without blocking
        
        This is the method called when the server is started with
        serve_forever.
        
        """
        request = None
        client_address = None
        _send_traceback_header = True
        try:
            (request, client_address) = self.get_request()
            if self.verify_request(request, client_address):
                # FIXME - work-around for circular dep
                from . import crypt
                # make the client cert available
                cert = crypt.Certificate(
                    cert_string=request.get_peer_cert().as_pem()
                )
                print cert
                request.client_cert_info = {
                    'CN' : cert.CN,
                    'O' : cert.O,
                    'OU' : cert.OU,
                    'serial_number' : cert.serial_number
                }
                self.process_request(request, client_address)
        except (socket.error, SSLError), e:
            logger.debug('socket.error: %s' % str(e))
            self.handle_error(request, client_address, e)
            self.close_request(request)
            del request

    def close_request(self, request):
        ##logger.debug('called close_request on %s' % request)
        if request is not None:
            request.set_shutdown(
                SSL.SSL_RECEIVED_SHUTDOWN | SSL.SSL_SENT_SHUTDOWN
            )
            request.close()

    def handle_error(self, request, client_address, error=None):
        if error:
            emsg = "%s - %s" % (str(error), client_address)
            logger.error(emsg, exc_info=True)
        else:
            logger.debug('handle_error called with no error argument.')
            logger.debug('%s, %s' % (request, client_address))
            logger.error('traceback', exc_info=True)

class ThreadedSBHTTPSServer(SocketServer.ThreadingMixIn, SBHTTPSServer):
    """multi-threaded HTTPS Server

    This is a multi-threaded HTTPS server.

    By default, it listens on all interfaces.

    """

    pass
