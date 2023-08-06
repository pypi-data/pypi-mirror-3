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

This file contains internal PythonMindmeister function, which perform correct
calls to the mindmeister.org API interface.
Additional information can be found by this URL:
http://www.mindmeister.com/developers/authentication

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


from repr import repr

'''
Base URL to be used to access mindmeister API services.
'''
BaseUrl = "http://www.mindmeister.com/services"

from hashlib import md5
from urllib2 import urlopen, build_opener, ProxyHandler
from urllib import quote

def calculateApiSig (secret, **params):
    '''
    Calculate API signature of the parameters list.

    Arguments:
    secret -- shared secret to be used for calculation.
    Optional (keyword) Arguments -- any arguments.
    '''
    builder = secret
    keys = params.keys()
    keys.sort()
    for iter in keys:
        if params[iter] == None:
            continue
        builder = builder + iter + str (params[iter])
    return md5(builder).hexdigest()

def createUrl (service, secret, **params):
    '''
    Create URL with request for mindmeister API.

    Arguments:
    service -- service mindmeister service to use.
    secret -- shared secret
    Optional (keyword) Arguments -- any service parameters
    '''
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

def performProxyRequest (proxy, service, secret, **params):
    '''
    Perform request to mindmeister API with proxy.

    Arguments:
    proxy -- http proxy address.
    service -- service mindmeister service to use.
    secret -- shared secret
    Optional (keyword) Arguments -- any service parameters
    '''
    proxy_handler = ProxyHandler({'http':proxy})
    opener = build_opener(proxy_handler)
    url = createUrl(service, secret, **params)
    url = quote (url, safe="%/:=&?~#+!$,;'@()*[]")
    result = opener.open(url).read()
    return result

def performRequest (service, token, **params):
    '''
    Perform request to mindmeister API.

    Arguments:
    service -- service mindmeister service to use.
    secret -- shared secret
    Optional (keyword) Arguments -- any service parameters
    '''
    if token.proxy != None:
      proxy_handler = ProxyHandler({'http': token.proxy})
      opener = build_opener (proxy_handler)
    else:
      opener = build_opener ()
    url = createUrl(service, token.secret, api_key = token.api_key, auth_token = token.token, **params)
    url = quote (url, safe="%/:=&?~#+!$,;'@()*[]")
    result = opener.open(url).read()
    return result

