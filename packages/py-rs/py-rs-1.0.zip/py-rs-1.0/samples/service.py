#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    service
    ~~~~~~~

    CANNONICAL REST SERVICE
    
"""


import httplib
import json

import rs


@rs.path('/service')
class Service(object):

    def __init__(self):
        self.data = {
            1: {"id": 1, "title": "first"},
            2: {"id": 2, "title": "second"},
            3: {"id": 3, "title": "third"},
        }

    @rs.get
    @rs.path('{id}')
    @rs.produces('application/json; charset=utf-8', json.dumps)
    def get_service(self, id):
        try:
            id = int(id)
            assert id > 0
            return self.data[id]
        except (ValueError, AssertionError):
            raise rs.error(httplib.BAD_REQUEST)
        except KeyError:
            raise rs.error(httplib.NOT_FOUND)

    @rs.get
    @rs.produces('application/json; charset=utf-8', json.dumps)
    def get_services(self, skip=None, take=None):
        try:
            if skip is not None:
                skip_ = int(skip)
                if skip_ < 0:
                    raise rs.error(httplib.BAD_REQUEST)
            else:
                skip_ = 0
            if take is not None:
                take_ = int(take)
                if take_ < 0:
                    raise rs.error(httplib.BAD_REQUEST)
            else:
                take_ = len(self.data)
        except ValueError:
            raise rs.error(httplib.BAD_REQUEST)
        else:
            return self.data.values()[skip_:skip_+take_]

    @rs.post
    @rs.consumes('application/json', json.loads)
    @rs.produces('application/json; charset=utf-8', json.dumps)
    def post_service(self, entity=rs.context.entity):
        try:
            id = entity['id']
            if id in self.data:
                raise rs.error(httplib.CONFLICT)
            self.data[id] = entity
            return entity, 201, {
                'Location':'/{id}'.format(id=id)
            }
        except KeyError:
            raise rs.error(httplib.BAD_REQUEST)

    @rs.put
    @rs.path('{id}')
    @rs.consumes('application/json', json.loads)
    @rs.produces('application/json; charset=utf-8', json.dumps)
    def put_service(self, id, entity=rs.context.entity):
        try:
            entity_id = entity['id']
            id = int(id)
            assert id > 0
            if 666 == id:
                raise rs.error(httplib.NOT_FOUND)
            assert entity_id == id
            created = id not in self.data
            self.data[id] = entity
            if created:
                return entity, 201, {
                    'Location':'/service/{id}'.format(id=id)
                }
            else:
                return entity
        except (KeyError, ValueError, AssertionError):
            raise rs.error(httplib.BAD_REQUEST)

    @rs.delete
    @rs.path('{id}')
    @rs.produces('application/json; charset=utf-8', json.dumps)
    def delete_service(self, id):
        try:
            id = int(id)
            assert id > 0
            return self.data.pop(int(id))
        except (ValueError, AssertionError):
            raise rs.error(httplib.BAD_REQUEST)
        except KeyError:
            raise rs.error(httplib.NOT_FOUND)


application = rs.application([Service])


if '__main__' == __name__:
    #import logging
    #logging.getLogger('rs.debug').propagate = 0
    application.run('', 8001, debug=True)