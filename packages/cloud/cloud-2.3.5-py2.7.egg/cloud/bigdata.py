"""
Beta --- not yet functional

For managing files on PiCloud's S3 store.

cloud.setkey() must be called before using any functions in this module.

.. note::

    This module cannot be used to access files stored on PiCloud's conventional file system
"""
from __future__ import with_statement
"""
Copyright (c) 2011 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html    
"""

"""User beware: list is defined in this module; list will not map to builtin list!"""

import os
import bz2
import sys
import math
import logging
import threading
from datetime import datetime

__httpConnection = None
__url = None
__query_lock = threading.Lock() #lock on http adapter updates

from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection

#cloudLog = logging.getLogger('Cloud.files')
logger = logging.getLogger('bigdata-client')
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('/var/tmp/bigdata-client.log')
logger.addHandler(handler)

# https://api.picloud.com/*insert query here*
_new_file_query = 'bigdata/new_file/'
_new_chunk_query = 'bigdata/upload_chunk/'

"""
This module utilizes the cloud object extensively
The functions can be viewed as instance methods of the Cloud (hence accessing of protected variables)
"""

def _get_cloud():
    cl = getattr(sys.modules['cloud'],'__cloud')
    cl._checkOpen()
    return cl


def _getConnection(cloud):
    """Return connection object associated Cloud
    Errors if object is not an HttpConnection"""
    
    if not isinstance(cloud.adapter, SerializingAdapter):
        raise RuntimeError('Unexpected cloud adapter being used')
    conn = cloud.adapter.connection
    if isinstance(conn, HttpConnection):
        return conn    
    elif conn.connection_info()['connection_type'] in ['HTTP', 'HTTPS']:
        #Retval of _post is not picklable. One day we should fix this
        raise RuntimeError('Cannot use cloud.files functions within a job running through cloud.mp')
    else:
        raise RuntimeError('Cannot use cloud.files functions when in simulation. conn is %s' % conn.connection_info())


def _post(conn, url, post_values, headers={}):
    """Use HttpConnection *conn* to issue a post request at *url* with values *post_values*"""
    
    #remove UNICODE from addresses
    url = url.decode('ascii', 'replace').encode('ascii', 'replace')
    
    if 'success_action_redirect' in headers:
        headers['success_action_redirect'] = headers['success_action_redirect'].decode('ascii', 'replace').encode('ascii', 'replace')
    if post_values and 'success_action_redirect' in post_values:
        post_values['success_action_redirect'] = post_values['success_action_redirect'].decode('ascii', 'replace').encode('ascii', 'replace')
    
    cloudLog.debug('post url %s with post_values=%s. headers=%s' % (url, post_values, headers))
    response =  conn.post(url, post_values, headers, use_gzip=False)
    return response


class CloudFile(object):
    """A CloudFile represents a file stored on PiCloud as a readonly file-like stream.
    Seeking is not available."""
    
    __http_response = None
    
    def __init__(self, http_response):
        self.__http_response = http_response
    
    def __iter__(self):
        return self
    
    def close(self):        
        return self.__http_response.close()
    
    def next(self):
        return self.__http_response.next()
    
    def read(self, size=-1):
        return self.__http_response.read(size)
        
    def readline(self, size=-1):
        return self.__http_response.readline(size)
        
    def readlines(self, sizehint=0):
        return self.__http_response.readlines(sizehint)
    
class CompressedFileStream(object):
    """
    This is a skeleton that is not complete.  It should
    have all the same functions that ChunkedFileStream has
    
    ChunkedFileStream.size() may not be needed
    """
    
    file = None
    bytes_read = None
    compressor = None
    
    def __init__(self, f):
        self.file = f
        self.bytes_read = 0
        self.compressor = bz2.BZ2Compressor()
    
    def __iter__(self):
        return self
        
    def next(self):
        pass
    
    def close(self):
        self.file.close()
        
    def read(self):
        """
        This will return a chunk of data
        """
        pass
            
class ChunkedFileStream(object):
    file = None
    chunk_size = None
    part = None
    bytes_read = None
    
    def __init__(self, f, part, chunk_size):
        logger.debug('[%s] Making ChunkedFileStream' % datetime.now())
        self.file = f
        self.file_size = os.path.getsize(self.file.name)
        self.part = part
        self.chunk_size = chunk_size
        self.bytes_read = 0
        self.position = self.part * self.chunk_size
        
        logger.debug('[%s] Part: %s chunk_size: %s' % (datetime.now(),
                                                       part,
                                                       chunk_size))
        
        # setting up self.file to be reading from the correct
        # location
        self.file.seek(self.part * self.chunk_size)
        
    def a_flag(self):
        return True
        
    def close(self):
        logger.debug('[%s] Closing' % datetime.now())
        self.file.close()
        
    def size(self):
        if (self.part+1) * self.chunk_size > self.file_size:
            return self.file_size - self.part * self.chunk_size
        else:
            return self.chunk_size
        
    def read(self, size=-1):
        logger.debug('[%s] Reading: %s' % (datetime.now(), size))
        if self.position == (self.part+1) * self.chunk_size:
            return ''
        elif size == -1:
            # returns amount up to the chunk size
            amount_to_read = ((self.part+1)*self.chunk_size) - self.position 
            data = self.file.read(amount_to_read)
            self.position += len(data)
#            logger.debug('[%s] Data: %s' % (datetime.now(), data))
            return data
        else:
            if self.position + size >= ((self.part+1)*self.chunk_size):
                data = self.file.read(((self.part+1)*self.chunk_size) - self.position)
            else:
                data = self.file.read(size)
            self.position += len(data)
#            logger.debug('[%s] Data: %s' % (datetime.now(), data))
            return data
        
    def seek(self, new_position):
        logger.debug('[%s] Seeking to: %s' % (datetime.now(), new_position))
        if new_position < 0:
            # bad shit
            pass
        else:
            position_in_chunk = new_position + (self.part * self.chunk_size)
            if position_in_chunk >= (self.part + 1) * self.chunk_size:
                self.position = (self.part+1) * self.chunk_size
                self.file.seek((self.part+1) * self.chunk_size)
            else:
                self.position = position_in_chunk
                self.file.seek(position_in_chunk)

def put(file_path, name=None):
    """
    Transfers the file specified by ``file_path`` to PiCloud. The file can be retrieved
    later using the get function.    
    
    If ``name`` is specified, the file will be stored as name on PiCloud.
    Otherwise it will be stored as the basename of file_path.
    
    Example::    
    
        cloud.files.put('data/names.txt') 
    
    This will transfer the file from the local path 'data/names.txt'
    to PiCloud and store it as 'names.txt'.
    It can later retrieved via cloud.files.get('names.txt') 
    """

    if not name:
        name = os.path.basename(file_path)
    
    # check extension name, or find cross-platform tool for determining file type
    # if gzip...
    # decompress using import gzip
    
    
    # open the requested file in binary mode (relevant in windows)
    f = open(file_path, 'rb')
    
    putf(f, name)

# added by kevin
# TODO: finish
def putf(f, name, resume=False):
    """
    Similar to put.
    putf, however, accepts a file object (file, StringIO, etc.) ``f`` instead of a file_path.
    
    .. warning::
    
        If the file object does not correspond to an actual file on disk,
        it will be read entirely into memory before being transferred to PiCloud.   
    """
    
    if isinstance(f, (str, unicode)):
        from cStringIO import StringIO
        f = StringIO(f)
    
    cloud = _get_cloud()
    conn = _getConnection(cloud)
    
    original_file_name = f.name
    file_size = os.path.getsize(original_file_name)
    logger.debug('[%s] file name: %s, file_size: %s' % (datetime.now(),
                                                        original_file_name,
                                                        file_size))
    compression_list = None
        
    # The None is for the POST Data.  Not sending the file yet
    logger.debug('[%s] Sending new file request' % datetime.now())
    new_file_get_vars = {'file_name': name, 'size': file_size}
    new_file_resp = conn.send_request(_new_file_query, None, get_values=new_file_get_vars)
    logger.debug('[%s] Resp: %s' % (datetime.now(), new_file_resp))
    
    if 'error' in new_file_resp:
        return new_file_resp['error']
    elif 'ready' in new_file_resp and new_file_resp['ready'] == 'True':
        compression_list = new_file_resp['c_types']
        file_id = new_file_resp['file_id']
        
        # this chunk size is in bytes
        chunk_size = new_file_resp['chunk_size']
    else:
        logger.debug('putf - Some error occurred.  new_file_resp is weird')
        return
    
    if compression_list:
        # make file wrapper and start sending the file over in chunks
        # start sending file in chunks
        num_of_chunks = int(math.ceil(file_size/float(chunk_size)))
        for part in xrange(num_of_chunks):
            logger.debug('[%s] file_id: %s, part: %s' % (datetime.now(),
                                                         file_id,
                                                         part))
            chunk = ChunkedFileStream(f, part, chunk_size)
            logger.debug('[%s] Sending new chunk request' % datetime.now())
            chunk_get_vars = {'file_id': file_id, 'part': part}
            chunk_resp = conn.send_request(_new_chunk_query, {name: chunk}, get_values=chunk_get_vars)
            logger.debug('[%s] Resp: %s' % (datetime.now(), chunk_resp))
            
        
    else:
        return 'error.  No compression list from server'
        
    #resp1 = conn.send_request(_bigdata_upload_params)
    #resp1['c_type'], resp1['volume_size']
    # your iterator will need to close the compressed file when it hits a GB,
    # and then start a new compressed file


def resume(f, name):
    pass


def list():
    """
    List all files stored on PiCloud.
    """
       
    cloud = _get_cloud()
    conn = _getConnection(cloud)         

    resp = conn.send_request(_file_list_query, {})
    files = resp['files']
    return files


def exists(file_name):
    """
    Check if a file named ``file_name`` is stored on PiCloud.
    """
    cloud = _get_cloud()
    conn = _getConnection(cloud)         
    
    resp = conn.send_request(_file_exists_query, {'name': file_name})
    exists = resp['exists']
    return exists

    
def delete(file_name):
    """
    Deletes the file named ``file_name`` from PiCloud.
    """

    cloud = _get_cloud()
    conn = _getConnection(cloud)         

    resp = conn.send_request(_file_delete_query, {'name': file_name})
    deleted = resp['deleted']
    return deleted


# don't need for now...
# do if you have time...
def get(file_name, save_path=None):
    """
    Retrieves the file named by ``file_name`` from PiCloud and stores it to ``save_path``.
        
    Example::    
    
        cloud.files.get('names.txt','data/names.txt') 
    
    This will retrieve the 'names.txt' file on PiCloud and save it locally to 
    'data/names.txt'. 
    """
    
    if not save_path:
        save_path = os.path.basename(file_name)
        
    cloud_file = getf(file_name)
    
    chunk_size = 64000
    f = open(save_path, 'wb')
    
    while True:
        data = cloud_file.read(chunk_size)
        if not data:
            break
        f.write(data)
    
    f.close()

def getf(file_name):
    """
    Retrieves the file named by ``file_name`` from PiCloud.
    Returns a CloudFile (file-like object) that can be read() to retrieve the file's contents 
    """    

    cloud = _get_cloud()
    conn = _getConnection(cloud)         

    # get ticket
    resp = conn.send_request(_file_get_query, {'name': file_name})
    
    ticket = resp['ticket']
    params = resp['params']
    
    # Set post_values to None to force GET request
    resp =  _post(conn,params['action'], None, ticket)
    
    cloud_file = CloudFile(resp)
    
    return cloud_file

###########################################################
################     PiCloud MapReduce     ################
###########################################################
    
def map_reduce(mapper_func, reducer_func, bigdata_file):
    
    # get dependencies for the mapper and reducer functions
    
    # bigdata_file is a string that is the filename that was uploaded
    
    # These objects are then cPickled and sent to the web server, which does all the work
    # of starting the MapReduce job.
    
    # I was thinking of having this function return a single jid that corresponds to a
    # single mapreduce job.
    
    cloud = _get_cloud()
    adapter = cloud.adapter
    
    cloud._checkOpen()

    if not callable(mapper_func):
        raise TypeError('bigdata.map_reduce first argument (%s) is not callable'  % (str(mapper_func) ))
    if not callable(reducer_func):
        raise TypeError('bigdata.map_reduce second argument (%s) is not callable'  % (str(mapper_func) ))
    
    jid = adapter.map_reduce_job(mapper_func, reducer_func, bigdata_file)     

    return jid

