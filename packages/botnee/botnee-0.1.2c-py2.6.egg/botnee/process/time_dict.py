"""
Wrapper class over standard dictionary
"""

from ordereddict import OrderedDict

from botnee import debug

import botnee_config

class TimeDict(OrderedDict):
    def __init__(self, start_time=None):
        OrderedDict.__init__(self)
        #self['dictionary'] = None
        #self['process_docs'] = None
        #self['doc_freq'] = None
        #self['tf'] = None
        #self['idf'] = None
        #self['tfidf'] = None
        
        self.start_time = start_time

    def write_csv(self, verbose=False, logger=None):
        with debug.Timer(None, None, verbose, logger):
            if not self.start_time:
                return
            fname = botnee_config.LOG_DIRECTORY + 'time_dict_' + \
                               self.start_time + '.csv'
            debug.write_csv(fname, [(k,v) for k,v in self.items()])
