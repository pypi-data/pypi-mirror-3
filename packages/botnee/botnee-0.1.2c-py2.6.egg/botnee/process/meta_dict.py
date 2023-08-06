"""
Wrapper class over standard dictionary with some added functionality 
(print summary etc)
"""

from botnee import debug
from bidict import bidict
from ordereddict import OrderedDict
from botnee.persistent_dict import PersistentDict
import logging

import botnee_config

TYPES = {
    'inserts': list,
    'updates': list,
    'deletes': list,
    'pseudos': list,
    'guids': bidict,
    'expected_sparsity': float,
    'last_reindex': str,
    'last_query': str,
    'last_insert': str,
    }

IGNORE_ON_LOAD = (
    'tokens_bad',
    'bad_ids',
        )

# And for ngrams
for ngstr in ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
    TYPES['tokens_map' + ngstr] = dict
    TYPES['tokens_map_inv' + ngstr] = dict
    TYPES['bad_ids' + ngstr] = dict
    TYPES['bad_ids_inv' + ngstr] = dict

class MetaDict(PersistentDict):
    """
    Wrapper class over standard dictionary with some added functionality 
    (print summary etc)
    Provides default elements:
        inserts         guids of docs to be inserted
        updates         guids of docs to be updated
        deletes         guids of docs to be deleted
        pseudos         pseudo docs for retrieval
        guids           bidict mapping guids to indices
        last_index      last index for creating new indices
        tokens_map      mapping of tokens to token indices
        tokens_map_inv  reverse mapping of above
    """
    
    def __init__(self, initial={}, verbose=True, persistent=True):
        """
        Takes an initial dictionary as a parameter (default empty)
        """
        params = {
            'filename': botnee_config.META_DICT_FILE + '.dat',
            'flag':  'c',
            'mode':  None,
            'format': botnee_config.DATA_DICT_STORE_TYPE,
            'persistent': persistent,
            'ignore_on_load': IGNORE_ON_LOAD,
                }
        self.logger = logging.getLogger(__name__)
        
        PersistentDict.__init__(self, params, verbose, self.logger)
        
        for key, value in TYPES.iteritems():
            if key not in self:
                self[key] = value()
        
        if 'n_docs' not in self:
            self['n_docs'] = 0
        if 'last_index' not in self:
            self['last_index'] = -1
        if 'expected_sparsity' not in initial:
            self['expected_sparsity'] = float(botnee_config.EXPECTED_SPARSITY)
        
        if initial:
            # Update the dictionary and flush the new data straight to disk
            self.update(initial)
            self.flush(verbose, self.logger)
    
    def check_types(self):
        """
        Checks the types of the items in the dictionary according to TYPES
        """
        for key, value in TYPES.iteritems():
            if type(self[key]) is not value:
                msg = 'key=%s. Expected %s, got %s' % (key, type(self[key]), value)
                raise TypeError(msg)
    
    
    def get_summary_as_list(self):
        #summary = [
        #        "", 
        #        "%35s\t%35s\t%35s" % tuple(["-"*35]*3), 
        #        "%35s\t%35s\t%35s" % ("meta_dict key", "Type", "Length"), 
        #        "%35s\t%35s\t%35s" % tuple(["-"*35]*3)
        #        ]
        
        summary = []
        
        for key, value in self.items():
            if type(value) in [list, dict, bidict, OrderedDict]:
                #summary.append("%35s\t%35s\t%35d" 
                #            % (key, type(value), len(value)))
                summary.append({'name': key, 'info': str(type(value)), 'size': len(value)})
            elif type(value) is int:
                #summary.append("%35s\t%35s\t%35d" 
                #            % (key, type(value), value))
                summary.append({'name': key, 'info': str(type(value)), 'size': value})
            else:
                #summary.append("%35s\t%35s" % (key, type(value)))
                try:
                    summary.append({'name': key, 'info': str(type(value)), 'size': len(value)})
                except:
                    summary.append({'name': key, 'info': str(type(value))})
        
        #summary.append("%35s\t%35s\t%35s" % tuple(["-"*35]*3))
        #summary.append("")
        return summary
    
    def print_summary(self, verbose=True):
        for line in self.get_summary_as_list():
            debug.print_verbose(line, verbose, self.logger)


