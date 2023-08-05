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


import re

from sys import maxint
from urlparse import parse_qs
from urllib import unquote_plus

from rs.core import rs_dict
from rs.error import Error
from rs.message import parse_media, parse_accept
from rs.status import (NOT_FOUND, NOT_ACCEPTABLE,
                       UNSUPPORTED_MEDIA_TYPE, METHOD_NOT_ALLOWED)


__all__ = [
    'Request',
    'dispatch',
]


class Request(object):
    def __init__(self):
        self.method = None
        self.uri = None
        self.version = None
        self.headers = {}
        self.entity = None

        
class RequestDispatcher(object):
    
    def __init__(self, resources):
        
        self.resources = resources
        self.q_key = {}
        self.m_key = {}
        self.params = rs_dict()
        
    def dispatch(self, request):
        resources = self.resources
        try:
            self.resources = self.resolve_path(request.uri.path)
            self.resources = self.resolve_method(request.method)
            self.resources = self.resolve_media(
                request.headers.get('content-type'))
            self.resources = self.resolve_accept(
                request.headers.get('accept'))
            self.resources = sorted(
                self.resources,
                key=lambda res: (self.q_key.get(res, 1),
                                 len(self.m_key[res].groups()) or maxint,
                                 len(res.path),),
                reverse=True)
            resource = self.resources[0]
            self.params.path = self.extract_path_params(self.m_key[resource])
            self.params.query = self.extract_query_params(request.uri.query)
            self.params.form = self.extract_form_params(request)
            return resource, self.params
        finally:
            self.__init__(resources)

    def resolve_path(self, path):
        resources = []
        for res in self.resources:
            m = res.pattern.match(path.strip('/'))
            if not m: continue
            self.m_key[res] = m
            resources.append(res)
        if not resources:
            raise Error(NOT_FOUND)
        return resources

    def resolve_method(self, method):
        resources = [res for res in self.resources if res.method == method]
        if not resources:
            error = Error(METHOD_NOT_ALLOWED)
            error.headers['allow'] = ', '.join(
                set([res.method for res in self.resources])
            )
            raise error
        return resources

    def resolve_media(self, media):
        if not media:
            resources = self.resources
        else:
            def resolve_consumer(consumer):
                if consumer:
                    supported_media, consumer = consumer
                    supported_media = parse_media(supported_media)
                    return re.match(supported_media.value.replace('*', '.*'),
                                    parse_media(media).value)
                else:
                    return True
            resources = [res for res in self.resources
                         if resolve_consumer(res.consumer)]
            if not resources:
                raise Error(UNSUPPORTED_MEDIA_TYPE)
        return resources

    def resolve_accept(self, accept):
        if not accept:
            resources = self.resources
        else:
            def resolve_producer(producer):
                if producer:
                    produced_media, producer = producer
                    produced_media = parse_media(produced_media)
                    for accepted_media in parse_accept(accept):
                        if re.match(accepted_media.value.replace('*', '.*'),
                                    produced_media.value):
                            return (float(accepted_media.q)
                                    if accepted_media.q else 1.0)
                else:
                    return 1.0
            resources = []
            for res in self.resources:
                q = resolve_producer(res.producer)
                if not q: continue
                self.q_key[res] = q
                resources.append(res)
            if not resources:
                raise Error(NOT_ACCEPTABLE)
        return resources

    def extract_path_params(self, match):
        return match.groupdict() or {}

    def extract_query_params(self, query):
        parsed = parse_qs(query, True) if query else {}
        return dict([(k, v if len(v) > 1 else v[0])
                    for k,v in parsed.iteritems()])

    def extract_form_params(self, request):
        if ('POST' == request.method and
            'application/x-www-form-urlencoded' ==
                request.headers.get('content-type', '').lower()):
            return self.extract_query_params(request.entity)
        return {}
            

def dispatch(resources, request):
    return RequestDispatcher(resources).dispatch(request)