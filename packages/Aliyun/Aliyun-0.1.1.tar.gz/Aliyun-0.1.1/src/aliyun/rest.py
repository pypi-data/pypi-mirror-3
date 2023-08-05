#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from urllib import urlencode

REST_METHODS = ['GET', 'POST', 'DELETE', 'HEAD', 'OPTIONS', 'PUT']

class REST_BASE(object):
    def __init__(self):
        self.headers = {}
        self.finename = None
        self.stdin = False
        self.params = []
        self.host = 'http://api.aliyun-dev.com'

        '''
        if options.accept:
            self.headers['accept'] = options.accept

        for head in options.headers:
            pass
    
        if options.params:
            if self._allow_params:
                self.params = [tuple(p.split('=', 1)) for p in options.param]
    '''
                
    def request(self, uri, data = None, auth=None):       
        if data:
            request = urllib2.Request(self.host + uri, urlencode(data))
        else:
            request = urllib2.Request(self.host + uri)
        request.get_method = lambda: self._method
        result = urllib2.urlopen(request)
        return result.read()

class REST_GET(REST_BASE):
    _method = 'GET'
    _allow_request_body = False
    _allow_params = True

class REST_HEAD(REST_BASE):
    _method = 'HEAD'
    _allow_request_body = False
    _allow_params = True

class REST_POST(REST_BASE):
    _method = 'POST'
    _allow_request_body = True
    _allow_params = True

class REST_PUT(REST_BASE):
    _method = 'PUT'
    _allow_request_body = True
    _allow_params = True

class REST_DELETE(REST_BASE):
    _method = 'DELETE'
    _allow_request_body = False
    _allow_params = True

class REST_OPTIONS(REST_BASE):
    _method = 'OPTIONS'
    _allow_request_body = False
    _allow_params = False

def simple_rest_factory(method):
    method = method.lower()
    if method == 'get':
        return REST_GET()
    elif method == 'post':
        return REST_POST()

if __name__ == '__main__':
    from urllib import quote, urlencode
    print "Test REST_POST"
    statement = """insert overwrite table src_dest select * from src"""
    post = simple_rest_factory('post')
    uri = '/query/'
    data = {'statement': statement,}
    print post.request(uri, data)

    print "Test REST_GET"
    job_name = 'taobao/job_20110725033501158_21405'
    get = simple_rest_factory('get')
    uri = '/status/%s/' % quote(job_name.encode('utf-8')).replace('/', '%252F')
    print uri
    print get.request(uri)

    
