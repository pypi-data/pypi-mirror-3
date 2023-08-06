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

This file contains MindMeister API calls for ideas. Additional information can
be found by this URL:
http://www.mindmeister.com/developers/explore

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


import common
import  parser
from objects import Idea
from diagnostic import MindException


def addAttachment (token, file, idea_id, map_id):
    '''
    Adds an attachment to a node.

    Arguments:
    file
    idea_id
    map_id
    Optional (keyword) Arguments:

    This function calls mm.ideas.addAttachment MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.addAttachment
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.addAttachment", file = file, idea_id = idea_id, map_id = map_id)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.addAttachment', root[0])
    return Idea(root[0])

def change (token, idea_id, map_id, **args):
    '''
    Changes an idea on a given map.

    Arguments:
    idea_id
    map_id
    Optional (keyword) Arguments:
    icon
    link
    note
    style
    task
    title
    x_pos
    y_pos

    This function calls mm.ideas.change MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.change
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.change", idea_id = idea_id, map_id = map_id, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.change', root[0])
    return Idea(root[0])

def deleteAttachment (token, attachment_id, idea_id, map_id):
    '''
    Deletes an attachment.

    Arguments:
    attachment_id
    idea_id
    map_id
    Optional (keyword) Arguments:

    This function calls mm.ideas.deleteAttachment MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.deleteAttachment
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.deleteAttachment", attachment_id = attachment_id, idea_id = idea_id, map_id = map_id)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.deleteAttachment', root[0])

def delete (token, idea_id, map_id):
    '''
    Deletes an idea on a given map.

    Arguments:
    idea_id
    map_id
    Optional (keyword) Arguments:

    This function calls mm.ideas.delete MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.delete
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.delete", idea_id = idea_id, map_id = map_id)
    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.delete', root[0])
    return Idea(root[0])

def insert (token, map_id, parent_id, title, **args):
    '''
    Inserts a new idea on a given map.

    Arguments:
    map_id
    parent_id
    title
    Optional (keyword) Arguments:
    icon
    link
    note
    rank
    style
    task
    x_pos
    y_pos

    This function calls mm.ideas.insert MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.insert
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.insert", map_id = map_id, parent_id = parent_id, title = title, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.insert', root[0])
    return Idea(root[0])

def move (token, idea_id, map_id, parent_id, rank, **args):
    '''
    Moves an idea on a given map.

    Arguments:
    idea_id
    map_id
    parent_id
    rank
    Optional (keyword) Arguments:
    x_pos
    y_pos

    This function calls mm.ideas.move MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.move
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.move", idea_id = idea_id, map_id = map_id, parent_id = parent_id, rank = rank, **args)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.move', root[0])
    return Idea(root[0])

def toggleClosed (token, idea_id, map_id, closed = None):
    '''
    Toggles (or sets) the open/closed status of a branch.

    Arguments:
    idea_id
    map_id
    Optional (keyword) Arguments:
    closed

    This function calls mm.ideas.toggleClosed MindMeister API method
    More documentation can be found by this URL:
    http://www.mindmeister.com/developers/explore_method?method=mm.ideas.toggleClosed
    '''
    rawResult = common.performRequest ("rest", token, method="mm.ideas.toggleClosed", idea_id = idea_id, map_id = map_id, closed = closed)

    root = parser.parse (rawResult)
    if root.attrib['stat'] != "ok":
        raise MindException('mm.ideas.toggleClosed', root[0])

