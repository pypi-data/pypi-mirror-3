"""
Python account management.
This module allows the user to manage account information programmatically.
Currently allows managing real time core requests.

Note that your api_key must be set before using any functions.
"""
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
import sys, logging, datetime

__username = None
__password = None
__httpAdapter = None
__url = None

from .transport.adapter import SerializingAdapter
from .transport.network import HttpConnection

cloudLog = logging.getLogger('Cloud.account')        

_rt_request_query = 'account/rt/request/'
_rt_release_query = 'account/rt/release/'
_rt_list_query = 'account/rt/list/'        

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
    
    if not isinstance(cloud.adapter,SerializingAdapter):
        raise Exception('Unexpected cloud adapter being used')
    conn = cloud.adapter.connection
    if isinstance(conn,HttpConnection):
        return conn
    else:
        raise RuntimeError('Cannot use cloud.account functions when in simulation')

def _fix_time_element(dct, key):
    item = dct.get(key)
    if item == 'None': #returned by web instead of a NoneType None
        item = None
        dct[key] = item
    if item:
        dct[key] = datetime.datetime.strptime(item,'%Y-%m-%d %H:%M:%S')
    return dct

        
"""
Real time requests management
"""
def list_rt_cores(request_id = ""):
    """Returns a list of dictionaries describing realtime core requests.
    If *request_id* is specified, only show realtime core request with that request_id
    
    The keys within each returned dictionary are:
    
    * request_id: numeric ID associated with the request 
    * type: Type of computation resource this request grants
    * cores: Number of (type) cores this request grants
    * start_time: Time when real time request was satisfied; None if still pending"""
    
    if request_id != "":
        try:
            int(request_id)
        except ValueError:
            raise TypeError('Optional parameter to list_rt_cores must be a numeric request_id')

    conn = _getConnection(_get_cloud())
    rt_list = conn.send_request(_rt_list_query, {'rid': str(request_id)})
    return [_fix_time_element(rt,'start_time') for rt in rt_list['requests']]

def request_rt_cores(type, cores):
    """Request a number of *cores* of a certain compure resource *type*  
    Returns a dictionary describing the newly created realtime request, with the same format
    as the requests returned by list_rt_cores.
    
    Note: *Cores* must a multiple of a base number depending on *type*:
    c1: 10
    c2: 8
    m1: 8
    s1: 1
    
    e.g. 5 c1 cannot be reserved; 20 c1 can be.    
    """
    
    conn = _getConnection(_get_cloud())
    return _fix_time_element(conn.send_request(_rt_request_query, 
                                               {'rt_cores': cores,
                                                'rt_type' : type}), 
                             'start_time')

def release_rt_cores(request_id):
    """Release the realtime core request associated with *request_id*. 
    Request must have been satisfied to terminate."""
    
    try:
        int(request_id)
    except ValueError:
        raise TypeError('release_rt_cores requires a numeric request_id')
    
    conn = _getConnection(_get_cloud())    
    return _fix_time_element(conn.send_request(_rt_release_query, {'rid': str(request_id)}), 'start_time')
