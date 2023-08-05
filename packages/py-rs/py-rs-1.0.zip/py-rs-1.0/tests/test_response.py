# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-15


import unittest

import rs.status
import rs.response


class ResponseTest(unittest.TestCase):

    def test_init(self):
        response = rs.response.Response()
        eq = self.assertEquals
        eq(None, response.status)
        eq({}, response.headers)
        eq(None, response.entity)
        response = rs.response.Response(rs.status.NO_CONTENT)
        eq(rs.status.NO_CONTENT, response.status)
        eq({}, response.headers)
        eq(None, response.entity)


if __name__ == '__main__':
    unittest.main()