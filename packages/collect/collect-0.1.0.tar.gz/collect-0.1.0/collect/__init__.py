import couchdbkit
import datetime

from collect import settings


class Connection(object):
    """
    Connection object that abstracts access to the CouchDB server.
    
    @param uri: URI of the CouchDB server
    """
    def __init__(self, uri):
        self._uri = uri
        self._server = couchdbkit.Server(uri=self._uri)
    
    def __repr__(self):
        return '<Connection "%s">' % self._uri
    
    def collection(self, name):
        """
        Get or create a collection from the server and return a collect.Collection object.
        
        @param name: name of the collection
        """
        return Collection(self, name)


class Collection(object):
    """
    Collection object that abstracts access to a CouchDB database.
    
    @param connection: a collect.Connection object
    @param name: name of the collection i.e. CouchDB database
    """
    def __init__(self, connection, name):
        self._connection = connection
        self.name = name
        self._db = self._connection._server.get_or_create_db(self.name)
    
    def __repr__(self):
        return '<Collection "%s">' % self.name
    
    def collect(self, data):
        """
        Collect data in the collection i.e. send it to the server and store it in the database.
        The current date and time is automatically added to each collected data record in the `timestamp` attribute.
        
        @param data: the data to be stored, as a dictionary
        """
        if not isinstance(data, dict):
            raise TypeError, "data needs to be a dict"
        if not len(data):
            raise TypeError, "data is empty"
        data.update(timestamp=datetime.datetime.now().isoformat()[:19])
        res = self._db.save_doc(data)
        if not res['ok']:
            raise SystemError, "saving data failed"
        return res['id']
    
    def remove(self):
        """
        Remove the collection and its contents from the server.
        """
        return self._connection._server.delete_db(self.name)
    
    def all(self):
        """
        Return all data saved in that collection.
        """
        docs = self._db.all_docs()
        return docs


def connect(uri=settings.DEFAULT_SERVER_URI):
    """
    Connect to the collect server and return a collect.Connection object.
    
    @param uri: URI of the CouchDB server (default: collect.settings.DEFAULT_SERVER_URI, "http://data.collect.io/")
    """
    return Connection(uri=uri)
