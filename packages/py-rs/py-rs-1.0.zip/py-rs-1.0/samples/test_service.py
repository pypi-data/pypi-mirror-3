#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    test_service
    ~~~~~~~~~~~~

    CANNONICAL REST SERVICE TEST
    
"""


import httplib
import json

from collections import namedtuple
from functools import partial
from contextlib import closing


media = 'application/json'
produce = lambda e: json.dumps(e) if e is not None else e
consume = lambda e: json.loads(e) if e is not None else e
response = namedtuple('response', 'status, entity, headers')
entity = dict


c = httplib.HTTPConnection('127.0.0.1', 8001)
c.set_debuglevel(0)


def request(method, uri, entity=None, headers_=None, strict=False):
    headers = headers_ or {}
    if entity is not None:
        headers['content-type'] = media
    c.request(method,
              uri,
              body=entity if strict else produce(entity),
              headers=headers)
    with closing(c.getresponse()) as r:
        return response(
            r.status,
            consume(r.read() if r.status in (httplib.OK,
                                             httplib.CREATED) else None),
            dict(r.getheaders())
        )


get = partial(request, 'GET')
post = partial(request, 'POST')
put = partial(request, 'PUT')
delete = partial(request, 'DELETE')


##############################
# Tests for template GET/{key}
##############################
# 1.	GET MUST return a resource given a key if the resource with that key exists
r = get('service/1')
assert 200 == r.status
assert r.entity is not None
# 2.	GET MUST return 400-BadRequest if the key is invalid
r = get('service/-1')
assert 400 == r.status
# 3.	GET MUST return 404-NotFound if the key is not found
r = get('service/404')
assert 404 == r.status
# 4.	GET MUST return 304-NotModified if Conditional GET conditions are met using If-None-Match
# TODO: GET MUST return 304-NotModified if Conditional GET conditions are met using If-None-Match
# 5.	GET SHOULD return an ETag header
# TODO: GET SHOULD return an ETag header
#################################################
# Tests for template GET/?skip={skip}&take={take}
#################################################
# 1.	GET MUST skip {skip} resources in the collection and return up to {take} resources.
r = get('service/?skip=1&take=1')
assert 200 == r.status
assert 1 == len(r.entity)
assert 2 == r.entity[0]['id']
r = get('service/?skip=1&take=2')
assert 200 == r.status
assert 2 == len(r.entity)
assert 2 == r.entity[0]['id']
assert 3 == r.entity[1]['id']
# 2.	GET MUST return resources starting with the first one when {skip} is not defined
r = get('service/?take=1')
assert 200 == r.status
assert 1 == len(r.entity)
assert 1 == r.entity[0]['id']
# 3.	GET MUST return zero resources when {skip} is greater than the number of resources in the collection
r = get('service/?skip=3')
assert 200 == r.status
assert 0 == len(r.entity)
# 4.	GET MUST return 400-BadRequest if {skip} is < 0
r = get('service/?skip=-1000&take=1')
assert 400 == r.status
# 5.	GET MUST return zero or more resources when {take} is not provided
r = get('service/?skip=1')
assert 2 == len(r.entity)
assert 2 == r.entity[0]['id']
assert 3 == r.entity[1]['id']
# 6.	GET MUST return 400-BadRequest if {take} is < 0
r = get('service/?skip=1&take=-1000')
assert 400 == r.status
##############
# Tests POST /
##############
# 1.	POST MUST append a valid resource to the resource collection using a server generated key and return
#       201 – Created with a location header, entity tag and entity body
r = post('service', entity(id=4, title='fourth'))
assert 201 == r.status
assert r.entity is not None
assert r.entity['id'] == 4
assert r.entity['title'] == 'fourth'
assert r.headers['location'] == '/4'
# TODO: 201 – Created with a location header, **entity tag** and entity body
# 2.	POST MUST return 400-Bad Request if the entity is invalid
r = post('service', repr(object), strict=True)
assert 400 == r.status
# 3.	POST MUST return 409-Conflict if the entity conflicts with another entity
r = post('service', entity(id=1, title='no matter'))
assert 409 == r.status
# 4.	POST MUST ignore writes to entity fields the server considers read only
# PASS
#################
# Tests PUT/{key}
#################
# 1.	PUT MUST Update the entity identified by the URI if it exists and return 200-OK with the modified entity
#       and etag header
# TODO: 200-OK with the modified entity and **etag header**
r = put('service/4', entity(id=4, title='updated'))
assert 200 == r.status
assert r.entity is not None
assert r.entity['id'] == 4
assert r.entity['title'] == 'updated'
# 2.	PUT MAY Add a new entity using the key provided in the URI and return 201-Created with entity location
#       and etag
r = put('service/5', entity(id=5, title='fifth'))
assert 201 == r.status
assert r.entity is not None
assert r.entity['id'] == 5
assert r.entity['title'] == 'fifth'
assert r.headers['location'] == '/service/5'
# TODO: 201-Created with entity location and **etag**
# 3.	PUT MUST respect the Precondition If-Match
# TODO: PUT MUST respect the Precondition If-Match
# 4.	PUT MUST be Idempotent
# PASS
# 5.	PUT MUST NOT alter the key of the entity so that it does not match the key of the URI
r = put('service/5', entity(id=6, title='sixth'))
assert 400 == r.status
r = get('service/5')
assert 200 == r.status
assert r.entity is not None
assert r.entity['id'] == 5
assert r.entity['title'] == 'fifth'
# 6.	PUT MUST return 400-BadRequest if the entity is invalid
r = put('service/6', repr(object), strict=True)
assert 400 == r.status
# 7.	PUT MUST return 400-BadRequest if the key is invalid
r = put('service/-10', entity(id=-10, title='invalid'))
assert 400 == r.status
# 8.	PUT MUST ignore writes to entity fields the server considers read only
# PASS
# 9.	PUT MUST return 404-NotFound if the server does not allow new entities to be added with PUT
r = put('service/666', entity(id=666, title='hell yeah'))
assert 404 == r.status
#####################
# Tests DELETE /{key}
#####################
# 1.	DELETE SHOULD delete an entity that exists and return 200-OK with the deleted entity or 204-No Content
#       if the response does not include the entity
r = delete('service/4')
assert 200 == r.status
assert r.entity is not None
assert r.entity['id'] == 4
assert r.entity['title'] == 'updated'
r = delete('service/5')
assert 200 == r.status
assert r.entity is not None
assert r.entity['id'] == 5
assert r.entity['title'] == 'fifth'
# 2.	DELETE SHOULD be idempotent
# PASS
# 3.	DELETE SHOULD return with 412-PreconditionFailed if no matching entity for If-Matchetag
# TODO: DELETE SHOULD return with 412-PreconditionFailed if no matching entity for If-Matchetag
# 4.	DELETE SHOULD succeed if matching entity for If-Matchetag
# TODO: DELETE SHOULD succeed if matching entity for If-Matchetag
# 5.	DELETE SHOULD succeed if wildcard used in If-Match etag
# TODO: DELETE SHOULD succeed if wildcard used in If-Match etag
# 6.	DELETE SHOULD return 202-Accepted if the request to delete has not been enacted
# PASS
# 7.	DELETE SHOULD return 400-BadRequest if the key is invalid
r = delete('service/-1')
assert 400 == r.status

print 'Ok!'