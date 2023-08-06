"""
Store of processed documents. Currently uses mongoDB
"""

import pymongo
#import bson
#from bson.code import Code
import logging
#from time import time
from bidict import bidict
import hashlib

import numpy as np
from scipy import sparse
import marshal
import cPickle as pickle
#import bsddb
#import itertools

from webhelpers.feedgenerator import rfc3339_date as rfc_date

from botnee.standard_document import StandardDocument
from botnee.process.meta_dict import MetaDict
from botnee.process.data_dict import DataDict
from botnee.process.matrix_dict import MatrixDict
from botnee.process.time_dict import TimeDict

from botnee import debug, errors

import botnee_config

class DocStore(object):
    """
    Stores doc data, currently using MongoDB
    
    The following fields are stored
             |
             - guid                     global identifier
             - tokens                   actual tokens
             - url                      document url
             - urls                     any urls found in the document
             - emails                   any emails found in the document
             - dois                     any dois found in the document
             - authors                  author list
             - publication              publication type
             - publication-date         publication date
             - content_type             e.g. text/plain
             - doi                      DOI if present
             - content_hash             content hash if present
    """
    
    def __init__(self, 
                docs=None, 
                server='localhost', 
                port=27017,
                replicaset="",
                db_name='botnee',
                clean_database=False,
                verbose=False
                ):
        self.logger = logging.getLogger(__name__)
        self._port = port
        self._server = server
        self._db_name = db_name
        self._replicaset = replicaset
        
        
        def connect(replicaset=""):
            msg = "Connecting to database:\n" + server + ": " + str(port) + \
                "\ndb: " + db_name + "\nreplica set: " + replicaset
            debug.print_verbose(msg,  verbose, self.logger, logging.INFO)
            
            try:
                if replicaset == "":
                    self._connection = pymongo.Connection(server, port)
                else:
                    self._connection = pymongo.ReplicaSetConnection(server, port, \
                        replicaset=replicaset)
            except pymongo.errors.AutoReconnect as e:
                raise errors.DocStoreError(e, self.logger)
                return False
            except pymongo.errors.OperationFailure:
                return False
            return True
        
        if replicaset != "":
            if not connect(replicaset):
                connect("")
        else:
            connect("")
        
        msg = "Initialising internal meta data store"
        debug.print_verbose(msg,  verbose, self.logger, logging.INFO)
        
        self._database = self._connection[db_name]
        
        if clean_database:
            msg = "Dropping tables docs and data"
            with debug.Timer(msg, None, verbose, self.logger):
                self._database.docs.drop()
                #self._database.data.drop()
                #self._database.meta.drop()
                for ngram in botnee_config.NGRAMS.keys():
                    self._database['dictionary_%d' % ngram].drop()
        
        # create index on the indices and publication-date
        
        self.ensure_indexes(verbose)
        
        if docs:
            self.update(docs)
        
    def __del__(self):
        #self.close()
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()
    
    def ensure_indexes(self, verbose=False):
        for (index, unique) in botnee_config.MONGO_INDEXES:
            msg = "(%s)" % index
            with debug.Timer(msg, None, verbose, self.logger):
                self._database.docs.ensure_index(index, unique=unique)
    
    def update(self, docs, verbose=False):
        """
        Push data to mongodb. We're only intersted in the following fields:
            - dictionary
            - tokens_map
            - docs
        """
        
        db = self._database
        
        if type(docs) is list:
            for doc in docs:
                self.update(doc)
        elif type(docs) is StandardDocument:
            doc = docs
            if 'index' not in doc.keys():
                raise errors.DocStoreError('Missing Index %d' % index)
            else:
                if doc.has_key('guid'):
                    msg = 'Upserting %s: %d' % (doc['guid'], doc['index'])
                    debug.print_verbose(msg, verbose, self.logger)
                    doc['_id'] = doc['guid']
                    del doc['guid']
                query = {'_id': doc['_id']}
                
                if doc['_id'] in ['bmj:seed', 'bmj:dummy'] and botnee_config.DEBUG:
                    #debug.debug_here()
                    pass
                
                gle = db.docs.update(query, doc, upsert=True, safe=True)
                if gle['err']:
                    debug.debug_here()
                    msg = 'Failed to update document: ' + str(gle['err'])
                    raise errors.DocStoreError(err)
        #elif docs is None:
        #    pass
        else:
            msg = 'Expected StandardDocument or list, got ' + str(type(docs))
            raise TypeError(msg)
        
        #self.ensure_indexes(verbose)
        
    
    def update_fields(self, guid, doc):
        """
        Updates the fields in a document (i.e. does not overwrite document)
        """
        db = self._database
        try:
            query = {'_id': guid}
            gle = db.docs.update(query, {'$set': doc}, upsert=False, safe=True)
        except pymongo.errors.DuplicateKeyError as e:
            raise errors.DocStoreError(str(e))
        if gle['err']:
            debug.debug_here()
            msg = 'Failed to update document: ' + str(gle['err'])
            raise errors.DocStoreError(err)
    
    def close(self):
        if self._connection is not None:
            self._connection.close()
    
    def find_one(self):
        """
        For testing only - pulls a single document out
        """
        return self._database.docs.find_one()
    
    def get_by_guid(self, guids, fields={'_id':1, 'title':1, 'url':1, 
                            'publication': 1, 'publication-date': 1}, verbose=False):
        """
        Retrieves document by guid. By default returns the fields:
            guid
            title
            url
            publication
            publication-date
        """
        with debug.Timer(None, None, verbose, self.logger):
            if type(guids) in [str, unicode]:
                guids = [guids]
            
            query = {'_id': {"$in": guids}}
            cursor = self._database.docs.find(query, fields)
            
            if cursor.count() != len(guids):
                #raise errors.DocStoreError("guid not found: " + guid)
                #print "guid not found: " + guid
                #debug.debug_here()
                #return StandardDocument() #fields
                #raise errors.DocStoreError("One or more guids not found")
                errors.DocStoreWarning("One or more guids not found", self.logger)
            #cursor[0]['guid'] = cursor[0]['_id']
            
            docs = [StandardDocument(c) for c in cursor]
            #if doc.check_for_failures() is not None:
            #    str_err = doc['failed']['reason'] + ": " + doc['failed']['extra']
            
            if fields is not None and len(fields) > 0:
                for doc in docs:
                    for key, value in fields.items():
                        if value==1 and key not in doc:
                            doc[key] = ""
            
            return docs
    
    def get_ngram_lists_by_guid(self, guids, ngram):
        """
        Yield n-grams for a guid as tuple of guid and n-grams
        """
        
        tstring = "tokens_%d" % ngram
        #tstring = "tokens_hash_%d" % ngram
        
        if ngram == 1:
            caster = unicode
        else:
            caster = tuple
        
        db = self._database
        fields = {tstring: 1, 'index': 1}
        for guid in guids:
            query = {'_id': guid}
            cursor = db.docs.find(query, fields)
            
            if cursor.count() == 1:
                try:
                    yield (cursor[0]['_id'], cursor[0]['index'], cursor[0][tstring])
                except KeyError as e:
                    errors.DocStoreWarning(e.__repr__(), self.logger)
                    yield (cursor[0]['_id'], cursor[0]['index'], caster())
            else:
                msg = "Missing guid %s (index %d)" % (guid, index)
                raise errors.DocStoreError(msg, self.logger)
    
    
    '''
    def get_tokens(self, verbose=False):
        """
        Return iterator to all tokens as list of lists
        """
        with debug.Timer(None, None, verbose, self.logger):
            db = self._database
            query = None
            fields = {'tokens': 1, 'index': 1}
            #sort = [('index', pymongo.ASCENDING)]
            cursor = db.docs.find(query, fields, timeout=False)#, sort=sort)
            
            return ((c['index'], c['tokens']) for c in cursor)
    '''
    
    #def get_guids(self):
    #    cursor = self._database.docs.find(None, {'guid': 1, '_id': 0})
    #    return [c['guid'] for c in cursor]
    
    '''
    def get_ngram_tokens(self, n, verbose=False):
        """
        Return iterator to tuples of tokens as list of tuples
        """
        def get_ngrams(token_list):
            #print len(token_list)
            #token_list = [token for token in token_list\
            #         if hash(token) in self._engine._meta_dict['dictionary']]
            #print len(token_list)
            ng_lists = []
            for i in xrange(0,n):
                ng_lists.append(token_list[i:-n+i])
            #debug.debug_here()
            #return zip(*ng_lists)
            return itertools.product(*ng_lists)
        
        with debug.Timer(None, None, verbose, self.logger):
            db = self._database
            query = None
            fields = {'tokens': 1, 'index': 1}
            cursor = db.docs.find(query, fields)
            
            #debug.debug_here()
            return ((c['index'], get_ngrams(c['tokens'])) for c in cursor)
    '''
    
    def get_tokens_count(self, indices, suffix="", verbose=False):
        """
        Return the length of the tokens array for each document
        """
        if suffix == "":
            msg = ""
        else:
            msg = "(%s)" % suffix
        
        with debug.Timer(msg, None, verbose, self.logger):
            db = self._database
            query = {'index': {'$in': indices}}
            fields = {'tokens' + suffix + '_len': 1}
            sort = [('index', pymongo.ASCENDING)]
            cursor = db.docs.find(query, fields)
            
            if cursor.count() != len(indices):
                debug.debug_here()
                raise errors.DocStoreError('Missing indices')
            
            return [c['tokens' + suffix + '_len'] for c in cursor]
    
    def get_dates(self, guids=None, verbose=False):
        """
        Gets the dates for the guids specified (and indices)
        """
        with debug.Timer(None, None, verbose, self.logger):
            db = self._database
            if guids:
                query = {'_id': {'$in': guids}}
            else:
                query = {}
            fields = {'_id': 0, 'index': 1, 'publication-date': 1}
            #fields = {'_id': 1, 'publication-date': 1}
            #sort = [('publication-date', pymongo.DESCENDING)]
            sort = [('index', pymongo.ASCENDING)]
            #sort = None
            cursor = db.docs.find(query, fields, sort=sort)
            return [(c['index'], c['publication-date']) for c in cursor]
            #return dict((c['_id'], c['publication-date']) for c in cursor)
    
    '''
    def count_all_tokens(self):
        """
        Counts the total number of tokens in all documents (map/reduce)
        """
        mapf = Code("function () { this.tokens_hash.forEach(function(z) { \
                        emit(z, 1); }); }")
        reducef = Code("function (key, values) { var total = 0; \
                        for (var i = 0; i < values.length; i++) { \
                            total += values[i]; } return total; }" )
        result = self._database.docs.map_reduce(mapf, reducef, "tmp")
        return sum([r['value'] for r in result.find()])
    '''
    
    def get_guid_indices(self, indices=None, verbose=False):
        """
        Gets the indices of the guids. Requires the index field to be indexed
        """
        with debug.Timer(None, None, verbose, self.logger):
            self.ensure_indexes(verbose)
            
            query = None
            if indices:
                query = {'index': {'$in': indices}}
            fields = {'_id': 1, 'index': 1, 'operation': 1}
            #sort = [('index', pymongo.ASCENDING)]
            sort = None
            cursor = self._database.docs.find(query, fields, sort=sort)
            #guid_indices = bidict()
            #for c in cursor:
            #    try:
            #        guid_indices.update({c['guid']: c['index']})
            #        #print c['guid'], c['index']
            #    except KeyError as e:
            #        print "Failed to load: " + c['guid'] + "(no index)"
            #        print c
            #        pass
            return bidict([(c['_id'], c['index']) for c in cursor \
                            if c['operation'] != 'delete'])
            #return guid_indices
    
    def get_doc_count(self):
        """
        Count of all documents
        """
        return self._database.docs.count()
    
    def get_guids_by_indices(self, indices):
        """
        Gets the guid for the index
        """
        query = {'index': {'$in': indices}}
        fields = {'_id': 1, 'index': 1}
        cursor = self._database.docs.find(query, fields)
        if cursor.count() != len(indices):
            return None
        return [c['_id'] for c in cursor]
    
    def get_indices_by_guids(self, guids, sort_by_date=False):
        """
        Gets the index of the guid.
        """
        query = {'_id': {'$in': guids} }
        fields = {'_id': 1, 'index': 1}
        if sort_by_date:
            sort = [('publication-date', pymongo.DESCENDING)]
        else:
            sort = None
        
        cursor = self._database.docs.find(query, fields, sort=sort)
        if cursor.count() != len(guids):
            return None
        return [c['index'] for c in cursor]
    
    def get_all_docs(self, verbose=False):
        """
        Simply retrieve all docs (all fields). Could be very slow!
        """
        with debug.Timer(None, None, verbose, self.logger):
            cursor = self._database.docs.find(None)
            return dict(c for c in cursor)
    
    def get_num_docs(self, verbose=False):
        """
        Gets number of documents in database
        """
        with debug.Timer(None, None, verbose, self.logger):
            return self._database.docs.find(None).count()
    
    '''
    def get_tokens_hash(self, suffix="", ngstr=""):
        """
        Returns a generator over the database to 
        get tuples of guids and tokens_hash lists. 
        Sorts by index, and generates a (guid, index, tokens_hash) tuple.
        """
        
        name = 'tokens_hash' + suffix + ngstr
        query = None
        sort = [('index', pymongo.ASCENDING)]
        fields = {'_id': 1, 'index': 1, name: 1}
        cursor = self._database.docs.find(query, fields, sort=sort)
        
        return ((c['_id'], c['index'], c[name]) for c in cursor)
        #for item in cursor:
        #    yield dict((c['guid'], c['tokens_hash']) for c in cursor)
    '''
    
    def get_tokens_by_guid(self, guids=None, suffix="", ngstr="", verbose=False):
        """
        Returns the token list for the guids specified.
        """
        name = 'tokens' + suffix + ngstr
        #name = 'tokens_hash' + suffix + ngstr
        
        #with debug.Timer("(%s)" % name, None, verbose, self.logger):
        db = self._database
        if type(guids) in [str, unicode]:
            guids = [guids]
        query = {'_id': {'$in': guids}}
        fields = {'_id': 1, name: 1}
        cursor = db.docs.find(query, fields)
        
        if cursor.count() != len(guids):
            for guid in guids:
                if not self.get_indices_by_guids([guids]):
                    debug.debug_here()
                    raise errors.DocStoreError('guid not found: ' + guid)
        
        tokens = {}
        for c in cursor:
            tokens[c['_id']] = c[name]
            if not c[name] and verbose==2:
                msg = 'No tokens (%s) for %s' % (name, c['_id'])
                debug.print_verbose(msg, verbose, self.logger)
        return tokens
    
    '''
    def put_meta(self, meta_dict, verbose=False):
        """
        Puts the meta_dict data into MongoDB (dictionary, hash_map)
        guids can be recovered from the "index" field of docs
        """
        db = self._database
        
        debug.print_verbose('Putting dictionary into mongo', verbose, self.logger)
        #for k,v in meta_dict['dictionary'].items():
        #    db.meta.dictionary.update({}, {str(k): v}, upsert=True)
        db.meta.dictionary.update({}, {'dictionary': meta_dict['dictionary'].values()}, upsert=True)
        debug.print_verbose('Putting hash_map into mongo', verbose, self.logger)
        db.meta.update({}, {'hash_map': [(k,v) for k,v in meta_dict['hash_map'].items()]}, upsert=True)
        debug.print_verbose('Putting bad_ids into mongo', verbose, self.logger)
        db.meta.update({}, {'bad_ids': [(k,v) for k,v in meta_dict['bad_ids'].items()]}, upsert=True)
        debug.print_verbose('Putting doc_freq into mongo', verbose, self.logger)
        db.meta.update({}, {'doc_freq': meta_dict['doc_freq'].items()}, upsert=True)
        fs.put(meta_dict['doc_freq'].items(), filename='doc_freq')
        debug.print_verbose('Putting term_freq into mongo', verbose, self.logger)
        db.meta.update({}, {'term_freq': meta_dict['term_freq'].items()}, upsert=True)
        
    def get_meta(self, meta_dict, verbose=False):
        """
        Gets the meta_dict data from MongoDB (dictionary, guids, hash_map)
        """
        db = self._database
        query = None
        fields = {'dictionary': 1, 'hash_map': 1}
        cursor = db.meta.dictionary.find(query, fields)
        if cursor.count() != 2:
            raise errors.DocStoreError('Dictionary/hash map not found')
        debug.print_verbose('Getting dictionary from mongo', verbose, self.logger)
        meta_dict['dictionary'] = dict([(hash(t), t) for t in cursor[0]['dictionary']])
        debug.print_verbose('Done', verbose, self.logger)
        debug.print_verbose('Getting hash_map from mongo', verbose, self.logger)
        meta_dict['hash_map'] = bidict(cursor[1]['hash_map'])
        debug.print_verbose('Done', verbose, self.logger)
        debug.print_verbose('Getting bad_ids from mongo', verbose, self.logger)
        meta_dict['bad_ids'] = OrderedDict(cursor[1]['bad_ids'])
        debug.print_verbose('Done', verbose, self.logger)
        meta_dict['n_docs'] = self.get_num_docs()
        # Now for the guids
        #meta_dict['guids'] = self.get_guid_indices()
        debug.print_verbose('Getting doc_freq from mongo', verbose, self.logger)
        meta_dict['doc_freq'] = db.meta.find(None, {'doc_freq': 1, '_id': 0})[0]
        debug.print_verbose('Done', verbose, self.logger)
        debug.print_verbose('Getting term_freq from mongo', verbose, self.logger)
        meta_dict['term_freq'] = db.meta.find(None, {'term_freq': 1, '_id': 0})[0]
        debug.print_verbose('Done', verbose, self.logger)
    '''
    
    '''
    def update_dictionary(self, list_of_dicts, ngram, verbose=False):
        """
        Updates the mongo dictionary of the given name with key and value.
        Keys are used as _id field
        """
        db = self._database
        
        name = 'dictionary'
        if ngram > 1:
            name += '_%d' % ngram
        
        ids = []
        #if list_of_dicts:
        #    ids = db.meta[name].insert(list_of_dicts, safe=False)
        for item in list_of_dicts:
            ids.append(db.meta[name].insert(item, safe=False))
        
        if len(ids) != len(list_of_dicts):
            missing = [item['_id'] for item in list_of_dicts if item['_id'] not in ids]
            print missing
            debug.debug_here()
        
        if botnee_config.DEBUG:
            for item in list_of_dicts:
                token = self.get_token(item['_id'], ngram)
                if token != item['token']:
                    msg = "Hash collision for %s and %s" % (str(token), str(item['token']))
                    #debug.print_verbose(msg, verbose, self.logger)
                    errors.DocStoreWarning(msg, self.logger)
                    #debug.debug_here()
        
        #for item in list_of_dicts:
        #    try:
        #       query = {'_id': item['_id']}
        #       gle = db.meta[name].update(query, {'$set': item}, upsert=False, safe=True)
        #   except pymongo.errors.DuplicateKeyError as e:
        #        raise errors.DocStoreError(str(e))
        #    if gle['err']:
        #        debug.debug_here()
        #        msg = 'Failed to update dictionary: ' + str(gle['err'])
        #        raise errors.DocStoreError(err)
    
    def get_token(self, key, ngram):
        """
        Gets a token from the dictionary
        """
        def tupleise(t):
            return tuple(map(tupleise, t)) if isinstance(t, (list, tuple)) else t
        
        db = self._database
        
        name = 'dictionary'
        if ngram > 1:
            name += '_%d' % ngram
        
        cursor = db.meta[name].find({'_id': key}, {'token': 1})
        if cursor.count() != 1:
            return ()
        else:
            token = tupleise(cursor[0]['token'])
            return token
    '''
    
    def get_dictionary_count(self, ngram):
        """
        Count lenght of the dictionary
        """
        name = 'dictionary'
        if ngram > 1:
            name += '_%d' % ngram
        return self._database.meta[name].count()
    
    
    def put_data(self, meta_dict, data_dict, matx_dict, time_dict, verbose=False):
        """
        Puts all of the data (TF, TFIDF etc) into MongoDB
        """
        db = self._database
        inserts = set() 
        updates = set()
        deletes = set()
        
        matrix_types = botnee_config.MATRIX_TYPES
        
        #ngstrs = [""] + ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]
        ngstrs = ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]
        
        with debug.Timer('(mongo)', time_dict, verbose, self.logger):
            debug.print_verbose("Flushing to mongo", verbose, self.logger)
            msg = "Inserts: %d, Updates: %d, Deletes: %d" % \
                    (len(meta_dict['inserts']), 
                     len(meta_dict['updates']), 
                     len(meta_dict['deletes']))
            debug.print_verbose(msg, verbose, self.logger)
            
            # First process inserts
            for name in matrix_types.keys():
                for suffix in botnee_config.SUFFIXES:
                    for ngstr in ngstrs:
                        full_name = name + suffix + ngstr
                        debug.print_verbose("", False, None)
                        msg = "Flushing " + full_name
                        debug.print_verbose(msg, verbose, self.logger)
                        matrix = matx_dict[full_name]
                        if matrix is None:
                            debug.print_verbose(full_name + ' empty', verbose, 
                                                self.logger, logging.WARNING)
                            #debug.debug_here()
                            continue
                        
                        matrix.sort_indices()
                        
                        for i, guid in enumerate(meta_dict['inserts'] + meta_dict['updates']):
                            debug.print_dot(i, verbose)
                            
                            index = meta_dict['guids'][guid]
                            
                            doc = {}
                            
                            if index < 0 or index >= matrix.shape[0]:
                                print matrix.shape
                                raise IndexError('index (%d) out of range' % index)
                            
                            row = matrix[index,:]
                            
                            row_indices = row.indices.tolist()
                            row_data    = row.data.tolist()
                            
                            ihash = hash(tuple(row_indices))
                            dhash = hash(tuple(row_data))
                            
                            doc[full_name] = { 
                                           'indices': row_indices,
                                           'data'   : row_data,
                                           'nnz'    : len(row.data),
                                           'ihash'  : ihash,
                                           'dhash'  : dhash
                                             }
                            
                            if botnee_config.DEBUG and guid == 'bmj:seed' \
                                            and suffix == "" and ngstr == "_1":
                                try:
                                    print "put_data", ihash, dhash
                                    assert ihash == meta_dict['seed_freq_ihash']
                                    assert dhash == meta_dict['seed_freq_dhash']
                                except:
                                    #debug.debug_here()
                                    pass
                            
                            if not botnee_config.STORE_DATA_IN_MONGO:
                                self.marshal_save(guid, name, doc[full_name])
                            
                            if botnee_config.STORE_DATA_IN_MONGO:
                                self.update_fields(guid, doc)
                            
                            if guid in meta_dict['inserts']:
                                inserts.add(guid)
                            else:
                                updates.add(guid)
            
            meta_dict['inserts'] = []
            meta_dict['updates'] = []
            
            for guid in meta_dict['deletes']:
                result = self.get_by_guid(guid, None)
                if len(result) != 1:
                    continue
                doc = result[0]
                if doc:
                    doc['operation'] = 'delete'
                    index = meta_dict['guids'][guid]
                    
                    for name in matrix_types.keys():
                        for suffix in botnee_config.SUFFIXES:
                            for ngstr in ngstrs:
                                full_name = name + suffix + ngstr
                                doc[full_name] = {
                                        'indices': [], 
                                        'data': [], 
                                        'nnz': 0,
                                        'ihash': hash(()),
                                        'dhash': hash(())
                                                }
                                if not botnee_config.STORE_DATA_IN_MONGO:
                                    self.marshal_save(guid, name, doc[full_name])
                    
                    if botnee_config.STORE_DATA_IN_MONGO:
                        query = {'_id': guid}
                        fields = {'$set': doc}
                        db.docs.update(query, fields, upsert=False, safe=True)
                    
                    deletes.append(guid)
            
            meta_dict['deletes'] = []
        
        # also marshal file
        #with debug.Timer('(marshal)', None, verbose, self.logger):
        #    for name in matrix_types.keys():
        #        fname = botnee_config.DATA_DIRECTORY + 'marshal/' + name + '.dat'
        #        with open(fname, 'wb') as outfile:
        #            marshal.dump(doc[name], outfile, marshal.HIGHEST_PROTOCOL)
        
        return (list(inserts), list(updates), list(deletes))
    
    def get_data(self, meta_dict, data_dict, matx_dict, time_dict, verbose=False):
        """
        Get TF/TFIDF from mongo
        """
        if type(meta_dict) is not MetaDict:
            raise TypeError('expected MetaDict got ' + str(type(meta_dict)))
        if type(data_dict) is not DataDict:
            raise TypeError('expected DataDict got ' + str(type(data_dict)))
        if type(matx_dict) is not MatrixDict:
            raise TypeError('expected MatrixDict got ' + str(type(matx_dict)))
        if type(time_dict) is not TimeDict:
            raise TypeError('expected TimeDict got ' + str(type(time_dict)))
        
        if botnee_config.STORE_DATA_IN_MONGO:
            msg = '(mongo)'
        else:
            msg = '(marshal)'
        
        #ngstrs = [""] + ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]
        ngstrs = ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]
        
        def count_nnz():
            """
            Helper function to calculate number of nonzeros.
            CAN THIS BE DONE VIA MAP-REDUCE??
            """
            with debug.Timer(None, time_dict, verbose, self.logger):
                query = {'operation': ""}
                fields = {'_id': 1}
                for name in botnee_config.MATRIX_TYPES:
                    for suffix in botnee_config.SUFFIXES:
                        for ngstr in ngstrs:
                            full_name = name + suffix + ngstr
                            fields[full_name + '.nnz'] = 1
                            all_data[full_name]['nnz'] = 0
                
                cursor = db.docs.find(query, fields)
                
                for cur in cursor:
                    for name in botnee_config.MATRIX_TYPES:
                        for suffix in botnee_config.SUFFIXES:
                            for ngstr in ngstrs:
                                full_name = name + suffix + ngstr
                                try:
                                    all_data[full_name]['nnz'] += cur[full_name]['nnz']
                                except Exception as e:
                                    msg = cur['_id'] + ': ' + e.__repr__()
                                    errors.DocStoreWarning(msg, self.logger)
                                    pass
        
        def setup_data_structures():
            """
            Helper function to setup data structures
            """
            # Set up the data structures
            with debug.Timer(None, time_dict, verbose, self.logger):
                for name, dtype in botnee_config.MATRIX_TYPES.items():
                    for suffix in botnee_config.SUFFIXES:
                        for ngstr in ngstrs:
                            full_name = name + suffix + ngstr
                            #tf_data = []
                            # nnz = 0
                            all_data[full_name]['data'] = \
                                        np.zeros(all_data[full_name]['nnz'], dtype)
                            
                            all_data[full_name]['indices'] = [
                                        np.zeros(all_data[full_name]['nnz'], np.uint64),
                                        np.zeros(all_data[full_name]['nnz'], np.uint64)
                                      ]
                            all_data[full_name]['ptr'] = 0
        
        def iterate_over_cursor():
            """
            Helper function to iterate over cursor and pull data down
            """
            # now iterate over the cursor
            with debug.Timer(None, time_dict, verbose, self.logger):
                for i, cur in enumerate(cursor):
                    debug.print_dot(i, verbose)
                    if not cur:
                        continue
                    for name, dtype in matrix_types.items():
                        for suffix in botnee_config.SUFFIXES:
                            for ngstr in ngstrs:
                                full_name = name + suffix + ngstr
                                try:
                                    cnnz = cur[full_name]['nnz']
                                except KeyError as e:
                                    msg = cur['_id'] + ': ' + e.__repr__()
                                    errors.DocStoreWarning(msg, self.logger)
                                    continue
                                rng = range(all_data[full_name]['ptr'], 
                                            all_data[full_name]['ptr']+cnnz)
                                #idxs = np.ones(cnnz, dtype=np.uint64) * cur['index']
                                
                                #idx = i
                                #idx = cur['index']
                                idx = meta_dict['guids'][cur['_id']]
                                
                                if idx != cur['index']:
                                    debug.debug_here()
                                    raise errors.DocStoreError('Indices in memory not aligned with database')
                                
                                row_data = cur[full_name]['data']
                                row_indices = cur[full_name]['indices']
                                
                                dhash = cur[full_name]['dhash']
                                ihash = cur[full_name]['ihash']
                                
                                try:
                                    assert(dhash == hash(tuple(row_data)))
                                    assert(ihash == hash(tuple(row_indices)))
                                except:
                                    debug.debug_here()
                                
                                all_data[full_name]['data'][rng] = row_data
                                all_data[full_name]['indices'][0][rng] = idx#idxs
                                all_data[full_name]['indices'][1][rng] = row_indices
                                
                                all_data[full_name]['ptr'] += cnnz
                                
                                if botnee_config.DEBUG and cur['_id'] == 'bmj:seed' and suffix == "":
                                    try:
                                        print "get_data", ihash, dhash
                                        assert ihash == meta_dict['seed_freq_ihash']
                                        assert dhash == meta_dict['seed_freq_dhash']
                                    except:
                                        debug.debug_here()
        
        def create_matrices():
            """
            Helper function to create matrices
            """
            # finally create the matrices
            with debug.Timer(None, time_dict, verbose, self.logger):
                for name, dtype in matrix_types.items():
                    for suffix in botnee_config.SUFFIXES:
                        for ngstr in ngstrs:
                            full_name = name + suffix + ngstr
                            indices = all_data[full_name]['indices']
                            if len(indices[0])==0 and len(indices[1])==0:
                                shape = (
                                    meta_dict['last_index']+1,
                                    len(meta_dict['tokens_map' + ngstr])
                                        )
                            else:
                                shape = (
                                    max(max(indices[0]), meta_dict['last_index']+1),
                                    max(max(indices[1]), len(meta_dict['tokens_map' + ngstr]))
                                    )
                            
                            try:
                                matx_dict[full_name] = sparse.coo_matrix(
                                    (all_data[full_name]['data'], 
                                     all_data[full_name]['indices']), 
                                    shape=shape, dtype=dtype).tocsr()
                            except ValueError as e:
                                errors.DocStoreWarning(e.__repr__(), self.logger)
                                matx_dict[full_name] = sparse.csr_matrix(shape, dtype=dtype)
                            #matx_dict[full_name] = matx_dict[full_name].tocsr()
        
        with debug.Timer(msg, time_dict, verbose, self.logger):
            db = self._database
            matrix_types = botnee_config.MATRIX_TYPES
            
            if not meta_dict['n_docs']:
                meta_dict['n_docs'] = self.get_num_docs()
            
            if not meta_dict['guids']:
                meta_dict['guids'] = self.get_guid_indices()
            
            all_data = {}
            query = {'operation' : ''}
            fields = {'_id': 1, 'index': 1}
            for name in matrix_types.keys():
                for suffix in botnee_config.SUFFIXES:
                    for ngstr in ngstrs:
                        full_name = name + suffix + ngstr
                        all_data[full_name] = {}
                        fields[full_name] = 1
            
            sort = [('index', pymongo.ASCENDING)]
            cursor = db.docs.find(query, fields, sort=sort)
            
            # Call all of the helper functions
            count_nnz()
            setup_data_structures()
            iterate_over_cursor()
            try:
                create_matrices()
            except ValueError as e:
                errors.DocStoreWarning(e.__repr__(), self.logger)
                
                pass
    
    def marshal_save(self, guid, name, data):
        """
        Saves the data to files (marshal)
        """
        fname = botnee_config.DATA_DIRECTORY + 'marshal/' + \
                hashlib.md5(guid).hexdigest() + '_' + name + '.dat'
        with open(fname, 'wb') as outfile:
            marshal.dump(data, outfile, marshal.version)
    
    def marshal_load(self, guid, name):
        """
        Loads the data from files (marshal)
        """
        data = None
        fname = botnee_config.DATA_DIRECTORY + 'marshal/' + \
                hashlib.md5(guid).hexdigest() + '_' + name + '.dat'
        with open(fname, 'rb') as infile:
            data = marshal.load(infile)
        return data
    
    def pickle_save(self, guid, name, data):
        """
        Saves the data to files (pickle)
        """
        fname = botnee_config.DATA_DIRECTORY + 'pickle/' + \
                hashlib.md5(guid).hexdigest() + '_' + name + '.dat'
        with open(fname, 'wb') as outfile:
            marshal.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
    
    def pickle_load(self, guid, name):
        """
        Loads the data from files (pickle)
        """
        data = None
        fname = botnee_config.DATA_DIRECTORY + 'marshal/' + \
                hashlib.md5(guid).hexdigest() + '_' + name + '.dat'
        with open(fname, 'rb') as infile:
            data = marshal.load(infile)
        return data
    
    def get_summary_as_list(self, verbose=False):
        """
        Gets a summary of statistics of docs. Could be slow!
        """
        
        summary = []
        
        db = self._database
        
        # Print the number of documents
        #msg = "%20s: %d" % ("# docs", db.docs.count())
        msg = {'name': "# docs", 'info': db.docs.count()}
        summary.append(msg)
        #summary.append("")
        
        # Print the date range
        sort = [('publication-date', pymongo.ASCENDING)]
        cursor = db.docs.find({}, {'publication-date': 1}, sort=sort, limit=1)
        try:
            min_date = rfc_date(cursor[0]['publication-date'])
        except ValueError as e:
            debug.print_verbose(e, verbose, self.logger)
            min_date = str(cursor[0]['publication-date'])
        except AttributeError as e:
            debug.print_verbose(e, verbose, self.logger)
            min_date = str(cursor[0]['publication-date'])
        #msg = "%20s: %s (%s)" % ("Min date", min_date, cursor[0]['_id'])
        msg = {'name': "Min date", 'info': "%s (%s)"  % (min_date, cursor[0]['_id'])}
        summary.append(msg)
        #summary.append("")
        
        sort = [('publication-date', pymongo.DESCENDING)]
        cursor = db.docs.find({}, {'publication-date': 1}, sort=sort, limit=1)
        try:
            max_date = rfc_date(cursor[0]['publication-date'])
        except ValueError as e:
            debug.print_verbose(e, verbose, self.logger)
            max_date = str(cursor[0]['publication-date'])
        except AttributeError as e:
            debug.print_verbose(e, verbose, self.logger)
            max_date = str(cursor[0]['publication-date'])
        #msg = "%20s: %s (%s)" % ("Max date", max_date, cursor[0]['_id'])
        msg = {'name': "Max date", 'info': "%s (%s)" % (max_date, cursor[0]['_id'])}
        summary.append(msg)
        #summary.append("")
        
        # Print the unique publication types and article types
        for dq in ['publication', 'article_type', 'journal_section']:
            result = sorted(db.docs.distinct(dq))
            #msg = "%20s: %d" % ("#Unique " + dq, len(result))
            msg = { 'name': "#Unique " + dq,
                    'info': str(len(result))}
            summary.append(msg)
            for i, item in enumerate(result):
            #    msg = "\t%s" % (item)
                msg = {'name': "%d: %s" % (i, dq), 'info': str(item)}
                summary.append(msg)
            #summary.append("")
        
        # and article types
        
        return summary


# helper function to add nnz to all matrices
#gen = (guid for guid in guids.keys())
#for guid in gen:
#    cursor = db.docs.find({'_id': guid})
#    for suffix in botnee_config.SUFFIXES:
#        nnz = len(cursor[0]['tf'+suffix]['data'])
#        db.docs.update({'_id': guid}, {'$set': {'tf'+suffix + '.nnz': nnz}})

# helper function to change dates to datetime objects
"""
import botnee
import datetime
import dateutil
engine = botnee.engine.Engine(get_data=False)
db = engine._doc_store._database
cursor = db.docs.find({}, {'_id': 1, 'publication-date': 1})
for c in cursor:
    date = dateutil.parser.parse(c['publication-date'])
    db.docs.update({'_id': c['_id']}, {'$set': {'publication-date': date}})
"""

# helper function to put token lengths in
"""
import botnee
engine = botnee.engine.Engine(get_data=False)
db = engine._doc_store._database
for suffix in botnee_config.SUFFIXES:
    cursor = db.docs.find({}, {'_id': 1, 'tokens' + suffix: 1})
    for c in cursor:
        length = len(c['tokens' + suffix])
        db.docs.update({'_id': c['_id']}, {'$set': {'tokens' + suffix + '_len': length}})
"""
