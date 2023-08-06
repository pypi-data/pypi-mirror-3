"""xmlrpc functionality specific to the storage node

"""

import os
import re
import shutil
import logging
import xmlrpclib
import threading
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from BaseHTTPServer import BaseHTTPRequestHandler
from M2Crypto import SSL
from ..util import datetime_from_string, datetime_to_string
from ..errors import AuthenticationError
from ..xmlrpc import RPCProxy
from ..xmlrpc import RPCRequestHandler
from ..xmlrpc import RPCServer
from ..xmlrpc import ThreadedRPCServer
from ..xmlrpc import ControlNodeProxy
from ..xmlrpc import StorageNodeProxy
from ..xmlrpc import gen_storage_node_proxy_creator
from ..https import SBHTTPSServer
from ..https import ThreadedSBHTTPSServer
from .node import StorageNode
from .node import StorageNodeConfig

logger = logging.getLogger(__name__)


class StorageXMLRPCRequestHandler(RPCRequestHandler):
    """Request handler adding GET and PUT handling for file transfers.

    Transferring binary files over XMLRPC is too wasteful because it uses
    base64 encoding, increasing the size about 30%.  This class adds GET and
    PUT handling to enable simple binary file transfer.  The information
    required to authorize the transfer is put in the headers, similar to S3's
    REST API.

    """

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    # match URL
    file_re = re.compile(
        r'^/sbfile/(C-[A-Z0-9]+)$')

    def do_GET(self):
        """Send all or part of a file."""
        client_node_id = None
        storage_node_id = None
        auth = self.headers.get('x-sb-auth')
        auth_ts = datetime_from_string(self.headers.get('x-sb-auth-ts'))
        expire_time = datetime_from_string(
                                    self.headers.get('x-sb-expire-time'))
        byte_range = self.headers.get('bytes')
        cert_info = self.request.client_cert_info
        match = self.file_re.match(self.path)
        # send either 404 or 200
        if not match:
            logger.debug('%s not found' % self.path)
            self.send_error(404, "File not found")
            return
        elif match:
            (chunk_name, ) = match.groups()
            f_args = [cert_info, auth, auth_ts, expire_time, chunk_name]
            if byte_range:
                (byte_start, byte_end) = map(int, (byte_range.split('-')))
                # HTTP uses inclusive range - we do not.
                byte_end += 1
                f_args.extend([byte_start, byte_end])
            (f, file_size) = self.server.storage_node.retrieve_chunk(*f_args)
            msg = 'sending %s of size %s' % (chunk_name, file_size)
            logger.debug(msg)
        self.send_response(206)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(file_size))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        return

    def do_PUT(self):
        """Check and store a file."""

        logger.debug('got put request')
        logger.debug(str(self.headers.items()))
        cert_info = self.request.client_cert_info
        assert cert_info
        data_size = int(self.headers['content-length'])
        sig = self.headers.get('x-sb-sig')
        sig_ts = self.headers.get('x-sb-sig-ts')
        transfer_name = self.headers.get('x-sb-transfer-name')
        chunk_hash_salt = self.headers.get('x-sb-hash-salt')
        sig_ts = datetime_from_string(sig_ts)
        expire_time = self.headers.get('x-sb-expire-time')
        expire_time = datetime_from_string(expire_time)
        chunk_name = os.path.basename(self.path)
        chunk_file = SBChunkFile(self.rfile, data_size)
        logger.debug('passing it off to storage node instance')
        try:
            response = self.server.storage_node.store_chunk(
                cert_info, sig, sig_ts, expire_time, transfer_name,
                chunk_name, chunk_hash_salt, chunk_file
            )
        except Exception, e:
            print 'error', e
            raise
        self.send_response(201)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)

    def log_message(self, format, *args):
        (host, port) = self.client_address[:2]
        address = '%s:%s' % (host, port)
        msg = "%s - - [%s] %s\n" % (address, self.log_date_time_string(),
                                    format%args)
        logger.log(19, msg)

    def report_404(self):
        self.send_response(404)
        response = "No such page"
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        self.connection.shutdown(1)

    ##def finish(self):
    ##    logger.debug('calling finish for request handler')
    ##    self.request.set_shutdown(
    ##        SSL.SSL_RECEIVED_SHUTDOWN | SSL.SSL_SENT_SHUTDOWN
    ##    )
    ##    print self.request
    ##    self.request.close()
    ##    del self.request


##class StorageNodeServer(ThreadingMixIn, SimpleXMLRPCServer):


class SBChunkFile(object):
    """Mimic a file object with read method.
    
    This is required to adapt the request handler's method for reading to the
    StorageNode.
    
    """

    max_chunk_size = 5*1024*1024
    
    def __init__(self, rfile, content_length):
        self.rfile = rfile
        self.position = 0
        self.content_length = content_length

    def read(self, size=None):
        rfile = self.rfile
        data = []
        content_length = self.content_length
        if size is None:
            while self.position < content_length:
                bytes_remaining = content_length - self.position
                chunk_size = min(bytes_remaining, self.max_chunk_size)
                data_read = rfile.read(chunk_size)
                self.position += len(data_read)
                data.append(data_read)
        else:
            read_to_pos = min(self.position + size, self.content_length) 
            while self.position < read_to_pos:
                bytes_remaining = content_length - self.position
                chunk_size = min(bytes_remaining, self.max_chunk_size, size)
                data_read = rfile.read(chunk_size)
                self.position += len(data_read)
                data.append(data_read)
        if data is not None:
            return ''.join(data)


class StorageNodeServer(RPCServer):
    """XMLRPC Server for a storage node.

    single threaded SBHTTPSServer

    """

    def __init__(self, storage_node, log_requests=True):
        self.storage_node = storage_node
        config = storage_node.config
        listen_address = config.get('listen_address')
        listen_port = config.get('listen_port')
        ssl_context = config.make_ssl_context()
        RPCServer.__init__(
            self, (listen_address, listen_port), ssl_context,
            StorageXMLRPCRequestHandler, log_requests
        )
        self.register_instance(storage_node)
                           
    def shutdown(self):
        try:
            self.storage_node.shutdown()
        finally:
            logger.debug('shutting down XMLRPC server')
            SBHTTPSServer.shutdown(self)


class ThreadedStorageNodeServer(ThreadedRPCServer):
    """XMLRPC Server for a storage node.

    multi-threaded SBHTTPSServer

    """

    def __init__(self, storage_node, log_requests=True):
        self.storage_node = storage_node
        config = storage_node.config
        # for logging requests
        self.requests_log_path = config.get('requests_log_path')
        listen_address = config.get('listen_address')
        listen_port = config.get('listen_port')
        logger.info('listening on: %s:%s' % (listen_address, listen_port))
        ssl_context = config.make_ssl_context()
        ThreadedRPCServer.__init__(
            self, (listen_address, listen_port), ssl_context,
            StorageXMLRPCRequestHandler, log_requests
        )
        self.register_instance(storage_node)

    def shutdown(self):
        try:
            self.storage_node.shutdown()
        finally:
            logger.debug('shutting down XMLRPC server')
            ThreadedSBHTTPSServer.shutdown(self)


def create_storage_node(control_node_proxy=None,
                                storage_node_proxy_creator=None, config=None):
    """factory for StorageNode

    unlike scatterbytes.storage.node.create_storage_node, this factory is
    xmlrpc specific

    """
    if config is None:
        config = StorageNodeConfig.get_config()
    if control_node_proxy is None:
        control_node_proxy = ControlNodeProxy(config)
    if storage_node_proxy_creator is None:
        storage_node_proxy_creator = gen_storage_node_proxy_creator(config)
    return StorageNode(control_node_proxy, storage_node_proxy_creator, config)

##class RCSHostRequestHandler(SimpleXMLRPCRequestHandler):
##
##    def log_message(self, format, *args):
##        (host, port) = self.client_address[:2]
##        address = '%s:%s' % (host, port)
##        msg = "%s - - [%s] %s\n" % (address, self.log_date_time_string(),
##                                    format%args)
##        logger.log(19, msg)
