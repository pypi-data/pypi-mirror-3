# -*- coding: utf-8 -*-
#
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


from logging import getLogger

from rs.error import Error
from rs.status import (INTERNAL_SERVER_ERROR,
                       NOT_MODIFIED,
                       NO_CONTENT,
                       responses)


__all__ = [
    'WSGIApplication',
]


_logger = getLogger(__name__)

_CHUNK_LENGTH = 8192

def _chunks(l, n=_CHUNK_LENGTH):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class ResourceManager(object):

    def init(self, resources):
        from rs.resource import build_all
        if resources is None:
            from rs.core import registry as resources
        self.resources = build_all(resources)

    def __get__(self, controller, cls):
        if controller is None:
            return self
        class resource_factory(object):
            def __getitem__(self_, request):
                from rs.request import dispatch
                return dispatch(self.resources, request)
        return resource_factory()


class InstanceManager(object):

    def init(self):
        self.instances = {}

    def __get__(self, controller, cls):
        if controller is None:
            return self
        class instance_factory(object):
            def __getitem__(self_, type_):
                if type_ is not None and type_ not in self.instances:
                    self.instances[type_] = type_()
                return self.instances[type_]
        return instance_factory()


class ContextManager(object):

    def __get__(self, controller, cls):
        if controller is None:
            return self
        class context_factory(object):
            def __getitem__(self_, request):
                from rs.context import Context
                return Context(controller,
                               request,
                               *controller.resources[request])
        return context_factory()


class WSGIApplication(object):

    class ResponseFailure(Exception): pass

    resources = ResourceManager()
    instances = InstanceManager()
    context = ContextManager()

    def __init__(self, resources=None):
        WSGIApplication.resources.init(resources)
        WSGIApplication.instances.init()

    def complete_request(self, environ):
        from rs.request import Request
        from rs.message import parse_media, entity, uri
        request = Request()
        request.version = environ['SERVER_PROTOCOL']
        request.method = environ['REQUEST_METHOD']
        request.uri = uri(environ.get('PATH_INFO', '/'),
                          environ.get('QUERY_STRING', ''))
        headers = [(k[5:].replace('_', '-').lower(), v)
                    for k,v in environ.iteritems() if k.startswith('HTTP_')]
        headers.append(('content-length', environ.get('CONTENT_LENGTH', '')))
        headers.append(('content-type', environ.get('CONTENT_TYPE', '')))
        request.headers = dict(headers)
        entity_len = int(request.headers['content-length'] or '0')
        if entity_len:
            charset = parse_media(request.headers.get('content-type')).charset
            request.entity = entity(environ['wsgi.input'].read(entity_len),
                                    charset)
        return request

    def complete_response(self, response, environ, start_response):
        try:
            entity = ''
            if (environ['REQUEST_METHOD'] != 'HEAD' and
                response.entity is not None and
                response.entity is not str and
                response.status not in (NO_CONTENT,NOT_MODIFIED)):
                entity = str(response.entity)
            status = '{status} {reason}'.format(
                status=response.status,
                reason=responses.get(response.status, ''))
            start_response(status, list(response.headers.iteritems()))
        except Exception as e:
            raise WSGIApplication.ResponseFailure(e)
        return _chunks(entity)

    def __call__(self, environ, start_response):
        try:
            request = self.complete_request(environ)
            with self.context[request] as context:
                response = context.resource(context)
                return self.complete_response(response,
                                              environ,
                                              start_response)
        except Error as e:
            return self.complete_response(e, environ, start_response)
        except (IOError, WSGIApplication.ResponseFailure) as e:
            _logger.exception(e)
        except Exception:
            from traceback import format_exception
            from sys import exc_info
            _logger.critical(''.join(format_exception(*exc_info())))
            return self.complete_response(Error(INTERNAL_SERVER_ERROR),
                                          environ, start_response)
        return []

    def run(self, host, port, make_server=None, debug=False):
        try:
            if debug:
                try: from rs.debug import debug as enable_debug
                except ImportError: pass
                else: enable_debug()
            if not getLogger(__package__).handlers:
                try: from rs.debug import basic_logging
                except ImportError: pass
                else:
                    from logging import INFO, DEBUG
                    basic_logging(DEBUG if debug else INFO)
            if not make_server:
                from wsgiref.simple_server import make_server
            server = make_server(host or '127.0.0.1', port, self)
            from contextlib import closing
            with closing(server.socket):
                server.serve_forever()
        except (KeyboardInterrupt, SystemExit): pass