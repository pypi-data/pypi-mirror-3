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


from lxml import etree
import dateutil.parser
import time
from tempfile import mkstemp
import maps


class Revision:
  def __init__(self, data):
    self.__dict__.update (data.attrib)

  def __str__(self):
    return "Revision: " + self.revision + " (" + self.created + ")"

class Idea:
  def __init__(self, data):
    for field in data:
      setattr (self, field.tag, field.text)
    if hasattr (self, 'modifiedat'):
      modifiedat = dateutil.parser.parse (self.modifiedat)
      self.timestamp = int (time.mktime (modifiedat.timetuple()))
    else:
      self.timestamp = int (time.time ())
    self.ideas = []

class Map:
  def __init__(self, data):
    self.__dict__.update (data.attrib)

class FullMap:
  def __init__(self, data):
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

  def process_node(self, idea, parent):
    timestamp = str (idea.timestamp)
    node = etree.SubElement(parent, "note", time=timestamp, priority="default")
    node.text = idea.title
    for child in idea.ideas:
      self.process_node (child, node)

  def update(self, token):
    new = maps.getMap (token, self.map.id)
    self.map = new.map
    self.ideas = new.ideas

class Folder:
  def __init__(self, data):
    self.__dict__.update (data.attrib)
