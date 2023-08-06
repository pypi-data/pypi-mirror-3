import os
import shutil
import unittest
from .. import util
from .. import crypt
from ..client.node import ClientNodeConfig
from . import util as testutil

class StandardClientTestCase(unittest.TestCase):

    def setUp(self):
        testutil.setup_test_directory()
        config_path = os.path.join(
            testutil.TEST_DIR, 'client_nodes', 'AAA',
            ClientNodeConfig.config_name
        )
        self.config = ClientNodeConfig(config_path=config_path)

    def test_defaults(self):
        config = self.config
        self.assertEqual(config.get('encrypt'), True)
        newkey = util.b64encode(os.urandom(32))
        config.encrypt_key = newkey
        self.assertEqual(newkey, config.encrypt_key)
        config.set('encrypt', False)
        self.assertEqual(config.get('encrypt'), False)
        self.assertEqual(config.get('compress'), True)
        self.assertEqual(config.get('download_thread_count'), 10)
        self.assertEqual(config.get('upload_thread_count'), 3)

    def tearDown(self):
        testutil.cleanup_test_directory()
