# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-31


import unittest

from rs.debug import *


class tmp_logger(object):
    def set_log(self, log_callback):
        self.log_callback = log_callback
    def log(self, lvl, msg):
        self.log_callback(lvl, msg)
    def exception(self, e):
        self.log_callback('EXCEPTION', str(e))


def decorator(value=None):
    def d(f):
        def df():
            return value
        return df
    return d


logger=tmp_logger()

@log_params('a', 'b', logger=logger, level='INFO')
@log_return(logger=logger, level='DEBUG')
@log_exception(ZeroDivisionError, logger=logger)
def f(a, b):
    return a/b
    

class DebugTest(unittest.TestCase):

    class log_check(object):
        def __init__(self, test, seq):
            self.test, self.expected = test, []
            self.num, self.seq = 0, seq
        def add_expected(self, lvl, msg):
            self.expected.append((lvl, msg))
        def __call__(self, lvl, msg):
            self.num += 1
            if self.num in self.seq:
                self.seq.remove(self.num)
                e_lvl, e_msg = self.expected.pop(0)
                self.test.assertEquals(e_lvl, lvl)
                self.test.assertEquals(e_msg, msg)


    def test_conditional(self):
        @conditional(False, decorator(False))
        def is_true():
            return True
        @conditional(True, decorator(False))
        def is_false():
            return True
        self.assertEqual(True, is_true())
        self.assertEqual(False, is_false())

    def test_log_params(self):
        check = DebugTest.log_check(self, [1,2])
        check.add_expected('INFO', 27)
        check.add_expected('INFO', 3)
        logger.set_log(check)
        f(27, 3)

    def test_log_return(self):
        check = DebugTest.log_check(self, [3,])
        check.add_expected('DEBUG', 9)
        logger.set_log(check)
        f(27, 3)

    def test_log_exception(self):
        check = DebugTest.log_check(self, [3,])
        check.add_expected('EXCEPTION', 'integer division or modulo by zero')
        logger.set_log(check)
        try:
            f(27, 0)
        except ZeroDivisionError:
            pass


if __name__ == '__main__':
    unittest.main()