from urllib import urlencode
from urllib2 import urlopen, HTTPError
from urlparse import parse_qs
from zlib import decompress, error, MAX_WBITS

from request import Request
from site import Site
from url import APIError, URL

## @cond META
## Meta class making it possible to call global methods as attributes.
class MetaAPI(type):
    
    # Note that filter is omitted here because the Filter class
    # provides access to these methods.
    _methods = ['access_tokens',
                'apps',
                'errors',
                'inbox',
                'notifications',
                'sites',
                'users',]
    
    ## Returns a request object initialized to the specified method.
    # @param method the name of the method
    # @return a Request object
    def __getattr__(self, method):
        if not method in self._methods:
            raise KeyError('The "%s" method does not exist.' % method)
        # For obvious reasons we need the user to use an underscore for
        # access-token instead of a dash. Now correct it back.
        if method == 'access_tokens':
            method = 'access-tokens'
        # If the requested method was 'sites' then we want the objects
        # returned in the response to be Site objects
        return Request(URL(), method, Site if method == 'sites' else None)
## @endcond

## Represents an entry point to the global network-wide methods.
class API:
    
    # The metaclass used for providing static attributes
    __metaclass__ = MetaAPI
    
    ## The API key used for all requests.
    #
    # Note: it is highly recommended that you register for an API key as you
    # gain the benefit of a much greater request quota and usage statistics.
    key = ''
    
    ## The client ID of the current application.
    client_id = None
    
    ## The client secret used exclusively for the explicit authentication flow.
    client_secret = None
    
    ## Begins the explicit authentication flow.
    # @param scope the type of access the application is requesting (separate more than one item with a comma)
    # @param redirect_uri the URL to redirect to when the process completes
    # @param state an optional string to be returned after completion
    # @return the URL that the client should be redirected to in order to continue the process
    #
    # Note that this method requires that API.client_id be set.
    @staticmethod
    def begin_explicit(scope, redirect_uri, state=''):
        return 'https://stackexchange.com/oauth?%s' % urlencode({
            'client_id':    API.client_id,
            'scope':        scope,
            'redirect_uri': redirect_uri,
            'state':        state,
        })
    
    ## Completes the explicit authentication flow.
    # @param code the value of the GET parameter 'code'
    # @param redirect_uri the same URL you provided to API.begin_explicit
    # @return the access token
    #
    # Note that this method requires that API.client_id and API.client_secret be set.
    @staticmethod
    def complete_explicit(code, redirect_uri):
        # Catch any HTTP errors because we want to grab error messages
        try:
            raw_data = urlopen('https://stackexchange.com/oauth/access_token',
                               data=urlencode({'client_id':     API.client_id,
                                               'client_secret': API.client_secret,
                                               'code':          code,
                                               'redirect_uri':  redirect_uri,})).read()
            return parse_qs(raw_data)['access_token'][0]
        except HTTPError, e:
            try:
                json_data = decompress(e.read(), 16 + MAX_WBITS).decode('UTF-8')
                data = loads(json_data)
                raise APIError(data['error']['type'], data['error']['message'] if 'message' in data['error'] else 'unknown error')
            except error:
                raise APIError(0, 'unable to decompress GZipped response from API server')
    
    ## Begins the implicit authentication flow.
    # @param scope the type of access the application is requesting (separate more than one item with a comma)
    # @param redirect_uri the URL to redirect to when the process completes
    # @param state an optional string to be returned after completion
    # @return the URL that the client should be redirected to in order to continue the process
    #
    # Note that this method requires that API.client_id be set. Also note that there is no
    # method for completing the implicit flow because the access token is returned as a hash
    # in the URL.
    @staticmethod
    def begin_implicit(scope, redirect_uri, state=''):
        return 'https://stackexchange.com/oauth/dialog?%s' % urlencode({
            'client_id':    API.client_id,
            'scope':        scope,
            'redirect_uri': redirect_uri,
            'state':        state,
        })