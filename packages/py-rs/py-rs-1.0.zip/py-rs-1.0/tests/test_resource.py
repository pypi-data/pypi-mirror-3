# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-16


import unittest
import json

import rs
import rs.resource

from data1 import *
from data2 import _server, _params
from test_request import _request


@rs.post
@rs.path('/rs/tests/{method}/{id}')
@rs.consumes('application/json', json.loads)
@rs.produces('application/json; charset="windows-1251"', json.dumps)
def testres(id,
            method_=rs.context.alias('method','method_'),
            entity=rs.context.entity):
    return [{'params': (method_, id)}]


class ResourceBuilderTest(unittest.TestCase):

    def test_build_EmptyRes(self):
        res = rs.resource.build(EmptyRes)
        eq = self.assertEquals
        eq(0, len(res))

    def test_build_DummyRes(self):
        res = rs.resource.build(DummyRes)
        eq = self.assertEquals
        eq(3, len(res))
        dummy, deepest, dumb = res[0], res[1], res[2]
        eq('GET', dumb.method)
        eq('/default/dumb/dumbest', dumb.path)
        eq(DummyRes.DumbRes, dumb.type)
        eq(DummyRes.DumbRes.__dict__['dumb'], dumb.target)
        eq('^default/dumb/dumbest$', dumb.pattern.pattern)
        eq('GET', dummy.method)
        eq('/default/dummy', dummy.path)
        eq(DummyRes, dummy.type)
        eq(DummyRes.__dict__['dummy'], dummy.target)
        eq('^default/dummy$', dummy.pattern.pattern)
        eq('GET', deepest.method)
        eq('/default/dumb/deepest/res', deepest.path)
        eq('^default/dumb/deepest/res$', deepest.pattern.pattern)
        eq(DummyRes.DumbRes.DeepestRes, deepest.type)
        eq(DummyRes.DumbRes.DeepestRes.__dict__['res'], deepest.target)

    def test_build_MultiRes(self):
        res = rs.resource.build(MultiRes)
        eq = self.assertEquals
        eq(2, len(res))
        create, get = res[0], res[1]
        eq('POST', create.method)
        eq('/multi/services/{id}', create.path)
        eq('^multi/services/(?P<id>.+)$', create.pattern.pattern)
        eq(MultiRes, create.type)
        eq(MultiRes.__dict__['create_service'], create.target)
        eq('GET', get.method)
        eq('/multi/services', get.path)
        eq('^multi/services$', get.pattern.pattern)
        eq(MultiRes, get.type)
        eq(MultiRes.__dict__['get_services'], get.target)

    def test_build_funcRes(self):
        res = rs.resource.build(funcRes)
        eq = self.assertEquals
        eq(1, len(res))
        func = res[0]
        eq('GET', func.method)
        eq('/index.html', func.path)
        eq('^index.html$', func.pattern.pattern)
        eq(None, func.type)
        eq(funcRes, func.target)

    def test_build_all(self):
        res = rs.resource.build_all([MultiRes, DummyRes, MultiRes, funcRes])
        self.assertEquals(6, len(res))
        

class ResourceTest(unittest.TestCase):

    def setUp(self):
        self.res = rs.resource.build(testres)[0]
        self.req = _request()
        self.req.method = 'POST'
        self.req.uri = '/rs/tests/ADD/1'
        self.req.entity = '{"ENTITY":"YES"}'
        self.req.headers['content-length'] = str(len(self.req.entity))
        self.req.headers['content-type'] = 'application/json'
        self.srv = _server()
        self.params = _params()
        self.params.path['method'] = 'ADD'
        self.params.path['id'] = '1'
        

    def test_make_response(self):
        res = rs.resource.Resource()
        entity = ('', 201, {'location':'uri'})
        response = res.make_response(*entity)
        eq = self.assertEquals
        eq(201, response.status)
        eq('uri', response.headers.get('location'))
        eq('', response.entity)
        entity = (None, 204)
        response = res.make_response(*entity)
        eq(204, response.status)
        eq(0, len(response.headers))
        eq(None, response.entity)

    def test_resolve_params(self):
        params = dict(self.res.resolve_params(rs.context(self.srv, self.req, self.res, self.params)))
        eq = self.assertEquals
        eq('ADD', params['method_'])
        eq('1', params['id'])
        eq(json.loads(self.req.entity), params['entity'])

    def test_resolve_params_empty_entity(self):
        self.req.entity = None
        del self.req.headers['content-length']
        params = dict(self.res.resolve_params(rs.context(self.srv, self.req, self.res, self.params)))
        eq = self.assertEquals
        eq('ADD', params['method_'])
        eq('1', params['id'])
        eq(None, params['entity'])

    def test_resolve_params_bad_request_if_bad_entity(self):
        try:
            self.req.entity = repr(object)
            self.req.headers['content-length'] = len(self.req.entity)
            self.req.headers['content-type'] = 'text/plain'
            dict(self.res.resolve_params(rs.context(self.srv, self.req, self.res, self.params)))
        except rs.error as e:
            self.assertEquals(rs.status.BAD_REQUEST, e.status)
        else:
            self.fail('400 status expected.')

    def test_resolve_params_bad_request_if_not_enough_args(self):
        try:
            params = _params()
            params.path = {}
            params.query['id'] = 1
            print dict(self.res.resolve_params(rs.context(self.srv, self.req, self.res, params)))
        except rs.error as e:
            self.assertEquals(rs.status.BAD_REQUEST, e.status)
        else:
            self.fail('400 status expected.')


if __name__ == '__main__':
    unittest.main()