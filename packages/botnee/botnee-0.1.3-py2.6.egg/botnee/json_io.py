"""
Reading of JSON files and management of mongodb connection. 
Superceded by the standard_document_io.py module for now.
"""

import codecs
import json
import warnings
import sys
import numpy as np

from botnee import debug

def read_json(fname):
    '''Reads JSON text file (UTF-8)'''
    with codecs.open(fname, encoding='utf-8', mode='rU') as f:
        jtxt = f.read()
        f.close()
    jsplit = jtxt.splitlines()
    jobj = []
    for idx, line in enumerate(jsplit):
        #import pdb; pdb.set_trace()
        #print line.__len__()
        try:
            jobj.append(json.loads(line))
        except ValueError:
            #import pdb; pdb.set_trace()
            print 'Error parsing ' + fname + '(line: ' + str(idx) + ')'
            debug.debug_here()
    return jobj

def get_all_text(jobj):
    '''Takes JSON object and retrieves all text fields'''
    
    '''Deal with empty content'''
    if (not jobj.has_key('content')) or jobj['content'] == []:
        if jobj.has_key('abstract') and jobj['abstract'] != []:
            text = extract_content_from_blocks(jobj['abstract'])
        else:
            if jobj.has_key('article-title'):
                text = jobj['article-title']
            else:
                warnings.warn('Object '+ jobj['_id'].__str__() + ' has no title, abstract, or content!!')
    else:
        text = extract_content_from_blocks(jobj['content'])
    return text

def extract_content_from_blocks(content):
    """Expecting the data to sit in multiple title/paragraph blocks. 
    This simply takes all of the text in the paras and concatenates it."""
    text = ''
    for content_block in content:
        if content_block.__len__() != 1:
            raise Exception('Content block length not 1!')
        if content_block.keys()==['text']:
            text += '\n'+content_block.items()[0][1]
        elif content_block.keys()==['title']:
            # do nothing
            pass
        else:
            warnings.warn('Unexpected content type: ' + content_block.keys())
    return text

def load_text_from_database(connection):
    """Pulls all of the articles down from the database, 
    returns a list where each item is a blob of text"""
    alltext = []
    i = 0
    for article in connection.journals.articles.find():
        text = ''
        print i
        for content_block in article['content']:
            if content_block.__len__() != 1:
                raise Exception('Content block length not 1!')
            if content_block.keys()==['text']:
                text += '\n'+content_block.items()[0][1]
            elif content_block.keys()==['title']:
                # do nothing
                pass
            else:
                warning('Unexpected content type: ' + content_block.keys())
        alltext.append(text)
        i += 1
    return alltext

def save_tokens_to_database(connection, tokens_list):
    """Saves the tokens list into MongoDB"""
    articles = connection.journals.articles.find()
    for i in range(articles.count()):
        sys.stdout.write('.')
        if np.mod(i, 1000)==0:
            sys.stdout.write(i.__str__())
        article = articles[i]

        #article['tokens'] = tokens_list[i]
        #connection.journals.articles.update({'_id': articles[0]['_id']} , article)
        article['tokens'] = tokens_list[i]
        article['_id'] = articles[i]['_id']

        connection.journals.articles.update({'_id': articles[i]['_id']}, article, safe=True)

