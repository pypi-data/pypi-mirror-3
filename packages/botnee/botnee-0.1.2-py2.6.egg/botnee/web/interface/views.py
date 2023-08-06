# Create your views here.
from django.shortcuts import render_to_response, render
from django import forms #, template
#from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.middleware.gzip import GZipMiddleware
from django.template import RequestContext #, RequestConfig

#from time import time
import datetime

import json
import StringIO
import codecs
import os
from ordereddict import OrderedDict
#from django.core.context_processors import csrf

from botnee import debug
#from botnee.timeout_lock import TimeoutLock
from botnee.filters import Filters
from botnee.get_related import GetRelated
from botnee import rss_writer
#from botnee.standard_document import StandardDocument
from botnee import START_TIME
from botnee.json_token_parser import json_token_parser

from models import engine #, get_related

#import zlib

import botnee_config
#import logging

#web_logger = logging.getLogger(__name__)
from botnee import logger as web_logger

gzip_middleware = GZipMiddleware()

MATRIX_TABLE = None
META_TABLE = None

import django_tables2 as tables
from django_tables2.config import RequestConfig

class BasicTable(tables.Table):
    class Meta:
        attrs = {'class': 'paleblue'}

class SummaryTable(tables.Table):
    name = tables.Column()
    info = tables.Column()
    size = tables.Column()
    sparsity = tables.Column()
    class Meta:
        attrs = {'class': 'paleblue'}

class MatrixTable(tables.Table):
    guid0 = tables.Column()
    guid1 = tables.Column()
    score = tables.Column()
    class Meta:
        attrs = {'class': 'paleblue'}

RETRIEVAL_CHOICES = (('TFIDF', 'TFIDF'), ('BM25', 'BM25'))
QUERY_CHOICES = (('index', 'index'), ('guid', 'guid'), ('text','text'), ('tokens', 'tokens'))

def get_engine_summary(request):
    """
    Gets a summary from the engine, formats as a table, and returns the context
    """
    web_summary = engine.get_summary_as_list()
    
    summary = OrderedDict()
    for key, value in web_summary.items():
        if key == 'META DICT':
            exclude = ['sparsity']
        elif key in ['DATA DICT', 'MATRIX DICT']:
            exclude = []
        else:
            exclude = ['size', 'sparsity']
        
        summary[key] = SummaryTable(value, exclude=exclude)
        summary[key].prefix = key
        RequestConfig(request).configure(summary[key])
    
    #c = {'table': table}
    
    return summary

def home(request, input="No input supplied"):
    context_instance = RequestContext(request)
    c = {'summary': get_engine_summary(request)}
    
#    return render_to_response('home.html', c, context_instance)
    return render(request, 'home.html', c)

def flush(request):
    if request.method == 'POST':
        result = engine.flush(False, botnee_config.VERBOSE)
    else:
        result = [[],[],[]]
    
    c = {
        'output': [
                    'inserts: ' + unicode(result[0]), 
                    'updates: ' + unicode(result[1]), 
                    'deletes: ' + unicode(result[2])
                   ]
        }
    
    return render(request, 'home.html', c)

def recalculate_idf(request):
    engine.recalculate_idf(botnee_config.VERBOSE)
    #c = {'output': engine.get_summary_as_list()}
    #c = {'summary': get_engine_summary(request)}
    c = {'output': ["Done"]}
    
    return render(request, 'home.html', c)

def dump_dictionaries(request):
    c = {'output': engine.dump_dictionaries(botnee_config.VERBOSE)}
    
    return render(request, 'home.html', c)

class QueryForm(forms.Form):
    guid = forms.CharField(max_length=512, required=False)
    index = forms.IntegerField(min_value=0, 
                    max_value=len(engine._meta_dict['guids'])-1, required=False)
    n_results = forms.IntegerField(min_value=1, max_value=1000, initial=20, required=True)
    title_boost = forms.FloatField(min_value=0, max_value=1, required=True, 
                                         initial=botnee_config.TITLE_BOOST)
    abstract_boost = forms.FloatField(min_value=0, max_value=1, required=True, 
                                         initial=botnee_config.ABSTRACT_BOOST)
    date_boost = forms.FloatField(min_value=0, max_value=1, required=True, 
                                         initial=botnee_config.DATE_BOOST)
    ngram_boost = forms.CharField(max_length=128, 
            initial=[v['boost'] for v in botnee_config.NGRAMS.values()], required=False)
    retrieval_type = forms.ChoiceField(choices=RETRIEVAL_CHOICES, 
                                     initial='TFIDF', required=True)
    feed_title = forms.CharField(max_length=512, required=True, 
                                         initial = u"Botnee Feed")
    feed_description = forms.CharField(max_length=1024, required=True, 
                                         initial = u"A Sample Feed")
    feed_url = forms.CharField(max_length=1024, required=True, 
                                        initial = u"http://www.bmjgroup.com")
    title = forms.CharField(max_length=10000, required=False, 
                                                    widget=forms.Textarea)
    abstract = forms.CharField(max_length=100000, required=False, 
                                                    widget=forms.Textarea)
    body = forms.CharField(max_length=1000000, required=False, 
                                                    widget=forms.Textarea)
    filters = forms.CharField(max_length=1000000, required=False, 
                                                    widget=forms.Textarea)
    query_type = forms.ChoiceField(choices=QUERY_CHOICES, initial='text', required=True)

class MatrixForm(forms.Form):
    filters = forms.CharField(max_length=1000000, required=False, 
                                                    widget=forms.Textarea)

class MetaForm(forms.Form):
    filters = forms.CharField(max_length=1000000, required=False,
                                                    widget=forms.Textarea)
    required_fields_only = forms.BooleanField(required=False, initial=True)

class DumpForm(forms.Form):
    input = forms.CharField(required=False, widget=forms.Textarea)
    #inputs = []
    #for i in xrange(100):
    #    inputs.append(forms.CharField(required=False, widget=forms.Textarea)
    def __init__(self, *args, **kwargs):
        super(DumpForm, self).__init__(*args, **kwargs)
        
        for index in xrange(botnee_config.MAX_BATCH_SIZE):
            # generate extra fields in the number specified via extra_fields
            self.fields['input%d' % index] = forms.CharField(required=False)


class ReIndexForm(forms.Form):
    # Simple Form that causes database reindex
    reprocess_docs = forms.BooleanField(required=False, initial=True) 


class DeleteForm(forms.Form):
    guid = forms.CharField(max_length=512, required=True)

#@csrf_exempt
def query(request):
    c = {}
    #c.update(csrf(request))
    context_instance = RequestContext(request)
    
    verbose = botnee_config.VERBOSE
    
    if request.method == 'POST': # If the form has been submitted...
        form = QueryForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            #assert False, botnee_config.VERBOSE
            with debug.Timer('Received web Query', None, verbose, web_logger):
                
                guid = form.cleaned_data['guid'].strip()
                index = form.cleaned_data['index']
                json_object = form.cleaned_data['filters']
                date_boost = form.cleaned_data['date_boost']
                title_boost = form.cleaned_data['title_boost']
                abstract_boost = form.cleaned_data['abstract_boost']
                n_results = form.cleaned_data['n_results']
                
                try:
                    ngram_boost = json.loads(form.cleaned_data['ngram_boost'])
                except:
                    ngram_boost = [v['boost'] for v in botnee_config.NGRAMS.values()]
                
                title = form.cleaned_data['title']
                abstract = form.cleaned_data['abstract']
                body = form.cleaned_data['body']
                
                query_type = form.cleaned_data['query_type']
                
                if query_type == 'tokens':
                    tokens_dict = {}
                    for suffix in botnee_config.SUFFIXES:
                        if suffix.startswith('_'):
                            text = form.cleaned_data[suffix[1:]]
                        else:
                            text = form.cleaned_data['body']
                    tokens_dict.update(json_token_parser(text, verbose, web_logger))
                    
                    debug.print_verbose(tokens_dict, verbose, web_logger)
                
                feed_title = form.cleaned_data['feed_title']
                feed_description = form.cleaned_data['feed_description']
                feed_url = form.cleaned_data['feed_url']
                
                retrieval_type = form.cleaned_data['retrieval_type']
                #print retrieval_type
                
                filters = Filters(json_object, engine._doc_store, True)
                
                get_related = GetRelated(engine, filters, verbose,
                                        title_boost, abstract_boost, date_boost,
                                        retrieval_type, ngram_boost)
                
                scores = None
                idxs = None
                
                if query_type == 'index':
                    c['query'] = "By index: " + str(index)
                    results = get_related.by_index(int(index), n_results, verbose)
                elif query_type == 'guid':
                    c['query'] = "By guid: " + guid
                    results = get_related.by_guid(guid, n_results, verbose)
                #elif len(free_text) > 0:
                #    c['query'] = "By Text: " + free_text
                #    (scores, idxs) = get_related.by_text(
                #                free_text, n_results, True)
                elif query_type == 'text':
                    c['query'] = "By text:\n%s\n\n%s\n\n%s" % (title, abstract, body)
                    results = get_related.by_text(title, abstract, body, n_results, verbose)
                    
                elif query_type == 'tokens':
                    c['query'] = "By tokens:\n%s" % tokens_dict
                    results = get_related.by_tokens(tokens_dict, n_results, verbose)
                    
                else:
                    # All fields empty
                    #c['error'] = "All fields empty"
                    #return render_to_response('query.html', c)
                    return handler500(request)
                
                #(scores, idxs, extra) = results
                if results:
                    scores = results['scores']
                    idxs = results['indices']
                    
                    #print scores, idxs
                    
                    #if scores is not None and idxs is not None:
                    summary = get_related.get_summary_as_list(results, n_results, True)
                    if 'query' in request.POST:
                        c['summary'] = summary
                        c['form'] = form
                        response = render_to_response('query.html', c, context_instance)
                    elif 'rss' in request.POST:
                        feed = rss_writer.write_feed(summary, 
                                                    feed_title, 
                                                    feed_description,
                                                    feed_url,
                                                    c['query'],
                                                    verbose)
                        #return HttpResponse(get_related.get_rss_feed(summary, True))
                        #print feed
                        response = HttpResponse(feed)
                    elif 'text' in request.POST:
                        text_summary = u""
                        inc = ['title', 'guid', 'url', 'publication', 
                                'article_type', 'journal_section']
                        if botnee_config.DEBUG:
                            inc.append('extra')
                        
                        for row in summary:
                            for key, value in row.items():
                                if key in inc:
                                    content = value.replace('<br/>', '\n')
                                    text_summary += "%s:\t%s\n" % (key, content)
                            text_summary += "\n"
                        response = HttpResponse(text_summary.encode('utf-8'), mimetype='text/plain')
                    now = datetime.datetime.now()
                    engine._meta_dict['last_query'] = now.strftime("%Y-%m-%d %H:%M")
                    return response
    else:
        form = QueryForm() # An unbound form
    
    c['form'] = form
    
    return render(request, 'query.html', c)

class StringIOStream(StringIO.StringIO):
    def __init__(self):
        StringIO.StringIO.__init__(self)
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass

#@csrf_exempt
def get_matrix_summary(request):
    c = {}
    global MATRIX_TABLE
    
    context_instance = RequestContext(request)
    
    if request.method == 'POST':
        form = MatrixForm(request.POST)
        c['form'] = form
        if form.is_valid():
            verbose = botnee_config.VERBOSE
            with debug.Timer('Received web matrix request', None,
                            verbose, web_logger):
                
                json_object = form.cleaned_data['filters']
                filters = Filters(json_object, engine._doc_store, True)
                
                rtype = botnee_config.RETRIEVAL_TYPE
                
                get_related = GetRelated(engine, filters, verbose, 0, 0, 0, rtype)
                
                matrix = get_related.get_matrix(verbose)
                
                #text_summary = matrix.__repr__()
                if 'query' in request.POST:
                    response = None
                    #with StringIO.StringIO() as stream:
                    with StringIOStream() as stream:
                        
                        get_related.format_matrix_summary(matrix, stream, verbose)
                        
                        stream.seek(0)
                        summary = stream.read()
                        
                        #debug.debug_here()
                        table_rows = []
                        
                        for line in summary.split('\n'):
                            items = line.split(',')
                            if len(items) == 3:
                                (guid0, guid1, score) = items
                                table_rows.append({'guid0': guid0,
                                                   'guid1': guid1,
                                                   'score': score})
                        
                        table = MatrixTable(table_rows)
                        table.prefix = 'Result'
                        #table.sortable = False
                        #RequestConfig(request).configure(table)
                        
                        c['summary'] = {'RESULT': table}
                        
                        MATRIX_TABLE = table
                        #response = HttpResponse(summary)
                        
                    #return response
                    return render(request, 'matrix.html', c)
                    
                elif 'file' in request.POST:
                    strfile = 'matrix_summary_' + START_TIME + '.txt'
                    fname = os.path.join(botnee_config.LOG_DIRECTORY, strfile)
                    with codecs.open(fname, encoding='utf-8', mode='w') as stream:
                        
                        get_related.format_matrix_summary(matrix, stream, verbose)
                        
                    response = 'Summary saved to: ' + fname
                    
                    return HttpResponse(response)
    else:
        form = MatrixForm()
    
    c['form'] = form
    
    if MATRIX_TABLE:
        c['summary'] = {'RESULT': MATRIX_TABLE}
        RequestConfig(request, paginate=False).configure(MATRIX_TABLE)
    
    return render(request, 'matrix.html', c)

#@csrf_exempt
def meta(request):
    c = {}
    
    global META_TABLE
    context_instance = RequestContext(request)
    
    if request.method == 'POST':
        form = MetaForm(request.POST)
        c['form'] = form
        if form.is_valid():
            verbose = botnee_config.VERBOSE
            with debug.Timer('Received web meta data request', None,
                            verbose, web_logger):
                
                json_object = form.cleaned_data['filters']
                filters = Filters(json_object, engine._doc_store, True)
                
                if not filters.guids:
                    filters.guids = engine._meta_dict['guids'].keys()
                
                flag = form.cleaned_data['required_fields_only']
                
                if flag:
                    docs = engine._doc_store.get_by_guid(filters.guids, verbose=verbose)
                else:
                    fields = {}
                    for suffix in botnee_config.SUFFIXES:
                        for ng in botnee_config.NGRAMS.keys():
                            fields["tokens%s_%d" % (suffix, ng)] = 0
                            fields["term_freq%s_%d" % (suffix, ng)] = 0
                            for mt in botnee_config.MATRIX_TYPES.keys():
                                fields["%s%s_%d" % (mt, suffix, ng)] = 0
                    
                    debug.debug_here()
                    
                    docs = engine._doc_store.get_by_guid(filters.guids, fields, verbose)
                
                #debug.debug_here()
                
                #text_summary = matrix.__repr__()
                text_summary = u""
                
                #fields = botnee_config.REQUIRED_FIELDS
                s = set()
                for doc in docs:
                    s.update(doc.keys())
                fields = sorted(list(s))
                
                table = BasicTable([])
                
                for field in fields:
                    if field == 'url':
                        table.base_columns[field] = tables.URLColumn()
                    elif field not in ['body', '_id', 'operation', 'failed']:
                        table.base_columns[field] = tables.Column()
                
                for field in fields:
                    text_summary += field + ","
                text_summary = text_summary[:-1] + u"\n"
                
                for doc in docs:
                    text_summary += doc.get_summary() + u"\n"
                
                table.data = tables.tables.TableData([dict(doc) for doc in docs], table)
                table.columns = tables.columns.BoundColumns(table)
                table.rows = tables.rows.BoundRows(table.data)
                table.prefix = 'Result'
                META_TABLE = table
                
                c['summary'] = {'RESULT': table}
    
    else:
        form = MetaForm()
    
    c['form'] = form
    
    if META_TABLE:
        c['summary'] = {'RESULT': META_TABLE}
        RequestConfig(request, paginate=False).configure(META_TABLE)
    
    return render(request, 'meta.html', c)

#@csrf_exempt
def dump(request):
    #try:
        #context_instance = RequestContext(request)
        
        verbose = botnee_config.VERBOSE
        
        n_bytes = sum(len(v) for v in request.POST.values())
        msg = 'Received dump request (%d bytes)' % n_bytes
        debug.print_verbose(msg, verbose, web_logger)
        
        def get_std_docs(form_dict):
            with debug.Timer(None, None, verbose, web_logger):
                for key in form_dict.keys():
                    if key.startswith('input') and form_dict[key]:
                        #yield form_dict[key]
                        return form_dict[key]
        
        #time0 = time()
        #print time0
        c = {'output': ""}
        
        if request.method == 'POST':
            form = DumpForm(request.POST)
            c['form'] = form
            if form.is_valid():
                with debug.Timer(None, None, verbose, web_logger):
                    
                    std_docs = (doc for key, doc in form.cleaned_data.items() \
                                        if 'input' in key and doc)
                    
                    #std_docs = (get_std_docs(form.cleaned_data))
                    
                    (inserts, updates, deletes) = engine.insert_standard_docs(
                            std_docs, reindex=False, verbose=verbose)
                    
                    #c['guids']= u''
                    #for guid in inserts + updates:
                    #    c['guids'] += guid + '\n'
                    c['guids'] = [guid for guid in inserts + updates]
                    
                    c['output'] = [
                                    'inserts: ' + unicode(inserts), 
                                    'updates: ' + unicode(updates), 
                                    'deletes: ' + unicode(deletes)
                                   ]
                    
                    #for guid in inserts:
                    #    c['output'] = [u"Inserted: " + guid, "", ""]
                    #for guid in updates:
                    #    c['output'] = [u"Updated: " + guid, "", ""]
                    #for guid in failures:
                    #    c['output'] = [u"Failed: " + guid, "", ""]
                    #return HttpResponse(status=202)
                    
                    #c['output'] += engine.get_summary_as_list(verbose)
                    #c['summary'] = get_engine_summary(request)
                    
                    #for line in c['output']:
                    #    print line
                    
                    engine.check_integrity(verbose=verbose)
                
                return render(request, 'dump_result.html', c)
                #return c['guids']
        else:
            c['form'] = DumpForm() # An unbound form
        return render(request, 'dump.html', c)
        
    #except Exception as e:
    #    print e.__repr__()
    #    debug.debug_here()
    #    raise e
    #    #return render_to_response('dump.html', c, context_instance)

#@csrf_exempt
def delete(request):
    c = {}
    
    #context_instance = RequestContext(request)
    
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        c['form'] = form
        if form.is_valid():
            with debug.Timer('Received web delete request', None,
                                botnee_config.VERBOSE, web_logger):
            
                guid = form.cleaned_data['guid']
                (inserts, updates, deletes) = engine.delete(
                                            [guid], 
                                            reindex=False, 
                                            verbose=botnee_config.VERBOSE)
                
                if len(deletes) == 1:
                    c['output'] = [u"Successfully deleted: " + guid, "", ""]
                else:
                    c['output'] = [u"Unable to delete: " + guid, "", ""]
                
                #c['output'] += engine.get_summary_as_list()
                
                c['summary'] = get_engine_summary(request)
                
                engine.check_integrity()
                
                #for line in c['output']:
                #    print line
            
            return render(request, 'delete.html', c)
    else:
        c['form'] = DeleteForm() # An unbound form
    
    return render(request, 'delete.html', c)

#@csrf_exempt
def force_reindex(request):
    c = {}
    
    #context_instance = RequestContext(request)
    
    if request.method == 'POST':
        form = ReIndexForm(request.POST)
        c['form'] = form
        if form.is_valid():
            verbose=botnee_config.VERBOSE
            #verbose=True
            
            reprocess_docs = form.cleaned_data['reprocess_docs']
            
            with debug.Timer('Received dump request', None,
                    botnee_config.VERBOSE, web_logger) as t:
                
                engine.force_reindex(reprocess_docs, verbose)
                
                #c['output'] = engine.get_summary_as_list()
                #c['summary'] = get_engine_summary(request)
                
                engine.check_integrity()
                
                #for line in c['output']:
                #    try:
                #        debug.print_verbose(line, verbose, web_logger)
                #    except UnicodeEncodeError as e:
                #        errors.BotneeWarning(e.__repr__(), web_logger)
                #        pass
            
            c['output'] = ["Re-index" + t.t_str]
            
            return render(request, 'force_reindex.html', c)
    else:
        c['form'] = ReIndexForm() # An unbound form
    
    return render(request, 'force_reindex.html', c)


def handler500(request):
    if request.method == 'POST':
        form = DumpForm(request.POST)
        if form.is_valid():
            return render_to_response('500.html', {'form': form, 'output': ['Failed', '', form.cleaned_data['input']] }, context_instance)
    #return render_to_response('query.html', {'form': form})
    return home(request)

