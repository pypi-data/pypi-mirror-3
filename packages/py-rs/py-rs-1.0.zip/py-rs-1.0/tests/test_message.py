# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-26


import unittest

import rs.message

from data2 import dummy


class EntityTest(unittest.TestCase):

    def test_entity(self):
        eq = self.assertEquals
        eq('entity', rs.message.entity('entity'))
        eq('entity_u', rs.message.entity(u'entity_u'))
        eq('entity_Я', rs.message.entity('entity_Я'))
        eq('entity_уЯ', rs.message.entity(u'entity_уЯ'))

    def test_set_entity(self):
        dummy_entity = u'<html><head><title>This is a titleЯ</title></head><body/></html>'.encode('windows-1251')
        message = dummy()
        message.headers = {}
        message.entity = None
        rs.message.set_entity(message, dummy_entity, 'text/html; charset="windows-1251"')
        eq = self.assertEquals
        eq('text/html; charset="windows-1251"', message.headers.get('content-type'))
        eq(str(len(dummy_entity)), message.headers.get('content-length'))
        eq(dummy_entity, message.entity)

    def test_set_headers(self):
        message = dummy()
        message.headers = {}
        headers = {
            'Accept': 'application/json',
            'CACHE': 'no-cache'
        }
        rs.message.set_headers(message, headers)
        eq = self.assertEquals
        eq('application/json', message.headers.get('accept'))
        eq('no-cache', message.headers.get('cache'))

    def test_parse_header(self):
        parsed = rs.message.parse_header('application/json; charset="windows-1251"')
        self.assertEquals('application/json', parsed.value)
        self.assertEquals('"windows-1251"', parsed.charset)
        self.assertEquals('application/json; charset="windows-1251"', parsed.header)

    def test_parse_media(self):
        parsed = rs.message.parse_media('application/json; charset="windows-1251"')
        self.assertEquals('application/json', parsed.value)
        self.assertEquals('"windows-1251"', parsed.charset)
        self.assertEquals('application', parsed.type)
        self.assertEquals('json', parsed.subtype)

    def test_parse_accept(self):
        parsed = rs.message.parse_accept('text/*, text/html, text/html;level=1, */*')
        self.assertEquals(4, len(parsed))
        self.assertEquals('text/html', parsed[0].value)
        self.assertEquals('1', parsed[0].level)
        self.assertEquals('text/html', parsed[1].value)
        self.assertEquals(None, parsed[1].level)
        self.assertEquals('text/*', parsed[2].value)
        self.assertEquals('*/*', parsed[3].value)
        parsed = rs.message.parse_accept("""text/*;q=0.3, text/html;q=0.7, text/html;level=1, \
text/html;level=2;q=0.4, */*;q=0.5""")
        self.assertEquals(5, len(parsed))
        self.assertEquals('text/html', parsed[0].value)
        self.assertEquals('1', parsed[0].level)
        self.assertEquals('text/html', parsed[1].value)
        self.assertEquals(None, parsed[1].level)
        self.assertEquals('*/*', parsed[2].value)
        self.assertEquals('text/html', parsed[3].value)
        self.assertEquals('2', parsed[3].level)
        self.assertEquals('text/*', parsed[4].value)

    def test_combine_header(self):
        self.assertEquals('text/plain;charset=utf-8', rs.message.combine_header('text/plain', ('charset', 'utf-8')))
        self.assertEquals('text/plain;q=0.4;level=1', rs.message.combine_header('text/plain',
                                                                                ('q', '0.4'),
                                                                                ('level', '1')))

if __name__ == '__main__':
    unittest.main()