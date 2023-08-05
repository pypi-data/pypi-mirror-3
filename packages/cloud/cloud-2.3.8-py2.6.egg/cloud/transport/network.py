"""
PiCloud network connections
This module manages communication with the PiCloud server

Copyright (c) 2010 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

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
from __future__ import with_statement
import errno
import os
import sys
import time
import base64
import urllib
import random
import socket
import urllib2
import threading


from ..util import urllib2_file
from ..cloud import CloudException
from .. import cloudconfig as cc
from .connection import CloudConnection

import logging
cloudLog = logging.getLogger('Cloud.HTTPConnection')

try:
    from json import dumps as serialize
    from json import loads as deserialize
except ImportError: #If python version < 2.6, we need to use simplejson
    from simplejson import dumps as serialize
    from simplejson import loads as deserialize
    
#xrange serialization:
from ..util.xrange_helper import encode_maybe_xrange, decode_maybe_xrange, iterate_xrange_limit 

#zipping:
from ..util.zip_packer import Packer

#version transport:
from ..versioninfo import release_version

def unicode_container_to_str(data):
    """Recursively converts data from unicode to str.
    Responses from the server may be in unicode."""
    
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, dict):
        return dict(map(unicode_container_to_str, data.iteritems()))
    elif isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(map(unicode_container_to_str, data))
    else:
        return data
  

class HttpConnection(CloudConnection):
    """
    HTTPConnnection finds an available cloud cluster, and provides
    a gateway to query it.
    """
    
    api_key = cc.account_configurable('api_key',
                                     default='None',
                                     comment='your application\'s api key provided by PiCloud')
    api_secretkey = cc.account_configurable('api_secretkey',
                                           default='None',
                                           comment='your application\'s secret key provided by PiCloud')
    
    __api_default_url = 'http://api.picloud.com/servers/list/'
    server_list_url = cc.account_configurable('server_list_url',
                                           default=__api_default_url,
                                           comment="url to list of PiCloud servers",hidden=False) 
    #hack for users utilizing old api
    if server_list_url == 'http://www.picloud.com/pyapi/servers/list/':
        server_list_url = __api_default_url
    
    job_cache_size = cc.transport_configurable('cloud_status_cache_size',
                                  default=65536,
                                  comment="Number of job statuses to hold in local memory; set to 0 to disable caching. This option only applies when connected to PiCloud.")
    
    result_cache_size = cc.transport_configurable('cloud_result_cache_size',
                                  default=4096,
                                  comment="Amount (in kb) of job results to hold in local memory; set to 0 to disable caching. This option only applies when connected to PiCloud.")
    
    retry_attempts = cc.transport_configurable('retry_attempts',
                                               default=3, 
                                               comment='Number of times to retry requests if http error occurs',
                                               hidden=True)
    
    
    call_query = 'job/'
    map_query = 'job/map/add/'
    map_reduce_query = 'bigdata/map_reduce/add/'
    status_query =  'job/status/'
    result_query = 'job/result/serialized/'
    kill_query= 'job/kill/'
    delete_query= 'job/delete/'    
    info_query = 'job/info/'
    modules_add_query = 'module/add/'
    modules_check_query = 'module/check/'
    packages_list_query = 'package/list/'
        
    # Most status codes are interpretted by the server
    status_accept = 200
    
    url = cc.account_configurable('url', default='',
                                comment="url to picloud server.  Set by server_list_url if not found",hidden=True)
    
    hostname = cc.transport_configurable('hostname',
                                  default='',
                                  comment="Internal use only: hardcodes hostname.", hidden = True)
    
    #used to track cloud graph for webview
    parent_jid = cc.transport_configurable('parent_jid',
                                  default=-1, #default must be an int for configs to work
                                  comment="Internal use only: Tracks cloud graph for webview", hidden = True)
    if parent_jid < 0: #flag for None.  
        parent_jid = None
    
    #auto packages version received from server (or set by PiCloud)
    __ap_version = cc.transport_configurable('ap_version', default='', 
                                        comment="Internal use only. Deals with module versioning",
                                        hidden = True)  
    
    
    # protocol version
    # 1.0 --- xranges used to communicate
    # 1.1 --- new map uploading protocol
    # 1.2 --- GZIP individual elements
    # 1.3 --- Don't transport exception w/ status. Get through info
    # 2.0 --- New Cloud API
    version = '2.0'
    map_size_limit = 1800000 #1.8 MB map limit    
    map_job_limit = 500 #maximum number of map jobs per request    
    jid_size_limit = 10000 #maximum number of jids per request
        
               
    def __init__(self, api_key, api_secretkey, server_url=None):
        if api_key:
            self.api_key = str(api_key)
        if api_secretkey:
            self.api_secretkey = str(api_secretkey)
        if server_url:
            self.url= server_url
        if not self.hostname:
            self.hostname = str(socket.gethostname())
        self.openLock = threading.RLock()
        
        #module caching:
        self._modsInspected = set()
        self._modVersions = {}

    """Module version analysis"""
    def _get_mod_versions(self):
        for modname, module in sys.modules.items():
            if modname in self._modsInspected:
                continue            
            self._modsInspected.add(modname)
            if '.' in modname:  #only inspect top level
                continue      
            version_strings = ['__version__', 'version', 'Version']      
            for vs in version_strings:
                val = getattr(module, vs, None)    
                if isinstance(val, (str, int, long)): #must be primitive to be JSON'd
                    self._modVersions[modname] = val
        return self._modVersions            
        
        
    def open(self, force_open=False):
        
        #force_open is used if this does not need an api key                           
        with self.openLock:
            
            if self.opened:  #ignore multiple opens
                return
            
            if self.adapter:
                if not self.adapter.opened:
                    self.adapter.open()
                    
                self.adapter.cloud.job_cache_size = self.job_cache_size
                #config copy:            
                #no cache if size set to 0
                self.adapter.cloud.result_cache_size = self.result_cache_size*1024 \
                    if self.result_cache_size > 0 else None  
            
            if self.api_key == 'None' and not force_open:
                cloudLog.debug('No api_key set: using dummy connection')
                self.url = ''
                return False
            
            # get list of available servers if no url
            if not self.url:
                
                resp = self.send_request_helper(self.server_list_url, {})
                
                for accesspoint in resp['servers']:
                    try:
                        cloudLog.debug('Trying %s' % accesspoint)
                        # see if we can connect to the server
                        req = urllib2.Request(accesspoint)                    
                        resp = urllib2_file.urlopen(req, timeout = 30.0)
                        resp.read()
                    except Exception:
                        cloudLog.info('Could not connect to %s', exc_info = True)
                        pass                        
                    else:
                        self.url = accesspoint
                        cloudLog.info('Connected to %s' % accesspoint)
                        if req.get_type() != 'https':
                            cloudLog.warning('Connected over an insecure connection. Be sure that openssl and python-openssl are installed')
                        break
                else:
                    # if it could not establish a connection any of the listed servers
                    raise CloudException('HttpConnection.__init__: Could not find working cloud server',logger=cloudLog)
                
            #finish open
            self._isopen = True

    def connection_info(self):
        dict = CloudConnection.connection_info(self)
        dict['connection_type'] = 'HTTPS' if 'https://' in self.url else 'HTTP'
        dict['server_url'] = self.url
        dict['api_key'] = self.api_key
        dict['api_secretkey'] = self.api_secretkey
        return dict
    
    def needs_restart(self, **kwargs):
        
        api_key = kwargs.get('api_key')
        if api_key:
            if api_key != self.api_key:
                return True
        server_url = kwargs.get('server_url')
        if server_url:
            if server_url != self.url:
                return True        
        return False
    
    def post(self, url, post_values=None, headers={}, use_gzip=False):
        """Simple HTTP POST to the input url with the input post_values.
        If post_values are None, HTTP get issued"""
        
        request = urllib2.Request(url, post_values, headers)
        request.use_gzip = use_gzip
        response = urllib2_file.urlopen(request)
        
        return response
    
    def send_request_helper(self, url, post_values=None, headers={}, raw_response=False):
        """Creates an http connection to the given url with the post_values encoded.
        Returns the http response if the returned status code is > 200."""
        
        post_params = [] if post_values != None else None
        #post_values['version'] = self.version
        
        # remove None values
        if post_values:
            for key in post_values.keys():
                if post_values[key] == None:
                    del post_values[key]
                elif isinstance(post_values[key], (tuple, list)):
                    for v in post_values[key]:
                        post_params.append((key, v))
                    del post_values[key]
            
            post_params.extend(post_values.items()) 
        
        attempt = 0
                
        while attempt < self.retry_attempts:
            try:
                body = None
                
                response = self.post(url, post_params, headers)
                
                # read entire response
                body = response.read()
                
                response.close() #in python 2.5 not automatically done
                
                if raw_response:
                    resp = body
                    break
                else:
                    resp = self.parse_response(body)
                    if 'error_code' in resp:
                        raise CloudException(resp['error_msg'], status=resp['error_code'], 
                                         retry=resp['retry'], logger=cloudLog)
                    else:
                        break
            
            except Exception, e:
                
                attempt += 1
                
                #did we get an exception that should always be raised?
                must_raise_exc = isinstance(e, CloudException) and not e.retry  
                
                if not must_raise_exc:
                    if attempt < self.retry_attempts:
                        cloudLog.warn('rawquery: Problem connecting to PiCloud. Retrying. \nError is %s' % str(e))
                        logfunc = cloudLog.warn    
                    else:
                        cloudLog.exception('rawquery: http connection failed')
                        logfunc = cloudLog.error
                    
                    # HTTP Error
                    if hasattr(e, 'readlines'):
                        for line in e.readlines():
                            logfunc(line.rstrip())
                    
                    # if we received a body that we could not parse successfully
                    if body and not isinstance(e, CloudException):
                        logfunc('Specifically HTTP 200 with invalid data.')
                        for line in body.split('\n'):
                            logfunc(line.strip())
                
                if attempt == self.retry_attempts or must_raise_exc:
                    if isinstance(e, CloudException):
                        cloudLog.error('rawquery: received error from server: %s', e)
                        raise
                    else:
                        cloudLog.exception('rawquery: PiCloud appears to be unavailable. Showing traceback')
                        raise CloudException('PiCloud is unavailable. Please try again later.')
                else:
                    # exponential backoff
                    if isinstance(e, socket.error) and getattr(e, 'errno', e.args[0]) == errno.ECONNREFUSED:
                        # guarantee at least a 5 second sleep on a connection refused error
                        time.sleep(max(5, attempt*attempt*random.random()))
                    else:
                        time.sleep(max(1, attempt*attempt*random.random()))
                    continue
        
        return resp
    
    
    def parse_response(self, body):
        """Parses response"""
        
        offset = 0
        curly_count = 0
        for c in body:
            if c == '{':
                curly_count += 1
            elif c == '}':
                curly_count -= 1
            
            offset += 1
            if curly_count == 0:
                break
        else:
            raise Exception('Malformed body')
        
        resp = deserialize(body[:offset])
        resp['data'] = body[offset:]
        
        return resp
        
    
    def send_request(self, url, post_values, get_values=None, logfunc=cloudLog.info, raw_response=False):
        
        if self.api_key == 'None':
            raise CloudException('HttpConnection.query: api_key is not set. Please set it via cloudconf.py or calling cloud.setkey()', logger=cloudLog)
        
        if not self.opened:
            raise CloudException('HttpConnection.query: Connection is not open', logger=cloudLog)
        
        if logfunc:
            logfunc('query url %s with post_values =%s' % (url, post_values))
        
        headers = {}
        
        base64string = base64.encodestring('%s:%s' % (self.api_key, self.api_secretkey))[:-1]
        headers['Authorization'] = 'Basic %s' % base64string

        # add general information
        #post_values.update({'api_key': self.api_key,
        #                    'api_secretkey': self.api_secretkey})
        get_values = get_values or {}
        get_values['version'] = self.version
        
        # urlencode dict with sequence values
        query_string = urllib.urlencode(get_values, True) if get_values else ''
        if query_string:
            url += '?' + query_string

        if not url.startswith('http://') and not url.startswith('https://'):
            url = self.url + url 
        
        #print 'call %s' % url
        return self.send_request_helper(url, post_values, headers, raw_response = raw_response)
    
    def is_simulated(self):
        return False
    
    def _update_params(self, params):

        params.update({'hostname': str(self.hostname),
                       'process_id': str(os.getpid()),
                       'language': 'python',
                       'language_version': sys.version,
                       'ap_version': self.__ap_version,
                       })
        
        #get module versions
        params['mod_versions'] = self._get_mod_versions()
        params['cloud_version'] = release_version        
        
    
    def job_add(self, params, logdata=None):
        
        # let adapter make any needed calls for dep tracking
        self.adapter.dep_snapshot()
        
        self._update_params(params)
        
        #strip unicode from func_name:
        params['func_name'] = params['func_name'].decode('ascii', 'replace').encode('ascii', 'replace')
        
        data = Packer()
        
        data.add(params['func'])
        data.add(params['args'])
        data.add(params['kwargs'])
        
        del params['func'], params['args'], params['kwargs']
        
        params['data'] = data.finish()
        
        if params['depends_on']:
            params['depends_on'] = self.pack_jids(params['depends_on'])[0]
        
        resp = self.send_request(self.call_query, params, logfunc=cloudLog.debug)
        
        jid = resp['jids']
        
        cloudLog.info('call %s --> jid [%s]', params['func_name'], jid)
        
        return jid
    
    def jobs_map(self, params, mapargs, logdata=None):
        self._update_params(params)
        
        #strip unicode from func_name:
        params['func_name'] = params['func_name'].decode('ascii', 'replace').encode('ascii', 'replace')
        
        data = Packer()
        
        data.add(params['func'])
        size = len(params['func'])
        
        if params['depends_on']:
            params['depends_on'] = self.pack_jids(params['depends_on'])[0]        
        
        del params['func']
        
        # done indicates to the server when the last chunk of the map is being sent
        params['done'] = False
        
        # this tells the server what the first maparg index of the current map chunk is
        # for ex. first_maparg_index=0 (first request with 4 chunks),
        #         first_maparg_index=4 (second request)
        cnt = 0
        req_item_cnt = 0
        params['first_maparg_index'] = cnt
        
        first_iteration = True
        map_is_done = False
                        
        argIter =  mapargs
        
        fname = params['func_name']

        
        while True:

            try:
                next_elm = argIter.next()
            except StopIteration:
                map_is_done = True
                next_elm = None
                params['done'] = True

            
            if size > self.map_size_limit or req_item_cnt > self.map_job_limit or map_is_done:
                
                if cnt == 0:  #empty mapargs - don't send anything
                    return []
                
                self.adapter.dep_snapshot() #let adapter make any needed calls for dep tracking
                params['data'] = data.finish()  #payload
                params['hostname'] = str(self.hostname)
                params['ap_version'] = self.__ap_version
                
                resp = self.send_request(self.map_query, params, logfunc=cloudLog.debug) #actual query
                
                if not map_is_done:

                    if first_iteration:
                        # extract group_id from the response
                        group_id = resp['group_id']                                        
                    
                    # reset parameters
                    params = {'group_id': group_id,
                              'done': False,
                              'first_maparg_index': cnt}
                    
                    #rebuild data object
                    data = Packer()
                    
                else:
                    break
                
                size = 0
                req_item_cnt = 0
                
                # set first iteration to false only after the first *map chunk is sent*
                first_iteration = False

            if next_elm:
                data.add(next_elm)
                size += len(next_elm) 
                cnt += 1
                req_item_cnt += 1
            
        #print 'done sending mapargs'
        jids = decode_maybe_xrange(resp['jids'])
        
        cloudLog.info('map %s --> jids [%s]', fname, jids)
        
        return jids
    
    def add_map_reduce_job(self, params):
        
        self.adapter.dep_snapshot()
        
        self._update_params(params)
        
        data = Packer()
        
        data.add(params['mapper_func'])
        data.add(params['reducer_func'])
        data.add(params['bigdata_file'])
        
        del params['mapper_func'], params['reducer_func'], params['bigdata_file']
        
        params['data'] = data.finish()
        
        resp = self.send_request(self.map_reduce_query, params, logfunc=cloudLog.debug)
        
        jid = resp['jids']
        
        return jid
        
    
    @staticmethod
    def pack_jids(jids):
        packedJids = Packer()
        serialized_jids = serialize(encode_maybe_xrange(jids))
        packedJids.add(serialized_jids)
        return packedJids.finish(), serialized_jids
    
    def jobs_result(self, jids):
        # resp is in a pseudo-multipart format with a boundary
        # separating result fields

        results = []
        for rjids in iterate_xrange_limit(jids,self.jid_size_limit):    
            
            packed_jids, serialized_jids = self.pack_jids(rjids)        
            cloudLog.info('query result of jids %s' % serialized_jids) 
            
            resp = self.send_request(self.result_query, {'jids': packed_jids}, logfunc=None)
            
            # THINK: We could throw a warning if there is potentially a Python version incompatibility
            if resp['language'] != 'python':
                raise CloudException('HttpConnection.jobs_result: Result data is not Python compatible because it was generated in %s.' % resp['language'], logger=cloudLog)
            
            data = resp['data']
            
            boundary_index = data.index('\n')
            
            # parse boundary definition
            boundary = data[len('boundary='):boundary_index]
            
            # separate the boundary definition from the rest of the data
            rest = data[boundary_index+1:]
            
            # split results by boundary
            results_data = rest.split(boundary)
        
            # filter out empty strings
            results.extend([datum for datum in results_data if datum])
        
        return results
    
    def jobs_kill(self, jids):                
        if jids == None:
            #send 'kill all' command to server, which is encoded as kill([])
            packed_jids = self.pack_jids([])[0]
            cloudLog.info('kill all jobs')
            self.send_request(self.kill_query, {'jids': packed_jids}, logfunc=None)
            
        for rjids in iterate_xrange_limit(jids,self.jid_size_limit):
            packed_jids, serialized_jids = self.pack_jids(rjids)
            cloudLog.info('kill jids %s' % serialized_jids)
            self.send_request(self.kill_query, {'jids': packed_jids}, logfunc=None)

    def jobs_delete(self, jids):
        for rjids in iterate_xrange_limit(jids,self.jid_size_limit):
            packed_jids, serialized_jids = self.pack_jids(rjids)
            cloudLog.info('delete jids %s' % serialized_jids)
            self.send_request(self.delete_query, {'jids':  packed_jids}, logfunc=None)
        
    def jobs_info(self, jids, info_requested):
        
        infos = {}
        for rjids in iterate_xrange_limit(jids, self.jid_size_limit):    
            
            packed_jids, serialized_jids = self.pack_jids(rjids)        
            serialized_info = serialize(info_requested)
            cloudLog.info('query [%s] on jids %s' % (serialized_info, serialized_jids)) 
            
            resp = self.send_request(self.info_query,
                                     post_values={'jids':  packed_jids},
                                     get_values={'field': info_requested},
                                     logfunc=None)
            info_dct = resp['info']
            
            conv_dct = [(long(x), unicode_container_to_str(y)) for (x, y) in info_dct.iteritems()]                         
            infos.update(conv_dct)
            
            
        return infos
    
    def modules_check(self, modules):
        """modules_check determines which modules must be sent from the client
        to the server.
        modules: list of tuples where each tuple is (filename, timestamp)
        
        Returns a list of filenames to send."""
        
        packedMods = Packer()
        packedMods.add(serialize(modules))      
        data = packedMods.finish()

        resp = self.send_request(self.modules_check_query,
                                 {'data': data,
                                  'hostname': str(self.hostname),
                                  'language': 'python'})        
        
        mods = resp['modules']
        
        if 'ap_version' in resp:
            self.__ap_version = resp['ap_version']
            #cloudLog.info("network.py: modules_check(): result['ap_version'] of query: %s" % resp['ap_version'])
            
        cloudLog.info('network.py: modules_check(): ap_version is now %s. needed mods are %s', 
                      self.__ap_version, mods)
        
        return mods
    
    def modules_add(self, modules, modules_tarball):
        """modules_add adds the specified modules to the picloud system.
        modules is a list of tuples, where each tuple is (name, timestamp).
        modules_tarball is a string representing the tarball of all the included modules."""
        
        packedMods = Packer()
        packedMods.add(serialize(modules))
        packedMods.add(modules_tarball)        
        data = packedMods.finish()

        resp = self.send_request(self.modules_add_query,
                                 {'data': data,
                                  'hostname': str(self.hostname),
                                  'language': 'python'})
        
        if 'ap_version' in resp:
            self.__ap_version = resp['ap_version']
            #cloudLog.info("network.py: modules_add(): result['ap_version'] of query: %s" % resp['ap_version'])
            
        cloudLog.info('network.py: modules_add(): ap_version is %s' % self.__ap_version)
        
        
    def packages_list(self):
        """Get list of pre-installed packages from server"""
        
        resp = self.send_request(self.packages_list_query,
                                 {'language': 'python',
                                  'language_version': sys.version})
        
        # convert from unicode to ascii
        return map(str, resp['packages'])
    
    def report_name(self):
        return 'HTTPConnection'
        
    