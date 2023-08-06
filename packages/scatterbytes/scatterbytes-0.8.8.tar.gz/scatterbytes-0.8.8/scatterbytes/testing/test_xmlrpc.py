import unittest
import threading
import xmlrpclib
from M2Crypto import m2
from M2Crypto import SSL
from .. import xmlrpc
from ..https import make_context
from . import tls
from . import util as testutil

def setup():
    testutil.setup_test_directory()
    tls.gen_tls_all()

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        client_name = 'xmlrpc_client'
        server_name = 'xmlrpc_server'
        # generate a cert
        tls.gen_tls_node(client_name)
        tls.gen_tls_node(server_name)
        ca_cert_path = tls.get_cert_path('ca_root')
        # client_context
        key_path = tls.get_key_path(client_name)
        cert_path = tls.get_cert_path(client_name)
        self.client_ctx = make_context(ca_cert_path, cert_path, key_path)
        # server_context
        key_path = tls.get_key_path(server_name)
        cert_path = tls.get_cert_path(server_name)
        server_ctx = make_context(ca_cert_path, cert_path, key_path, 'server')
        self.server = xmlrpc.RPCServer(('127.0.0.1', 8888),
                                       ssl_context=server_ctx)
        def echo(cert_info, message):
            return message
        self.server.register_function(echo, 'echo')
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

    def test_echo(self):
        url = 'https://127.0.0.1:8888'
        client = xmlrpc.RPCProxy(url, self.client_ctx)
        for i in xrange(100):
            try:
                print client.echo('hello world - %s' % i)
            except Exception, e:
                print e
                raise

    def test_register_instance(self):

        class A(object):

            def method_1(self, cert_info):
                return 'm1'

            method_1.published = True

            def method_2(self, cert_info):
                return 'm2'

            method_2.published = True

        instance = A()
        self.server.register_instance(instance)
        url = 'https://127.0.0.1:8888'
        client = xmlrpc.RPCProxy(url, self.client_ctx)
        self.assertEqual(client.method_1(), 'm1')
        self.assertEqual(client.method_2(), 'm2')

    def test_method_publish(self):

        class A(object):

            def method_1(self, cert_info):
                return 'm1'

            method_1.published = True

            def method_2(self, cert_info):
                return 'm2'

        instance = A()
        self.server.register_instance(instance)
        url = 'https://127.0.0.1:8888'
        client = xmlrpc.RPCProxy(url, self.client_ctx)
        self.assertEqual(client.method_1(), 'm1')
        self.assertRaises(xmlrpclib.Fault, client.method_2)


    def tearDown(self):
        shutdown_thread = threading.Thread(target=self.server.shutdown)
        print 'shutting down'
        shutdown_thread.start()
        shutdown_thread.join()
        self.server_thread.join()
        # deleting this reference explicitly is critical to the release of the
        # bound port
        del self.server

def teardown():
    testutil.cleanup_test_directory()
