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


__all__ = [
    'Context',
]

class context_property(property):

    def __init__(self, fget, *args, **kwargs):
        property.__init__(self, fget)
        self.args, self.kwargs = args, kwargs

    def __nonzero__(self):
        return False

    def __call__(self, *args, **kwargs):
        obj = type(self).__new__(self.__class__)
        obj.__init__(self.fget, *args, **kwargs)
        return obj

    def __get__(self, context, cls=None):
        if context is None:
            return self
        return self.fget(context, *self.args, **self.kwargs)

class application_property(property):

    def __init__(self, fget):
        property.__init__(self, fget)
        self.cache = {}

    def __get__(self, context, cls=None):
        if context is None:
            return self
        if context not in self.cache:
            self.cache[context] = self.fget(context)
        return self.cache[context]

    def __delete__(self, context):
        if context in self.cache:
            del self.cache[context]
        

class Context(object):

    def __init__(self, application, request, resource, params):
        """

        """
        self._app = application
        self._request = request
        self._resource = resource
        self._params = params

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        del self.instances
        del self.resources

    @context_property
    def entity(self):
        entity = self._request.entity
        if entity is not None and self._resource.consumer:
            media, consume = self._resource.consumer
            if consume:
                entity = consume(entity)
        return entity

    @context_property
    def request(self):
        return self._request

    @context_property
    def uri(self):
        return self._request.uri

    @context_property
    def alias(self, *aliases, **kwargs):
        for dict in (self._params.path,
                     self._params.query,
                     self._params.form):
            for alias in aliases:
                if alias in dict:
                    return dict[alias]
        if 'default' not in kwargs:
            raise ValueError('None of {0} values found'.format(aliases))
        return kwargs['default']

    @application_property
    def resources(self):
        return self._app.resources

    @application_property
    def instances(self):
        return self._app.instances

    @property
    def params(self):
        return self._params

    @property
    def resource(self):
        return self._resource
