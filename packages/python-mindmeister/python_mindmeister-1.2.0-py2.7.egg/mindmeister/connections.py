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
import parser
from objects import Error


def add (token, from_id, map_id, to_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.connections.add", from_id = from_id, map_id = map_id, to_id = to_id, auth_token =token.token)
    root = parser.parse ("mm.connections.add", rawResult)
    if root.attrib['stat'] != "ok":
        return Error(root[0])


def changeColor (token, color, from_id, map_id, to_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.connections.changeColor", color = color, from_id = from_id, map_id = map_id, to_id = to_id, auth_token =token.token)
    root = parser.parse ("mm.connections.changeColor", rawResult)
    if root.attrib['stat'] != "ok":
        return Error(root[0])

def delete (token, from_id, map_id, to_id):
    rawResult = common.performRequest ("rest", token.secret, api_key = token.api_key, method="mm.connections.delete", from_id = from_id, map_id = map_id, to_id = to_id, auth_token =token.token)
    root = parser.parse ("mm.connections.delete", rawResult)
    if root.attrib['stat'] != "ok":
        return Error(root[0])

