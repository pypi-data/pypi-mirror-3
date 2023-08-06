import urllib
import urllib2
import xml.dom.minidom
import signal
import logging

from botnee import debug

import botnee_config

CONCEPT_FIELDS = (
    'cui', 
    'displayName', 
    'preferredName', 
    'sources', 
    'semanticTypes', 
    'matchedText'
    )

class TimeoutException(Exception): 
    pass 

class MetamapWrapper(object):
    """
    Wrapper class for the RESTful metamamap server instance
    """
    def __init__(self):
        self.url = botnee_config.METAMAP_SERVER
        self.timeout = botnee_config.METAMAP_TIMEOUT
        self.logger = logging.getLogger(__name__)
    
    def query_by_text(self, text, verbose=False):
        """
        Queries the metamap instance using the supplied text string
        Uses signal module to create a timeout
        """
        def timeout_handler(signum, frame):
            raise TimeoutException()
        
        if self.timeout > 0:
            signal.signal(signal.SIGALRM, timeout_handler) 
            signal.alarm(self.timeout) # triger alarm in 3 seconds
        
        with debug.Timer(None, None, verbose, self.logger):
            
            atext = text.encode('ascii', 'ignore')
            values = {'text': atext}
            data = urllib.urlencode(values)
            
            try:
                req = urllib2.Request(self.url, data)
                try:
                    response = urllib2.urlopen(req)
                except urllib2.HTTPError as e:
                    #debug.debug_here()
                    #raise e
                    print e.__repr__()
                    return []
                the_page = response.read()
                self.xml_result = xml.dom.minidom.parseString(the_page)
                return self.process_result(self.xml_result)
            except TimeoutException:
                debug.print_verbose("Timed out", verbose, self.logger)
                return []
        
    def process_result(self, xml_result):
        """
        Takes the xml result and constructs a list of dictionary objects
        """
        tags = []
        
        for option in xml_result.getElementsByTagName('option'):
            tags.append({})
            
            for label in ['score', 'start', 'length']:
                tags[-1][label] = option.getElementsByTagName(label)[0].childNodes[0].data
            
            concept = option.getElementsByTagName('concept')[0]
            
            tags[-1]['concept'] = {}
            for concept_field in CONCEPT_FIELDS:
                nodes = concept.getElementsByTagName(concept_field)
                if len(nodes)==1:
                    tags[-1]['concept'][concept_field] = nodes[0].childNodes[0].data
                else:
                    tags[-1]['concept'][concept_field] = [node.childNodes[0].data for node in nodes]
        return tags

