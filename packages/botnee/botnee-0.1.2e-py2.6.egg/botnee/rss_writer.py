"""
Simple RSS Writer that uses WebHelpers Rss201rev2Feed

Example usage:

docs = [
    {
        'title': 'doc 1', 
        'url': 'http://www.test.com',
        'description': 'some description',
    },
    {
        'title': 'doc 2', 
        'url': 'http://www.abc.com',
        'description': 'another description',
    }
    ]
    
botnee.rss_writer.write_string(docs)

Result:
'<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel><title>Botnee Feed</title><link>http://www.bmjgroup.com</link><description>A sample feed, showing how to make and add entries</description><language>en</language><lastBuildDate>Thu, 01 Mar 2012 14:32:49 -0000</lastBuildDate><item><title>doc 1</title><link>http://www.test.com</link><description>Testing.</description></item><item><title>doc 2</title><link>http://www.abc.com</link><description>Testing.</description></item></channel></rss>'
"""

#from webhelpers.feedgenerator import Rss201rev2Feed as RssFeed
#from django.contrib.syndication.views import Feed as RssFeed
from django.utils.feedgenerator import Rss201rev2Feed as RssFeed
from webhelpers.feedgenerator import rfc3339_date as rfc_date
#from pylons import response
from time import time
import datetime
#import dateutil.parser
import hashlib
#import json

from botnee.standard_document import StandardDocument
from botnee import debug

import botnee_config

import logging

#from django.utils.xmlutils import SimplerXMLGenerator
#from xml.sax.saxutils import XMLGenerator

rss_logger = logging.getLogger(__name__)

BASE_URL = u"http://group.bmj.com/"

def write_feed(summary, 
                feed_title=u"Botnee Feed", 
                feed_description = u"A Sample Feed",
                feed_url = BASE_URL,
                feed_seed = u"",
                verbose=False):
    """
    Returns feed as string
    """
    with debug.Timer(None, None, verbose, rss_logger):
        #feed = create_feed(summary, feed_title, feed_description, feed_link, verbose)
        
        feed = BotneeFeed(summary, feed_title, feed_description, feed_url, feed_seed, verbose)
        
        try:
            feed_string = feed.writeString('utf-8')
        except Exception as e:
            errors.RssWriterWarning(e.__repr__(), rss_logger)
            feed_string = ""
        
        return feed_string

class BotneeFeed(RssFeed):
    """
    Subclass of generic feed with custom properties for botnee
    """
    def __init__(self, 
                summary, 
                feed_title=u"Botnee Feed", 
                feed_description = u"A Sample Feed",
                feed_url = u"http://www.bmjgroup.com",
                feed_seed = u"",
                verbose=False):
        
        feed_guid = u"bmj:botnee:" + hashlib.md5(str(time())).hexdigest()
        lastBuildDate = rfc_date(datetime.datetime.now()).decode('utf-8')
        #categories = [u"section"]
        
        if botnee_config.DEBUG:
            feed_description += "\n\n" + feed_seed
        
        RssFeed.__init__(self, 
                        feed_title,
                        feed_url,
                        feed_description,
                        feed_url = feed_url,
                        feed_guid = feed_guid,
                        #categories = categories,
                        lastBuildDate = lastBuildDate
                        )
        
        for doc in summary:
            #create_atom(self, atom, verbose)
            self.add_standard_doc(doc, verbose)
    
    def add_standard_doc(self, doc, verbose=False):
        """
        Creates atom from StandardDocument
        """
        if type(doc) is not StandardDocument:
            raise TypeError("Expected StandardDocument, got %s" % str(type(doc)))
        
        #fields = ['publication', 'score']
        #adict = dict((key, atom[key]) for key in fields)
        
        unique_id = doc['guid']
        title = doc['title']
        #title = "%s \t(score=%.6f)" % (doc['title'], doc['score'])
        link = doc['url']
        pubdate = doc['publication-date']
        source = doc['publication']
        #description = "some text"#doc['publication']
        description = doc['extra']
        
        if type(pubdate) is not datetime.datetime:
            raise TypeError("Expected datetime, got %s" % str(type(pubdate)))
        
        try:
            categories_cust = [('journal_section', doc['journal_section'])]
            #categories = [
            #                {
            #                    'term': 'journal_section', 
            #                    'journal_section': doc['journal_section']
            #                }
            #             ]
        except KeyError:
            categories_cust = []
            msg = '%s: No journal section' % unique_id
            debug.print_verbose(msg, verbose, rss_logger)
        
        self.add_item(
            title = title,
            link = link,
            pubdate = pubdate,
            unique_id = unique_id,
            categories_cust = categories_cust,
            source = source,
            description = description
                    )
        #handler = SimplerXMLGenerator(outfile, encoding)
        #self.addQuickElement("source", contents=doc['publiction'], attrs="publication")
    
    def add_item_elements(self, handler, item):
        RssFeed.add_item_elements(self, handler, item)
        if item['source'] is not None:
            try:
                handler.addQuickElement(u"source", item["source"], 
                                        {
                                    #u"xmlns:attr_type": u"publication",
                                    #u"domain": "publication",
                                     u"url": BASE_URL
                                        }
                                    )
                #handler.startElement("source", {"ref": "journal"})
                #handler.characters(item["source"])
                #handler.endElement("source")
            except Exception as e:
                errors.RssWriterWarning(e.__repr__(), rss_logger)
        if item['categories_cust'] is not None:
            try:
                for cat in item['categories_cust']:
                    handler.addQuickElement(u"category", cat[1], 
                                    #{u"xmlns:attr_type": cat[0]}
                                    {"domain": cat[0]}
                                    )
                #handler.addQuickElement(u"categoies_cust", item["categories"], {u"ref": })
                #handler.startElement("category", {"ref": "journal_section"})
                #handler.characters(item["category"])
                #handler.endElement("category")
            except Exception as e:
                errors.RssWriterWarning(e.__repr__(), rss_logger)




