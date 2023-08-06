'''
Copyright 2012 Alexey Kravets  <mr.kayrick@gmail.com>

This file is part of PyMind.

PyMind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMind.  If not, see <http://www.gnu.org/licenses/>.
'''


import common
import parser
from objects import Map, FullMap, Revision
from diagnostic import MindException

def getList(token):
    rawResult = common.performRequest("rest", token.secret,\
        api_key = token.api_key,\
        method = "mm.maps.getList", auth_token = token.token)

    root = parser.parse(rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.getList', root[0])
    else:
      return map (lambda curr: Map (curr), root[0])


def add (token):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.add", auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.maps.add', root[0])
    else:
        return Map(root[0])


def delete (token, map_id):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.delete",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.delete', root[0])

def duplicate (token, map_id):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.duplicate",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.duplicate', root[0])
    else:
        return Map(root[0])

def getMap (token, map_id, **args):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.getMap",\
        map_id = map_id, auth_token = token.token, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.maps.getMap', root[0])
    else:
        return FullMap(root)

def undo (token, map_id):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.undo",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.undo', root[0])

def redo (token, map_id):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.redo",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.redo', root[0])

def insertGeistesblitz (token, title):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.insertGeistesblitz",\
        auth_token = token.token, title = title)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.insertGeistesblitz', root[0])

def history (token, map_id, **args):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.history",\
        map_id = map_id, auth_token =token.token, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.history', root[0])
    else:
        return map (lambda curr: Revision(curr), root[0])
