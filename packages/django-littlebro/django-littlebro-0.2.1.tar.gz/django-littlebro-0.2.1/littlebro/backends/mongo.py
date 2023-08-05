import anyjson
from datetime import datetime
from time import time
from pymongo.connection import Connection
from littlebro.backends.base import BaseBackend
from littlebro.conf import settings

class MongoBackend(BaseBackend):
    """
    Backend to save event records to MongoDB.
    """
    def __init__(self, *args, **kwargs):
        BaseBackend.__init__(self, *args, **kwargs)
        self.host = settings.MONGODB_HOST
        self.port = settings.MONGODB_PORT
        self.collection = settings.DEFAULT_MONGO_COLLECTION
        self.db = settings.DEFAULT_MONGO_DB
        
    def _connect(self):
        """
        Returns a pymongo Connection object.
        """
        return Connection(host=self.host, port=self.port)
    
    def _get_db(self):
        """
        Returns instance's Mongo database string.
        """
        return self.db

    def _set_collection(self, collection):
        """
        Sets collection within a given Mongo database.
        """
        self.collection = collection
        return
    
    def _get_collection(self):
        """
        Gets collection within a given Mongo database.
        """
        conn = self._connect()
        return conn[self._get_db()][self.collection]
       
    def save(self, event, time=time(), params={}, collection=None):
        """
        Save event in MongoDB collection.
        """
        if collection:
            self._set_collection(collection)
        col = self._get_collection()
        col.insert({
            'event': event,
            'timestamp': datetime.fromtimestamp(time),
            'params': params
        })