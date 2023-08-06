"""functionality common to both client and storage nodes

UserNode
    
    base class for StorageNode and ClientNode

NodeProxyWrapper

    wrapper for a proxy to translate and check arguments and responses

"""

import os
import shutil
import zipfile
import logging
import threading
from .errors import SBError
from . import crypt

logger = logging.getLogger(__name__)

class UserNode(object):
    
    """base class for ClientNode and StorageNode

    config
        configuration instance

    control_node_proxy
        proxy instance for the control node

    snode_proxy_creator
        function to create a storage node proxy

    cert
        TLS Certificate

    """

    node_O = 'ScatterBytes Network'

    def __init__(self, control_node_proxy, snode_proxy_creator, config=None):
        if config:
            self.config = config
        else:
            self.config = self.config_class.get_config()
        self.control_node_proxy = control_node_proxy
        self.snode_proxy_creator = snode_proxy_creator
        self.ssl_context_gen_lock = threading.Lock()
        self.cert_cache = {}

    def _check_config(self):
        ca_root_cert_path = config.ca_root_cert_path
        if not os.path.exists(ca_root_cert_path):
            emsg = 'Root CA certificate should be at %s' % ca_root_cert_path
            raise SBError(emsg)

    def _create_private_key(self):
        key_path = self.config.private_key_path
        crypt.create_pkey(output_path=key_path)

    def get_certificate(self, owner_name):
        cert = self.cert_cache.get(owner_name, None)
        if not cert:
            cert_path = os.path.join(
                self.config.get('tls_dir'), "%s_cert.pem" % owner_name
            )
            cert = crypt.load_certificate(cert_path, wrap=True)
            self.cert_cache[owner_name] = cert
        return cert

    def load_certificates(self):
        """Get all server certificates from the control node.
        
        This includes:
            * software signer certificate
            * relay command signer certificate
            * root CA's CRL
            * signature for CRL (hack) - M2Crypto can't verify CRL

        """
        

        def save_cert(cert_name):
            # should be signed by ca_root_cert and not in revocation list
            cert_data = zf.read(cert_name)
            path = os.path.join(tls_dir, cert_name)
            path_tmp = os.path.join(tls_dir, cert_name + '.tmp')
            open(path_tmp, 'wb').write(cert_data)
            cert = crypt.Certificate(path_tmp)
            cert.verify(ca_root_cert.get_pubkey())
            assert cert.serial_number not in crl.serial_numbers
            # Everything check out.
            shutil.move(path_tmp, path)

        logger.info('loading certificates')
        tls_dir = self.config.get('tls_dir')
        f = self.control_node_proxy.get_certificates()
        # f should be a file-like object
        # data is in zip format
        zf = zipfile.ZipFile(f)
        assert not zf.testzip()
        crl_data = zf.read('ca_root_crl.pem')
        crl_data_sig = zf.read('ca_root_crl.pem.sig')
        # save to temporary path
        crl_path = os.path.join(tls_dir, 'ca_root_crl.pem')
        crl_path_tmp = os.path.join(tls_dir, 'ca_root_crl.pem.tmp')
        open(crl_path_tmp, 'wb').write(crl_data)
        # check the crl
        ca_root_cert = self.get_certificate('ca_root')
        crl = crypt.CRL(crl_path_tmp)
        crl.verify(crl_data_sig, ca_root_cert)
        # looks OK
        shutil.move(crl_path_tmp, crl_path)
        # get and check the certs now
        # software signing cert
        save_cert('software_signer_cert.pem')
        # software signing cert
        save_cert('relay_command_signer_cert.pem')

    def check_certificate(self):
        """Check our certificate and get a new one if needed.

        """
        if not os.path.exists(self.config.cert_path):
            self.request_new_certificate()
            
    def request_new_certificate(self):
        """Obtain an X509 certificate from the control node.
        
        If a valid certificate code is set in configuration, as is done during
        service initialization, a certificate is obtained from the control
        node.

        """

        # the private key should have already been generated. 
        if not os.path.exists(self.config.private_key_path):
            raise SBError("must first generate private key")
        logger.info('requesting X509 certificate')
        # generate a CSR
        pkey = crypt.load_pkey(self.config.private_key_path)
        csr = crypt.create_csr(pkey, self.node_id, self.node_O)
        # csr is in X509.Request form - must convert to pem in memory
        csr_pem = csr.as_pem()
        # segfault was occuring - maybe from loading this twice? - once here
        # and once at the control node
        del csr
        # base64 encoded - will require no special treatment
        recert_code = self.config.get('recert_code')
        if not recert_code:
            raise SBError('recert_code not set in config')
        proxy = self.control_node_proxy
        response = proxy.create_certificate(self.node_id, recert_code, csr_pem)
        # cert will be in pem format and ready to save
        cert_pem = response['certificate']
        cert_path = self.config.cert_path
        open(cert_path, 'wb').write(cert_pem)
        logger.info('got certificate')

    def make_ssl_context(self):
        "generate an ssl context for this node"
        with self.ssl_context_gen_lock:
            ctx = self.config.make_ssl_context()
        return ctx

    @property
    def certificate(self):
        """certificate belonging to this instance"""
        return self.config.certificate

    @property
    def node_id(self):
        return self.config.get('node_id')

    @node_id.setter
    def node_id(self, value):
        self.config.set('node_id', value)
        self.config.save()
