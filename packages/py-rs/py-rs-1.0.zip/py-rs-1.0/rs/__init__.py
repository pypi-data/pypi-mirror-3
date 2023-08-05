# Copyright (c) 2011 Sergey K.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
    rs
    ~~

    This is a WSGI application framework for robust and rapid RESTful service
    development in Python.

    Goals & Features:

      * Fast and robust development of RESTful interfaces of any complexity.

      * Lightweight and flexible APIs for easy development of new RESTful
        services and integration with existing ones.

      * The whole idea of this framework is based upon providing a set of APIs
        decorators which needs to be enough to apply to your code to represent
        a RESTful interface for it.

      * This is strict WSGI application framework, no production web server
        included, there are plenty of them available in Python, so use any of
        the WSGI server you like. Although for testing purposes default
        wsgiref.simple_server.WSGIServer is used.

    Example::

        import rs

        @rs.get
        @rs.path('index.html')
        @rs.produces('text/html')
        def index():
            return '<HTML><HEAD><TITLE>Let's rock!</TITLE></HEAD><BODY/></HTML>'

        @rs.get
        @rs.path('favicon.ico')
        @rs.produces('image/png')
        def favicon():
            return open('RS-ICON-LOGO.png', 'rb').read()

        application = rs.application()
        
        application.run('localhost', 8001)

    :copyright: Copyright 2011 by Sergey K.
    :license: MIT License, see LICENSE for details.
"""

__version__ = '1.0'

__author__  = 'Sergey K.'


from rs.core import method, get, post, put, delete, path, produces, consumes
from rs.error import Error as error
from rs.context import Context as context
from rs.application import WSGIApplication as application
