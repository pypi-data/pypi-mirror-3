import url

## Represents a filter for controlling the data returned in a response.
#
# Because the API is designed to only return a default set of data in each
# response, sometimes the need arises for additional data to be included. The
# Filter class provides an easy-to-use interface for constructing and using
# filters.
class Filter:
    
    ## Default filter to use for all requests.
    #
    # You can change this filter at any time and it will affect any filters that
    # are instantiated after setting this attribute.
    default = 'default'
    
    ## Constructs a filter object.
    # @param base the ID of an existing filter
    def __init__(self, base=None):
        self._filter_id = self.default if base is None else base # use the provided base filter for the current filter
        self._includes  = []
        self._excludes  = []
        self._dirty = False # indicates if the filter has unsaved changes
    
    ## Returns the internal representation of the filter.
    # @return the internal representation
    def __repr__(self):
        return '<Filter %s>' % ("'%s'" % self._filter_id if not self._dirty else '[* dirty]')
    
    ## Returns the filter ID, creating it if necessary.
    # @return the filter ID
    def __str__(self):
        # If the filter is dirty, then create it
        if self._dirty:
            self.create()
        return self._filter_id
    
    ## Adds the specified items to the filter's include list.
    # @param includes either a single item or list/tuple of items
    def add_includes(self, includes):
        if isinstance(includes, basestring):
            self._includes.append(includes)
        else:
            self._includes.extend(includes)
        self._dirty = True
        return self
    
    ## Adds the specified items to the filter's exclude list.
    # @param excludes either a single item or a list/tuple of items
    def add_excludes(self, excludes):
        if isinstance(excludes, basestring):
            self._excludes.append(excludes)
        else:
            self._excludes.extend(excludes)
        self._dirty = True
        return self
    
    ## Creates the filter.
    def create(self):
        f_url = url.URL()
        f_url.add_method('filters').add_method('create').add_parameter('base', self._filter_id)
        f_url.set_post_data({'include': ';'.join(self._includes),
                             'exclude': ';'.join(self._excludes),})
        self._filter_id = f_url.fetch(True)['items'][0]['filter']
        self._dirty = False
        return self
