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

from inspect import getargspec
from types import FunctionType, ClassType, TypeType

from rs.core import has_rs, get_rs
from rs.context import context_property
from rs.response import Response
from rs.status import OK, NO_CONTENT, BAD_REQUEST
from rs.error import Error
from rs.message import set_entity, set_headers


__all__ = [
    'Resource',
    'build',
    'build_all',
]


class Resource(object):
    
    def __init__(self):
        self.method = None
        self.path = None
        self.pattern = None
        self.consumer = None
        self.producer = None
        self.target = None
        self.type = None
        # inspect.ArgSpec, dictionary of default params
        self._argspec, self._argdefs = None, {}

    def __hash__(self):
        return hash(self.target) # for set()

    def __call__(self, context):
        result = self.target(**dict(self.resolve_params(context)))
        if result is None:
            response = Response(NO_CONTENT)
        elif isinstance(result, tuple):
            response = self.make_response(*result)
        elif not isinstance(result, Response):
            response = self.make_response(result)
        else:
            response = result
        return response


    def make_response(self, entity, status=None, headers=None):
        response = Response(status or OK)
        media = None
        if self.producer:
            media, produce = self.producer
            entity = produce(entity) if produce else entity
        set_entity(response, entity, media)
        set_headers(response, headers)
        return response

    def resolve_params(self,  context):
        for i, arg in enumerate(self._argspec.args):
            try:
                if i == 0 and self.type:
                    yield arg, context.instances[self.type]
                elif isinstance(self._argdefs.get(arg), context_property):
                    yield arg, self._argdefs[arg].__get__(context)
                elif arg in context.params.path:
                    yield arg, context.params.path[arg]
                elif arg in context.params.query:
                    yield arg, context.params.query[arg]
                elif arg in context.params.form:
                    yield arg, context.params.form[arg]
                elif arg in self._argdefs:
                    yield arg, self._argdefs[arg]
                else:
                    raise Error(BAD_REQUEST)
            except ValueError:
                raise Error(BAD_REQUEST)


class ResourceBuilder(object):

    def __init__(self, buildobj, _extends=None):
        if not isinstance(buildobj, (ClassType, TypeType, FunctionType)):
            raise TypeError(
                'unexpected type specified: {0}, must be class or function'
                .format(buildobj))
        self.buildobj = buildobj
        self._extends = []
        if _extends:
            self._extends.extend(_extends)

    def build(self):
        if isinstance(self.buildobj, (ClassType, TypeType)):
            return self.build_resources()
        elif isinstance(self.buildobj, FunctionType) and has_rs(self.buildobj):
            return [self.build_resource(target=self.buildobj)]
        return []

    def build_resources(self):
        resources = []
        if has_rs(self.buildobj):
            self._extends.append(get_rs(self.buildobj))
        for v in vars(self.buildobj).itervalues():
            if isinstance(v, (ClassType, TypeType)):
                resources.extend(ResourceBuilder(v,
                                    self._extends).build_resources())
            elif isinstance(v, FunctionType):
                if has_rs(v):
                    resources.append(self.build_resource(target=v,
                                                         type=self.buildobj))
        return resources

    def build_resource(self, target, type=None):
        resource = Resource()
        resource.target = target
        def combine_extends(rs_):
            for k,v in rs_.iteritems():
                if k in resource.__dict__ and not resource.__dict__.get(k):
                    resource.__dict__[k] = v
                elif k == 'path':
                    resource.path = (resource.path.rstrip('/') +
                                     '/' +
                                     v.strip('/'))
        if self._extends:
            for e in self._extends:
                combine_extends(e)
        combine_extends(get_rs(resource.target))
        if not resource.path:
            resource.path = '/'
        params = dict(('{{{0}}}'.format(p),
                       '(?P<{0}>.+)'.format(p)
                      ) for p in re.findall('\{(.+?)\}', resource.path))
        pattern = resource.path
        for k,v in params.iteritems():
            pattern = re.sub(k, v, pattern)
        resource.pattern = re.compile('^{0}$'.format(pattern.strip('/')))
        if type:
            resource.type = type
        resource._argspec = getargspec(resource.target)
        if resource._argspec.defaults:
            a = resource._argspec
            resource._argdefs = dict(zip(a.args[-len(a.defaults):],
                                         a.defaults))
        return resource


def build(resource):
    return ResourceBuilder(resource).build()


def build_all(resources):
    resources = set(resources)
    for c in [c for c in resources if isinstance(c, (ClassType, TypeType))]:
        for f in [f for f in vars(c).itervalues()
                  if isinstance(f, (ClassType, TypeType, FunctionType))]:
            if has_rs(f):
                resources.discard(f)
    resources = sum(map(build, resources), [])
    return resources