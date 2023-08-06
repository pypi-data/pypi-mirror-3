"""
Wrapper class over standard dictionary with some added functionality 
(print summary etc)
"""
from bidict import bidict
from ordereddict import OrderedDict
#from botnee.persistent_dict import PersistentDict

from scipy import sparse
import numpy as np
import logging

from botnee import debug

import botnee_config

class MatrixDict(OrderedDict):
    def __init__(self, initial={}, verbose=True):
        OrderedDict.__init__(self)
        
        self.reset()
        
        self.update(initial)
        self.logger = logging.getLogger(__name__)
    
    def reset(self):
        """
        Initalise/Reset matrices. 
        Only resets the matrices defined in the config (does not touch any 
        additional fields)
        """
        #flag='c'
        #mode=None
        #format = botnee_config.DATA_DICT_STORE_TYPE
        
        for name in botnee_config.MATRIX_TYPES:
            #fname = botnee_config.DATA_DIRECTORY + 'marshal/' + name + '.dat'
            #self[name] = PersistentDict(fname, flag, mode, format, initial, None)
            for suffix in botnee_config.SUFFIXES:
                for ngstr in ["_%d" % ngram for ngram in botnee_config.NGRAMS.keys()]:
                    fullname = name + suffix + ngstr
                    self[fullname] = None
    
    def get_summary_as_list(self):
        summary = []
            #"",
            #"%25s\t"*5 % tuple(["-"*25]*5),
            #"%25s\t"*5 
            #        % ("matx_dict key", "Type", "Shape", "Sparsity", "Memory"),
            #"%25s\t"*5 % tuple(["-"*25]*5)
            #]
        
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
                                'sparsity': sparsity,
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
                                    'sparsity': sparsity})
                except TypeError as e:
                    print e
            else:
                try:
                    #summary.append("%25s\t%25s\t%25s" % (k, type(v)))
                    summary.append({'name': k,
                                    'info': str(type(v))
                                    })
                except TypeError:
                    pass
        #summary.append("%25s\t"*5 % tuple(["-"*25]*5))
        #summary.append("")
        return summary
    
    def print_summary(self, verbose):
        for line in self.get_summary_as_list():
            debug.print_verbose(line, verbose, self.logger)




