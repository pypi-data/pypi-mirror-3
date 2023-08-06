"""
Filter class: 
Interfaces to doc_store and/or doc_manager_store to peform filtering on mongodb
Filters file should be in JSON format
"""

#import os
import json
import logging
#from datetime import datetime
import dateutil

from botnee.doc_store import DocStore

from botnee import debug, errors

#import botnee_config

class Filters(object):
    """
    Loads filters from a json object
    """
    def __init__(self, json_object, doc_store, verbose=False):
        if type(doc_store) is not DocStore:
            raise TypeError('Expected DocStore, got ' + str(type(doc_store)))
        
        self.logger = logging.getLogger(__name__)

        with debug.Timer(None, None, verbose, self.logger):
            self.doc_store = doc_store
            
            #self.title_boost = botnee_config.TITLE_BOOST
            #self.date_boost = botnee_config.DATE_BOOST
            #self.abstract_boost = botnee_config.ABSTRACT_BOOST
            
            self.load_filters(json_object, verbose)
            
            self.guids = self.execute(verbose)
    
    def load_filters(self, json_object, verbose=False):
        """
        Loads the filters from a json object
        Searches for 'date' in keys, and converts to datetime object if found
        """
        with debug.Timer(None, None, verbose, self.logger):
            try:
                self.filters = json.loads(json_object)
            except ValueError as e:
                errors.FiltersWarning("Failed to parse JSON\n"+ str(e), self.logger)
                self.filters = None
                return
            except TypeError as e:
                msg = "Failed to parse JSON\n%s got %s" % \
                            (str(e), str(type(json_object)))
                errors.FiltersWarning(msg, self.logger)
                self.filters = None
                return
            except Exception as e:
                errors.FiltersWarning("Failed to parse JSON\n"+ str(e), self.logger)
                self.filters = None
                return
            
            for key, value in self.filters.items():
                # Special cases
                if key == 'publication-date':# and len(value)==1:
                    for k,v in value.items():
                        try:
                            #value = dateutil.parser.parse(value)
                            #k,v = value.items()[0]
                            self.filters[key][k] = dateutil.parser.parse(v)
                            msg = "Date parsed ok"
                            debug.print_verbose(msg, verbose, self.logger)
                        except ValueError as e:
                            msg = "Invalid date format\n" + str(e),
                            debug.print_verbose(msg, verbose, self.logger, logging.WARNING)
                            self.filters = None
                            return
                        except AttributeError as e:
                            msg = "Invalid date format\n" + str(e),
                            debug.print_verbose(msg, verbose, self.logger, logging.WARNING)
                            self.filters = None
                            return
                #elif key in ['title-boost', 'abstract-boost', 'date-boost']:
                #    try:
                #        boost = float(value)
                #        if value < 0 or value > 1:
                #            msg = key + " should be in range [0...1]"
                #            errors.FiltersWarning(msg, self.logger)
                #        else:
                #            exec "self." + key.replace('-', '_') + " = boost"
                #    except ValueError as e:
                #        msg = key + " should be in range [0...1]"
                #        errors.FiltersWarning(msg, self.logger)
        
    def execute(self, verbose=False):
        """
        Performs the filter query and stores the guids
        """
        def evaluate_cursor(cursor):
            with debug.Timer(None, None, verbose, self.logger):
                return [c['_id'] for c in cursor]
        
        with debug.Timer(None, None, verbose, self.logger):
            if not self.filters:
                errors.FiltersWarning("Filters not set", self.logger)
                return []
            
            db = self.doc_store._database
            cursor = db.docs.find(self.filters, {'_id': 1})
            
            msg = "Filter resulted in %d hits" % (cursor.count())
            debug.print_verbose(msg, verbose)
            
            guids = evaluate_cursor(cursor)
            
            return guids
    
    def get_summary_as_list(self):
        """
        Gets a summary of the filters as a list of strings
        """
        
        msg_list = []
        
        if not self.filters:
            return []
        
        for key, value in self.filters.items():
            msg_list.append("%20s: %s" % (key, str(value)))
        
        return msg_list
        
    def print_summary(self, verbose=False):
        """
        Prints the summary to screen (and log)
        """
        
        msg_list = self.get_summary_as_list()
        
        for msg in msg_list:
            debug.print_verbose(msg, verbose, self.logger)

