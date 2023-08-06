"""common configuration functionality

Contains the functionality shared by the ClientNodeConfig and
StorageNodeConfig.

"""
from __future__ import with_statement

import os
import sys
import shutil
import logging
import tempfile
import binascii
import threading
import ConfigParser
from . import https
from .errors import ConfigError

logger = logging.getLogger(__name__)

# Are we testing?

TESTING = 'SB_TESTING' in os.environ

if TESTING:
    CA_URL = 'https://controlnode.test.scatterbytes.com/ca_certs.pem'
else:
    CA_URL = 'https://controlnode.scatterbytes.com/ca_certs.pem'

# Disabled for some testing.
FSYNC_ON_SAVE=True

# Setting this will affect where data and config files are read/written to.
# This was created for testing.
DATA_DIRECTORY = None

class ConfigBase(object):

    """base class for storage and client node configs

    config_path
        full path to config file

    """

    if TESTING:
        defaults = {
            'node_id' : ('', None),
            'control_node_address' : ('controlnode.test.scatterbytes.net', None),
            'control_node_port' : (8080, 'int'),
            'debug' : (True, 'boolean'),
        }
    else:
        defaults = {
            'node_id' : ('', None),
            'control_node_address' : ('controlnode.scatterbytes.net', None),
            'control_node_port' : (8080, 'int'),
            'debug' : (False, 'boolean'),
        }

    main_section = 'main'
    cached_config = None

    def __init__(self, config_path=None):
        if config_path is None:
            config_dir = self.find_config_dir()
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, 0700)
            config_path = os.path.join(config_dir, self.config_name) 
        self.modified = False
        parser = ConfigParser.SafeConfigParser()
        self.config_path = config_path
        self.parser = parser
        self.lock = threading.RLock()
        self.read()
        # set the defaults if need be
        section = self.main_section
        if not parser.has_section(section):
            parser.add_section(section)
        updated = False
        self._setting_defaults = True
        for key in self.defaults:
            if not parser.has_option(section, key):
                updated = True
                self.set(key, self.defaults[key][0])
        self._setting_defaults = False
        config_dir = os.path.dirname(config_path)
        if not parser.has_option(section, 'tls_dir'):
            tls_dir = os.path.join(config_dir, 'tls')
            if not os.path.exists(tls_dir):
                os.makedirs(tls_dir, 0700)
            self.set('tls_dir', tls_dir)
            updated = True
        if not parser.has_option(section, 'log_path'):
            log_path = os.path.join(config_dir, self.log_filename)
            self.set('log_path', log_path)
            updated = True
        self._init_prep()
        if self.modified:
            self.save()

    def init_prep(self):
        pass

    def _init_prep(self):
        from . import crypt
        if not os.path.exists(self.ca_root_cert_path):
            logger.info('Writing Root CA Cert')
            open(self.ca_root_cert_path, 'wb').write(CA_ROOT_CERT_PEM)
            logger.info('Creating RSA Key')
        if not os.path.exists(self.private_key_path):
            crypt.create_pkey(output_path=self.private_key_path)
        self.init_prep()

    @classmethod
    def get_config(cls):
        config_dir = find_config_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_path = os.path.join(config_dir, cls.config_name)
        config = cls(config_path)
        return config

    def read(self):
        with self.lock:
            if os.path.exists(self.config_path):
                self.parser.read(self.config_path)

    def save(self):
        with self.lock:
            if not FSYNC_ON_SAVE:
                f = open(self.config_path, 'wb')
                self.parser.write(f)
                f.close()
                return
            (f, file_path) = tempfile.mkstemp(prefix='scatterbytes_')
            try:
                f = open(file_path, 'wb')
                self.parser.write(f)
                f.flush()
                os.fsync(f.fileno())
                f.close()
                shutil.move(file_path, self.config_path)
            except:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                raise
            self.modified = False

    def get(self, key, raw=False):
        with self.lock:
            parser = self.parser
            section = self.main_section
            if hasattr(self, '_get_' + key):
                return getattr(self, '_get_' + key)()
            if key in self.defaults and self.defaults[key][1]:
                method_name = 'get' + self.defaults[key][1]
                return getattr(parser, method_name)(section, key)
            else:
                try:
                    value = self.parser.get(self.main_section, key, raw=raw)
                except ConfigParser.NoOptionError:
                    return None
            return value

    def set(self, key, value):
        with self.lock:
            self.modified = True
            parser = self.parser
            if hasattr(self, '_set_' + key):
                return getattr(self, '_set_' + key)(value)
            return parser.set(self.main_section, key, str(value))

    # for convenience
    @property
    def data_directory(self):
        dd = self.get('data_directory')
        if not dd:
            return os.path.dirname(self.config_path)
        return dd

    @data_directory.setter
    def data_directory(self, value):
        # make sure it exists
        assert os.path.exists(value), '%s does not exist' % value
        self.set('data_directory', value)

    @property
    def private_key_path(self):
        key_name = '%s_key.pem'%self.config_name.split('.')[0]
        return os.path.join(self.get('tls_dir'), key_name)

    @property
    def ca_root_cert_path(self):
        return os.path.join(self.get('tls_dir'), 'ca_root_cert.pem')

    @property
    def cert_path(self):
        cert_name = '%s_cert.pem'%self.config_name.split('.')[0]
        return os.path.join(self.get('tls_dir'), cert_name)

    @property
    def certificate(self):
        from . import crypt
        return crypt.Certificate(self.cert_path)

    @property
    def cert_info(self):
        return self.certificate.info

    def make_ssl_context(self):
        "create an M2Crypto.SSL.Context" 
        # somewhat of a hack
        if self.__class__.__name__ == 'ClientNodeConfig':
            ctx_type = 'client'
        else:
            ctx_type = 'server'
        if not os.path.exists(self.cert_path):
            ctx_type = 'init'
        return https.make_context(self.ca_root_cert_path, self.cert_path,
                                  self.private_key_path, mode=ctx_type)

    @classmethod
    def find_config_dir(cls):
        return find_config_dir()

CA_ROOT_CERT_PEM = """
-----BEGIN CERTIFICATE-----
MIIC7TCCAdWgAwIBAgIBATANBgkqhkiG9w0BAQUFADAxMRAwDgYDVQQDEwdSb290
IENBMR0wGwYDVQQKExRTY2F0dGVyQnl0ZXMgTmV0d29yazAeFw0xMjAxMjAxNTA0
MTNaFw0zNzAxMTMxNTA0MTNaMDExEDAOBgNVBAMTB1Jvb3QgQ0ExHTAbBgNVBAoT
FFNjYXR0ZXJCeXRlcyBOZXR3b3JrMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEApb0M5hjLcWAt59KlyIKDrqGelrvzpH4+VW6Zqx2jqGAaMJ4uwupXuRAN
JBckHDbIZkCoBAC2edUngx8Zmbjud0EoH2nWuibWALrw/FdwYC8TMhSfwF1a7+5N
go0S7ZUKWemDl4oIDWEGPb0eIBDKujq+gsHFj9T9XEtz+zhgthqGld8SVVl6zIaJ
J54H7oslTWl23tXw0eir0uJMQqlJK2hBSzlvOBgdwKlrc8B4YJgXOH5jz0+jPuZx
vaW78wZy0WmzMv5UNg6fbghTsduMuchrBY49cGc4390hFvleoFWpBnr3D0InKqn9
5pgzX1hxx9OWC6X0F/fWHtK9nfskawIDAQABoxAwDjAMBgNVHRMEBTADAQH/MA0G
CSqGSIb3DQEBBQUAA4IBAQA1Icz1s2OgQcgXaG2qpFZYUbSjw2lbNn7JfcfiDL2A
+Y585xXMZXq482LPxkj7MxaOEY3LPIAK1mp6CD/cmbL8ZkAKgUWQnNQreCvI6wnk
WP3Amg3zYBT1puSL/FT9nF1HQ0lKu8WM6Zw+6EPc+MHw2dE0dZRvzcyvge6aiYhs
zFYTiqeEKuS8et5+8IFqQ97pH55dX8/xocsGoJuAPO+4JTrT7GdQkBB1tAL3hhbJ
cOgLVWbW40a9JXVNr+iiIKgP7oWCbpgnfkaWXSOYSOR5zTwbPG8e/wYyi8M1Ujl/
XIUOqvFRY63WUKL3DfGY+bKPPgBbi4bBxHc3UCFI5kwE
-----END CERTIFICATE-----
"""

if TESTING and 'SB_CACHE_DIR' in os.environ:
    CA_ROOT_CERT_PEM = open(
        os.path.join(
            os.environ['SB_CACHE_DIR'], 'tls', 'ca_root', 'cert.pem'
        )
    ).read()

def find_home_dir():
    if sys.platform.startswith('win'):
        home = os.environ.get('HOMEPATH', None)
        if not home:
            home = os.path.expanduser('~')
    else:
        home = os.path.expanduser('~')
    if not home:
        raise ConfigError("can't find home")
    return home

def find_data_dir():
    if DATA_DIRECTORY and os.path.exists(DATA_DIRECTORY):
        logger.debug('DATA_DIRECTORY is %s' % DATA_DIRECTORY)
        return DATA_DIRECTORY
    if sys.platform.startswith('win'):
        app_data = os.environ.get('APPDATA', None)
        if not app_data:
            app_data == find_home_dir()
        sb_dir = os.path.join(app_data, 'ScatterBytes')
    else:
        sb_dir = os.path.join(find_home_dir(), '.local', 'scatterbytes')
    if not sb_dir:
        raise ConfigError("can't find application data directory")
    return sb_dir

def find_config_dir():
    return find_data_dir()
