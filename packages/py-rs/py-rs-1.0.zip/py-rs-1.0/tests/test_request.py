# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-15


import re
import unittest

import rs
import rs.core
import rs.resource
import rs.request
import rs.resource
import rs.status

from data2 import dummy


@rs.path('/')
class AppData(object):

    @rs.put
    @rs.path('/services/{id}')
    @rs.consumes('application/json')
    def update_service(self): pass

    @rs.get
    @rs.path('/services')
    @rs.produces('application/json')
    def get_services_json(self): pass

    @rs.get
    @rs.path('/services')
    @rs.produces('application/xml')
    def get_services_xml(self): pass

    @rs.post
    @rs.path('/services')
    @rs.consumes('application/json')
    def create_service(self): pass

    @rs.post
    @rs.path('/services/{method}')
    @rs.consumes('application/*')
    def call_services(self): pass

    @rs.post
    @rs.path('/services/re(set|start)')
    @rs.consumes('application/json')
    @rs.produces('application/json')
    def restart_services(self): pass

    @rs.post
    @rs.path('/services/reset')
    @rs.consumes('application/json')
    @rs.produces('application/json')
    def reset_services(self): pass


@rs.get
@rs.path('/index.html')
@rs.produces('text/html')
def index(): pass


@rs.get
@rs.path('/login.html')
@rs.produces('text/html')
def login(): pass


def _request():
    request = dummy()
    request.uri = dummy()
    request.uri.query = ''
    request.headers = {}
    return request


class RequestDispatcherTest(unittest.TestCase):

    resources = rs.resource.build_all(rs.core.registry)

    def setUp(self):
        self.dispatcher = rs.request.RequestDispatcher(self.resources)

    def test_resolve_path(self):
        res = self.dispatcher.resolve_path('/index.html')
        self.assertEquals(1, len(res))

    def test_resolve_path_not_found(self):
        try:
            self.dispatcher.resolve_path('/index')
        except rs.error as e:
            self.assertEquals(rs.status.NOT_FOUND, e.status)
        else:
            self.fail('404 status expected.')

    def test_resolve_method(self):
        res = self.dispatcher.resolve_method('GET')
        self.assertEquals(4, len(res))

    def test_resolve_method_not_allowed(self):
        try:
            self.dispatcher.resolve_method('GOT')
        except rs.error as e:
            self.assertEquals(rs.status.METHOD_NOT_ALLOWED, e.status)
            self.assertTrue(e is not None)
            allow_header = e.headers.get('allow')
            self.assertTrue(allow_header is not None)
            self.assertEquals('PUT, POST, GET', allow_header)
        else:
            self.fail('405 status expected.')

    def test_resolve_media(self):
        res = self.dispatcher.resolve_media('application/json')
        self.assertEquals(9, len(res))

    def test_resolve_media_unsupported(self):
        try:
            # due to resolve_media includes resources with no implicitly
            # defined consumer's descriptor we need first to apply some
            # other resolve function to expect 415 status further.
            self.dispatcher.resources = self.dispatcher.resolve_method('POST')
            self.dispatcher.resolve_media('text/xml')
        except rs.error as e:
            self.assertEquals(rs.status.UNSUPPORTED_MEDIA_TYPE, e.status)
        else:
            self.fail('415 status expected.')

    def test_resolve_accept(self):
        res = self.dispatcher.resolve_accept('application/json')
        self.assertEquals(6, len(res))
        res = self.dispatcher.resolve_accept('text/html')
        self.assertEquals(5, len(res))
        res = self.dispatcher.resolve_accept('x-text/html,*/*;q=0.5,x-text/xml')
        self.assertEquals(9, len(res))

    def test_resolve_accept_not_acceptable(self):
        try:
            # due to resolve_accept includes resources with no implicitly
            # defined provider's descriptor we need first to apply some
            # other resolve function to expect 406 status further.
            self.dispatcher.resources = self.dispatcher.resolve_path('index.html')
            self.dispatcher.resolve_accept('application/pdf, text/pdf')
        except rs.error as e:
            self.assertEquals(rs.status.NOT_ACCEPTABLE, e.status)
        else:
            self.fail('406 status expected.')

    def test_dispatch_PUT(self):
        req = _request()
        req.method = 'PUT'
        req.uri.path = '/services/911'
        req.headers['content-type'] = 'application/json; charset="windows-1251"'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['update_service'])
        self.assertEquals('911', params.path['id'])

    def test_dispatch_GET(self):
        req = _request()
        req.method = 'GET'
        req.uri.path = '/services'
        req.uri.query = 'lang=en&debug=0&lang=ru'
        req.headers['accept'] = 'application/json; q=0.9, application/xml; q=0.8'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['get_services_json'])
        self.assertEquals('0', params.query['debug'])
        self.assertEquals(['en', 'ru'], params.query['lang'])

    def test_dispatch_POST(self):
        req = _request()
        req.method = 'POST'
        req.uri.path = '/services'
        req.headers['content-type'] = 'application/json'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['create_service'])
        self.assertFalse(len(params.path))
        self.assertFalse(len(params.query))

    def test_dispatch_with_re(self):
        req = _request()
        req.method = 'POST'
        req.uri.path = '/services/restarting'
        req.headers['content-type'] = 'application/json'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['call_services'])
        req.uri.path = '/services/restart'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['restart_services'])
        self.assertFalse(len(params.path))
        self.assertFalse(len(params.query))
        req.uri.path = '/services/reset'
        res, params = self.dispatcher.dispatch(req)
        self.assertFalse(res is None)
        self.assertTrue(res.target is AppData.__dict__['reset_services'])

    def test_extract_path_params(self):
        match = re.match('/services/(?P<id>.*)', '/services/112')
        params = self.dispatcher.extract_path_params(match)
        self.assertEquals(1, len(params))
        self.assertEquals('112', params['id'])
        match = re.match('/services/re(start|set|load)', '/services/reload')
        params = self.dispatcher.extract_path_params(match)
        self.assertEquals(0, len(params))

    def test_extract_query_params(self):
        query = 'lang=en&debug=0&lang=ru'
        params = self.dispatcher.extract_query_params(query)
        self.assertEquals(2, len(params))
        self.assertEquals('0', params['debug'])
        self.assertEquals(['en', 'ru'], params['lang'])
        query = 'lang=en&debug=0&lang=ru&sort'
        params = self.dispatcher.extract_query_params(query)
        self.assertEquals(3, len(params))
        self.assertEquals('0', params['debug'])
        self.assertEquals(['en', 'ru'], params['lang'])
        self.assertEquals('', params['sort'])

    def test_extract_form_params(self):
        req = _request()
        req.method = 'POST'
        req.uri.path = '/submit'
        req.entity = 'lang=en&debug=0&lang=ru'
        req.headers['content-type'] = 'application/x-www-form-urlencoded'
        req.headers['content-length'] = len(req.entity)
        params = self.dispatcher.extract_form_params(req)
        self.assertEquals(2, len(params))
        self.assertEquals('0', params['debug'])
        self.assertEquals(['en', 'ru'], params['lang'])
        req.entity = 'lang=en&debug=0&lang=ru&sort'
        req.headers['content-length'] = len(req.entity)
        params = self.dispatcher.extract_form_params(req)
        self.assertEquals(3, len(params))
        self.assertEquals('0', params['debug'])
        self.assertEquals(['en', 'ru'], params['lang'])
        self.assertEquals('', params['sort'])
                
        

if __name__ == '__main__':
    unittest.main()