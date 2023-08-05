"""
For managing files on PiCloud's S3 store.

cloud.setkey() must be called before using any functions in this module.

.. note::

    This module cannot be used to access files stored on PiCloud's conventional file system
    
TODO: Support files larger than 5 gb    
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
import sys
import logging
import threading

__httpConnection = None
__url = None
__query_lock = threading.Lock() #lock on http adapter updates

from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection
from .cloud import CloudException

cloudLog = logging.getLogger('Cloud.files')

_file_new_query = 'file/new/'
_file_put_query = 'file/put/'
_file_list_query = 'file/list/'
_file_get_query = 'file/get/'
_file_exists_query = 'file/exists/'
_file_md5_query = 'file/md5/'
_file_delete_query = 'file/delete/'
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
    """
    if url.startswith('https'):
        print 'disable security'
        url = 'http' + url[len('https'):]
    """
    
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
        """
        Close the file, blocking further I/O operations
        """
        
        return self.__http_response.close()
    
    @property
    def md5(self):
        """The md5 checksum of file contents"""
        return self.__http_response.headers['etag'].strip('"')
    
    def next(self):
        return self.__http_response.next()
    
    def read(self, size=-1):
        """
        read([size]) -> read at most size bytes, returned as a string.
       
        If the size argument is negative or omitted, read until EOF is reached.
        """
        return self.__http_response.read(size)
        
    def readline(self, size=-1):
        """
        readline([size]) -> next line from the file, as a string.
       
        Retain newline.  A non-negative size argument limits the maximum
        number of bytes to return (an incomplete line may be returned then).
        Return an empty string at EOF.
        """

        return self.__http_response.readline(size)
        
    def readlines(self, sizehint=0):
        """
        readlines([size]) -> list of strings, each a line from the file.
       
        Call readline() repeatedly and return a list of the lines so read.
        The optional size argument, if given, is an approximate bound on the
        total number of bytes in the lines returned.
        """
        return self.__http_response.readlines(sizehint)
            
def _compute_md5(f, buffersize = 8192):
    """Computes the md5 hash of file-like object
    f must have seek ability to perform this operation
    
    buffersize controls how much of file is read at once
    """
    
    try:
        start_loc = f.tell()
        f.seek(start_loc)  #test seek
    except (AttributeError, IOError), e:
        raise IOError('%s is not seekable. Cannot compute MD5 hash. Exact error is %s' % (str(f), str(e)))
    
    try:
        from hashlib import md5
    except ImportError:
        from md5 import md5
    
    m = md5()    
    s = f.read(buffersize)
    while s:
        m.update(s)
        s = f.read(buffersize)
    
    f.seek(start_loc)
    hex_md5 = m.hexdigest()
    return hex_md5                

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
    
    # open the requested file in binary mode (relevant in windows)
    f = open(file_path, 'rb')
    
    putf(f, name)


def putf(f, name):
    """
    Similar to put.
    putf, however, accepts a file object (file, StringIO, etc.) ``f`` instead of a file_path.
    
    .. note::
        
        ``f`` is not rewound. f.read() from current position will be placed on PiCloud
    
    .. warning:: 
    
        If the file object does not correspond to an actual file on disk,
        it will be read entirely into memory before being transferred to PiCloud.   
    """
    
    if isinstance(name, unicode):
        raise TypeError('name must be str, unicode is not supported')
    
    if '../..' in name:
        raise ValueError('"../.." cannot be in name')
    
    if isinstance(f, (str, unicode)):
        from cStringIO import StringIO
        f = StringIO(f)
    
    cloud = _get_cloud()
    conn = _getConnection(cloud)         
    
    try:
        # get a file ticket
        resp = conn.send_request(_file_new_query, {'name': name})
        ticket = resp['ticket']
        params = resp['params']
        
        url = params['action']
        
        # set file in ticket
        ticket['file'] = f
        
        # post file using information in ticket
        ticket['key'] = str(ticket['key'])
        resp =  _post(conn,url, ticket)
        resp.read()
        
    finally:
        f.close()

def sync_to_cloud(file_path, name=None):
    """
    Upload file if it has changed.
    
    cloud.files.put(file_path,name) 
    only if contents of local file (specified by *file_path*)
    differ from those on PiCloud (specified by *name* or basename(*file_path*))
    (or if file does not exist on PiCloud) 
    """
    if not name:
        name = os.path.basename(file_path)
    
    # open the requested file in binary mode (relevant in windows)
    f = open(file_path, 'rb')
    local_md5 = _compute_md5(f)
    try:
        remote_md5 = get_md5(name, log_missing_file_error = False)
    except CloudException: #file not found
        remote_md5 = ''
    
    do_update = remote_md5 != local_md5
    cloudLog.debug('remote_md5=%s. local_md5=%s. uploading? %s',
                   remote_md5, local_md5, do_update
                   )
    if do_update:
        putf(f, name)
 
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

def get_md5(file_name, log_missing_file_error = True):
    """
    Return the md5 checksum of the file named ``file_name`` stored on PiCloud
    """
    cloud = _get_cloud()
    conn = _getConnection(cloud)         
    
    resp = conn.send_request(_file_md5_query, {'name': file_name},
                             log_cloud_excp = log_missing_file_error)
    md5sum = resp['md5sum']
    return md5sum

    
def delete(file_name):
    """
    Deletes the file named ``file_name`` from PiCloud.
    """

    cloud = _get_cloud()
    conn = _getConnection(cloud)         

    resp = conn.send_request(_file_delete_query, {'name': file_name})
    deleted = resp['deleted']
    return deleted
    
def get(file_name, save_path=None, byte_range=None):
    """
    Retrieves the file named by ``file_name`` from PiCloud and stores it to ``save_path``.
        
    Example::    
    
        cloud.files.get('names.txt','data/names.txt') 
    
    This will retrieve the 'names.txt' file on PiCloud and save it locally to 
    'data/names.txt'. 
    
    If save_path is None, save_path will be file_name
    
    An optional ``byte_range`` can be specified as a two-element tuple [starting_byte, ending_byte],
    where only the data between *starting_byte* and *ending_byte* is returned. 
    If ending_byte exceeds the size of the file, the contents from *starting_byte* to end of file returned.
    
    """
    
    if not save_path:
        save_path = file_name
        
    cloud_file = getf(file_name, byte_range)
    
    chunk_size = 64000
    f = open(save_path, 'wb')
    
    while True:
        data = cloud_file.read(chunk_size)
        if not data:
            break
        f.write(data)
    
    f.close()
    
def sync_from_cloud(file_name, save_path=None):
    """
    Download file if it has changed.
    
    cloud.files.get(file_name,save_path) 
    only if contents of local file (specified by *save_path* or basename(*file_name))
    differ from those on PiCloud (specified by *name*) 
    (or *save_path* does not exist locally)
    """
    
    if not save_path:
        save_path = file_name
    
    if not os.path.exists(save_path):
        do_update = True
    else:
        f = open(save_path, 'rb')
        local_md5 = _compute_md5(f)
        f.close()
        try:
            remote_md5 = get_md5(file_name, log_missing_file_error = False)
        except CloudException: #file not found
            remote_md5 = ''
    
        do_update = remote_md5 != local_md5
        cloudLog.debug('remote_md5=%s. local_md5=%s. downloading? %s',
                   remote_md5, local_md5, do_update
                   )
    if do_update:
        get(file_name, save_path)
       

def getf(file_name, byte_range=None):
    """
    Retrieves the file named by ``file_name`` from PiCloud. 

    An optional ``byte_range`` can be specified as a two-element tuple [starting_byte, ending_byte],
    where only the data between *starting_byte* and *ending_byte* is returned. 
    If ending_byte exceeds the size of the file, the contents from *starting_byte* to end of file returned.

    Return value is a CloudFile (file-like object) that can be read() to retrieve the file's contents 
    """    

    cloud = _get_cloud()
    conn = _getConnection(cloud)         

    if byte_range and not len(byte_range) == 2:
        raise Exception('byte_range should be a list of two elements [starting_byte, ending_byte]')

    # get ticket
    resp = conn.send_request(_file_get_query, {'name': file_name})
    
    ticket = resp['ticket']
    params = resp['params']
    
    if byte_range:
        ticket['Range'] = 'bytes=%s-%s' % tuple(byte_range)
    
    # Set post_values to None to force GET request
    resp =  _post(conn,params['action'], None, ticket)
    
    cloud_file = CloudFile(resp)
    
    return cloud_file
