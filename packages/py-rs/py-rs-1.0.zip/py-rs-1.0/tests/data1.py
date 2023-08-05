# -*- coding: utf-8 -*-

# Version: Python 2.6.6
# Author: Sergey K.
# Created: 2011-08-20


import rs


@rs.method('GET')
class EmptyRes(object):
    pass


@rs.method('GET')
@rs.path('default')
class DummyRes(object):

    @rs.path('dumb')
    class DumbRes(object):

        @rs.path('dumbest')
        def dumb(self):
            pass

        @rs.path('deepest')
        class DeepestRes(object):
            @rs.path('res')
            def res(self):
                pass


    @rs.path('dummy')
    def dummy(self):
        pass


@rs.path('multi')
class MultiRes(object):

    @rs.method('POST')
    @rs.path('services\\{id}')
    def create_service(self): pass

    @rs.method('GET')
    @rs.path('services\\')
    def get_services(self): pass


@rs.get
@rs.path('index.html')
@rs.produces('application/xml; charset="utf-8"')
def funcRes():
    pass

    