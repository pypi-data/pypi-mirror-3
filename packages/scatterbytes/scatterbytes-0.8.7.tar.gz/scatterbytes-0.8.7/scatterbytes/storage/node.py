"""Storage Node

"""
from __future__ import with_statement

import os
import re
import sys
import time
import gzip
import shutil
import hashlib
import logging
import tempfile
import datetime
import threading
from operator import itemgetter
from ..config import ConfigBase
from .. import util
from .. import crypt
from ..node import UserNode
from ..errors import StaleCommandRelayError
from ..errors import ChunkChecksumError
from ..errors import RequestExpiredError
from ..errors import OutOfStorageError
from ..errors import ChunkError
from ..errors import ChunkNotFoundError
from ..errors import AuthenticationError
from ..chunk import Chunk

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = 1
from .. import __version__ as SOFTWARE_VERSION


# A chunk should never exceed two megabytes in size.
CHUNK_SIZE_MAX = 2 * 2**30

# Give enough time for relays from the control node.
TS_STRAY_PAST = datetime.timedelta(minutes=30)
# Timestamps should not be in the future (by much).
TS_STRAY_FUTURE = datetime.timedelta(seconds=30)

# Absolutely no relayed commands older than one hour.
SIGNATURE_TS_DELTA_MAX = datetime.timedelta(minutes=60)

VALID_CHUNK_NAME_RE = re.compile(r'C-[A-Z2-7]{13}')

def get_datetime():
    return util.control_node_time.utcnow()

def verify_relay_command(node, args, exclude_sigchecks=None):
    # Message will be signed and sender and receiver will be present.
    # This instance should be the receiver while the cert identity
    # should match the sender.
    # args looks like this:
    # args[0] == caller certificate info (dict with serial_number and CN)
    # args[1] == signature
    # args[2] == signature_ts
    # args[3] == expire_time
    # After inserting the serial numbers, the argument construct shall be as
    # follows.
    # sig_args[0] == signature_ts
    # sig_args[1] == sender_serial_number
    # sig_args[2] == receiver_serial_number
    # sig_args[3] == expire_time
    args = list(args)
    print str(args)
    logger.debug(str(args))
    cert_info = args[0]
    signature = args[1]
    signature_ts = args[2]
    expire_time = args[3]
    # construct signature args which include cert serial numbers
    sig_args = args[1:4]
    sig_args.insert(2, cert_info['serial_number'])
    sig_args.insert(3, node.certificate.serial_number)
    if expire_time < get_datetime():
        raise RequestExpiredError
    try:
        # should be signed by the relay command signer
        relay_command_cert = node.get_certificate('relay_command_signer')
        sigkey = crypt.SigKey(relay_command_cert.public_key)
        if exclude_sigchecks:
            # include sig_ts and expire_time by default
            for (position, arg) in enumerate(args[4:]):
                position += 1
                if position not in exclude_sigchecks:
                    sig_args.append(arg) 
        else:
            sig_args.extend(args[4:])
        sigkey.verify(sig_args)
        # signature matched - sender and receiver verified along with method
        # arguments
    except Exception, e:
        logger.error(str(e), exc_info=True)
        raise AuthenticationError

def publish(relay=False, exclude_sigchecks=None, pass_cert=False,
                                                        restricted=True):
    """Define publishing attributes.

    relay
        a call relayed from control node

    exclude_sigchecks
        position of arguments not signed

    pass_cert
        pass certificate information to method

    restricted
        should only be called by control node or via relay
    
    """
    def publish_inner(f):
        def newf(storage_node, *args):
            # first argument is always the public certificate
            caller_cert_info = args[0]
            if relay:
                verify_relay_command(storage_node, args, exclude_sigchecks)
                method_args = args[4:]
            else:
                # only the control node should call
                if restricted and caller_cert_info['CN'] != 'Control Node':
                    raise AuthenticationError
                if pass_cert:
                    method_args = args[:]
                else:
                    method_args = args[1:]
            response = f(storage_node, *method_args)
            return response
        newf.published = True
        newf.relay = relay
        return newf
    return publish_inner


class StorageChunk(Chunk):
    
    def __init__(self, chunk_path):
        Chunk.__init__(self, chunk_path)


class SendingJob(threading.Thread):
    
    def __init__(self, transfer_data, proxy):
        threading.Thread.__init__(self)
        self.transfer_data = transfer_data
        self.proxy = proxy

    def send_chunk(self):
        transfer_data = self.transfer_data
        transfer_name = transfer_data['transfer_name']
        chunk_name = transfer_data['chunk_name']
        chunk_hash_salt = transfer_data['chunk_hash_salt']
        expire_time = transfer_data['expire_time']
        signature = transfer_data['signature']
        signature_ts = transfer_data['signature_ts']
        chunk = transfer_data['chunk']
        args = [transfer_name, expire_time]
        msg = 'putting data to %s:%s with args %s'
        chunk_f = open(chunk.file_path, 'rb')
        response = self.proxy.store_chunk(
            signature, signature_ts, expire_time, transfer_name, chunk_name,
            chunk_hash_salt, chunk_f
        )

    def run(self):
        try:
            self.send_chunk()
        except:
            logging.error('send failed', exc_info=True)


class SendingQueue(threading.Thread):
    """manages queue of chunks to send

    This thread will not run in daemon mode and the parent process should wait
    on it to finish before exiting.

    """

    sleep_period = 1.0

    def __init__(self, proxy_creator, config, shutdown_event,
                                                            concurrent_max=3):
        threading.Thread.__init__(self)
        self.daemon = True
        self.job_queue_lock = threading.Lock()
        self.job_queue = []
        self.jobs = []
        self.concurrent_max = concurrent_max
        self.proxy_creator = proxy_creator
        self.config = config
        self.shutdown_event = shutdown_event

    def run(self):
        while not self.shutdown_event.is_set():
            # clean up
            for j in self.jobs:
                if not j.is_alive():
                    j.join()
                    self.jobs.remove(j)
            # start new jobs
            with self.job_queue_lock:
                while self.job_queue and len(self.jobs) < self.concurrent_max:
                    now = get_datetime()
                    # make sure it hasn't expired
                    job_info = self.job_queue.pop(0)
                    if job_info[1] < now:
                        # expired
                        continue
                    transfer_data = job_info[2]
                    proxy = self.create_proxy(uri=transfer_data['uri'])
                    msg = "creating send job for %s "
                    msg = msg % transfer_data['transfer_name']
                    logger.debug(msg)
                    job = SendingJob(transfer_data, proxy)
                    self.jobs.append(job)
                    job.start()
            time.sleep(self.sleep_period)
        logger.debug('send queue is exiting')

    def create_proxy(self, uri):
        proxy = self.proxy_creator(uri)
        return proxy

    def add(self, transfer_data, priority=2):
        msg = "adding transfer %s with priority %s"
        msg = msg % (transfer_data['transfer_name'], priority)
        logger.debug(msg)
        expire_time = transfer_data['expire_time']
        with self.job_queue_lock:
            self.job_queue.append((priority, expire_time, transfer_data))
            # sort by priority, then time entered.
            self.job_queue.sort(key=itemgetter(0,1))


class RegistrationUpdater(threading.Thread):
    """Register and periodically check the storage node status.

    """

    sleep_period = 2.0

    def __init__(self, control_node_proxy, config, shutdown_event):
        threading.Thread.__init__(
            self, name='RegistrationUpdater-%s' % (config.get('node_id'))
        )
        self.wait = 0
        self.daemon = True
        self.control_node_proxy = control_node_proxy
        self.config = config
        self.status = None
        self.shutdown_event = shutdown_event
        # shutdown event specific to this thread
        self.register_shutdown_event = threading.Event()

    def run(self):
        while not self.shutdown_event.is_set() and not \
                                    self.register_shutdown_event.is_set():
            if self.status is None and self.wait < 1:
                try:
                    self.register()
                except AuthenticationError, e:
                    logger.error('AuthenticationError')
                    return
                except Exception, e:
                    self.wait = 30
                    emsg = 'registration failed - '
                    emsg = emsg + 'trying again in %s seconds'
                    emsg = emsg % self.wait
                    logger.error(emsg)
                    # try again in 30 seconds
            elif self.wait > 1:
                self.wait = self.wait - self.sleep_period
            time.sleep(self.sleep_period)

    def shutdown(self):
        self.register_shutdown_event.set()

    def register(self):
        port = self.config.get('listen_port')
        software = 'ScatterBytes Python Client %s' % SOFTWARE_VERSION
        # report the min of what is configured and what is available
        available_storage = util.get_available_storage(
            self.config.get('storage_directory')
        )
        configured_storage = self.config.get('max_storage')
        storage = min(available_storage, configured_storage)
        args = [port, PROTOCOL_VERSION, software, storage]
        logger.info('registering')
        response = self.control_node_proxy.register_storage_node(*args)
        status = response['status']
        self.status = status
        # status for storage nodes
        # inactive
        # unavailable
        # available
        # unreachable
        # recovery required
        # recovery in progress
        # If recovery is pending, need to inventory and upload chunks.
        if status == 'unavailable':
            emsg = ('Your storage node cannot be reached on port %(port)s. '
                     'If you are behind NAT, configure it to send port '
                     '%(port)s to %(address)s.')
            logger.error(emsg % dict(port=port, address=address))
        else:
            self.registered = True
        logger.info('status is: %s' % status)
        self.status = status


class StorageNode(UserNode):
    """node that stores data chunks for the clients

    control_node_proxy
      proxy to the control node

    sending_queue
      queue used to prioritize outgoing chunks

    housekeeper
      daemon thread to prune the request log and keep time

    """

    def __init__(self, control_node_proxy, snode_proxy_creator, config=None):
        self.control_node_proxy = control_node_proxy
        if snode_proxy_creator is None:
            snode_proxy_creator = StorageNode
        UserNode.__init__(
            self, control_node_proxy, snode_proxy_creator, config=config
        )
        self.registered = False
        self.sending_queue = None
        self.registration_updater = None

    def startup(self):
        """Start threads that did not start on init.

        For instance, registration shouldn't begin until the HTTPS server is
        listening.

        """

        logger.debug('starting sending_queue and registration_updater')
        while 1:
            try:
                self.load_certificates()
                break
            except Exception as e:
                emsg = 'could not load certs - try again in 30 seconds'
                logger.error(emsg)
                logger.error(str(e))
                time.sleep(30)
        # event to shut down all threads
        self.shutdown_event = threading.Event()
        self.sending_queue = SendingQueue(
            self.snode_proxy_creator, self.config, self.shutdown_event
        )
        self.sending_queue.start()
        self.registration_updater = RegistrationUpdater(
            self.control_node_proxy, self.config, self.shutdown_event
        )
        self.registration_updater.start()

    def shutdown(self):
        """Execute cleanup operations for shutdown.
        
        """
        # Make sure we don't try to register after unregistering.
        logging.info('shutting down storage node')
        if self.registration_updater:
            self.registration_updater.shutdown()
            self.registration_updater.join()
            self.unregister()
        if hasattr(self, 'shutdown_event'):
            self.shutdown_event.set()
        if self.sending_queue:
            self.sending_queue.join()
        logging.info('clean shutdown')

    @publish(pass_cert=True, restricted=False)
    def hello(self, cert_info):
        """Say hello with certificate's CN

        Used to determine if host is reachable.

        """
        return "Hello %s!" % cert_info['CN']

    @publish()
    def send_chunk(self, chunk_name, chunk_hash_salt, dest_uri, transfer_name,
                   priority, signature, signature_ts, expire_time):
        logger.debug('request to send chunk %s' % chunk_name)
        chunk = self._get_chunk(chunk_name)
        chunk.verify_checksum()
        transfer_data = {
            'signature': signature,
            'signature_ts': signature_ts,
            'expire_time' : expire_time,
            'transfer_name' : transfer_name,
            'chunk_name' : chunk_name,
            'chunk_hash_salt' : chunk_hash_salt,
            'uri' : dest_uri,
            'chunk' : chunk
        }
        self.sending_queue.add(transfer_data, priority)
        return 'OK'

    @publish(relay=True, exclude_sigchecks=[4,])
    def store_chunk(self, transfer_name, chunk_name, chunk_hash_salt,
                                                                chunk_file):
        """Store data chunk from a client or storage node.

        transfer_name
            ID assigned to this transfer by the control node

        chunk_file
            A file like object where the chunk data can be read.

        chunk_name
            Name to use on the filesystem.

        chunk_hash_salt
            salt to use when calculating the secure hash


        This can be a storage request from either a client node or another
        storage node. In either case, the transfer is authorized by the
        control node by signing the request using this instance's public RSA
        key.

        A storage node should not report success until it has confirmed the
        transfer with the control node.

        """
        logger.info(
            'storing chunk %s in transfer %s' % (chunk_name, transfer_name)
        )
        storage_dir = self.config.get('storage_directory')
        # Make sure there is enough room to store this.
        if util.get_available_storage(storage_dir) < 10:
            raise OutOfStorageError
        chunk_name_tmp = "tmp_transfer_%s" % transfer_name
        chunk_path_tmp = os.path.join(storage_dir, chunk_name_tmp)
        logger.debug('writing to %s' % chunk_path_tmp)
        ftmp = open(chunk_path_tmp, 'wb')
        chunk_path = self.find_chunk_path(chunk_name)
        try:
            shutil.copyfileobj(chunk_file, ftmp)
            ftmp.close()
            logger.debug('checking chunk')
            chunk_tmp = StorageChunk(chunk_path_tmp)
            if chunk_tmp.size > CHUNK_SIZE_MAX:
                raise ChunkError('data size exceeds %s' % CHUNK_SIZE_MAX)
            # crc32 checksum
            chunk_tmp.verify_checksum()
            chunk_hash = chunk_tmp.calc_hash(
                util.b64decode(chunk_hash_salt)
            )
            # move it to its final path before confirming
            shutil.move(chunk_path_tmp, chunk_path)
            logger.debug('stored to %s' % chunk_path)
            logger.debug('checks OK. confirming transfer')
            response = self.confirm_transfer(
                transfer_name, chunk_name, chunk_hash
            )
            return 'OK'
        except Exception, e:
            logger.error(str(e), exc_info=True)
            if os.path.exists(chunk_path):
                os.unlink(chunk_path)
            raise
        finally:
            if os.path.exists(chunk_path_tmp):
                os.unlink(chunk_path_tmp)

    @publish()
    def delete_chunk(self, chunk_name):
        logger.info('request to delete chunk %s' % chunk_name)
        # This will raise the appropriate error if it does not exist.
        try:
            chunk = self._get_chunk(chunk_name)
            os.unlink(chunk.file_path)
            return 'OK'
        except ChunkNotFoundError:
            logger.error('did not find chunk %s for deletion' % chunk_name)
            raise

    @publish()
    def check_hash(self, chunk_name, salt):
        """compute a hash for chunk_name using salt

        This is the primary means for enforcing the integrity of a storage
        node and also serves to confirm the node is available and functioning
        properly.

        """

        if not salt:
            salt = None
        chunk = self._get_chunk(chunk_name)
        chunk_hash = chunk.calc_hash(salt=util.b64decode(salt))
        response = dict(chunk_hash=chunk_hash)
        return response

    @publish(relay=True, exclude_sigchecks=[2,3])
    def retrieve_chunk(self, chunk_name, byte_start=0, byte_end=0):
        msg = 'looking for chunk %s bytes %s-%s, %s bytes'
        msg = msg % (chunk_name, byte_start, byte_end, byte_end - byte_start)
        logger.debug(msg)
        # byte_end is inclusive
        chunk = self._get_chunk(chunk_name)
        chunk.verify_checksum()
        file_path = chunk.file_path
        f = open(file_path, 'rb')
        file_size = os.fstat(f.fileno()).st_size
        byte_range_size = byte_end - byte_start
        if byte_range_size < file_size:
            file_size = byte_range_size
        if byte_end > 0:
            file_reader = util.LimitedFileReader(f, byte_start, byte_end)
        else:
            file_reader = f
        return (file_reader, file_size)

    def confirm_transfer(self, transfer_name, chunk_name, chunk_hash):
        """Tell the control node the transfer is complete.

        If the transfer exists, the control node could confirm it by seeing
        who it was assigned to and verifying the signature.  Sending a node_id
        allows it to log any confirmations on transfers that do not exist.

        """
        logger.debug('confirming transfer %s' % transfer_name)
        f = self.control_node_proxy.confirm_transfer
        response = f(transfer_name, chunk_name, chunk_hash)
        logger.debug('transfer confirmed')
        return response

    def recover(self):
        storage_directory = self.config.get('storage_directory')
        output_path = os.path.join(storage_directory, 'recovery_info.gz')
        collect_recovery_info(storage_directory, output_path)
        try:
            self.control_node_proxy.send_recovery_data(output_path)
        finally:
            os.unlink(output_path)

    def unregister(self):
        if self.registration_updater.status == 'available':
            response = self.control_node_proxy.unregister_storage_node()
            self.registered = False
            return response

    def find_chunk_path(self, chunk_name):
        return self.config.find_chunk_path(chunk_name)

    def _get_chunk(self, chunk_name):
        chunk_path = self.find_chunk_path(chunk_name)
        return StorageChunk(chunk_path)


class StorageNodeConfig(ConfigBase):

    """StorageNode Configuration

    """

    config_name = 'storage_node.config'
    log_filename = 'storage_node.log'
    requests_log_filename = 'storage_node_requests.log'

    defaults = ConfigBase.defaults.copy()
    defaults.update({
        'listen_address' : ('0.0.0.0', None),
        'listen_port' : (8085, 'int'),
        'max_storage' : (10000, 'int'),
    })

    def __init__(self, config_path):
        ConfigBase.__init__(self, config_path)
        if self.get('storage_directory') is None:
            if self.config_path:
                path = os.path.join(
                    os.path.dirname(self.config_path), 'scatterbytes_files'
                )
            else:
                path = os.path.join(
                    scatterbytes.config.find_config_dir(), 'scatterbytes_files'
                )
            self.set('storage_directory', path)
            if not os.path.exists(path):
                os.mkdir(path)
            self.modified = True
        if self.get('requests_log_path') is None:
            requests_log_path = os.path.join(
                os.path.dirname(self.config_path),
                self.requests_log_filename
            )
            self.set('requests_log_path', requests_log_path)
            self.modified = True
        if self.modified:
            self.save()

    def find_chunk_path(self, chunk_name):
        """Find the filesystem path to chunk_name.

        To keep from overwhelming some filesystems (and users who may ask for
        a directory listing), there are 32**2 directories.  Each chunk is put
        into a directory based on the last two characters in its name. The
        last characters are used because the base32 encoding may be left
        padded, which would bias the directory contents.

        1 TB of 1 MB chunks would therefore contain 1024 directories each
        containing 1024 files.

        """
        dir = os.path.join(
            self.get('storage_directory'), chunk_name[-1], chunk_name[-2:]
        )
        if not os.path.exists(dir):
            os.makedirs(dir)
        chunk_path = os.path.join(dir, chunk_name)
        logger.debug('chunk_path is %s' % chunk_path)
        return chunk_path

StorageNode.config_class = StorageNodeConfig

def create_storage_node(control_node_proxy=None, snode_proxy_creator=None,
                                                                config=None):
    sn = StorageNode(control_node_proxy, snode_proxy_creator, config)
    return sn

def collect_recovery_info(storage_directory, output_path):
    """Collect name and hash of every chunk and write it to a file.

    """
    logger.info('collecting filenames and hashes for recovery')
    logger.info('This could take a while.  Please do not interrupt.')
    zfile = gzip.open(output_path, 'wb')
    for (root, dirs, filenames) in os.walk(storage_directory):
        for filename in filenames:
            if not VALID_CHUNK_NAME_RE.match(filename):
                logger.warning('invalid filename %s' % filename)
                # don't report or delete anything but our files
                continue
            chunk_path = os.path.join(root, filename)
            try:
                chunk = StorageChunk(chunk_path)
                hash = chunk.calc_hash()
            except Exception, e:
                emsg = 'unexpected error occurred for file %s' % filename
                logger.error(emsg, exc_info=True)
            zfile.write('%s,%s\n' % (filename, hash))
    zfile.close()


class IntegrityChecker(threading.Thread):
    """checks the integrity of stored files using crc32 checksum

    """

    def __init__(self, storage_directory, control_node_proxy):
        threading.Thread.__init__(self)
        self.storage_directory = storage_directory
        self.control_node_proxy = control_node_proxy

    def run(self):
        logger.info('Integrity checks started.')
        try:
            self.checksum_files()
        except Exception, e:
            logger.error('Integrity checks failed.', exc_info=True)
        logger.info('Integrity checks completed.')

    def checksum_files(self):
        corrupt_files = []
        for (root, dirs, filenames) in os.walk(self.storage_directory):
            for filename in filenames:
                # make sure the filename looks valid
                if not VALID_CHUNK_NAME_RE.match(filename):
                    logger.warning('invalid filename %s' % filename)
                    continue
                chunk_path = os.path.join(root, filename)
                chunk = StorageChunk(chunk_path)
                try:
                    chunk.verify_checksum()
                except ChunkChecksumError:
                    logger.warning('chunk %s failed crc32 check' % filename)
                    corrupt_files.append(filename)
                except Exception, e:
                    emsg = 'unexpected error occurred for file %s' % filename
                    logger.error(emsg, exc_info=True)
                    corrupt_files.append(filename)
        # If there are corrupt files, they can be replaced.  A large number of
        # corrupt files indicates something may be terribly wrong.
        # If there are fewer than 10 corrupt files, try to replace them.
        # Otherwise, change status until this can be resolved.
        control_node_proxy = self.control_node_proxy
        if corrupt_files:
            if len(corrupt_files) > 10:
                emsg = ("%s corrupt files were detected. Recovery will not "
                        "be attempted because there is likely a problem "
                        "with the storage medium.")
                logger.error(emsg % len(corrupt_files))
            else:
                control_node_proxy.replace_chunks(corrupt_files) 
                emsg = '%s corrupt chunks detected. Requested replacements.'
                logger.warning(emsg % len(corrupt_files))
            return
