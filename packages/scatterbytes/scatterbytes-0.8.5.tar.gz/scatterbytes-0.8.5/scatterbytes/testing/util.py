import os
import sys
import time
import uuid
import socket
import struct
import shutil
import random
import hashlib
import logging
import datetime
import tempfile
import M2Crypto
from .. import crypt
from .. import config
from ..util import base10_to_base32
from ..client.chunk import split_file
from ..client.chunk import append_checksum
from ..client.chunk import calc_chunk_sizes
from ..client.chunk import CHUNK_SIZE_MIN
from ..client.chunk import CHUNK_SIZE_TGT
from ..client.chunk import CHUNK_SIZE_MAX
from ..client.util import create_flags

logger = logging.getLogger(__name__)

FAKE_FILE_HASH = crypt.calc_hash('hello world', 'salt')

TEST_DIR = None

# Data that is expensive to compute, like RSA keys, can be cached between test
# runs by setting the SB_CACHE_DIR environment variable.
CACHE_DIR = None
if 'SB_CACHE_DIR' in os.environ:
    CACHE_DIR = os.path.abspath(os.environ['SB_CACHE_DIR'])
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
def setup_test_directory():
    global TEST_DIR
    if TEST_DIR is None:
        TEST_DIR = tempfile.mkdtemp(prefix='sb_tests_') 
    # in case it was deleted
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
    return TEST_DIR

def cleanup_test_directory():
    global TEST_DIR
    if TEST_DIR is not None and os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def create_temp_file(byte_count):
    if CACHE_DIR:
        test_files_path = os.path.join(CACHE_DIR, 'test_files')
    else:
        setup_test_directory()
        test_files_path = os.path.join(TEST_DIR, 'test_files')
    if not os.path.exists(test_files_path):
        os.makedirs(test_files_path)
    # try to find one that exists for this size
    for listing in os.listdir(test_files_path):
        path = os.path.join(test_files_path, listing)
        if listing.startswith('sb_') and os.path.isfile(path) and \
                                    os.stat(path).st_size == byte_count:
            return path
    (handle, path) = tempfile.mkstemp(prefix='sb_', dir=test_files_path)
    logger.debug('creating test file %s bytes' % byte_count)
    open(path, 'wb').write(os.urandom(byte_count))
    logger.debug('finished creating test file')
    return path

def create_chunks(file_path, key):
    file_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    output_dir = os.path.join(dir_name, '%s_chunks' % file_name)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.listdir(output_dir):
        split_file(file_path, output_dir, True, True, key)

def ip_to_integer(ip):
    return struct.unpack('!L', socket.inet_aton(ip))[0]

def integer_to_ip(n):
    return socket.inet_ntoa(struct.pack('!L',n))

def integer_to_chunk_name(i):
    return 'C-%s' % base10_to_base32(i).rjust(13, 'A')
