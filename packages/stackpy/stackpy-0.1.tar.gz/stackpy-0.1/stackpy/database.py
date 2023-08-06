from sqlite3 import connect
from time import time

CACHE_TABLE_SCHEMA = '''
  CREATE TABLE cache (
    url varchar(255) NOT NULL,
    data text NOT NULL,
    expires int(11) NOT NULL,
    PRIMARY KEY (url)
  );
'''

## Provides a means of managing connections to a database.
#
# This class is used for a number of purposes, the most important of which is
# for caching request responses.
class Database:
    
    ## The current database that is being used.
    current = None
    
    ## Determines if a database is initialized and initializes one otherwise.
    #
    # If you attempt to fetch data before specifying a database class, an
    # in-memory SQLite database will be used by default. This database only
    # exists while the current process is running.
    @staticmethod
    def prepare():
        if Database.current is None:
            Database.current = SQLiteDatabase(':memory:')

## Provides an interface to an SQLite database.
class SQLiteDatabase:
    
    ## Creates / initializes the specified SQLite database.
    # @param database the filename of the database to use
    # @param clear whether to clear expired entries from the cache at startup or not
    #
    # Note: you may use ':memory:' for the database parameter to specify an
    # in-memory database.
    def __init__(self, database, clear=True):
        self._connection = connect(database)
        if not self._table_exists('cache'):
            self._connection.execute(CACHE_TABLE_SCHEMA)
        elif clear:
            self.clear()
    
    ## Determines whether the specified table exists within the database.
    # @param name the name of the table to check
    # @return True if the table exists
    def _table_exists(self, name):
        c = self._connection.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?', [name,])
        return not c.fetchone() is None
    
    ## Adds the specified URL and data to the cache.
    # @param url the URL of the request
    # @param data the data that corresponds with the URL
    # @param ttl the Time-To-Live (TTL) for this entry
    def add_to_cache(self, url, data, ttl):
        # Remove any existing entries and enter the new one
        self._connection.execute('DELETE FROM cache WHERE url = ?', (url,))
        self._connection.execute('INSERT INTO cache (url, data, expires) VALUES (?,?,?)',
                                 [unicode(url), unicode(data), int(time()) + ttl,])
    
    ## Purges entries from the cache.
    # @param clear_all whether to purge all entries from the cache instead of only expired ones
    def clear(self, clear_all=False):
        if clear_all:
            self._connection.execute('DELETE FROM cache')
        else:
            self._connection.execute('DELETE FROM cache WHERE expires < ?', [int(time()),])
    
    ## Retrieves the data for the specified URL from the cache.
    # @param url the URL of the request
    # @return the corresponding data or None if unavailable
    def retrieve_from_cache(self, url):
        c = self._connection.execute('SELECT data FROM cache WHERE url = ? AND expires >= ?',
                                     [unicode(url), int(time()),])
        row = c.fetchone()
        # If the row was found, return the first item
        if not row is None:
            row = row[0]
        return row