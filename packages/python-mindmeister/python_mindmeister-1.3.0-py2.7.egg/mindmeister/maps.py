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

This file contains MindMeister API calls for maps. Additional information can
be found by this URL:
http://www.mindmeister.com/developers/explore

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


import common
import parser
from objects import Map, FullMap, Revision
from diagnostic import MindException

def getList(token):
    '''
    Returns the list of maps of the current user.

    Arguments:
    Optional (keyword) Arguments:
    expand_people
    include_folder
    page
    per_page
    query

    This function calls mm.maps.add MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.getList
    '''
    rawResult = common.performRequest("rest", token.secret,\
        api_key = token.api_key,\
        method = "mm.maps.getList", auth_token = token.token)

    root = parser.parse(rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.getList', root[0])
    else:
      return map (lambda curr: Map (curr), root[0])


def add (token):
    '''
    Creates a map.

    Arguments:
    Optional (keyword) Arguments:

    This function calls mm.maps.add MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.add
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.add", auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.maps.add', root[0])
    else:
        return Map(root[0])


def delete (token, map_id):
    '''
    Deletes a map.

    Arguments:
    map_id
    Optional (keyword) Arguments:

    This function calls mm.maps.delete MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.delete
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.delete",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.delete', root[0])

def duplicate (token, map_id):
    '''
    Duplicates a map.

    Arguments:
    map_id
    Optional (keyword) Arguments:
    revision

    This function calls mm.maps.duplicate MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.duplicate
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.duplicate",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.duplicate', root[0])
    else:
        return Map(root[0])

def getMap (token, map_id, **args):
    '''
    Get all ideas of a map.

    Arguments:
    map_id
    Optional (keyword) Arguments:
    expand_people
    include_folder
    include_theme
    revision

    This function calls mm.maps.getMap MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.getMap
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.getMap",\
        map_id = map_id, auth_token = token.token, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.maps.getMap', root[0])
    else:
        return FullMap(root)

def undo (token, map_id):
    '''
    Undo last modification on map.

    Arguments:
    map_id
    Optional (keyword) Arguments:

    This function calls mm.maps.undo MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.undo
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.undo",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.undo', root[0])

def redo (token, map_id):
    '''
    Redo last modification on map.

    Arguments:
    map_id
    Optional (keyword) Arguments:

    This function calls mm.maps.redo MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.redo
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.redo",\
        map_id = map_id, auth_token =token.token)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.redo', root[0])

def insertGeistesblitz (token, title):
    '''
    Inserts a Geistesblitz in the default map.

    Arguments:
    title
    Optional (keyword) Arguments:

    This function calls mm.maps.insertGeistesblitz MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.insertGeistesblitz
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.insertGeistesblitz",\
        auth_token = token.token, title = title)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.insertGeistesblitz', root[0])

def history (token, map_id, **args):
    '''
    Gets the revisions of a map.

    Arguments:
    map_id
    Optional (keyword) Arguments:
    only_last
    show_redo

    This function calls mm.maps.history MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.maps.history
    '''
    rawResult = common.performRequest ("rest", token.secret,\
        api_key = token.api_key, method="mm.maps.history",\
        map_id = map_id, auth_token =token.token, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException ('mm.maps.history', root[0])
    else:
        return map (lambda curr: Revision(curr), root[0])
