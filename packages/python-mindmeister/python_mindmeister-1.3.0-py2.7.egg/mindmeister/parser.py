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

This file implement parsing of the XML responses to the mindmeister API calls.

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


from lxml import etree


__parser = etree.XMLParser()

def parse(response):
    '''
    Parse response

    Arguments:
    response -- XML response (int plain text)
    Optional (keyword) Arguments:
    '''
    text = response.replace('\n','')
    return etree.fromstring(text, __parser)
