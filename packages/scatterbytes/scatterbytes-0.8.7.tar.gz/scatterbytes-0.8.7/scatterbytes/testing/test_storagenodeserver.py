import os
import time
import logging
import hashlib
import unittest
import threading
import xmlrpclib
from M2Crypto import m2
from M2Crypto import SSL
from . import tls
from . import util as testutil
from .. import util
from .. import errors
from ..xmlrpc import gen_storage_node_proxy_creator
from ..xmlrpc import StorageNodeProxy
from ..client.node import ClientNode
from ..client.node import ClientNodeConfig
from ..client.chunk import split_file, append_checksum
from ..storage.node import StorageNode
from ..storage.xmlrpc import create_storage_node
from ..storage.xmlrpc import StorageNodeServer
from . import node as node_util
from .test_storagenode import gen_chunk_name
from .test_storagenode import gen_transfer_name
from .test_storagenode import make_expiretime
from .test_storagenode import ControlNodeMockup

logger = logging.getLogger(__name__)

TEST_FILE_PATH = None
TEST_CHUNKS = None

LISTEN_ADDRESS = '127.0.0.1'


def setup():
    TEST_DIR = testutil.setup_test_directory()
    global TEST_FILE_PATH
    TEST_FILE_PATH = testutil.create_temp_file(int(2**22 * 1.5))
    output_dir = os.path.join(TEST_DIR, 'file_chunks')
    os.mkdir(output_dir)
    logger.debug('splitting file %s' % TEST_FILE_PATH)
    chunks = split_file(TEST_FILE_PATH, output_dir, compress=False,
                        encrypt=False)
    global TEST_CHUNKS
    TEST_CHUNKS = chunks
    logger.debug('done splitting file')
    # generate tls keys and certs
    tls.gen_tls_all()


def make_control_node_context():
    ca_cert_path = tls.get_cert_path('ca_root')
    key_path = tls.get_key_path('control_node')
    cert_path = tls.get_cert_path('control_node')
    ctx = SSL.Context('tlsv1')
    ctx.load_cert_chain(cert_path, key_path)
    ctx.load_verify_locations(ca_cert_path)
    ctx.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, 2)
    ctx.set_session_id_ctx('ScatterBytes')
    ctx.load_client_ca(ca_cert_path)
    ctx.set_session_cache_mode(m2.SSL_SESS_CACHE_SERVER)
    return ctx


class BaseMixIn(object):

    def _upload_chunk(self, chunk, transfer_name, chunk_name):
        chunk_size = chunk.size
        expire_time = make_expiretime(2)
        transfers = self.control_node_proxy.transfers
        self.transfers = transfers
        snode_serial_number = self.snode_config.cert_info['serial_number']
        transfers[transfer_name] = {
            'chunk' : chunk,
            'chunk_name' : chunk_name,
            # serial number
            'receiving_node_id': snode_serial_number,
            'chunk_name' : chunk_name
        }
        self.transfer = transfers[transfer_name]
        self.transfer_name = transfer_name
        # auth relayed from the server through the client
        cert_info = self.client_config.cert_info
        # sender serial, receiver serial, .., ..
        chunk_hash_salt = util.b64encode(os.urandom(4))
        chunk.salt = chunk_hash_salt
        sn_args = [1002, self.snode_config.cert_info['serial_number'],
                   expire_time, transfer_name, chunk_name, chunk_hash_salt]
        sn_proxy = self.make_sn_proxy()
        self.control_node_proxy._sign_args(sn_args)
        # don't have to pass serial numbers
        del sn_args[2]
        del sn_args[2]
        f = open(chunk.file_path, 'rb')
        sn_args.append(f)
        response = sn_proxy.store_chunk(*sn_args)
        self.assertEqual(response, 'OK')

    def create_storage_node_server(self):
        if not hasattr(self, 'storage_nodes'):
            self.storage_nodes = {}
            self.storage_node_ports = []
        node_names = self.storage_nodes.keys()
        node_names.sort()
        if not node_names:
            node_name = 'SN000001'
            node_port = 40000
        else:
            last_name = node_names[-1]
            node_name = 'SN' + str(int(last_name[2:]) + 1).zfill(6)
            node_port = self.storage_node_ports[-1] + 1
        self.storage_node_ports.append(node_port)
        # generate a cert
        ##tls.gen_tls_node(node_name)
        snode_config = node_util.prepare_node(node_name, 'storage', True)
        snode_config.set('listen_address', LISTEN_ADDRESS)
        snode_config.set('listen_port', node_port)
        proxy_creator = gen_storage_node_proxy_creator(snode_config)
        storage_node = create_storage_node(
            self.control_node_proxy,
            proxy_creator,
            snode_config
        )
        server = StorageNodeServer(storage_node)
        server.storage_node.startup()
        t = threading.Thread(target=server.serve_forever)
        t.start()
        self.storage_nodes[node_name] = {
            'port' : node_port,
            'server' : server,
            'server_thread' : t,
            'storage_node' : storage_node
        }
        return node_name

    @property
    def storage_node(self):
        # default storage node
        return self.storage_nodes[self.snode_name]['storage_node']

    def make_sn_proxy(self, ssl_context=None, port=None):
        if ssl_context is None:
            ssl_context = self.client_ctx
        if port is None:
            port = self.snode_port
        sn_proxy = StorageNodeProxy(
            "https://%s:%s" % (LISTEN_ADDRESS, port), ssl_context
        )
        return sn_proxy

    def test_check_hash(self):
        chunk = TEST_CHUNKS[3]
        sn_proxy = self.make_sn_proxy(ssl_context=self.control_node_ctx)
        self._upload_chunk(chunk, gen_transfer_name(), gen_chunk_name())
        chunk_name = self.transfer['chunk_name']
        salt = os.urandom(4)
        hash = chunk.calc_hash(salt=salt)
        cert_info = self.control_node_proxy._cert.info
        response = sn_proxy.check_hash(chunk_name, util.b64encode(salt)) 
        self.assertEqual(response['chunk_hash'], hash)


class SingleThreadedTestCase(unittest.TestCase, BaseMixIn):

    def setUp(self):
        client_node_name = 'EEFFGGFF'
        self.client_node_name = client_node_name
        # generate a cert
        tls.gen_tls_node(client_node_name)
        client_config = node_util.prepare_node(
            client_node_name, 'client', True
        )
        self.client_config = client_config
        control_node_proxy = ControlNodeMockup()
        self.control_node_proxy = control_node_proxy
        # create 1 storage node to begin with
        self.snode_name = self.create_storage_node_server()
        snode_info = self.storage_nodes[self.snode_name]
        self.snode_port = snode_info['port']
        self.snode_config = snode_info['storage_node'].config
        # client_context
        self.client_ctx = client_config.make_ssl_context()
        # control node context
        self.control_node_ctx = make_control_node_context()

    def test_hello(self):
        sn_proxy = self.make_sn_proxy()
        response = sn_proxy.hello()
        self.assertEqual(response, "Hello %s!" % self.client_node_name)

    def test_send_chunk(self):
        chunk = TEST_CHUNKS[0]
        transfer_name = gen_transfer_name()
        chunk_name = gen_chunk_name()
        self._upload_chunk(chunk, transfer_name, chunk_name)
        # create a nother server
        snode2_name = self.create_storage_node_server()
        snode2_info = self.storage_nodes[snode2_name]
        snode2_port = snode2_info['port']
        snode2 = snode2_info['storage_node']
        # need the serial number to sign the request
        snode2_serial_number = snode2.certificate.serial_number
        # create argument list to sign
        from_serial = self.storage_node.certificate.serial_number
        to_serial = snode2_serial_number
        expire_time = make_expiretime(5)
        transfer_name = gen_transfer_name()
        auth_args = [from_serial, to_serial, expire_time, transfer_name,
                     chunk_name, chunk.salt]
        self.control_node_proxy._sign_args(auth_args)
        chunk_name = self.transfer['chunk_name']
        signature = auth_args[0]
        signature_ts = auth_args[1]
        # register a new transfer on the control node
        self.transfers[transfer_name] =  {
            'chunk_name' : chunk_name,
            'chunk' : chunk,
            'receiving_node_id': to_serial,
        }
        # use the context of the control node
        sn_proxy = self.make_sn_proxy(self.control_node_ctx, self.snode_port)
        priority = 20
        uri = "https://%s:%s" % ('127.0.0.1', snode2_port)
        response = sn_proxy.send_chunk(
            chunk_name, chunk.salt, uri, transfer_name, priority,
            signature, signature_ts, expire_time
        )
        self.assertEqual(response, 'OK')
        # Second storage node should have the chunk.
        # Give it time to make the transfer.
        time.sleep(.5)
        try:
            chunk_new = snode2._get_chunk(chunk_name)
        except errors.ChunkNotFoundError:
            time.sleep(.5)
            chunk_new = snode2._get_chunk(chunk_name)
        self.assertEqual(
            chunk.calc_hash(),
            chunk_new.calc_hash()
        )

    def test_store_chunk(self):
        chunk = TEST_CHUNKS[0]
        transfer_name = gen_transfer_name()
        chunk_name = gen_chunk_name()
        self._upload_chunk(chunk, transfer_name, chunk_name)
        # check what was sent to the server
        cn_proxy = self.control_node_proxy
        args = cn_proxy.confirm_transfer_args
        self.assertEqual(args[0], self.storage_node.certificate.serial_number)
        self.assertEqual(args[1], transfer_name)
        self.assertEqual(args[2], chunk.calc_hash(util.b64decode(chunk.salt)))
        new_path = self.storage_node.config.find_chunk_path(
                                    self.transfer['chunk_name'])
        self.assert_(os.path.exists(new_path))

    def test_retrieve_chunk(self):
        chunk = TEST_CHUNKS[3]
        expire_time = make_expiretime(30)
        self._upload_chunk(chunk, gen_transfer_name(), gen_chunk_name())
        chunk_name = self.transfer['chunk_name']
        f = open(chunk.file_path, 'rb')
        f.seek(30)
        byte = f.read(1)
        f.close()
        expire_time = make_expiretime(5)
        # sender serial, receiver serial, .., ..
        auth_args = [1002, self.storage_node.certificate.serial_number,
                     expire_time, chunk_name]
        self.control_node_proxy._sign_args(auth_args)
        args = auth_args
        args.insert(6, 31)
        args.insert(6, 30)
        # remove serial
        args.pop(2)
        args.pop(2)
        sn_proxy = self.make_sn_proxy()
        f = sn_proxy.retrieve_chunk(*args) 
        self.assertEqual(f.read(), byte)
        # read the last byte
        file_size = os.stat(chunk.file_path).st_size
        f = open(chunk.file_path, 'rb')
        f.seek(file_size - 1)
        byte = f.read()
        f.close()
        args[-2] = file_size - 1
        args[-1] = file_size
        f = sn_proxy.retrieve_chunk(*args) 
        self.assertEqual(f.read(), byte)
        # read the first byte
        f = open(chunk.file_path, 'rb')
        byte = f.read(1)
        f.close()
        args[-2] = 0
        args[-1] = 1
        f = sn_proxy.retrieve_chunk(*args) 
        self.assertEqual(f.read(), byte)
        # read 200K
        f = open(chunk.file_path, 'rb')
        f.seek(500)
        bytes = f.read(2048)
        f.close()
        args[-2] = 500
        args[-1] = 500 + 2048
        f = sn_proxy.retrieve_chunk(*args) 
        self.assertEqual(
            hashlib.sha1(f.read()).hexdigest(),
            hashlib.sha1(bytes).hexdigest()
        )
        # read entire file
        args[-2] = 0
        args[-1] = file_size
        f = sn_proxy.retrieve_chunk(*args) 
        self.assertEqual(
            hashlib.sha1(f.read()).hexdigest(),
            hashlib.sha1(open(chunk.file_path, 'rb').read()).hexdigest()
        )

    def test_delete_chunk(self):
        chunk = TEST_CHUNKS[3]
        self._upload_chunk(chunk, gen_transfer_name(), gen_chunk_name())
        chunk_name = self.transfer['chunk_name']
        chunk_path = self.storage_node.config.find_chunk_path(chunk_name)
        self.assert_(os.path.exists(chunk_path))
        sn_proxy = self.make_sn_proxy(ssl_context=self.control_node_ctx)
        response = sn_proxy.delete_chunk(chunk_name)
        self.assertEqual(response, 'OK')
        self.assert_(not os.path.exists(chunk_path))

    def tearDown(self):

        for (node_name, node_info) in self.storage_nodes.items():
            logger.debug('shutting down %s' % node_name)
            server = node_info['server']
            t_shut = threading.Thread(target=server.shutdown)
            self.storage_nodes[node_name]['shutdown_thread'] = t_shut
            t_shut.start()
        for (node_name, node_info) in self.storage_nodes.items():
            logger.debug('joining %s shutdown thread' % node_name)
            node_info['shutdown_thread'].join()
            logger.debug('joining %s server thread' % node_name)
            node_info['server_thread'].join()
            del node_info['server']
        del self.storage_nodes

def teardown():
    testutil.cleanup_test_directory()
