from json import loads
from urllib import urlencode
from urllib2 import urlopen, HTTPError
from zlib import decompress, MAX_WBITS

import api
from database import Database
from filter import Filter

## Represents an error that occurred while accessing the API.
class APIError(Exception):
    
    ## Constructs the exception object.
    def __init__(self, error_id, error_message):
        self._error_id      = error_id
        self._error_message = error_message
    
    ## Returns a string representation of the exception
    # @return the error string
    def __str__(self):
        return 'API error %d: %s.' % (self._error_id, self._error_message,)
    
    ## Returns the unique ID for the error.
    # @return the unique ID
    def error_id(self):
        return self._error_id

## Represents a %URL for accessing an API resource.
#
# The URL class provides methods for manipulating a %URL that will eventually be
# used to access an API method. There is rarely a need to interact with this
# class directly - instead use the methods of API and Site.
class URL:
    
    ## Constructs a URL object optionally initialized to a domain.
    # @param domain a site domain name
    def __init__(self, domain=None):
        self._prefix       = 'http'
        self._method       = 'GET'
        self._methods      = []
        self._base_methods = []
        self._parameters   = {}
        # Add two default parameters to accompany each request
        self._parameters['key']    = api.API.key
        self._parameters['filter'] = Filter.default
        if not domain is None:
            self._parameters['site'] = domain
        self._ttl = 600 # cache data for 10 minutes by default
    
    ## Returns an internal representation of the URL.
    # @return the internal representation
    def __repr__(self):
        return "<%s request for '%s'>" % (self._method,
                                          '/'.join(self._methods),)
    
    ## Constructs the string representation of the URL.
    # @return the complete URL as a string
    def __str__(self):
        return '%s://api.stackexchange.com/2.1/%s%s' % (self._prefix,
                                                        '/'.join(self._methods),
                                                        '?' + urlencode(self._parameters) if self._method == 'GET' else '',)
    
    ## Retrieves the JSON data for the provided URL.
    # @param forbid_empty raises an error if fewer than one item is returned
    # @returns the JSON response
    #
    # This method will generate the URL for the request and either retrieve the
    # JSON for that URL or return the latest value from the cache.
    def fetch(self, forbid_empty=False):
        url = str(self)
        # If caching is enabled for this URL, check the cache
        if self._ttl:
            Database.prepare()
            json_data = Database.current.retrieve_from_cache(url)
            if not json_data is None:
                return loads(json_data)
        # Catch any HTTP errors because we want to grab error messages
        try:
            post_data = urlencode(self._parameters) if self._method == 'POST' else None
            raw_data = urlopen(url, data=post_data).read()
        except HTTPError, e:
            raw_data = e.read()
        json_data = decompress(raw_data, 16 + MAX_WBITS).decode('UTF-8')
        data = loads(json_data)
        # Check the data for errors
        if 'error_id' in data and 'error_message' in data:
            raise APIError(data['error_id'], data['error_message'])
        if not 'items' in data:
            raise KeyError('"items" missing from server response.')
        # Add it to the cache for next time
        if self._ttl:
            Database.current.add_to_cache(url, json_data, self._ttl)
        # If the caller wants at least one item, make sure there is
        if forbid_empty and not len(data['items']):
            raise IndexError('"items" is empty but at least one item was expected.')
        return data
    
    ## Adds a method to the end of the URL.
    # @param method the name of the method
    # @param is_variable whether this 'method' can vary between requests
    #
    # A bit of an explanation for this method seems in order. The `is_variable`
    # parameter indicates whether this particular part of the method is
    # constant or if it represents an ID or tag or some other variant.
    def add_method(self, method, is_variable=False):
        self._methods.append(method)
        self._base_methods.append('*' if is_variable else method)
        return self
    
    ## Adds a query string parameter to the URL.
    # @param name the name of the parameter
    # @param value the value for the parameter
    #
    # Note: if a parameter with the same name already exists, it will be replaced. Also,
    # if name is set to 'access_token', then the URL will switch to HTTPS.
    def add_parameter(self, name, value):
        self._parameters[name] = str(value)
        if name == 'access_token':
            self.secure()
        return self
    
    ## Returns the base method used for the request.
    # @return the base method
    #
    # The return value of this method is used extensively in the meta type
    # system Stack.PY employs as well as observing the rate limit.
    def base_method(self):
        return '/'.join(self._base_methods)
    
    ## Enables the secure HTTP protocol (HTTPS) for the URL.
    def secure(self):
        self._prefix = 'https'
        return self
    
    ## Sets the Time-To-Live (TTL) for this request.
    # @param ttl the TTL value for the URL
    #
    # Note: passing a value of 0 for ttl will result in caching being disabled for the URL
    def set_ttl(self, ttl):
        self._ttl = ttl
        return self
    
    ## Switches the URL to a POST request instead of a GET request.
    #
    # Note: this will disable caching
    def switch_to_post(self):
        self._method = 'POST'
        self._ttl = 0
        return self