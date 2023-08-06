#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

try:
    import simplejson as json
except ImportError:
    import json

import base64
import hashlib
import hmac
import inspect
import string
import time
import urllib

# 3rd party libraries that might not be present during initial install
#  but we need to import for the version #
try:
    import httplib2
    import poster
except ImportError:
    pass



__version__ = '20120430'
__author__ = u'Mike Lewis'

API_ENDPOINT = 'http://api.singleplatform.co'

# Number of times to retry http requests
NUM_REQUEST_RETRIES = 3



# Generic SinglePlatform exception
class SinglePlatformException(Exception): pass

error_types = {
}


def b64_key_to_binary(key):
    """Convert a base64 encoded key to binary"""
    padding_factor = (4 - len(key) % 4) % 4
    key += "=" * padding_factor
    return base64.b64decode(unicode(key).translate(dict(zip(map(ord, u'-_'), u'+/'))))


class SinglePlatform(object):
    """SinglePlatform API wrapper"""

    def __init__(self, client_id, signing_key, api_key=None):
        """Sets up the api object"""
        binary_key = b64_key_to_binary(signing_key)
        # Set up endpoints
        self.base_requester = self.Requester(client_id, binary_key, api_key)
        # Dynamically enable endpoints
        self._attach_endpoints()

    def _attach_endpoints(self):
        """Dynamically attach endpoint callables to this client"""
        for name, endpoint in inspect.getmembers(self):
            if inspect.isclass(endpoint) and issubclass(endpoint, self._Endpoint) and (endpoint is not self._Endpoint):
                endpoint_instance = endpoint(self.base_requester)
                setattr(self, endpoint_instance.endpoint, endpoint_instance)


    class Requester(object):
        """Api requesting object"""
        def __init__(self, client_id, binary_key, api_key=None,):
            """Sets up the api object"""
            self.api_key = api_key
            self.client_id = client_id
            self.binary_key = binary_key

        def GET(self, path, params=None):
            """GET request that returns processed data"""
            if not params: params = {}
            # Attach the client id
            params['client'] = self.client_id
            # Get the uri and it's corresponding signature
            relative_uri = self.build_uri(path, params)
            params['sig'] = self.sign_uri(relative_uri)
            # Include the API key if provided
            if self.api_key:
                params['apiKey'] = self.api_key
            # Make the request, including the sig
            final_uri = u'{API_ENDPOINT}{signed_uri}'.format(
                API_ENDPOINT=API_ENDPOINT,
                signed_uri=self.build_uri(path, params)
            )
            log.debug(u'GET url: {0}'.format(final_uri))
            return _request_with_retry(final_uri)

        def build_uri(self, path, params=None):
            """Construct a url to use"""
            _params = {}
            if params:
                _params.update(params)
            return '{path}?{params}'.format(
                path=path,
                params=urllib.urlencode(_params)
            )

        def sign_uri(self, uri):
            """Sign this uri"""
            digest = hmac.new(self.binary_key, uri, hashlib.sha1).digest()
            digest = base64.b64encode(digest)
            digest =  digest.translate(string.maketrans('+/', '-_'))
            return digest.rstrip('=')


    class _Endpoint(object):
        """Generic endpoint class"""
        def __init__(self, requester):
            """Stores the request function for retrieving data"""
            self.requester = requester

        def _expanded_path(self, path=None):
            """Gets the expanded path, given this endpoint"""
            return '/{expanded_path}'.format(
                expanded_path='/'.join(p for p in (self.endpoint, path) if p)
            )

        def GET(self, path=None, *args, **kwargs):
            """Use the requester to get the data"""
            return self.requester.GET(self._expanded_path(path), *args, **kwargs)



    class Restaurants(_Endpoint):
        """Restaurant specific endpoint"""
        endpoint = 'restaurants'

        def search(self, params):
            """https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantssearch"""
            return self.GET('search', params)

        def location(self, LOCATION):
            """https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATION"""
            return self.GET('{LOCATION}'.format(LOCATION=LOCATION))

        def menu(self, LOCATION):
            """https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATIONmenu"""
            return self.GET('{LOCATION}/menu'.format(LOCATION=LOCATION))

        def shortmenu(self, LOCATION):
            """https://singleplatform.jira.com/wiki/display/PubDocs/SinglePlatform+Publisher+Integration#SinglePlatformPublisherIntegration-URIrestaurantsLOCATIONshortmenu"""
            return self.GET('{LOCATION}/shortmenu'.format(LOCATION=LOCATION))




"""
Network helper functions
"""
def _request_with_retry(url, data=None):
    """Tries to load data from an endpoint using retries"""
    for i in xrange(NUM_REQUEST_RETRIES):
        try:
            return _process_request_with_httplib2(url, data)
        except SinglePlatformException, e:
            # Some errors don't bear repeating
            if e.__class__ in []: raise
            if ((i + 1) == NUM_REQUEST_RETRIES): raise
        time.sleep(1)

def _process_request_with_httplib2(url, data=None):
    """Make the request and handle exception processing"""
    try:
        h = httplib2.Http()
        if data:
            datagen, headers = poster.encode.multipart_encode(data)
            data = ''.join(datagen)
            method = 'POST'
        else:
            headers = {}
            method = 'GET'
        headers['Accept'] = u'application/json'
        response, body = h.request(url, method, headers=headers, body=data)
        data = _json_to_data(body)
        # Default case, Got proper response
        if response.status == 200:
            return data
        return _check_response(data)
    except httplib2.HttpLib2Error, e:
        log.error(e)
        raise SinglePlatformException(u'Error connecting with SinglePlatform API')

def _json_to_data(s):
    """Convert a response string to data"""
    try:
        return json.loads(s)
    except ValueError, e:
        log.error('Invalid response: {0}'.format(e))
        raise SinglePlatformException(e)

def _check_response(data):
    """Processes the response data"""
    if data.get('ok') == u'true': return data
    exc = error_types.get(data.get('status'))
    if exc:
        raise exc(data.get('status'))
    else:
        log.error(u'Unknown error type: {0}'.format(data.get('status')))
        raise SinglePlatformException(data.get('status'))
