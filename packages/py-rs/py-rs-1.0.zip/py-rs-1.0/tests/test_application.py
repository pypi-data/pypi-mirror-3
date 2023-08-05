# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-09-27


import unittest
import cStringIO

from rs.application import WSGIApplication, ResourceManager
from rs.response import Response


class ApplicationTest(unittest.TestCase):

    def test_complete_request(self):
        environ = {
            'SERVER_PROTOCOL':'HTTP/1.1',
            'REQUEST_METHOD':'HEAD',
            'PATH_INFO':'/service',
            'QUERY_STRING':'name=App&version=1',
            'CONTENT_LENGTH': '',
            'wsgi.input':cStringIO.StringIO(),
            'HTTP_ACCEPT':'text/html'
        }
        app = WSGIApplication()
        request = app.complete_request(environ)
        eq = self.assertEquals
        eq('HTTP/1.1', request.version)
        eq('HEAD', request.method)
        eq('/service', request.uri.path)
        eq('name=App&version=1', request.uri.query)
        eq('', request.headers['content-length'])
        eq('text/html', request.headers['accept'])
        eq(None, request.entity)
        content = 'Here is some contentЯ'
        environ = {
            'SERVER_PROTOCOL':'HTTP/1.1',
            'REQUEST_METHOD':'GET',
            'PATH_INFO':'/text',
            'CONTENT_LENGTH': str(len(content)),
            'CONTENT_TYPE':'text/plain',
            'wsgi.input':cStringIO.StringIO(content),
            'HTTP_CONTENT_LANGUAGE':'mixed'
        }
        request = app.complete_request(environ)
        eq('HTTP/1.1', request.version)
        eq('GET', request.method)
        eq('/text', request.uri.path)
        eq('', request.uri.query)
        eq(environ['CONTENT_LENGTH'], request.headers['content-length'])
        eq('text/plain', request.headers['content-type'])
        eq('mixed', request.headers['content-language'])
        eq(content, request.entity)

    def test_complete_response(self):
        content = 'This is a post contentЯ'
        entity = 'This is a response entityЯ'
        environ = {
            'SERVER_PROTOCOL':'HTTP/1.1',
            'REQUEST_METHOD':'POST',
            'PATH_INFO':'/service',
            'CONTENT_LENGTH': str(len(content)),
            'CONTENT_TYPE':'text/plain',
            'wsgi.input':cStringIO.StringIO(content),
        }
        eq = self.assertEquals
        def start_response(status, headers):
            headers = dict(headers)
            eq('200 OK', status)
            eq('mixed', headers['content-language'])
            eq(str(len(entity)), headers['content-length'])
        response = Response()
        response.status = 200
        response.headers = {
            'content-language':'mixed'
        }
        from rs.message import set_entity
        set_entity(response, entity)
        app = WSGIApplication()
        data = app.complete_response(response, environ, start_response)
        eq(entity, list(data)[0]) # No chunks
        

    def test_complete_response_with_failure(self):
        try:
            app = WSGIApplication()
            app.complete_response(Response(), None, None)
        except WSGIApplication.ResponseFailure:
            pass
        else:
            self.fail('Application.ResponseFailure expected.')


class ResourceManagerTest(unittest.TestCase):

    def test_init(self):
        import rs
        import rs.core
        rs.core.registry.clear()
        @rs.path('/res1')
        def res1(): pass
        @rs.path('/res2')
        def res2(): pass
        eq = self.assertEquals
        manager = ResourceManager()
        eq(False, hasattr(manager, 'resources'))
        manager.init(None) # if None whole rs.core.registry is used.
        eq(2, len(manager.resources))
        manager = ResourceManager()
        manager.init([res1, res1, res1])
        eq(1, len(manager.resources))
        

if '__main__' == __name__:
    unittest.main()