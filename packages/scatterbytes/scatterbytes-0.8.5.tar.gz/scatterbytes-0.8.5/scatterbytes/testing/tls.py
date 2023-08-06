import os
import time
import shutil
import zipfile
import datetime
import M2Crypto
from .. import crypt
from . import util as testutil


SERIAL_NUMBER = 10001

def get_tls_dir():
    if testutil.CACHE_DIR:
        tls_dir = os.path.join(testutil.CACHE_DIR, 'tls')
    else:
        assert testutil.TEST_DIR
        tls_dir = os.path.join(testutil.TEST_DIR, 'tls')
    if not os.path.exists(tls_dir):
        os.makedirs(tls_dir)
    return tls_dir

def get_tls_owner_dir(owner_name):
    tls_dir = get_tls_dir()
    output_path = os.path.join(tls_dir, owner_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def get_key_path(owner_name):
    owner_dir = get_tls_owner_dir(owner_name)
    key_path = os.path.join(owner_dir, 'key.pem')
    if not os.path.exists(key_path):
        pkey = create_key(owner_name)
    return key_path

def get_key(owner_name):
    key_path = get_key_path(owner_name)
    return crypt.load_pkey(key_path)

def get_sig_key(owner_name):
    k = get_key(owner_name)
    return crypt.SigKey(k)

def get_cert_path(owner_name):
    return os.path.join(get_tls_owner_dir(owner_name), 'cert.pem')

def get_cert(owner_name):
    return crypt.load_certificate(get_cert_path(owner_name))

def create_key(owner_name):
    # check for a cached key first
    owner_dir = get_tls_owner_dir(owner_name)
    key_path = os.path.join(owner_dir, 'key.pem')
    if not os.path.exists(key_path):
        pkey = crypt.create_pkey()
        pkey.save_key(key_path, None)
    else:
        pkey = crypt.load_pkey(key_path)
    return pkey

def create_cert(owner_name, CN, O, serial_number, expire_months,
                 ca_name='ca_1', is_ca=False):
    global SERIAL_NUMBER
    if serial_number is None:
        serial_number = SERIAL_NUMBER
        SERIAL_NUMBER += 1
    tls_dir = get_tls_dir()
    owner_dir = get_tls_owner_dir(owner_name)
    cert_path = os.path.join(owner_dir, 'cert.pem')
    if not os.path.exists(cert_path):
        owner_key = get_key(owner_name)
        csr = crypt.create_csr(owner_key, CN, O)
        ca_key = get_key(ca_name)
        ca_cert = None
        if owner_name != ca_name:
            ca_cert = get_cert(ca_name)
        cert = crypt.create_certificate(
            csr, serial_number, expire_months * 30, ca_key, ca_cert, is_ca,
            cert_path
        )
    else:
        cert = crypt.load_certificate(cert_path)
    return cert

def create_cert_from_csr(csr_path, ca_name='ca_1', owner_name=None):
    csr = crypt.CSR(csr_path)
    if owner_name is None:
        owner_name = csr.CN
    O = csr.O
    CN = csr.CN
    serial_number = None
    expire_months = 9
    cert = create_cert(owner_name, CN, O, serial_number, expire_months,
                       ca_name)
    owner_dir = get_tls_owner_dir(owner_name)
    # should be here
    cert_path = os.path.join(owner_dir, 'cert.pem')
    return cert_path

def _print_ca(ca_path):
    import subprocess
    cmd = ['openssl', 'x509', '-noout', '-text', '-in', ca_path]
    subprocess.call(cmd)

def gen_tls_root_ca():
    name = 'ca_root'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Root CA', 'ScatterBytes Network',
                        0, 25 * 12, 'ca_root', is_ca=True)

def gen_tls_ca_1():
    name = 'ca_1'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Intermediate CA',
                        'ScatterBytes Network', 
                        1, 24, 'ca_root', is_ca=True)

def gen_tls_ca_2():
    name = 'ca_2'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Intermediate CA',
                        'ScatterBytes Network', 
                        2, 48, 'ca_root', is_ca=True)

def gen_tls_control_node():
    name = 'control_node'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Control Node',
                        'ScatterBytes Network',
                        3, 24, 'ca_root')

def gen_tls_software_signer():
    name = 'software_signer'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Software Signer',
                        'ScatterBytes Network',
                        4, 24, 'ca_root')

def gen_tls_relay_command_signer():
    name = 'relay_command_signer'
    pkey = create_key(name)
    cert = create_cert(name, 'ScatterBytes Relay Command Signer',
                        'ScatterBytes Network',
                        5, 24, 'ca_root')

def gen_tls_node(name):
    pkey = create_key(name)
    cert = create_cert(name, name,
                        'ScatterBytes Network',
                        None, 8, 'ca_1')

def prepare_node_tls_dir(node_id, node_type):
    """copy key and certs required by a node

    This is usually performed by the node as a function of the UserNode class,
    but I don't want to excercise UserNode for every test.
    
    """

    tls_dir = get_tls_dir()
    tls_tgt_dir = os.path.join(
        testutil.TEST_DIR, '%s_nodes' % node_type, node_id, 'tls'
    )

    # this will create certs if they do not exist
    gen_tls_node(node_id)
    tls_src_dir = get_tls_owner_dir(node_id)
    # copy root cert
    shutil.copy(
        os.path.join(tls_dir, 'ca_root', 'cert.pem'),
        os.path.join(tls_tgt_dir, 'ca_root_cert.pem')
    )
    # software signer
    shutil.copy(
        os.path.join(tls_dir, 'software_signer', 'cert.pem'),
        os.path.join(tls_tgt_dir, 'software_signer_cert.pem')
    )
    # relay command signer
    shutil.copy(
        os.path.join(tls_dir, 'relay_command_signer', 'cert.pem'),
        os.path.join(tls_tgt_dir, 'relay_command_signer_cert.pem')
    )
    if node_type == 'storage':
        # node cert
        shutil.copy(
            os.path.join(tls_src_dir, 'cert.pem'),
            os.path.join(tls_tgt_dir, 'storage_node_cert.pem')
        )
        # node key
        shutil.copy(
            os.path.join(tls_src_dir, 'key.pem'),
            os.path.join(tls_tgt_dir, 'storage_node_key.pem')
        )
    else:
        # node cert
        shutil.copy(
            os.path.join(tls_src_dir, 'cert.pem'),
            os.path.join(tls_tgt_dir, 'client_node_cert.pem')
        )
        # node key
        shutil.copy(
            os.path.join(tls_src_dir, 'key.pem'),
            os.path.join(tls_tgt_dir, 'client_node_key.pem')
        )

def gen_crl(serial_numbers=None):
    # need pyopenssl to run this
    import OpenSSL
    if serial_numbers is None:
        serial_numbers = [3,4]
    serial_numbers = map(str, serial_numbers)
    tls_dir = get_tls_dir()
    cert_path = os.path.join(tls_dir, 'ca_root', 'cert.pem')
    key_path = os.path.join(tls_dir, 'ca_root', 'key.pem')
    def null_callback(self, *args):
        pass
    passphrase = null_callback
    days = 90
    output_path = os.path.join(tls_dir, 'ca_root_crl.pem')
    crl = OpenSSL.crypto.CRL()
    now = datetime.datetime.utcnow()
    now_str = now.strftime('%Y%m%d%H%M%SZ')
    for serial_number in serial_numbers:
        revoked = OpenSSL.crypto.Revoked()
        revoked.set_serial(serial_number)
        revoked.set_rev_date(now_str)
    PEM = OpenSSL.crypto.FILETYPE_PEM
    cert = OpenSSL.crypto.load_certificate(PEM, open(cert_path, 'rb').read())
    pkey = OpenSSL.crypto.load_privatekey(
        PEM, open(key_path, 'rb').read(), passphrase
    )
    open(output_path, 'wb').write(crl.export(cert, pkey, days=days))
    # sig
    crl_path = output_path
    output_path = crl_path + '.sig'
    pkey = M2Crypto.EVP.load_key(key_path)
    pkey.sign_init()
    crl_data = open(crl_path, 'rb').read()
    pkey.sign_update(crl_data)
    sig = pkey.sign_final()
    open(output_path, 'wb').write(sig)

def collect_certs():
    # put certs and crl in a zip file
    tls_dir = get_tls_dir()
    output_path = os.path.join(tls_dir, 'scatterbytes_certs.zip')
    zf = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    def add_cert(name):
        path = os.path.join(tls_dir, name, 'cert.pem')
        file_name = '%s_cert.pem' % name
        print path, file_name
        zf.write(path, file_name)
    add_cert('control_node')
    add_cert('software_signer')
    add_cert('relay_command_signer')
    add_cert('ca_1')
    add_cert('ca_root')
    i = 2
    while 1:
        name = 'ca_%s_cert.pem'
        if os.path.exists(os.path.join(tls_dir, name)):
            add_file(name)
            i += 1
        else:
            break
    # add the crl
    zf.write(os.path.join(tls_dir, 'ca_root_crl.pem'), 'ca_root_crl.pem')
    zf.write(os.path.join(tls_dir, 'ca_root_crl.pem.sig'),
                                                        'ca_root_crl.pem.sig')

def gen_tls_all():
    gen_tls_root_ca()
    gen_tls_ca_1()
    gen_tls_ca_2()
    gen_tls_control_node()
    gen_tls_software_signer()
    gen_tls_relay_command_signer()
    gen_crl()
    collect_certs()

if __name__ == '__main__':
    test_dir = testutil.setup_test_directory()
    try:
        gen_tls_all()
        gen_tls_node('whodat')
    finally:
        testutil.cleanup_test_directory()
