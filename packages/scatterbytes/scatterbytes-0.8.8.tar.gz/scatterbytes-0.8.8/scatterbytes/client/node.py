"""client node

The client uploads files to storage nodes.  Files are split into chunks,
optionally compressed and encrypted, then uploaded to storage nodes.  The
control node tracks where each file chunk is stored.

"""

import re
import os
import math
import time
import Queue
import shutil
import pickle
import logging
import datetime
import tempfile
import threading
from operator import attrgetter
from .. import util
from .. import crypt
from ..config import ConfigBase
from ..config import find_data_dir
from ..errors import SBError
from ..errors import TransferLogError
from ..errors import FileNotFoundError, VolumeNotFoundError
from ..errors import FileExistsError
from ..node import UserNode
from . import chunk as chunklib
from . import util as client_util
from .downloader import ThreadedDownloader
from .util import ChunkTransferLog
from .util import FLAGS


logger = logging.getLogger(__name__)


class FileChunkInfo(object):
    """information about a chunked file

    The information includes if a file is encrypted or compressed, and the
    volume name, file name, and ID of the file on the Control Node.

    
    """
    
    def __init__(self):
        # cache read values
        self._data = {}

    @property
    def chunking_complete(self):
        """if the file chunking completed"""
        required_keys = ['encrypted', 'compressed', 'file_path']
        for key in required_keys:
            if not self.has_value(key):
                return False
        return True

    @property
    def encrypted(self):
        return self.get_value('encrypted')

    @property
    def compressed(self):
        return self.get_value('compressed')

    @property
    def file_path(self):
        return self.get_value('file_path')

    def has_value(self, attr_name):
        return attr_name in self._data

    def get_value(self, attr_name):
        return self._data.get(attr_name)

    def set_value(self, attr_name, value):
        self._data[attr_name] = value


class ClientNode(UserNode):
    """client node for sending and retrieving files

    control_node_proxy
        proxy for the control node

    """

    def __init__(self, control_node_proxy=None,
                 snode_proxy_creator=None, config=None):
        UserNode.__init__(self, control_node_proxy, snode_proxy_creator,
                          config)

    def create_volume(self, name, mirror_count):
        return self.control_node_proxy.create_volume(name, mirror_count) 

    def list_volumes(self):
        volume_data = self.control_node_proxy.list_volumes()
        return volume_data

    def find_files(self, volume_name, search_criteria, offset=0):
        """find files matching search criteria

        volume_name
            name of the volume to search on

        search_criteria
            list of tuples containing expressions for search
            example:
                    ['AND',
                     ('author', '=', 'Joe Smith'),
                     (
                        'OR',
                        ('filetype', '=', 'jpg'),
                        ('filetype', '=', 'tif')
                        ('filetype', '=', 'gif')
                     )
                    ]
    
            Both operands and conjunctions can be negated by prepending a "!"
            character. For example:
                     ['!AND',
                     ('author', '!=', 'Joe Smith'),
                     (
                        'OR',
                        ('filetype', '=', 'jpg'),
                        ('filetype', '=', 'tif')
                        ('filetype', '=', 'gif')
                     )
                    ]
       
        """

        cn = self.control_node_proxy
        return cn.find_files(volume_name, search_criteria, offset)

    def list_files(self, volume_name, detail_level=0):
        search_criteria = ('file_name', '~', '.*')
        file_list = []
        offset = 0
        cn = self.control_node_proxy
        while 1:
            response = cn.find_files(
                volume_name, search_criteria, detail_level, offset
            )
            file_info = response['file_info']
            file_list.extend(file_info)
            if len(file_info) < response['limit']:
                break
            else:
                offset = offset + len(file_info)
        return file_list

    def prepare_file(self, file_path, encrypt=True, compress=True):
        """Prepare a file for uploading.

        encrypt
            encrypt using AES-256

        compress
            compress using zlib


        """
        # Use the file hash as a directory name to store the chunks.
        hash = crypt.calc_file_hash(file_path, return_type='base32')
        working_dir = self.config.get('working_directory')
        uploads_dir = os.path.join(working_dir, 'uploads')
        if not os.path.exists(uploads_dir):
            os.mkdir(uploads_dir)
        chunk_output_dir = os.path.join(uploads_dir, hash)
        chunk_info_path = os.path.join(chunk_output_dir,
                                                        'file_chunk_info.pkl')
        if os.path.exists(chunk_output_dir):
            # Check to see if file preparation completed.  If so, just return.
            # Otherwise, clear the directory and start over.
            chunk_info = pickle.load(open(chunk_info_path, 'rb'))
            if chunk_info.chunking_complete:
                logger.info('file is already split')
                return chunk_output_dir
            else:
                shutil.rmtree(chunk_output_dir)
                os.mkdir(chunk_output_dir)
        else:
            os.mkdir(chunk_output_dir)
        encrypt_key = self.config.encrypt_key
        chunklib.split_file(file_path, chunk_output_dir, compress, encrypt,
                            encrypt_key)
        chunk_info = FileChunkInfo()
        chunk_info.set_value('file_path', file_path)
        chunk_info.set_value('encrypted', encrypt)
        chunk_info.set_value('compressed', compress)
        pickle.dump(chunk_info, open(chunk_info_path, 'wb'))
        return chunk_output_dir

    def resume_upload(self, file_chunks_path):
        """Resume an incomplete upload.
        
        """
        chunk_info_path = os.path.join(file_chunks_path,
                                                        'file_chunk_info.pkl')
        chunk_info = pickle.load(chunk_info_path)
        upload_options_path = os.path.join(file_chunks_path,
                                                         'upload_options.pkl')
        upload_options = pickle.load(upload_options_path)
        # If the upload opitions file exists, the upload process has begun.
        volume_name = upload_options['volume_name']
        thread_count = upload_options['thread_count']
        file_name = upload_options['file_name']
        metadata = upload_options['metadata']
        # First, get the incomplete uploads.
        incomplete_chunk_names = UploadLog.read_incomplete(file_chunks_path)
        chunks = chunklib.read_chunk_dir(file_chunks_path)
        for chunk in chunks:
            if chunk.file_name in incomplete_chunk_names:
                chunk.reuse_transfer = True
        uploader = ThreadedUploader(self.control_node_proxy,
                                    self.snode_proxy_creator,
                                    volume_name, file_name, chunks,
                                    thread_count, upload_log)
        uploader.start()
        uploader.join()

    def upload_file_chunks(self, file_chunks_path, volume_name=None,
                           thread_count=None, file_name=None, metadata=None):
        """Upload file chunks to the ScatterBytes network.

        The file should already be chunked using the prepare_file method. If
        an upload was interruped, it will be resumed.

        file_chunks_path
            path to the file chunks being uploaded

        thread_count
            number of concurrent upload threads to spawn

        file_name
            name to assign it - If not given, the file path will be used.

        metadata
            a dict containing extra metadata to be stored with the file.

        """

        # check that chunking is complete
        chunk_info_path = os.path.join(file_chunks_path, 'file_chunk_info.pkl')
        chunk_info = pickle.load(open(chunk_info_path, 'rb'))
        assert chunk_info.chunking_complete, 'file chunking incomplete'
        # get options
        if thread_count is None:
            thread_count = self.config.get('upload_thread_count')
        self.thread_count = thread_count
        if volume_name is None:
            volume_name = 'default'
        if file_name is None:
            file_name = chunk_info.get_value('file_path')
        assert file_name, 'file_name: %s is not valid' % file_name
        if len(file_name) > 1024:
            raise ValueError('file_name exceeds 1024 bytes')
        if metadata is None:
            metadata = {}
        chunks = chunklib.read_chunk_dir(file_chunks_path)
        # Size is the greater of the combined size of all of the chunks or 1
        # MB.  It is uploaded initially so the control node can check for
        # available capacity, but it's not stored.
        size = sum(chunk.size for chunk in chunks)
        flags = 0
        if chunk_info.encrypted:
            flags = flags | FLAGS['encrypted']
        if chunk_info.compressed:
            flags = flags | FLAGS['compressed']
        cn = self.control_node_proxy
        response = cn.create_file(
            volume_name, file_name, size, flags, metadata
        )
        # Nothing useful in the response - just a success message.
        assert response['status'] == 'OK'
        upload_options = {
            'volume_name' : volume_name,
            'thread_count' : thread_count,
            'file_name' : file_name,
            'metadata' : metadata
        }
        upload_options_path = os.path.join(file_chunks_path,
                                           'upload_options.pkl')
        f = open(upload_options_path, 'wb')
        pickle.dump(upload_options, f)
        f.flush()
        os.fsync(f.fileno())
        f.close()
        # log for progress
        upload_log = UploadLog(file_chunks_path)
        upload_thread_count = thread_count
        uploader = ThreadedUploader(self.control_node_proxy,
                                    self.snode_proxy_creator,
                                    volume_name, file_name,
                                    chunks, upload_thread_count, upload_log)
        uploader.start()
        uploader.join()

    def _wait_for_mirroring(self, mirror_count, chunk_sequence_numbers):
        cn = self.control_node_proxy
        volume_name = self.volume_name
        file_name = self.file_name
        for chunk_sequence_number in chunk_sequence_numbers:
            response = cn.get_chunk_status(
                volume_name, file_name, chunk_sequence_number
            )
            node_count = response['node_count']
            while node_count < mirror_count + 1:
                response = cn.get_chunk_status(
                    volume_name, file_name, chunk_sequence_number
                )
                node_count = response['node_count']
                logger.debug('waiting 5 seconds for chunk to mirror')
                time.sleep(5)

    def download_file(self, file_name, output_path, volume_name=None,
                      thread_count=None):
        cn = self.control_node_proxy
        file_info = cn.get_file_info(volume_name, file_name)
        # keys include, file_id, size, flags, chunk_count, init_ts,
        # status, init_ts, metadata
        # add the file_name and volume_name
        file_info['file_name'] = file_name
        file_info['volume_name'] = volume_name
        working_dir=self.config.get('working_directory')
        download_dir = os.path.join(working_dir, 'downloads')
        # see if output_path is a directory.
        if os.path.exists(output_path) and os.path.isdir(output_path):
            output_path = os.path.join(output_path, file_name)
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        if thread_count is None:
            thread_count = self.config.get('download_thread_count')
        downloader = ThreadedDownloader(
            file_info=file_info,
            control_node_proxy=cn,
            snode_proxy_creator=self.snode_proxy_creator,
            thread_count=thread_count,
            encrypt_key=self.config.encrypt_key,
            output_path=output_path,
            download_dir=download_dir
        )
        downloader.download()
        # clean up
        shutil.rmtree(downloader.chunk_download_dir)

    def delete_file(self, file_name, volume_name=None):
        if volume_name is None:
            volume_name = 'default'
        return self.control_node_proxy.delete_file(volume_name, file_name)

    def retrieve_chunk(self, snode_proxy, snode_args, chunk_md5sum):
        """Retrieve the chunk from the node given in node_info.

        """

        logger.debug('proxy is %s' % storage_node_proxy)
        f = storage_node_proxy.retrieve_chunk(*snode_args)
        # need to do something if checksum fails
        data = f.read()
        if util.checksum_data(data) != chunk_md5sum:
            raise MD5ChecksumError
        return data


class ClientNodeConfig(ConfigBase):

    """ClientNode configuration

    """

    config_name = 'client_node.config'
    log_filename = 'scatterbytes_client_node.log'

    defaults = ConfigBase.defaults.copy()
    defaults.update({
        'encrypt' : (True, 'boolean'),
        'encrypt_key' : ('', None),
        'compress': (True, 'boolean'),
        'download_thread_count' : (10, 'int'),
        'upload_thread_count' : (3, 'int'),
    })

    def __init__(self, config_path=None):
        ConfigBase.__init__(self, config_path)

    def init_prep(self):
        if not self.get('working_directory'):
            modified = True
            working_directory = os.path.join(
                os.path.dirname(self.config_path), 'client_data'
            )
            if not os.path.exists(working_directory):
                os.makedirs(working_directory, 0700)
            self.set('working_directory', working_directory)
        # if we don't have an encryption key, create one.
        if not self.encrypt_key:
            self.encrypt_key = util.b64encode(os.urandom(32))

    @property
    def encrypt_key(self):
        return self.get('encrypt_key')

    @encrypt_key.setter
    def encrypt_key(self, value):
        # check the length
        if len(util.b64decode(value)) != 32:
            raise ValueError('encrypt key should be 32 bytes')
        self.set('encrypt_key', value)


ClientNode.config_class = ClientNodeConfig


class UploadWorkerThread(threading.Thread):
    
    def __init__(self, sn_proxy_creator, transfer_info, chunk):
        threading.Thread.__init__(self)
        self.sn_proxy_creator = sn_proxy_creator
        self.chunk = chunk
        self.transfer_info = transfer_info
        self.completed = False

    def run(self):
        chunk = self.chunk
        transfer_info = self.transfer_info
        sequence_number = chunk.sequence_number
        # The control node returns a sequence number to verify.
        # It's the client's job to keep up with the chunk sequence.
        if sequence_number != transfer_info['sequence_number']:
            emsg = 'sequence numbers do not match \n'
            emsg += 'control node: %s\t' % transfer_info['sequence_number']
            emsg += 'local: %s' % sequence_number
            raise SBError(emsg)
        uri = transfer_info['uri']
        proxy = self.sn_proxy_creator(uri)
        self.transfer_name = transfer_info['transfer_name']
        logger.debug('sending chunk %s to %s' % (chunk.file_name, uri))
        chunk_file = open(chunk.file_path, 'rb')
        proxy_args = [
            transfer_info['signature'],
            transfer_info['signature_ts'],
            transfer_info['expire_time'],
            transfer_info['transfer_name'],
            transfer_info['chunk_name'],
            transfer_info['chunk_hash_salt'],
        ]
        proxy_args.append(chunk_file)
        response = proxy.store_chunk(*proxy_args)
        logger.debug('completed upload for chunk %s' % chunk.file_name)
        self.completed = True



class UploadLog(ChunkTransferLog):

    name = 'uploads.log'

    def append_assignment(self, chunk_file_name):
        msg = 'assigned %s' % (chunk_file_name)
        self.append(msg)

    def append_complete(self, chunk_file_name):
        self.append('completed %s' % chunk_file_name)

    @classmethod
    def read_incomplete(cls, chunks_dir_path):
        """"reads log to determine which chunks were not uploaded
        
        chunks_dir_path
            directory where chunks and this log file are
        
        """
        assigned = []
        completed = []
        file_path = os.path.join(chunks_dir_path, cls.name)
        for line in open(file_path, 'rb'):
            if line.startswith('assigned'):
                assigned.append(line.split()[1])
            elif line.startswith('completed'):  
                completed.append(line.split()[1])
        for chunk_file_name in completed:
            assigned.remove(chunk_file_name)
        return assigned



class ThreadedUploader(threading.Thread):

    """chunk uploader that uses a worker thread per chunk

    Chunks are sequenced according to their file name (e.g. chunk_0001).
    References to chunks on the control node are by volume_name, file_name, and
    chunk sequence number.

    """
    
    def __init__(self, cn_proxy, sn_proxy_creator, volume_name, file_name,
                 chunks, upload_thread_count, upload_log):
        threading.Thread.__init__(self)
        self.cn_proxy = cn_proxy
        self.volume_name = volume_name
        self.file_name = file_name
        self.chunks = chunks
        self.sn_proxy_creator = sn_proxy_creator
        self.upload_thread_count = upload_thread_count
        # the upload_log will assist in resuming uploads
        self.upload_log = upload_log
        # sort the chunks so that they can be fetched by index
        self.chunks.sort(key=attrgetter('sequence_number'))
        # check sequence is correct
        for (i, chunk) in enumerate(self.chunks):
            assert chunk.sequence_number == i + 1

    def request_storage(self):
        # Request storage for chunks.
        # Max is 25 - going with 10 as default.
        cn = self.cn_proxy
        if self.failed_uploads:
            response = []
            emsg = 'recovering from failed transfer %s'
            for (chunk, transfer_name) in self.failed_uploads:
                logger.debug(emsg % transfer_name)
                cn_response = cn.report_failed_transfer(transfer_name)
                transfer_info = cn_response['transfer_info']
                response.append((chunk, transfer_info))
                self.failed_uploads.remove((chunk, transfer_name))
            return response
        elif self.chunks_to_re_upload:
            response = []
            emsg = 're-uploading chunk %s'
            for chunk_sequence_number in self.chunks_to_re_upload:
                chunk = self.chunks(chunk_sequence_number - 1)
                logger.debug(emsg % chunk_sequence_number)
                reuse_transfer = hasattr(chunk, 'reuse_transfer') and \
                                                    chunk.reuse_transfer
                cn_response = cn.request_chunk_storage(
                    chunk_sequence_number, reuse_transfer
                )
                transfer_info = cn_response['transfer_info']
                response.append((chunk, transfer_info))
                # Set this to False in case it fails and needs a new transfer.
                chunk.reuse_transfer = False
                self.chunks_to_re_upload.remove(chunk_sequence_number)
            return response
        chunks_to_upload = self.chunks_to_upload
        chunks_request_info = []
        while len(chunks_request_info) < 10 and chunks_to_upload:
            chunk = chunks_to_upload.pop(0)
            flags = 0
            # TODO - include parity flag
            chunks_request_info.append((
                chunk,
                (chunk.size, chunk.calc_hash(os.urandom(4)), flags)
            ))
        cn_response = cn.request_file_storage(
            self.volume_name, self.file_name,
            [c[1] for c in chunks_request_info]
        )
        logger.info('got requested storage')
        transfer_info = cn_response['transfer_info']
        # Match the chunk up to the results.
        response = []
        for (i, r) in enumerate(transfer_info):
            chunk = chunks_request_info[i][0]
            response.append((chunk, r))
            self.upload_log.append_assignment(chunk.file_name)
        self.upload_log.fsync()
        return response

    def upload_chunks(self):

        def check_threads():
            "Check if a thread completed or not and clean up."
            for t in upload_threads:
                if t.is_alive():
                    continue
                if not t.completed:
                    # restore to be reprocessed
                    self.failed_uploads.append(
                        (t.chunk.file_name, t.transfer_name)
                    )
                else:
                    # log it
                    self.upload_log.append_complete(t.chunk.file_name)
                    self.upload_log.fsync()
                t.join()
                upload_threads.remove(t)
                         
        # Try really hard to maintain upload_thread_count worker threads.
        # Chunks on the control node are to be referenced by sequence number,
        # starting with 1. The reference is absolute and must include the
        # volume name and file name.
        upload_threads = []
        while self.chunks_to_upload or self.failed_uploads or \
                                                    self.chunks_to_re_upload:
            chunk_storage_info = self.request_storage()
            check_threads()
            while chunk_storage_info:
                while len(upload_threads) < self.upload_thread_count:
                    if not chunk_storage_info:
                        break
                    (chunk, transfer_info) = chunk_storage_info.pop(0)
                    uploader = UploadWorkerThread(
                        self.sn_proxy_creator, transfer_info, chunk
                    )
                    upload_threads.append(uploader)
                    uploader.start()
                time.sleep(.1)
                check_threads()
            check_threads()
        return
        cn = self.cn_proxy
        # Make sure the data is mirrored at least one time before exiting.
        # min_count is miniumum mirror count of all chunks.
        # 0 means the chunk is uploaded, but not mirrored
        response = cn.check_mirror_status(self.volume_name, self.file_name)
        missing_chunks = response.get('missing_chunks', [])
        min_mirror_count = response['min_count']
        if not missing_chunks and min_mirror_count > 0:
            # we're done
            return
        logger.info('waiting up to 60 seconds for data to be mirrored')
        t1 = time.time()
        min_mirror_count = 0
        while min_mirror_count < 1:
            # Wait 5 seconds between requests
            time.sleep(5)
            response = cn.check_mirror_status(self.volume_name, self.file_name)
            min_mirror_count = response['min_count']
            logger.debug('min mirror count is %s' % min_mirror_count)
            if 'missing_chunks' in response:
                logger.error("Missing chunks detected. Going to upload again.")
                for chunk_sequence_number in response['missing_chunks']:
                    self.chunks_to_re_upload.append(chunk_sequence_number)
                break
            elif time.time() - t1 > 60:
                # maybe need a list of chunks not mirrored so that we can
                # upload them ourself.
                if min_mirror_count == 0:
                    # probably OK - just hasn't mirrored yet.
                    emsg = ("Exiting after waiting on mirroring for "
                            "60 seconds. Not all data is mirrored yet, "
                            "but it does reside on storage nodes and should "
                            "be mirrored.")
                    logger.info(emsg)
                # Using the chunk_sequence_number for each unmirrored chunk,
                # we can upload it instead of waiting.
                chunk_sequence_numbers = cn.get_unmirrored_chunks(
                    self.volume_name, self.file_name, 1
                )
                if chunk_sequence_numbers:
                    self.chunks_to_re_upload.extend(chunk_sequence_numbers)
                break

    def run(self):
        # Request storage nodes from the control node.
        # max 25 at a time
        # Try to maintain the the requested thread count for uploads.
        # Reference the chunks based on their index.
        self.chunks_to_upload = self.chunks[:]
        self.failed_uploads = []
        self.chunks_to_re_upload = []
        for chunk in self.chunks:
            if hasattr(chunk, 'reuse_transfer') and chunk.reuse_transfer:
                # needs to be resumed
                self.chunks_to_re_upload.append(chunk.sequence_number)
                self.chunks_to_upload.remove(chunk)

        while self.chunks_to_upload or self.failed_uploads or \
                                                self.chunks_to_re_upload:
            self.upload_chunks()
        # all done, clean up
        logger.debug('cleaning up')
        output_dir = os.path.dirname(self.chunks[0].file_path)
        shutil.rmtree(output_dir)
