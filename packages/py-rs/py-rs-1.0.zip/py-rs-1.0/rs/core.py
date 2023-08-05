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


from types import FunctionType, ClassType, TypeType


__all__ = [
    'encoding',
    'registry',
    'method',
    'path',
    'produces',
    'consumes',
    'get',
    'post',
    'put',
    'delete',
]


encoding = 'utf-8' # default encoding.
registry = set()   # set of registered resources.


get_rs = lambda o: getattr(o, '__rs_dict__')
set_rs = lambda o, v: setattr(o, '__rs_dict__', v)
has_rs = lambda o: (get_rs(o)
                    if isinstance(o, rs_dict)
                    else hasattr(o, '__rs_dict__'))


class rs_dict(dict):
    __slots__ = ()
    __getattr__ = lambda self, k: self.get(k)
    __setattr__ = lambda self, k, v: self.setdefault(k, v)


def rs_api(rs_func):
    def rs_actual(resource):
        if not isinstance(resource, (ClassType, TypeType, FunctionType)):
            raise TypeError(
                'unexpected type specified: {0}, must be class or function'
                .format(resource))
        if not has_rs(resource):
            set_rs(resource, rs_dict())
            registry.add(resource)
        rs_func(get_rs(resource))
        return resource
    return rs_actual


def method(name):
    @rs_api
    def method_actual(rs):
        rs.method = name
    return method_actual


def path(pattern):
    @rs_api
    def path_actual(rs):
        rs.path = '/' + pattern.strip('/\\').replace('\\', '/')
    return path_actual


def produces(media, producer=None):
    @rs_api
    def produces_actual(rs):
        rs.producer = media.lower(), producer
    return produces_actual


def consumes(media, consumer=None):
    @rs_api
    def consumes_actual(rs):
        rs.consumer = media.lower(), consumer
    return consumes_actual


get     = method('GET')
post    = method('POST')
put     = method('PUT')
delete  = method('DELETE')