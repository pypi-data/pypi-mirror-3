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
import webbrowser
import parser
import diagnostic
from lxml import etree
import os.path
from diagnostic import MindException

token_file = os.path.join(os.environ['HOME'], '.pymind.token')

class AuthToken:
    def __init__(self, key, secret):
        self.api_key = key
        self.secret = secret
        self.token = None
        self.perms = None

    def load (self):
      if not os.path.isfile(token_file):
        return False
      rawXML = open(token_file).read()
      parser = etree.XMLParser()
      root = etree.fromstring(rawXML, parser)
      for item in root:
        key = item.attrib['key']
        value = item.text
        setattr (self, key, value)
      return True

    def store (self):
      root = etree.Element("root")
      store = {}
      store['token'] = self.token
      store['username'] = self.username
      store['fullname'] = self.fullname
      store['perms'] = self.perms

      for key,value in store.items():
        child = etree.SubElement(root, "value", key=key)
        child.text = value

      FILE = open(token_file,"w")
      FILE.writelines(etree.tostring(root, pretty_print=True))
      FILE.close()


def getFrob (token):
    rawFrob = common.performRequest("rest", token.secret, api_key = token.api_key, method = "mm.auth.getFrob")
    root = parser.parse(rawFrob)
    return root[0].text


def getTokenBegin (token, perms):
    frob = getFrob(token)
    authUrl = common.createUrl("auth", token.secret, api_key = token.api_key,\
                               perms = perms, frob = frob)
    webbrowser.open(authUrl)
    return frob

def getTokenEnd (token, frob):
    rawToken = common.performRequest("rest", token.secret, api_key = token.api_key,\
                                     frob = frob, method = "mm.auth.getToken")
    root = parser.parse(rawToken)
    auth = root [0]
    if root.attrib['stat'] != 'ok':
      raise MindException ("mm.auth.getToken", auth)
    token.token = auth[0].text
    token.perms = auth[1].text
    token.__dict__.update(auth[2].attrib)


def checkToken (token):
    rawToken =  common.performRequest("rest", token.secret, api_key = token.api_key,\
                                      method = "mm.auth.checkToken",\
                                      auth_token = token.token)
    root = parser.parse(rawToken)
    auth = root [0]
    return token.token == auth[0].text and token.perms == auth[1].text
