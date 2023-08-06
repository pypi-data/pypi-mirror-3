import urllib2
import xml.dom.minidom

#import bontee_config

url = 'http://10.1.204.8:8080/mm-service/rest/mapTerm'

CONCEPT_FIELDS = (
    'cui', 
    'displayName', 
    'preferredName', 
    'sources', 
    'semanticTypes', 
    'matchedText'
    )


class MetamapWrapper(object):
    """
    Wrapper class for the RESTful metamamap server instance
    """
    def __init__(self):
        self.url = botnee_config.METAMAP_SERVER
    
    def query_by_text(self, text):
        """
        Queries the metamap instance using the supplied text string
        """
        values = {'text': text}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        self.xml_result = xml.dom.minidom.parseString(the_page)
        return self.process_result(self.xml_result)
    
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

