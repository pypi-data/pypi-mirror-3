'''
Copyright 2012 Alexey Kravets  <mr.kayrick@gmail.com>

This file is part of PythonMindmeister.

PythonMindmeister is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PythonMindmeister is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PythonMindmeister.  If not, see <http://www.gnu.org/licenses/>.
'''


import common
import  parser
from objects import Idea
from diagnostic import MindException


def addAttachment (token, file, idea_id, map_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.addAttachment", file = file,\
                                       idea_id = idea_id, map_id = map_id, auth_token =token.token)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.addAttachment', root[0])
    return Idea(root[0])

def change (token, idea_id, map_id, **args):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.change", idea_id = idea_id,\
                                       map_id = map_id, auth_token = token.token, **args)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.change', root[0])
    return Idea(root[0])

def deleteAttachment (token, attachment_id, idea_id, map_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.deleteAttachment", attachment_id = attachment_id,\
                                       idea_id = idea_id, map_id = map_id, auth_token = token.token)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.deleteAttachment', root[0])

def delete (token, idea_id, map_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.delete", idea_id = idea_id, map_id = map_id,\
                                       auth_token =token.token)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.delete', root[0])
    return Idea(root[0])

def insert (token, map_id, parent_id, title, **args):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.insert", map_id = map_id,\
                                        parent_id = parent_id, title = title, auth_token = token.token, **args)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.insert', root[0])
    return Idea(root[0])

def move (token, idea_id, map_id, parent_id, rank, **args):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.move", idea_id = idea_id, map_id = map_id,\
                                       parent_id = parent_id, rank = rank, auth_token =token.token, **args)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.move', root[0])
    return Idea(root[0])

def toggleClosed (token, idea_id, map_id, closed = None):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.ideas.toggleClosed", idea_id = idea_id,\
                                       map_id = map_id, auth_token = token.token, closed = closed)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.toggleClosed', root[0])

