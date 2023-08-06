from request import Request

## Represents an entry point into any Stack Exchange site.
#
# A Site object is used to represent a Stack Exchange site and provide access to
# the site-specific methods. For example, to access questions on Stack Overflow,
# you would create a Site object initialized to Stack Overflow and then access
# the questions attribute.
#
# Alternatively, if you are providing the user with a choice of Stack Exchange
# sites, you may want to simply use API.sites to enumerate the sites and display
# the list to the user. This avoids the need to create a Site object since the
# return value of API.sites is a list of pre-initialized Site objects.
class Site:
    
    # A list of all top-level site-specific methods
    _methods = ['answers',
                'badges',
                'comments',
                'events',
                'info',
                'posts',
                'privileges',
                'questions',
                'revisions',
                'search',
                'similar',
                'suggested-edits',
                'tags',
                'users',]
    
    ## Constructs a Site object for the specified site.
    # @param data the domain name of the site or data returned from the /sites method
    # @param ignored this parameter is ignored
    def __init__(self, data, ignored=None):
        if isinstance(data, basestring):
            self._domain = data
            self._data = None
        else:
            self._domain = data['api_site_parameter']
            self._data = data
    
    ## Returns a Request object initialized to the specified method.
    # @param method the name of the method
    # @return a Request object
    def __getattr__(self, method):
        if not method in self._methods:
            raise KeyError('The "%s" method does not exist.' % method)
        return Request(self._domain, method)
    
    ## Returns basic information about the site.
    # @return the specified attribute
    #
    # Note: if the information has not been previously retrieved (such as by the
    # /sites method), this method will make the request to retrieve it.
    def __getitem__(self, index):
        return getattr(self._fetch(), index)
    
    ## Returns an internal representation of the current instance.
    # @return the internal representation
    def __repr__(self):
        return '<Site>' if self._data is None else "<Site '%s'>" % self._data.name
    
    ## Returns a string representation of the site.
    # @return the human-readable name of the site
    #
    # Note: this method will fetch the information if it hasn't already been
    # retrieved.
    def __str__(self):
        return self._fetch()['name']
    
    ## Either fetches the information for a site or returns it.
    # @returns the site's information
    def _fetch(self):
        if self._data is None:
            self._data = self.info.filter('!*qYPS3vhc(3')[0].site
        return self._data