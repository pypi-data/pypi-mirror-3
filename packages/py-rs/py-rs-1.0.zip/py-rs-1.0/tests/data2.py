# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-15

import rs

class dummy(object): pass

def _server():
    server = dummy()
    server.get_instance = lambda cls: None
    return server


def _params():
    params = rs.core.rs_dict()
    params.path = {}
    params.query = {}
    params.form = {}
    return params