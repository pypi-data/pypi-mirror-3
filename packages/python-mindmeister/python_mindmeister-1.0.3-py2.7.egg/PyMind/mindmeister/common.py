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


from repr import repr
BaseUrl = "http://www.mindmeister.com/services"

from hashlib import md5
from urllib2 import urlopen
from urllib import quote

class requestError (Exception):
    def __init__(self, reason):
        self.reason = reason;

    def __str__(self):
        return repr(self.reason)

def calculateApiSig (secret, **params):
    builder = secret
    keys = params.keys()
    keys.sort()
    for iter in keys:
        if params[iter] == None:
            continue
        builder = builder + iter + str (params[iter])
    return md5(builder).hexdigest()

def createUrl (service, secret, **params):
    builder = BaseUrl + "/" + service + "?"
    for iter in params.keys():
        if params[iter] == None:
            continue
        builder = builder + iter + "=" + str (params[iter]) + "&"
    if secret != None:
        api_sig = calculateApiSig(secret, **params)
        return builder + "api_sig=" + api_sig
    else:
        return builder

def performRequest (service, secret, **params):
    url = createUrl(service, secret, **params)
    url = quote (url, safe="%/:=&?~#+!$,;'@()*[]")
    result = urlopen(url).read()
    return result

