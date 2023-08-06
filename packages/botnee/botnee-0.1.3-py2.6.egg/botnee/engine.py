"""
Initial starting point for the botnee application 
- opens necessary DB connections and files
"""

#import pickle
import os
import threading
from time import asctime, localtime #, time
import datetime
import pp
import logging
import itertools
from ordereddict import OrderedDict
import psutil

import numpy as np
from scipy import sparse
#import tables

from botnee import debug, standard_document_io, START_TIME, errors

from botnee.standard_document import StandardDocument
from botnee.doc_store import DocStore
#from botnee.doc_manager_store import DocManagerStore

from botnee.process.meta_dict import MetaDict
from botnee.process.data_dict import DataDict
from botnee.process.matrix_dict import MatrixDict
from botnee.process.time_dict import TimeDict

from botnee.process.text import process_docs
from botnee.process.vector_space_model import vector_space_model
from botnee.process.vector_space_model import calculate_idf
from botnee.process.vector_space_model import VectorSpaceModel

from botnee.timeout_lock import TimeoutLock

import botnee_config

class Engine(object):
    """
    The Engine class can either be initialised with a directory of standard
    docs, in which case the collector_directory variable should be set, or 
    from existing databases. Settings should be placed in botnee_config.py. 
    Set parallel=True for parallel processing. Set recursive=True to recursively
    scan the collector directory (if specified). 
    
    The force_reindex flag is a fail-safe if the mongodb and pytables 
    databases become disaligned. Setting this to True will instruct botnee to 
    reload the documents from mongodb and process them again (dictionary, TF, 
    TFIDF etc).
    """
    
    def __init__(self, collector_directory=None, verbose=True, parallel=False, 
                    recursive=True, force_reindex=False, get_data=True):
        self.logger = logging.getLogger(__name__)
        verbose = botnee_config.VERBOSE
        
        with debug.Timer(None, None, verbose, self.logger):
            # Thread locking
            self._lock = threading.Lock()
            #self._lock = timeout_lock.TimeoutLock()
            
            if parallel:
                self._ppservers = ()
                self._job_server = pp.Server(ppservers = self._ppservers)
                ncpus = self._job_server.get_ncpus()
                debug.print_verbose("Using pp with %d workers" % (ncpus), verbose, self.logger)
            else:
                self._job_server = None
            
            # Connect to Document Manager Store
            #self._doc_manager_store = DocManagerStore(
            #        server='localhost', 
            #        port=27017,
            #        db_name='documentstore',
            #        verbose=False
            #        )
            
            self._matx_dict = MatrixDict(verbose=botnee_config.VERBOSE)
            self._time_dict = TimeDict(START_TIME)
            
            if not collector_directory:
                """
                We are opening extant files
                """
                # Open pytables
                #self._corpus_name = botnee_config.CORPUS_NAME
                
                # Create Corpus object
                #try:
                #    self._corpus = Corpus(self._corpus_name, self)
                #    
                #    finfo = os.stat(self._corpus._filename)
                #    
                #    debug.print_verbose("hdf5 file size: %.2fMb" % 
                #            (float(finfo.st_size)/1024/1024), verbose, self.logger)
                #except tables.exceptions.HDF5ExtError:
                #    debug.print_verbose("Problem loading hdf5 file -\
                #             reindex will be triggered", verbose, self.logger)
                #    # delete file
                #    os.remove(botnee_config.DATA_DIRECTORY 
                #                + self._corpus_name + "_corpus_table.h5")
                #    
                #    self._corpus = Corpus(self._corpus_name, self)
                #    
                #    force_reindex = True
                
                # open MongoDB
                try:
                    self._doc_store = DocStore(
                        docs = None, 
                        server = botnee_config.MONGO_SERVER, 
                        port = botnee_config.MONGO_PORT,
                        replicaset = botnee_config.MONGO_REPLICA_SET, 
                        db_name = botnee_config.MONGO_DB_NAME, 
                        clean_database = False,
                        verbose = botnee_config.VERBOSE
                            )
                except errors.DocStoreError as e:
                    debug.print_verbose('Doc Store Error - is mongodb running?', verbose, self.logger)
                    raise e
                
                # Load data structures from disk
                self._meta_dict = MetaDict({}, verbose, True)
                self._data_dict = DataDict({}, verbose, True)
                #self._dictionaries = Dictionaries(self._doc_store, verbose)
                
                if force_reindex:
                    # Get indices from mongo
                    self.force_reindex(True, verbose)
                else:
                    if get_data:
                        try:
                            #self._corpus.get_meta_dict(self._meta_dict, self._time_dict, verbose)
                            #self._corpus.get_data_dict(self._data_dict, self._time_dict, verbose)
                            #self._doc_store.get_meta(self._meta_dict, verbose)
                            self._doc_store.get_data(
                                self._meta_dict, 
                                self._data_dict, 
                                self._matx_dict, 
                                self._time_dict, 
                                verbose)
                        except ValueError as e:
                            errors.EngineWarning(e.__repr__(), self.logger)
                            self.force_reindex(True, verbose)
                        #except tables.exceptions.NoSuchNodeError as e:
                        #    debug.print_verbose(str(e), verbose, self.logger, logging.WARNING)
                        #    self.force_reindex(verbose)
                
                # Now print out some statistics about the data (sizes etc)
                self.print_summary(verbose)
                
                self.check_integrity(verbose)
                
            else:
                """
                Create databases from docs in collector_directory
                """
                
                # Remove files and instatiate data structures
                self.remove_files(verbose)
                self._meta_dict = MetaDict(verbose=verbose)
                self._data_dict = DataDict(verbose=verbose)
                
                if type(collector_directory) in [str, unicode]:
                    collector_directory = [collector_directory]
                
                read_dir = standard_document_io.read_directory
                
                debug.print_verbose('Creating generator over docs', verbose, self.logger)
                
                if len(collector_directory) == 1:
                    docs = read_dir(collector_directory[0], "txt", verbose, recursive)
                else:
                    gens = (read_dir(coll_dir, "txt", verbose, recursive) \
                                        for coll_dir in collector_directory)
                    docs = itertools.chain(*gens)
                
                debug.print_verbose('Done', verbose, self.logger)
                
                # For debugging - to be removed
                if botnee_config.DEBUG:
                    #self._test_doc = docs.next()
                    # for debugging
                    self._meta_dict['STOP_AT'] = botnee_config.STOP_AT
                
                debug.print_verbose('Creating Doc Store', verbose, self.logger)
                
                # Put documents into mongoDB
                self._doc_store = DocStore(
                        docs = None, 
                        server = botnee_config.MONGO_SERVER, 
                        port = botnee_config.MONGO_PORT,
                        replicaset = botnee_config.MONGO_REPLICA_SET, 
                        db_name = botnee_config.MONGO_DB_NAME, 
                        clean_database = True,
                        verbose = botnee_config.VERBOSE
                            )
                    
                #self._dictionaries = Dictionaries(self._doc_store, verbose)
                
                self.insert_and_flush(docs, True, verbose)
                
                if botnee_config.DEBUG:
                    del self._meta_dict['STOP_AT']
                
                debug.print_verbose("Loaded %d documents" % self._meta_dict['n_docs'], 
                                verbose, self.logger)
                
                # Now print out some statistics about the data (sizes etc)
                self.print_summary(verbose)
                
                self.check_integrity(verbose)
                
            # dump time info to disk
            self._time_dict.write_csv(verbose, self.logger)
    
    def __del__(self):
        """ Destructor, calls Corpus.close() """
        #self.close()
        
    def __enter__(self):
        return self
    def __exit__(self,ext_type,exc_value,traceback):
        """ Called if the last reference is deleted """
        self.close()
        if self._doc_store is not None:
            del self._doc_store
        #if self._corpus is not None:
        #    del self._corpus
        
    def close(self):
        """
        Closes database connections and flushes files
        """
        # Flush data first
        self.flush(False, True)
        # Close tables connection
        #if self._corpus:
        #    self._corpus.close()
        # Close mongo connection
        if self._doc_store:
            self._doc_store.close()
        #if self._doc_manager_store:
        #    self._doc_manager_store.close()
    
    def remove_files(self, verbose=True):
        """
        Removes existing datafiles
        """
        
        def remove_file(filename):
            try:
                debug.print_verbose('Deleting ' + filename, verbose, self.logger)
                os.remove(filename)
            except OSError as e:
                errors.EngineWarning(e.__repr__(), self.logger)
                pass
        
        with debug.Timer(None, None, verbose, self.logger):
            #if botnee_config.META_DICT_STORE_TYPE == 'pytables' and \
            #   botnee_config.DATA_DICT_STORE_TYPE == 'pytables':
            #    # Remove existing tables file
            #    filename = botnee_config.DATA_DIRECTORY + \
            #                    self._corpus_name + "_corpus_table.h5"
            #    remove_file(filename)
            
            if botnee_config.META_DICT_STORE_TYPE == 'marshal':
                filename = botnee_config.META_DICT_FILE + '.dat'
                remove_file(filename)
            
            if botnee_config.DATA_DICT_STORE_TYPE == 'marshal':
                filename = botnee_config.DATA_DICT_FILE + '.dat'
                remove_file(filename)
            
            #for ngram in botnee_config.NGRAMS.keys():
            #    filename = "%s_%d.dat" % (botnee_config.DICTIONARY_FILE, ngram)
            #    remove_file(filename)
        
    def insert_and_flush(self, docs, reindex=False, verbose=True):
        """
        Insert document(s) (pre-parsed StandardDocument format)
        Also flushes to disk/pymongo
        """
        if type(docs) is StandardDocument:
            self.insert_and_flush([docs], reindex, verbose)
        #elif type(docs) in list:
        #    for doc in docs:
        #        if doc and type(doc) is not StandardDocument:
        #            raise TypeError('Expected StandardDocument got ' + str(type(doc)))
        #else:
        #    raise TypeError('Expected list or StandardDocument got ' + str(type(docs)))
        
        with TimeoutLock(self._lock, botnee_config.TIMEOUT):
            #try:
            process_docs(
                    docs, 
                    self._meta_dict, 
                    self._data_dict, 
                    self._time_dict, 
                    self._doc_store, 
                    #self._dictionaries, 
                    reindex, 
                    verbose, 
                    )
            #except Exception as e:
            #errors.EngineWarning(e.__repr__(), self.logger)            
            #return
            
            #try:
            vector_space_model(
                    self._meta_dict, 
                    self._data_dict, 
                    self._matx_dict, 
                    self._time_dict, 
                    self._doc_store, 
                    reindex, 
                    self._job_server, 
                    verbose
                    )
            #except Exception as e:
            #    import traceback, os.path
            #    errors.EngineWarning(e.__repr__(), self.logger)
            #    #raise e
            #    return
            # commit to disk
            now = datetime.datetime.now()
            self._meta_dict['last_insert'] = now.strftime("%Y-%m-%d %H:%M")
            
            result = self.flush(reindex, verbose)
            
            #if reindex:
            #    self.force_reindex(verbose)
            
        return result
    
    def insert_standard_docs(self, std_docs, reindex=False, verbose=True):
        """
        Insert standard document
        """
        #debug.print_verbose('insert_standard_docs', verbose, self.logger)
        docs = [standard_document_io.parse_document(doc, verbose=verbose)
                    for doc in std_docs]
        
        return self.insert_and_flush(docs, reindex, verbose)

    def delete(self, guids, reindex=False, verbose=True):
        """
        Delete standard document
        """
        if type(guids) in [str, unicode]:
            guids = [guids]
        elif type(guids) is list:
            pass
        else:
            raise TypeError('Expected list of strings or string')
        with TimeoutLock(self._lock, botnee_config.TIMEOUT):
            # Add to deletes list
            self._meta_dict['deletes'] = guids
            
            result = self._doc_store.put_data(
                     self._meta_dict, 
                     self._data_dict, 
                     self._matx_dict, 
                     self._time_dict, 
                     verbose)
            
            deletes = result[2]
            
            #for guid in guids:
            for guid in deletes:
                index = self._meta_dict['guids'][guid]
                del self._meta_dict['guids'][guid]
                for name in botnee_config.MATRIX_TYPES:
                    matrix = self._matx_dict[name].tolil()
                    matrix[index,:] = np.zeros((1, matrix.shape[1]))
                    self._matx_dict[name] = matrix.tocsr()
            
            if reindex:
                self.force_reindex(True, verbose)
        return result
    
    def flush(self, reindex=False, verbose=True):
        """
        Flushes data to disk (pytables/mongodb/pickle)
        """
        #self._corpus.update(self._meta_dict, self._data_dict, True, verbose)
        #self._corpus.put_meta_dict(self._meta_dict, self._time_dict, verbose)
        #self._corpus.put_data_dict(self._data_dict, self._time_dict, verbose)
        with debug.Timer(None, self._time_dict, verbose, self.logger):
            result = self._doc_store.put_data(
                     self._meta_dict, 
                     self._data_dict, 
                     self._matx_dict, 
                     self._time_dict, 
                     verbose)
            
            # Now remove term_freq_bad
            #for ngstr in [""] + ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
            #for ngstr in ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
            #    if 'term_freq_bad' + ngstr in self._data_dict:
            #        del self._data_dict['term_freq_bad' + ngstr]
            #    if 'tokens_bad' + ngstr in self._meta_dict:
            #        del self._meta_dict['tokens_bad' + ngstr]
            #    if 'bad_ids' + ngstr in self._meta_dict:
            #        del self._meta_dict['bad_ids' + ngstr]
            
            self._meta_dict.flush(verbose)
            self._data_dict.flush(verbose)
            #self._matx_dict.flush(verbose)
            self._time_dict.write_csv(verbose, self.logger)
        
        return result
    
    def dump_dictionaries(self, verbose=True):
        # Dump dictionaries to disk
        try:
            retval = debug.dump_dictionaries(START_TIME, 
                    #self._dictionaries, 
                    self._meta_dict, 
                    self._data_dict,
                    verbose, 
                    self.logger)
        except Exception as e:
            errors.EngineWarning(e.__repr__(), self.logger)
            reval = ["Files not written"]
        return retval
    
    def force_reindex(self, reprocess_docs=True, verbose=True):
        """
        Force re-indexing - should only be called sporadically, 
        as this will block the application for a while!
        """
        with TimeoutLock(self._lock, botnee_config.TIMEOUT):
            debug.print_verbose("Force re-indexing", verbose, self.logger)
            debug.print_verbose(" - should only be called sporadically," + 
                " as this will block the application for a while!", verbose, self.logger)
            with debug.Timer('Re-indexing starting...', self._time_dict, verbose, self.logger):
                # initiate reindex
                if reprocess_docs:
                    process_docs(
                        [], 
                        self._meta_dict, 
                        self._data_dict, 
                        self._time_dict, 
                        self._doc_store, 
                        #self._dictionaries, 
                        True, 
                        verbose
                        )
                
                vector_space_model(
                            self._meta_dict, 
                            self._data_dict, 
                            self._matx_dict, 
                            self._time_dict,
                            self._doc_store,
                            True, 
                            self._job_server,
                            verbose
                            )
                
                # flush everything to disk
                self.flush(True, verbose)
            
            now = datetime.datetime.now()
            self._meta_dict['last_reindex'] = now.strftime("%Y-%m-%d %H:%M")
        
    
    def recalculate_idf(self, verbose=True):
        """
        Recalculate idf vectors only
        """
        VSM = VectorSpaceModel(
                                self._meta_dict, 
                                self._data_dict, 
                                self._matx_dict, 
                                self._time_dict, 
                                self._doc_store)
        
        for ngstr in ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
            
            # IDF calculation method
            idf_method = ""    # method from http://en.wikipedia.org/wiki/Tf%E2%80%93idf
            calculate_idf(VSM, idf_method, ngstr, verbose)
            idf_method = "_bm25"   # method from http://en.wikipedia.org/wiki/Okapi_BM25
            calculate_idf(VSM, idf_method, ngstr, verbose)
    
    def check_integrity(self, verbose=True):
        """
        Checks the integrity of the databases
        """
        def print_result(result, verbose):
            debug.print_verbose('', verbose, self.logger)
            debug.print_verbose('----------------------', verbose, self.logger)
            debug.print_verbose('Engine integrity: ' + result, verbose, self.logger)
            debug.print_verbose('----------------------', verbose, self.logger)
            debug.print_verbose('', verbose, self.logger)
        
        with debug.Timer(None, self._time_dict, verbose, self.logger):
            try:
                self._meta_dict.check_types()
                
                result = 'PASS'
                
                for string in ['inserts', 'updates', 'deletes']:
                    length = len(self._meta_dict[string]);
                    if length > 0:
                        debug.print_verbose(string + ' not completed (' 
                                + str(length) + ' remain)', verbose, self.logger)
                        result='FAIL'
                
                # Check tokens
                
                # Check Sizes of data items
                #m = self._meta_dict['n_docs']
                m = self._meta_dict['last_index'] + 1
                #n = len(self._meta_dict['dictionary'])
                
                ngstrs = ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]
                
                for name, matrix in self._matx_dict.items():
                    if 'pseudo' in name:
                        continue
                    if sparse.isspmatrix(matrix):
                        for ngstr in ngstrs:
                            if name.endswith(ngstr):
                                n = len(self._meta_dict['tokens_map' + ngstr])
                                break
                        
                        if matrix.shape != (m,n):
                            debug.print_verbose(name + '(mem) is ' 
                                    + str(matrix.shape) + ' expected ' 
                                    + str((m,n)), verbose, self.logger)
                            result='FAIL'
                    else:
                        debug.print_verbose(name + ' type: ' + str(type(matrix)))
                
                for name, array in self._data_dict.items():
                    if type(array) in [np.array, np.ndarray]:
                        
                        comp = None
                        
                        for ngstr in ngstrs:
                            n = len(self._meta_dict['tokens_map' + ngstr])
                            if name == 'idf' + ngstr:
                                comp = n
                                break
                            elif name == 'term_freq' + ngstr:
                                comp = n
                                break
                            #elif name == 'term_freq_bad' + ngstr:
                            #    comp = len(self._meta_dict['bad_ids' + ngstr])
                            #    break
                            #else:
                                #comp = n
                                #debug.debug_here()
                        
                        if comp and len(array) != comp:
                            debug.print_verbose(name + ' (mem) is ' 
                                    + str(len(array)) + ' expected ' 
                                    + str(comp), verbose, self.logger)
                            result = 'FAIL'
                    else:
                        #debug.debug_here()
                        debug.print_verbose(name + ' type: ' + str(type(matrix)))
                
                if m - self._meta_dict['n_docs'] > 1000:
                    debug.print_verbose("Number of missing indices > " +
                                        str(botnee_config.MISSING_INDEX_THRESHOLD) + 
                                        " - reindexing required", verbose, self.logger)
                    result = 'WARN'
                
                
                #guids0 = self._doc_store.get_guid_indices()
                #guids1 = self._doc_manager_store.get_guids()
                
                #if guids1:
                #    guid_set0 = set(guids0.keys())
                #    guid_set1 = set(guids1)
                
            except Exception as e:
                errors.EngineWarning(e.__repr__(), self.logger)
                result = 'FAIL'
                pass
            
            print_result(result, verbose)
            return result
    
    def get_summary_as_list(self, verbose=False):
        """
        Summary of memory footprint of objects as list
        """
        
        summary = OrderedDict()
        
        
        summary['BOTNEE Summary'] =  \
                [
                   {"name": "Start time", "info": START_TIME},
                   {"name": "Last re-index", "info": self._meta_dict['last_reindex']},
                   {"name": "Last query", "info": self._meta_dict['last_query']},
                   {"name": "Last insert", "info": self._meta_dict['last_insert']},
                ]
        
        #summary['botnee_config.py'] = botnee_config.get_summary()
        summary['botnee_config.py'] = [{'name': k, 'info': v} \
                                    for k, v in sorted(botnee_config.__dict__.items()) \
                                    if k != '__builtins__']
        
        try:
            if self._meta_dict:
                summary['META DICT'] = self._meta_dict.get_summary_as_list()
        except Exception as e:
            errors.EngineWarning(e.__repr__(), self.logger)
            pass
        
        try:
            if self._data_dict:
                summary['DATA DICT'] = self._data_dict.get_summary_as_list()
        except Exception as e:
            errors.EngineWarning(e.__repr__(), self.logger)
            pass
        
        try:
            if self._matx_dict:
                summary['MATRIX DICT'] = self._matx_dict.get_summary_as_list()
            
        except Exception as e:
            errors.EngineWarning(e.__repr__(), self.logger)
            pass
        
        try:
            if self._doc_store:
                summary['DOC STORE'] = self._doc_store.get_summary_as_list(verbose)
        except Exception as e:
            errors.EngineWarning(e.__repr__(), self.logger)
            pass
        
        return summary
    
    def print_summary(self, verbose=True):
        """
        Pretty prints a summary of meta and data dicts
        """
        with debug.Timer(None, self._time_dict, verbose, self.logger):
            for k, v in self.get_summary_as_list(verbose).items():
                msg = ("-" * len(k)) + "\n" + k + "\n" + ("-" * len(k))
                debug.print_verbose(msg, verbose, self.logger)
                for item in v:
                    try:
                        msg = "%30s\t%30s\t%10s\t%10s" % \
                            (item['name'], item['info'], item['size'], item['sparsity'])
                    except KeyError:
                        try:
                            msg = "%40s\t%s" % \
                            (item['name'], str(item['info']))
                        except:
                            debug.debug_here()
                    debug.print_verbose(msg, verbose, self.logger)
                debug.print_verbose("", verbose, self.logger)
    
    def get_proc_summary(self):
        with debug.Timer(None, None, verbose, self.logger):
            pm_usage = psutil.phymem_usage()
            vm_usage = psutil.virtmem_usage()
            pid = os.getpid()
            proc = psutil.Process(pid)
            
            return [
                "",
                "PHYSICAL MEMORY:",
                "Total %.2fGb" % (float(pm_usage[0])/1024/1024/1024),
                "Used  %.2fGb" % (float(pm_usage[1])/1024/1024/1024),
                "Free  %.2fGb" % (float(pm_usage[2])/1024/1024/1024),
                "Percent %.1f" % (pm_usage[3]),
                "",
                "VIRTUAL MEMORY:",
                "Total %.2fGb" % (float(vm_usage[0])/1024/1024/1024),
                "Used  %.2fGb" % (float(vm_usage[1])/1024/1024/1024),
                "Free  %.2fGb" % (float(vm_usage[2])/1024/1024/1024),
                "Percent %.1f" % (vm_usage[3]),
                "",
                "BOTNEE (pid=%d)" % (pid),
                "Executable: " + proc.exe,
                "Working directory: " + proc.getcwd(),
                "Command line: " + str(proc.cmdline),
                "Status: " + str(proc.status),
                "username: " + proc.username,
                "Create Time: " + asctime(localtime(proc.create_time)),
                "Terminal: " + proc.terminal,
                "uids: " + str(proc.uids),
                "gids: " + str(proc.gids),
                "",
                "CPU: %.1d%%" % (proc.get_cpu_percent(interval=1.0)),
                "Memory: %.1d%%" % (proc.get_memory_percent()),
                "Memory info: " + str(proc.get_memory_info()),
                "CPU Times: " + str(proc.get_cpu_times()),
                "IO Counters: " + str(proc.get_io_counters()),
                "Open Files: " + str(proc.get_open_files()),
                "Connections: " + str(proc.get_connections()),
                "Threads: " + str(proc.get_threads()),
                "",
                ]
    
    def realign_guids(self):
        """
        Gets the indices for the query using the guids stored in memory
        """
        with debug.Timer(None, self._time_dict, verbose, self.logger):
            #guids0 = self._doc_store.get_guid_indices()
            #guids1 = self._meta_dict['guids']
            
            #for key, value in guids0.items():
            #    try:
            #        guids1[key]
            #    except KeyError:
            #        debug.print_verbose(guid + " missing in memory", verbose, self.logger)
            #        result = 'FAIL'
            #    try:
            #        guids1[:value]
            #    except KeyError:
            #        debug.print_verbose(guid + " index error", verbose, self.logger)
            #
            #for key, value in guids1.items():
            #    try:
            #        guids0[key]
            #    except KeyError:
            #        debug.print_verbose(guid + " missing in memory", verbose, self.logger)
            #        result = 'FAIL'
            #    try:
            #        guids0[:value]
            #    except KeyError:
            #        debug.print_verbose(guid + " index error", verbose, self.logger)
            
            self._meta_dict['guids'] = self._doc_store.get_guid_indices()
            self._meta_dict.flush()




