"""
Reading of standard document files
"""

import os
#import codecs
import io
#import locale
#import sys
import re
import dateutil.parser
import logging

from botnee import debug
from botnee.standard_document import StandardDocument

regular_expressions = {
    "header":   re.compile(r'([^:]*) ?: ?(.*)'),
    "guid":     re.compile(r'[A-Za-z0-9:.\-/_]*'),
    }

#bmj:bmjjournals:adc:65.6.610.archdisch00661-0058
#bmj:bmjjournals:dtb:35.6.47 .1997_June_4

std_doc_logger = logging.getLogger(__name__)

def count_files(
        collector_directory = "/home/tdiethe/BMJ/journal-collector-output/", 
        suffix="txt", verbose=False, recursive=True):
    """
    Simply counts how many standard document files are in the directory
    (and subdirectories if recursive=True)
    """
    count = 0
    if recursive:
        for root, subs, allfiles in os.walk(collector_directory):
            for fname in allfiles:
                if fname.endswith(suffix):
                    count += 1
    else:
        for name in os.listdir(collector_directory):
            if name.endswith(suffix):
                count += 1
    return count

def read_directory(
        collector_directory = "/home/tdiethe/BMJ/journal-collector-output/", 
        suffix="txt", verbose=False, recursive=True):
    """
    Reads a directory - only processes files with the suffix given. 
    Returns a list of dictionary objects
    """
    docs = []
    
    ''' Pull in Standard Doc files'''
    if recursive:
        for root, subs, allfiles in os.walk(collector_directory):
            for fname in allfiles:
                if fname.endswith(suffix):
                    doc = load_document(os.path.join(root, fname), verbose)
                    if doc:
                        #docs.append(doc)
                        yield doc
    else:
        for name in os.listdir(collector_directory):
            if name.endswith(suffix):
                doc = load_document(os.path.join(collector_directory, name), verbose)
                if doc:
                    #docs.append(doc)
                    yield doc
    #return docs

def load_document(fname, verbose=False):
    """Loads a single file in standard document format"""
    #openfile = open(fname, 'r')
    with io.open(fname, "rU", encoding="utf-8") as f:
    #with codecs.open(fname, encoding='utf-8', mode='rU') as f:
        doc = parse_document(f, fname, verbose)
        #print(json.dumps(document))
        f.close()
        
        if doc:
            doc['filename'] = fname
            #debug.print_verbose("Loaded " + fname, verbose)
        else:
            pass
    return doc

def parse_document(input_doc, fname="web request", verbose=False):
    """
    Parses a single document using iterator functionality.
    doc could be a file or a list with a line on each row
    
    required_fields = ['guid', 'url', 'publication-date', 'title']
    
    publication-date must pass through dateutil.parser.parse()
    """
    #debug.print_verbose('parse_document', verbose, std_doc_logger)
    #debug.print_verbose(str(type(input_doc)), verbose)
    in_body = False
    
    if type(input_doc) in [str, unicode]:
        input_doc = input_doc.split('\n')
    elif type(input_doc) is io.TextIOWrapper:
        # do nothing
        pass
    else:
        #debug.print_verbose(type(input_doc), verbose, std_doc_logger)
        debug.debug_here()
        str_error = 'Unexpected input_doc type: ' + str(type(input_doc)) + \
                    ' - can handle text or files'
        debug.print_verbose(str_error, verbose, std_doc_logger)
        #raise errors.StandardDocumentError(str_error)
        return None
    
    #doc = {'body': ''}
    doc = StandardDocument()
    
    for line_num, line in enumerate(input_doc):
        line = line.strip()
        #print line
        #nl += 1
        if(line == ''):
            in_body = True
            continue
        
        if not in_body:
            #print(line)
            s = regular_expressions['header'].split(line)
            #print s[1]
            try:
                if s[1] == u'publication-date':
                    try:
                        doc[s[1]] = dateutil.parser.parse(s[2])
                    except ValueError as e:
                        debug.print_verbose('Unknown date format ' + s[2], 
                                        verbose, std_doc_logger)
                        debug.debug_here()
                        doc['failed'] = {'reason': 'date',
                                         'extra': s[2]}
                        return doc
                elif s[1] == u'guid':
                    guid = regular_expressions['guid'].match(s[2]).group()
                    if ' ' in guid or guid is not s[2]:
                        debug.print_verbose('Error in parsing ' + fname + \
                              ': invalid guid ' + guid, verbose, std_doc_logger)
                        doc['failed'] = {'reason': 'guid',
                                         'extra': guid}
                        #debug.debug_here()
                        return doc
                    doc[s[1]] = guid
                    #debug.print_verbose(guid, verbose, std_doc_logger)
                else:
                    doc[s[1]] = s[2]
            except IndexError as e:
                debug.print_verbose("Error in parsing %s at line %d" % \
                                (fname, line_num), verbose, std_doc_logger)
                try:
                    debug.print_verbose(line, verbose, std_doc_logger)
                except UnicodeEncodeError as e:
                    debug.print_verbose(e, verbose, std_doc_logger)
                doc['failed'] = {'reason': 'bad_line',
                                 'extra': (line_num, line)
                                 }
                #debug.debug_here()
                return doc
        else:
            doc['body'] += " " + line
    
    result =  doc.check_for_failures()
    if result is not None:
        debug.print_verbose('Error in parsing ' + fname + ': missing ' + result,
                        verbose, std_doc_logger)
        #debug.debug_here()
    return doc


