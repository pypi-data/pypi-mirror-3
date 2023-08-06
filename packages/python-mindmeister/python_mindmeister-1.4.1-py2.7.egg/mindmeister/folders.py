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

This file contains MindMeister API calls for folder. Additional information
can be found by this URL:
http://www.mindmeister.com/developers/explore

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


import common
import parser
from objects import Folder
from diagnostic import MindException

def add (token, name, **args):
    '''
    Adds a folder.

    Arguments:
    name
    Optional (keyword) Arguments:
    is_open
    parent_id

    This function calls mm.folders.add MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.folders.add
    '''
    rawResult = common.performRequest ("rest", token, method="mm.folders.add", name = name, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.add', root[0])
    else:
        return Folder(root[0])

def delete (token, folder_id):
    '''
    Deletes a folder.

    Arguments:
    folder_id
    Optional (keyword) Arguments:

    This function calls mm.folders.delete MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.folders.delete
    '''
    rawResult = common.performRequest ("rest", token, method="mm.folders.delete", folder_id = folder_id)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.delete', root[0])

def getList (token):
    '''
    List all folders for the current user.

    Arguments:
    Optional (keyword) Arguments:

    This function calls mm.folders.getList MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.folders.getList
    '''
    rawResult = common.performRequest ("rest", token, method="mm.folders.getList")

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.getList', root[0])
    else:
        return map (lambda curr: Folder (curr), root[0])

def move (token, folder_id, parent_id = None):
    '''
    Moves a folder.

    Arguments:
    folder_id
    Optional (keyword) Arguments:
    parent_id

    This function calls mm.folders.move MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.folders.move
    '''
    rawResult = common.performRequest ("rest", token, method="mm.folders.move", folder_id = folder_id, parent_id = parent_id)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.move', root[0])
    else:
        return Folder (root[0])

def rename (token, folder_id, name):
    '''
    Renames a folder.

    Arguments:
    folder_id
    name
    Optional (keyword) Arguments:

    This function calls mm.folders.rename MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.folders.rename
    '''
    rawResult = common.performRequest ("rest", token, method="mm.folders.rename", folder_id = folder_id, name = name)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.folders.rename', root[0])
    else:
        return Folder (root[0])

