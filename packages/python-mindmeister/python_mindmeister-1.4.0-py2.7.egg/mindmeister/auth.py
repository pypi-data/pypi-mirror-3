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

This file contains MindMeister API calls for authentication. Additional
information can be found by this URL:
http://www.mindmeister.com/developers/explore

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
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
    '''
    This class represent authentication token, used to sign API calls.

    Token can be created with API key and secret (provided by mindmeister or
    application). See
    http://www.mindmeister.com/developers/authentication
    for more details.
    Token can be stored as file for further use.

    In order to use token it must be registered by the following action
    sequence:
      1. token = AuthToken(api_key, secret)
      2. frob = getTokenBegin (token, method)
         MindMeister.com web page with confirmation dialog will be opened.
         User should confirm access to the application.
      4. getTokenEnd (token, frob)

    Method can be:
      1. read
      2. write
      3. delete
    '''
    def __init__(self, key, secret):
      '''
      Create new (unregistered) token.

      Arguments:
      key -- API key
      secret -- shared secret
      Optional (keyword) Arguments:
      '''
      self.api_key = key
      self.secret = secret
      self.token = None
      self.perms = None
      self.proxy = None

    def load (self):
      '''
      Load token from file. Returns true if token has been successfully loaded.

      Arguments:
      Optional (keyword) Arguments:
      '''
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
      '''
      Store token to a file.

      Arguments:
      Optional (keyword) Arguments:
      '''
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


    def getFrob (self):
        '''
        Returns a new frob for authentication.

        Arguments:
        Optional (keyword) Arguments:

        This function calls mm.auth.getFrob MindMeister API method
        More documentation can be found by this URL:
        http://www.mindmeister.com/developers/explore_method?method=mm.auth.getFrob
        '''
        rawFrob = common.performRequest("rest", self, method = "mm.auth.getFrob")
        root = parser.parse(rawFrob)
        return root[0].text


    def getTokenBegin (self, perms):
        '''
        Start token registration process.

        Arguments:
        perms -- permissions (method)
        Optional (keyword) Arguments:
        '''
        frob = self.getFrob()
        authUrl = common.createUrl("auth", self.secret, api_key = self.api_key,\
                                   perms = perms, frob = frob)
        webbrowser.open(authUrl)
        return frob

    def getTokenEnd (self, frob):
        '''
        Finish token registration process.

        Arguments:
        perms -- frob obtained from getTokenBegin call
        Optional (keyword) Arguments:
        '''
        rawToken = common.performRequest("rest", self, frob = frob, method = "mm.auth.getToken")
        root = parser.parse(rawToken)
        auth = root [0]
        if root.attrib['stat'] != 'ok':
          raise MindException ("mm.auth.getToken", auth)
        self.token = auth[0].text
        self.perms = auth[1].text
        self.__dict__.update(auth[2].attrib)

    def check (self):
        '''
        Checks the token for a user.

        Arguments:
        Optional (keyword) Arguments:

        This function calls mm.auth.checkToken MindMeister API method
        More documentation can be found by this URL:
        http://www.mindmeister.com/developers/explore_method?method=mm.auth.checkToken
        '''
        rawToken =  common.performRequest("rest", self, method = "mm.auth.checkToken")
        root = parser.parse(rawToken)
        auth = root [0]
        return self.token == auth[0].text and self.perms == auth[1].text

    def setProxy (self, proxy):
        '''
        Sets proxy to be used with this token.

        Arguments:
        proxy -- proxy to be used.
        Optional (keyword) Arguments:

        Sets proxy to be used with this token. Use None to disable proxy usage.
        '''
        self.proxy = proxy

