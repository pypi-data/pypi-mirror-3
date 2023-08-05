#    Coding: utf-8

#    py-activiti - Python Wrapper For Activiti BPMN2.0 API
#    Copyright (C) 2011  xtensive.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import  simplejson as json
import urllib2
import base64
import sys
import os
from string import upper
from activiti.multipart import MultipartPostHandler
from simplejson.decoder import JSONDecodeError
from urllib2 import HTTPError

try:
    ACTIVITI_SERVICES = os.environ['ACTIVITI_SERVICES']
except:
    #TODO: should move to settings.py
    ACTIVITI_SERVICES = "http://localhost:1234/activiti-webapp-rest2-5.9-SNAPSHOT/service/"


def _build_opener(is_multipart=False):
    if is_multipart:
        return urllib2.build_opener(MultipartPostHandler)
    return urllib2.build_opener()
    

def request_factory(service, username=None, password=None, method='GET', data=None, is_multipart=False):
    '''
    '''
    req = RequestWithMethod(ACTIVITI_SERVICES + service, method=method)
    if username and password:
        basic_auth = "Basic %s" % base64.standard_b64encode("%s:%s" % (username, password))
        #print >> sys.stderr, "Basic auth header : %s" % basic_auth
        req.add_header('Authorization', basic_auth)
    
    if data != None and not is_multipart:
        data = json.dumps(data)
        req.add_header('Content-Type', 'application/json')
    
    req.data = data
        
    return req

    
def process_json_response(data):
    return json.loads(data, 'utf-8')


def print_debug(data):
    print >> sys.stderr, "debug data = %s" % data
    
    
def call_service(service, username=None, password=None, debug=False, data=None, method='GET', is_multipart=False):
    req = request_factory(service, username, password, method, data, is_multipart)
    _opener = _build_opener(is_multipart)
    json_result = None
    
    json_result = _opener.open(req)
        
    try:
        _result = json_result.read()
        json_data = process_json_response(_result)
    except JSONDecodeError:
        json_data = _result

    if debug:
        print >> sys.stderr, "-------- DEBUG %s --------" % service
        print_debug(json_data)
        print >> sys.stderr, "-"*40
    return json_data



class RequestWithMethod(urllib2.Request):
  def __init__(self, *args, **kwargs):
    self._method = kwargs.get('method')
    if self._method:
        del kwargs['method']
    urllib2.Request.__init__(self, *args, **kwargs)

  def get_method(self):
    return self._method if self._method else super(RequestWithMethod, self).get_method()