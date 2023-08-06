from copy import deepcopy
from urllib import quote

from item import Item
from types import METHOD_TO_TYPE_MAPPING
from url import URL

## Represents a request for API data.
#
# The Request object provides a standard interface for creating requests for API
# data. An instance of this class is never directly initialized, but instead
# returned from a method in either the API or Site class.
class Request:
    
    # A list of all non-top-level methods including network and site-specific ones
    # This list is needed because __getattr__ needs to differentiate between methods and parameters
    # Note: 'create' is omitted here because it duplicates functionality found in the Filter class
    _methods = ['add',
                'advanced',
                'answers',
                'associated',
                'badges',
                'comments',
                'de_authenticate',
                'delete',
                'edit',
                'elected',
                'faq',
                'favorites',
                'featured',
                'full',
                'inbox',
                'info',
                'invalidate',
                'linked',
                'mentioned',
                'merges',
                'moderator_only',
                'moderators',
                'name',
                'no_answers',
                'notifications',
                'privileges',
                'questions',
                'recipients',
                'related',
                'reputation',
                'reputation_history',
                'required',
                'revisions',
                'suggested_edits',
                'synonyms',
                'tags',
                'timeline',
                'top_answer_tags',
                'top_answerers',
                'top_answers',
                'top_askers',
                'top_question_tags',
                'top_questions',
                'unaccepted',
                'unanswered',
                'unread',
                'wikis',
                'write_permissions',]
    
    # The presence of any of these methods will force all parameters to be
    # passed as POST parameters instead of with GET.
    _post_methods = ['add',
                     'delete',
                     'edit',]
    
    ## Creates a request object.
    # @param url the domain name to initialize the URL to or a URL instance
    # @param method a method name to append to the URL
    # @param response_type an optional type to use for returning the response
    def __init__(self, url=None, method=None, response_type=Item):
        self._url = URL(url) if isinstance(url, basestring) else url
        if not method is None:
            self._url.add_method(method)
        self._response_type = response_type
        self._data = None
    
    ## Provides a way to specify IDs.
    # @param items either a single item or a list/tuple of items
    def __call__(self, items):
        # This inline method converts any type to a string
        def item_str(item):
            return str(item.id() if issubclass(item.__class__, Item) else item)
        # Ensure that items is iterable - if not, put it in a list
        try:
            # Trigger the TypeError exception if this object is a string
            # so that it isn't treated like a list
            if isinstance(items, basestring):
                raise TypeError
            iter(items)
        except (KeyError, TypeError):
            items = [items,]
        # Now we have a list of 'things' - convert them to a list of strings and join them
        self._url.add_method(';'.join(quote(item_str(i), '/') for i in items), True)
        return self
    
    ## Appends the specified item to the appropriate part of the URL.
    # @param raw_item the item to be added
    #
    # Note: any underscores in the item name are converted to dashes.
    def __getattr__(self, raw_item):
        # access_token is a singular exception to this rule
        item = raw_item if raw_item == 'access_token' else raw_item.replace('_', '-')
        # No matter what, we're going to be modifying the URL, so make
        # a deep copy of it
        url = deepcopy(self._url)
        if item in self._methods:
            if item in self._post_methods:
                url.switch_to_post()
            return Request(url, item)
        else:
            # This is a neat trick - we return a local function that will
            # finish setting the parameter in the URL once the user provides
            # the value for the specified parameter.
            def set_parameter(value):
                url.add_parameter(item, value)
                return Request(url)
            return set_parameter
    
    ## Retrieves the item or data at the specified index and returns it.
    # @param index the index to retrieve the item / data from
    # @return the item / data at the specified index
    #
    # This method serves a dual purpose - if supplied with an integer value it
    # will return the item at such an index. If however, supplied with a string,
    # it will return the appropriate value from the response. For example, given
    # the value 'total', it will return the total number of items in the set.
    def __getitem__(self, index):
        return self._fetch()['items'][index] if type(index) == int else self._fetch()[index]
    
    ## Provides a means of iterating through the response.
    # @return an iterator for the response
    def __iter__(self):
        return iter(self._fetch()['items'])
    
    ## Returns the total number of items in the response.
    # @return the number of items in the response
    def __len__(self):
        return len(self._fetch()['items'])
    
    ## Returns an internal representation of the current instance.
    # @return the internal representation
    def __repr__(self):
        return "<Request '%s'>" % self._url
    
    ## Either fetches the data for the request or returns the data.
    # @return the data for the request
    def _fetch(self):
        if self._data is None:
            # Fetch the data and replace the 'items' entry with initialized response objects
            self._data = self._url.fetch()
            if self._url.base_method() in METHOD_TO_TYPE_MAPPING:
                item_type = METHOD_TO_TYPE_MAPPING[self._url.base_method()]
            else:
                item_type = self._data['type'] if 'type' in self._data else ''
            self._data['items'] = [self._response_type(i, item_type) for i in self._data['items']]
        return self._data