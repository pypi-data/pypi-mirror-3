import os
import time
import socket
import logging
import unittest
import StringIO
import threading
from SimpleHTTPServer import SimpleHTTPRequestHandler
from M2Crypto import m2
from M2Crypto import SSL
from M2Crypto import httpslib
from M2Crypto import threading as m2_threading
from scatterbytes.https import SBHTTPS
from scatterbytes.https import make_context
from scatterbytes.https import SBHTTPSServer
from scatterbytes.https import HandlerLoggingMixIn
from . import util as testutil
from . import tls

logger = logging.getLogger(__name__)


LISTEN_ADDRESS = '127.0.0.1'
LISTEN_PORT = 9876

CLIENT_NODE_NAME = 'test_client_node'
SERVER_NODE_NAME = 'test_server_node'

def setup():
    m2_threading.init()
    testutil.setup_test_directory()
    tls.gen_tls_all()
    tls.gen_tls_node(CLIENT_NODE_NAME)
    tls.gen_tls_node(SERVER_NODE_NAME)

def get_session_key(sess):
    for l in sess.as_text().split('\n'):
        if l.lstrip().startswith('Master'):
            return l.strip()

class TestHTTPRequestHandler(SimpleHTTPRequestHandler, HandlerLoggingMixIn):
   
    msg = "<html>hello you</html>"

    def send_head(self):
        msg = '<html>\n'
        msg += self.request.get_peer_cert().get_subject().as_text()
        msg += '\n</html>'
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", len(str(msg)))
        self.send_header("Last-Modified", self.date_time_string(
            time.time() - 30)
        )
        self.end_headers()
        f = StringIO.StringIO()
        f.write(msg)
        f.seek(0)
        return f

    def log_message(self, *args, **kwargs):
        return HandlerLoggingMixIn.log_message(self, *args, **kwargs)

def create_https_server():
    node_cert_path = tls.get_cert_path(SERVER_NODE_NAME)
    ca_root_path = tls.get_cert_path('ca_root')
    key_path = tls.get_key_path(SERVER_NODE_NAME)
    ctx = make_context(ca_root_path, node_cert_path, key_path)
    server_address = (LISTEN_ADDRESS, LISTEN_PORT)
    request_handler_class = TestHTTPRequestHandler
    server = SBHTTPSServer(
        (LISTEN_ADDRESS, LISTEN_PORT), TestHTTPRequestHandler, ctx
    )
    return server


def create_client_ssl_context():
    node_cert_path = tls.get_cert_path(CLIENT_NODE_NAME)
    ca_root_path = tls.get_cert_path('ca_root')
    key_path = tls.get_key_path(CLIENT_NODE_NAME)
    ctx = make_context(ca_root_path, node_cert_path, key_path, mode='client')
    return ctx


class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        self.server = create_https_server()
        self.server_thread = \
                        threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        print 'started server'

    def test_SBHTTPS(self):
        ctx = create_client_ssl_context()
        ssl = {'ssl_context' : ctx}
        h = SBHTTPS(host=LISTEN_ADDRESS, port=LISTEN_PORT, **ssl)
        h.connect()
        sess = h.get_session()
        h.putrequest('GET', '/test.html')
        h.endheaders()
        (status, reason, headers) = h.getreply()
        msg = h.getfile().read()
        self.assert_('test_client_node' in msg)
        h.close()

    def test_resume_session(self):
        ctx = create_client_ssl_context()
        ssl = {'ssl_context' : ctx}
        sess = None
        sess_key = None
        sess_key_last = None
        for i in xrange(10):
            try:
                hcon = SBHTTPS(host=LISTEN_ADDRESS, port=LISTEN_PORT, **ssl)
                if sess:
                    hcon.set_session(sess)
                hcon.connect()
                sess = hcon.get_session()
                ctx.add_session(sess)
                hcon.putrequest('GET', '/')
                hcon.endheaders()
                (status, reason, headers) = hcon.getreply()
                sess_key = get_session_key(sess)
                if sess_key_last:
                    self.assertEqual(sess_key_last, sess_key)
                self.sess_key_last = sess_key
                response = hcon.getfile().read()
                self.assert_('test_client_node' in response)
                hcon.close()
                del hcon
            except Exception, e:
                print e
                del hcon
                raise

    def tearDown(self):
        time.sleep(1)
        print threading.enumerate()
        print 'shutting down server'
        # The server thread is dying when an error is encountered.
        assert self.server_thread.isAlive()
        t = threading.Thread(target=self.server.shutdown)
        t.start()
        print 'joining shutdown thread'
        t.join()
        print threading.enumerate()
        print 'shutdown server'
        # Must let GC close socket. See explaination in
        # ServerManagementTestCase.
        del self.server
        self.server_thread.join()


class ServerManagementTestCase(unittest.TestCase):
    """Test server startup and shutdown."""

    def test_server_unbind(self):
        """Test that the server releases the port when it shuts down."""
        # start
        self.server = create_https_server()
        self.server_thread = \
                        threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        print 'started server'
        time.sleep(1)
        # stop
        print threading.enumerate()
        print 'shutting down server'
        # The server thread is dying when an error is encountered.
        assert self.server_thread.isAlive()
        t = threading.Thread(target=self.server.shutdown)
        t.start()
        print 'joining shutdown thread'
        t.join()
        print threading.enumerate()
        print 'shutdown server'
        # M2Crypto does not close the socket, as explained in httpslib.py:52.
        # It waits for GC to kick in and close it, so the simplist thing to do
        # is delete the server and create a new one.
        del self.server
        self.server_thread.join()
        # start
        self.server = create_https_server()
        self.server_thread = \
                        threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        print 'started server'
        time.sleep(1)
        # stop
        print threading.enumerate()
        print 'shutting down server'
        # The server thread is dying when an error is encountered.
        assert self.server_thread.isAlive()
        t = threading.Thread(target=self.server.shutdown)
        t.start()
        print 'joining shutdown thread'
        t.join()
        print threading.enumerate()
        print 'shutdown server'
        del self.server
        self.server_thread.join()


def teardown(self):
    testutil.cleanup_test_directory()
    m2_threading.cleanup()
