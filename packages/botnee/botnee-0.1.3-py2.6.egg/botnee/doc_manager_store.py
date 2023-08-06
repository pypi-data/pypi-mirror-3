"""
Document Manager Store connection wrapper class
"""

import pymongo
#import bson
#from bson.code import Code
import logging
#from time import time
#from bidict import bidict
#import hashlib

from standard_document import StandardDocument

from botnee import debug#, errors

#import botnee_config

class DocManagerStore(object):
    """
    Connects to the Document Manager's mongo store
    """
    
    def __init__(self, 
                server='localhost', 
                port=27017,
                db_name='documentstore',
                verbose=False
                ):
        self.logger = logging.getLogger(__name__)
        self._port = port
        self._server = server
        self._db_name = db_name
        
        msg = "Initialising connection to document manager store"
        debug.print_verbose(msg,  verbose, self.logger, logging.INFO)
        msg = "Connecting to database:\n" + server + ": " + str(port) + \
                "\ndb: " + db_name
        debug.print_verbose(msg,  verbose, self.logger, logging.INFO)
        
        self._connection = None
        self._database = None
        
        self.reconnect(verbose)
    
    def reconnect(self, verbose=False):
        if self._connection and self._database:
            return
        
        try:
            self._connection = pymongo.Connection(server, port)
            self._database = self._connection[db_name]
        except:
            debug.print_verbose('Cannot connect to document manager mongo',
                            verbose, self.logger, logging.WARNING)
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()
    
    def close(self):
        if self._connection is not None:
            self._connection.close()
    
    def find_one(self, verbose=False):
        """
        For testing only - pulls a single document out
        """
        self.reconnect(verbose)
        try:
            cursor = self._database.standardDocument.find_one()
            return StandardDocument(dict(cursor))
        except:
            return None
    
    def get_guids(self, verbose=False):
        self.reconnect(verbose)
        try:
            cursor = self._database.standardDocument.find(None, {'_id': 1})
            return [c['_id'] for c in cursor]
        except:
            return None
    
    def get_doc_count(self, verbose=False):
        """
        Count of all documents
        """
        self.reconnect(verbose)
        try:
            return self._database.standardDocument.count()
        except:
            return None
