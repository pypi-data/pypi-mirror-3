from datetime import datetime
from string import capwords

from types import TYPE_INFORMATION

## A common wrapper for all returned items.
#
# This class serves a very important purpose - it makes use of the meta type
# information to provide intelligent access to data members.
class Item:
    
    ## Constructs an Item to wrap the supplied dictionary.
    # @param data a dictionary
    # @param item_type the type of data
    def __init__(self, data, item_type):
        self._data      = data
        self._type_info = TYPE_INFORMATION[item_type] if item_type in TYPE_INFORMATION else {}
        self._type_name = capwords(item_type, '_').replace('_', ' ')
    
    ## Indicates whether the specified attribute exists in the disctionary.
    # @param index the index to retrieve
    # @return whether or not the index exists
    def __contains__(self, index):
        return index in self._data
    
    ## Returns the specified attribute from the dictionary.
    # @param index the index to retrieve
    # @return the item at the specified index
    def __getattr__(self, index):
        # Catch any KeyErrors and rethrow them as AttributeErrors
        try:
            # First determine if the requested member is a timestamp
            if index in self._type_field('date_fields', []):
                return datetime.fromtimestamp(self._data[index])
            # Either return the requested item or it if is another type, return a new Item instance
            if index in self._type_field('type_map', {}):
                return Item(self._data[index], self._type_info['type_map'][index])
            return self._data[index]
        except KeyError, e:
            raise AttributeError(e)
    
    ## Returns an internal representation of the response.
    # @return the internal representation
    def __repr__(self):
        try:
            return "<%s '%s'>" % (self._type_name, str(self),)
        except KeyError:
            return '<Unknown Item>'
    
    ## Returns a string representation of the response.
    # @return the string representation
    def __str__(self):
        str_field = self._type_field('str_field') if self._type_field('str_field') in self._data else self._type_field('id_field')
        if not str_field in self._data:
            raise KeyError('Unable to construct a string representation of the item.')
        return str(self._data[str_field])
    
    ## Returns data from the type information for this item.
    # @param index the index of the data to retrieve
    # @param default the default value to return in the event that index does not exist
    def _type_field(self, index, default=None):
        return self._type_info[index] if index in self._type_info else default
    
    ## Returns the ID of the item.
    # @return the ID of the item or None if unavailable
    def id(self):
        id_field = self._type_field('id_field')
        return self._data[id_field] if id_field in self._data else None
