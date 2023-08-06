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

This module represents entity classes, used within PythonMindmeister.

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


from lxml import etree
import dateutil.parser
import time

class Revision:
  '''
  This class represents map revision.
  '''
  def __init__(self, data):
    '''
    Construct new revision from XML response.
    Arguments:
    data -- XML response.
    Optional (keyword) Arguments:
    '''
    self.__dict__.update (data.attrib)

  def __str__(self):
    '''
    Convert object to string.
    '''
    return "Revision: " + self.revision + " (" + self.created + ")"

class Idea:
  '''
  This class represents single map item (idea).
  '''
  def __init__(self, data):
    '''
    Construct new revision from XML response.
    Arguments:
    data -- XML response.
    Optional (keyword) Arguments:
    '''
    for field in data:
      setattr (self, field.tag, field.text)
    if hasattr (self, 'modifiedat'):
      modifiedat = dateutil.parser.parse (self.modifiedat)
      self.timestamp = int (time.mktime (modifiedat.timetuple()))
    else:
      self.timestamp = int (time.time ())
    self.ideas = []
    self.icons = []
    if hasattr (self, 'icon') and self.icon != None:
      self.icons = self.icon.split(',')
      self.icons.sort()


class Map:
  '''
  This class represents map header:
    1. Title
    2. Id
    3. Creation date
    4. Date of the last modification

  See
  http://www.mindmeister.com/developers/explore_method?method=mm.maps.getList
  for more information.
  '''
  def __init__(self, data):
    '''
    Construct new map header from XML response.
    Arguments:
    data -- XML response.
    Optional (keyword) Arguments:
    '''
    self.__dict__.update (data.attrib)

class FullMap:
  '''
  This class represents map (as tree of Ideas).

  See
  http://www.mindmeister.com/developers/explore_method?method=mm.maps.getMap
  for more information.
  '''
  def __init__(self, data):
    '''
    Construct new map from XML response.
    Arguments:
    data -- XML response.
    Optional (keyword) Arguments:
    '''
    self.map = None
    self.ideas = []
    for item in data:
      if item.tag == 'map':
        self.map = Map (item)
      elif item.tag == 'ideas':
        ideas = map (lambda curr: Idea (curr), item)
        mapping = {}
        for idea in ideas:
          if idea.parent:
            parent = mapping[idea.parent]
          else:
            parent = self
          idea.int_parent = parent
          parent.ideas.append (idea)
          mapping[idea.id] = idea

class Folder:
  '''
  This class represents folder:
    1. Id
    2. Parent id
    3. Name

  See
  http://www.mindmeister.com/developers/explore_method?method=mm.folders.getList
  for more information.
  '''
  def __init__(self, data):
    '''
    Construct new folder from XML response.
    Arguments:
    data -- XML response.
    Optional (keyword) Arguments:
    '''
    self.__dict__.update (data.attrib)
