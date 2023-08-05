# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-09-14


import unittest
import json

import rs

from rs.context import context_property

from data2 import _server, _params
from test_request import _request


@rs.post
@rs.path('/rs/tests/{method}/{id}')
@rs.consumes('application/json', json.loads)
@rs.produces('application/json; charset="windows-1251"', json.dumps)
def testres(id,
            m=rs.context.alias('method','method_'),
            e=rs.context.entity,
            u=rs.context.uri):
    return [{'response': (id, m, e, u)}]


class ContextTest(unittest.TestCase):

    def setUp(self):
        self.res = rs.resource.build(testres)[0]
        self.req = _request()
        self.req.method = 'POST'
        self.req.uri = '/rs/tests/ADD/1'
        self.req.entity = '{"ENTITY":"YES"}'
        self.req.headers['content-length'] = str(len(self.req.entity))
        self.req.headers['content-type'] = 'application/json'
        self.srv = _server()
        self.srv.server_properties = 'server properties'
        self.params = _params()
        self.params.path['method'] = 'ADD'
        self.params.path['id'] = '1'
        self.ctx = rs.context(self.srv, self.req, self.res, self.params)

    def test_entity(self):
        self.assertEquals(json.loads(self.req.entity), self.ctx.entity)

    def test_request(self):
        self.assertEqual(self.req, self.ctx.request)

    def test_uri(self):
        self.assertEqual(self.req.uri, self.ctx.uri)

    def test_alias(self):
        self.assertEquals('ADD', rs.context.alias('method').__get__(self.ctx))
        self.assertEquals('1', rs.context.alias('id').__get__(self.ctx))
        self.assertEquals('DEFAULT', rs.context.alias('method_', default='DEFAULT').__get__(self.ctx))
        try:
            rs.context.alias('method_').__get__(self.ctx)
        except ValueError as e:
            pass
        else:
            self.fail('ValueError expected.')


class ContextDataTest(unittest.TestCase):

    def test_nonzero(self):
        self.assertFalse(rs.context.entity)
        self.assertFalse(rs.context.request)
        self.assertFalse(rs.context.uri)
        self.assertFalse(rs.context.alias)

    def test_call(self):
        def test_prop(prop):
            p = prop()
            self.assertTrue(isinstance(prop, context_property))
            self.assertTrue(isinstance(p, context_property))
            self.assertFalse(p is prop)
            self.assertFalse(p)
        test_prop(rs.context.entity)
        test_prop(rs.context.request)
        test_prop(rs.context.uri)
        test_prop(rs.context.alias)