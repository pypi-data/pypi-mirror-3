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
from objects import Folder
from diagnostic import MindException

def add (token, name, **args):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.folders.add",\
        name = name, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.add', root[0])
    else:
        return Folder(root[0])

def delete (token, folder_id):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.folders.delete",\
        folder_id = folder_id)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.delete', root[0])

def getList (token):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.folders.getList")

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.getList', root[0])
    else:
        return map (lambda curr: Folder (curr), root[0])

def move (token, folder_id, parent_id = None):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.folders.move",\
        folder_id = folder_id, parent_id = parent_id)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.move', root[0])
    else:
        return Folder (root[0])

def rename (token, folder_id, name):
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.folders.rename",\
        folder_id = folder_id, name = name)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.rename', root[0])
    else:
        return Folder (root[0])

