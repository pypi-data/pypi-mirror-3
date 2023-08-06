"""
Wrapper class over standard dictionary with some added functionality 
(print summary etc)
"""
from bidict import bidict
from ordereddict import OrderedDict

from botnee.persistent_dict import PersistentDict
from scipy import sparse
import numpy as np
import logging

from botnee import debug

import botnee_config

IGNORE_ON_LOAD = (
    "term_freq_bad",
        )

class DataDict(PersistentDict):
    def __init__(self, initial={}, verbose=True, persistent=True):
        params = {
            'filename': botnee_config.DATA_DICT_FILE + '.dat',
            'flag':  'c',
            'mode':  None,
            'format': botnee_config.DATA_DICT_STORE_TYPE,
            'persistent': persistent,
            'ingore_on_load': IGNORE_ON_LOAD,
                }
        self.logger = logging.getLogger(__name__)
        
        PersistentDict.__init__(self, params, verbose, self.logger)
        
        for ngram in botnee_config.NGRAMS.keys():
            ngstr = "_%d" % ngram
            if 'idf' + ngstr not in self:
                self['idf' + ngstr] = np.array([], dtype=np.uint16)
            if 'term_freq' + ngstr not in self:
                self['term_freq' + ngstr] = np.array([], dtype=np.uint16)
            #if 'term_freq_bad' not in self:
            #    self['term_freq_bad'] = np.array([], dtype=np.uint16)
                
        self.update(initial)
        
        self.flush(verbose, self.logger)
    
    def get_summary_as_list(self):
        #summary = [
        #        "",
        #        "%25s\t"*5 % tuple(["-"*25]*5),
        #        "%25s\t"*5 
        #            % ("data_dict key", "Type", "Shape", "Sparsity", "Memory"), 
        #        "%25s\t"*5 % tuple(["-"*25]*5), 
        #        ]
        summary = []
        
        for k,v in self.items():
            if type(v) in [dict, bidict, OrderedDict]:
                v = np.array(v.values())
            
            size = debug.get_size_as_string(v)
            if sparse.isspmatrix(v):
                sparsity = "%.4f" % (np.float32(v.nnz)/np.product(v.shape))
                #summary.append("%25s\t"*5 % 
                #            (k, "<type 'scipy.sparse'>", "(%d,%d)" % \
                #             v.shape, sparsity, size))
                summary.append({'name': k,
                                'info': "<type 'scipy.sparse'> (%d,%d)" % v.shape,
                                'size': size,
                                'sparsity': sparsity
                                })
            elif type(v) in [np.array, np.ndarray]:
                if len(v.shape)==1:
                    shapestr = "(%d,)" % v.shape
                else:
                    shapestr = "(%d,%d)" % v.shape
                try:
                    pshape = max(np.product(v.shape), 1)
                    sparsity = "%.4f" % (np.float32(np.count_nonzero(v))/pshape)
                    #summary.append("%25s\t"*5 %
                    #        (k, type(v), shapestr, sparsity, size))
                    summary.append({'name': k,
                                    'info': str(type(v)) + " " + shapestr,
                                    'size': size,
                                    'sparsity': sparsity
                                    })
                except TypeError as e:
                    print e
            else:
                try:
                    #summary.append("%25s\t%25s\t%25s" % (k, type(v)))
                    summary.append({'name': k, 'info': str(type(v))})
                except TypeError:
                    pass
        #summary.append("%25s\t"*5 % tuple(["-"*25]*5))
        #summary.append("")
        return summary
    
    def print_summary(self, verbose):
        for line in self.get_summary_as_list():
            debug.print_verbose(line, verbose, self.logger)

