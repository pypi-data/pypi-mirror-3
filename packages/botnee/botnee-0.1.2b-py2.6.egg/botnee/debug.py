"""
Some useful debugging functions.
"""
#!/usr/bin/env python
import logging
#import inspect

#import tables
from scipy import sparse
import numpy as np
import sys
from time import time
import csv
import os

import botnee_config

try:
    __IPYTHON__
#    try:
#        from IPython.Debugger import Tracer; debug_here = Tracer()
#    except ImportError:
    try:
        from IPython.core.debugger import Tracer; debug_here = Tracer()
    except ImportError:
        def empty():
            pass
        debug_here = empty
except NameError:
    print "Not inside ipython"
    if not botnee_config.DEBUG:
        def debug_here():
            return None
    else:
        import ipdb
        debug_here = ipdb.set_trace

def write_csv(filename, list_of_tuples, verbose=False, logger=None):
    """ Writes a list of tuples as a comma seperated variable file """
    with Timer('(%s)' % filename, None, verbose, logger):
        with open(filename, "w") as the_file:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
            writer = csv.writer(the_file, dialect="custom")
            for i, tup in enumerate(list_of_tuples):
                print_dot(i, verbose)
                writer.writerow(tup)

def print_verbose(statement, verbose=False, logger=None, logtype=logging.INFO):
    """ Simply prints the statement if verbose is True """
    if type(statement) is list:
        for x in statement: print_verbose(x, verbose, logger, logtype)
        return
    
    if(verbose):
        #print statement
        try:
            sys.stdout.write(unicode(statement) + '\n')
            sys.stdout.flush()
        except TypeError as e:
            print e
            pass
        except UnicodeEncodeError as e:
            print e
            pass
        except Exception as e:
            print e
            pass
        
    if(logger):
        logger.log(logtype, statement)

def print_dot(i=-1, verbose=False):
    """ Prints a dot '.' to the screen """
    if i==0:
        return
    if verbose and (np.mod(i,1000)==0):
        sys.stdout.write("%d\n" % i)
        sys.stdout.flush()
        return
    
    if verbose and (np.mod(i,100)==0 or i==-1):
        sys.stdout.write('.')
        sys.stdout.flush()

class Timer(object):
    def __init__(self, message=None, time_dict=None, verbose=False, logger=None):
        self.message = message
        self.time_dict = time_dict
        self.logger = logger
        self.verbose = verbose
        #if inspect.stack()[1][3] != inspect.stack()[2][3]:
        #    self.caller = inspect.stack()[2][3] + "." + inspect.stack()[1][3]
        #else:
        #    self.caller = inspect.stack()[1][3]
        
        frame = sys._current_frames().values()[0]
        back = frame.f_back
        flocals = back.f_locals
        try:
            class_name = str(type(flocals['self']))[8:-2]
            func_name = back.f_code.co_name
            self.caller = module_name + "." + class_name
        except:
            module_name = back.f_globals['__name__']
            func_name = back.f_code.co_name
            self.caller = module_name + "." + func_name
        
        #nframes = sys.__plen
        #for i in range(nframes):
        #    try:
        #        print sys._getframe(i)['self'].__str__()[1:-21]
        #    except:
        #        pass
        
        #debug_here()
        #self.caller = '.'.join(reversed([ist[3] for ist in inspect.stack()]))
        
    def __enter__(self):
        self.t_start = time()
        message = str(self.caller) + " started. "
        if self.message:
            message += self.message
        print_verbose(message, self.verbose, self.logger)
        return self
        
    def __exit__(self, type, value, traceback):
        self.t_end = time() - self.t_start
        self.t_str = " done. %.2f seconds" % self.t_end
        print_verbose(str(self.caller) +  self.t_str, self.verbose, self.logger)
        #if type(time_dict) is TimeDict:
        try:
            self.time_dict[str(self.caller)] = self.t_end
        except TypeError:
            pass

#def format_time(time0):
#    """ Formats a time value to a string using 2 decimal places """
#    return "{0:.2f} seconds".format(time()-time0)

#def print_end_time(time0, verbose=False, logger=None):
#    print_verbose('Done. ' + format_time(time0), verbose, logger)

def get_size(object):
    #if type(object) is tables.array.Array \
    #        or type(object) is tables.carray.CArray \
    #        or type(object) is tables.earray.EArray \
    #        or type(object) is tables.vlarray.VLArray:
    #    return np.product(object.shape) * object.atom.size
    if sparse.isspmatrix(object):
        return get_size(object.data) + get_size(object.indptr) + get_size(object.indices)
    if type(object) == np.ndarray:
        return float(object.nbytes)
    return float(sys.getsizeof(object))

def get_size_as_string(object):
    return "%.1fMb" % (get_size(object)/1024/1024)

def get_sparsity(object):
    return np.float32(object.nnz)/np.product(object.shape)

#def dump_dictionaries(start_time, dictionaries, meta_dict, data_dict, verbose=False, logger=None):
def dump_dictionaries(start_time, meta_dict, data_dict, verbose=False, logger=None):
    """
    Dumps good and bad ids to csv with document frequency, proportion, and idf
    """
    retval = ["--------------", "Files Written:", "--------------", ""]
    with Timer(None, None, verbose, logger):
        for i, ngram in enumerate(botnee_config.NGRAMS.keys()):
            ngstr = '_%d' % ngram
            
            fname = "tokens_good" + ngstr + "_" + start_time + ".csv"
            print_verbose(fname, verbose, logger)
            
            #dictionary = meta_dict['dictionary' + ngstr]
            #dictionary = dictionaries[i]
            n_docs = meta_dict['n_docs']
            tokens_map = meta_dict['tokens_map' + ngstr]
            freq = data_dict['term_freq' + ngstr]
            idf = data_dict['idf' + ngstr]
            idf_bm25 = data_dict['idf_bm25' + ngstr]
            
            try:
                lot = (
                    (k, 
                     #doc_store.get_token(k, ngram),
                     freq[v], 
                     "%.4f" % (float(freq[v])/n_docs,), 
                     "%.4f" % idf[v],
                     "%.4f" % idf_bm25[v]) \
                        for k,v in tokens_map.items())
            except KeyError as e:
                print e.__repr__()
                print "ngstr: ", ngstr
                #debug_here()
                pass
            
            fullname = os.path.join(botnee_config.LOG_DIRECTORY, fname)
            write_csv(fullname, lot)
            retval.append(fullname)
            
            if 'bad_ids' + ngstr in meta_dict and \
               'term_freq_bad' + ngstr in data_dict and \
               len(data_dict['term_freq_bad' + ngstr]) > 0:
                fname = 'tokens_bad' + ngstr + '_' + start_time + '.csv'
                print_verbose(fname, verbose, logger)
                
                tokens_map = meta_dict['bad_ids' + ngstr]
                freq = data_dict['term_freq_bad' + ngstr]
                
                #debug_here()
                lot = (
                    (k, 
                    #doc_store.get_token(k, ngram),
                    freq[v], "%.2f" % (float(freq[v])/n_docs,)) \
                        for k,v in tokens_map.items())
                fullname = os.path.join(botnee_config.LOG_DIRECTORY, fname)
                write_csv(fullname, lot)
                retval.append(fullname)
    return retval



