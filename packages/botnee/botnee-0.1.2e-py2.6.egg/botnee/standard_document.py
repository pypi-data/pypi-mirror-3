"""
StandardDocument class
"""
import datetime
from ordereddict import OrderedDict
#from botnee import debug
import botnee_config

class StandardDocument(OrderedDict):
    """
    Standard Document Class
    """
    def __init__(self, initial={}):
        """
        Takes an initial dictionary as a parameter (default empty)
        Intialised like so:
        
        OrderedDict.__init__(self)
        self['title'] = None
        self['guid'] = None
        self['url'] = None
        self['publication-date'] = None
        self.update(initial)
        """
        OrderedDict.__init__(self)
        self['title'] = None
        self['guid'] = None
        self['url'] = None
        self['publication-date'] = None
        self['body'] = u""
        self['failed'] = None
        self['operation'] = u""
        self.update(initial)
        if type(initial) is dict and initial.has_key('_id'):
            self['guid'] = self['_id']
            del self['_id']
    
    def check_for_failures(self):
        """
        Checks for failures, and returns the field of first failure if found
        """
        if(type(self['failed']) is dict):
            return self['failed']
        
        result = None
        for field in botnee_config.REQUIRED_FIELDS:
            if field not in self.keys() or not self[field]:
                result = field
        if result:
            self['failed'] = {'reason': 'missing_header', 'extra': result}
        
        if type(self['publication-date']) is not datetime.datetime:
            self['failed'] = {'reason': 'incorrect_date_format', 
                              'extra':  self['publication-date']}
        
        return result
    
    def get_required(self):
        """
        Gets the required fields as dict
        """
        if self.check_for_failures is not None:
            return {}
        
        return dict((key, self[key]) for key in botnee_config.REQUIRED_FIELDS)
    
    def get_summary(self, fields=botnee_config.REQUIRED_FIELDS):
        """
        Returns summary as string (requried fields only if fields is empty)
        """
        
        summary = u""
        
        if not fields:
            raise TypeError("Fields should not be empty")
        
        for field in fields:
            #if field == 'publication-date':
            #    debug.debug_here()
            #else:
            #summary += u"%s: %s\n" % (field, unicode(self[field]))
            summary += unicode(self[field]) + ","
        
        return summary[:-1]

