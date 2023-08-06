#!/usr/bin/env python
"""
Class for providing functionality to retrieve documents.
Has hooks into the main botnee engine. 
Capable of outputting as raw text, lists of dictionaries, or RSS
"""

#import h5py
import numpy
#import tables
from scipy import sparse
from sklearn import preprocessing

#import files
import bson
import logging
import datetime

#from bidict import bidict

from botnee import debug, errors

from botnee.process.vector_space_model import vector_space_model
from botnee.process.text import process_raw_text, process_raw_tokens
from botnee.process.meta_dict import MetaDict
from botnee.process.time_dict import TimeDict
#from botnee.process.matrix_dict import MatrixDict
from botnee.engine import Engine
#from botnee import rss_writer
from botnee.filters import Filters

import botnee_config

class GetRelated(object):
    """
    Class to perform queries.
    Instantiate with engine and a set of guids for the query.
    If guids is None, then all guids will be used.
    """
    def __init__(self, engine, filters=None, verbose=False, 
                    title_boost = 0, abstract_boost = 0, date_boost = 0,
                    retrieval_type = botnee_config.RETRIEVAL_TYPE,
                    ngram_boost = [v['boost'] for v in botnee_config.NGRAMS.values()]):
        """
        Initialisation. guids can be None, in which case 
        engine._meta_dict['guids'].keys() will be used
        """
        self.logger = logging.getLogger(__name__)
        
        if type(engine) is not Engine:
            raise TypeError("Expected Engine got " + str(type(engine)))
        
        with debug.Timer(None, None, verbose, self.logger):
            self._engine = engine
            self.set_filters(filters, verbose)
            
            self.title_boost = float(title_boost)
            self.abstract_boost = float(abstract_boost)
            self.date_boost = float(date_boost)
            self.ngram_boost = list(ngram_boost)
            
            if retrieval_type not in ['TFIDF', 'BM25']:
                msg = "Incorrect retrieval type specified" + retrieval_type
                raise errors.GetRelatedError(msg)
            
            self.retrieval_type = retrieval_type
            
            self.get_dates = self._engine._doc_store.get_dates
    
    def set_filters(self, filters, verbose=False):
        """
        Takes a Filters object and sets filters for retrieval
        """
        
        if filters is None:
            msg = "No filters set, using defaults from botnee_config.py"
            self.filters = Filters(None, self._engine._doc_store, verbose)
        else:
            if type(filters) is Filters:
                self.filters = filters
            else:
                raise TypeError("Expected Filters got " + str(type(filters)))
                self.filters = Filters(None, self._engine._doc_store, verbose)
        
        self.filters.print_summary(verbose)
    
    def get_valid_indices(self, verbose=True):
        """
        Gets the indices for the query using the guids stored in memory
        """
        with debug.Timer(None, None, verbose, self.logger):
            if self.filters.guids:
                valid_indices = [self._engine._meta_dict['guids'][guid]\
                                for guid in self.filters.guids]
            else:
                valid_indices = self._engine._meta_dict['guids'].values()
            
            if valid_indices is None or len(valid_indices)==0:
                msg = 'No valid indices'
                errors.GetRelatedWarning(msg, self.logger)
                return None
            
            return sorted(valid_indices)
    
    def calculate_similarity(self, source_indices, prefix="", target_index=0, verbose=False):
        """
        Calculate similarity.
        source_indices references into TF/TFIDF matrix
        """
        matx_dict = self._engine._matx_dict
        data_dict = self._engine._data_dict
        
        def get_data(suffix="", idf_method="", ngstr="_1"):
            msg = "(%s%s)" % (suffix, ngstr)
            
            with debug.Timer(msg, None, verbose, self.logger):
                if prefix + 'tfidf' + ngstr in matx_dict:
                    full_name = prefix + 'tfidf' + ngstr
                    col = matx_dict[full_name][target_index].transpose()
                    coln = sparse.csc_matrix(col, dtype=float)
                    
                    if suffix != "":
                        full_name_suf = prefix + 'tfidf' + suffix + ngstr
                        suf  = matx_dict[full_name_suf][target_index].transpose()
                        if suf is None or suf.nnz == 0:
                            msg = full_name_suf + ' empty, using body instead'
                            debug.print_verbose(msg, verbose, self.logger)
                            sufn = coln
                        else:
                            sufn = sparse.csc_matrix(suf, dtype=float)
                    else:
                        sufn = None
                    
                    mat = matx_dict['tfidf' + suffix + ngstr][source_indices,:]
                    matn = sparse.csc_matrix(mat, dtype=float)
                    
                    return coln, sufn, matn, None
                
                full_name = prefix + 'tf' + ngstr
                
                col = matx_dict[full_name][target_index].transpose()
                coln = sparse.csc_matrix(col, dtype=float)
                
                if suffix != "":
                    full_name_suf = prefix + 'tf' + suffix + ngstr
                    suf  = matx_dict[full_name_suf][target_index].transpose()
                    if suf is None or suf.nnz == 0:
                        msg = full_name_suf + ' empty, using body instead'
                        debug.print_verbose(msg, verbose, self.logger)
                        sufn = coln
                    else:
                        sufn = sparse.csc_matrix(suf, dtype=float)
                else:
                    sufn = None
                
                mat = matx_dict['tf' + suffix + ngstr][source_indices,:]
                
                idf = data_dict['idf' + idf_method + ngstr]
                
                matn = sparse.csc_matrix(mat, dtype=float)
                idfn = sparse.csr_matrix(idf, dtype=float)
                
                return coln, sufn, matn, idfn
        
        def tfidf(column, matrix, idf, suffix=""):
            with debug.Timer(suffix, None, verbose, self.logger):
                locs = column.nonzero()[0]
                vecs = numpy.zeros(matrix.shape[0], dtype=float)
                #if not locs:
                if len(locs) == 0:
                    return vecs
                
                mats = matrix[:,locs]
                
                if idf is None:
                    # Assume that TFIDF is precalculated
                    cols = column[locs]
                    vecs = mats * cols
                    return vecs.toarray().ravel()
                
                if idf.shape[1] == 1:
                    idfs = idf[locs].toarray() .ravel()
                else:
                    idfs = idf[:,locs].toarray().ravel()#.transpose()
                #cols.data *= idfs.data
                
                
                if botnee_config.NORMALISE:
                    if len(locs) == 1:
                        mats = preprocessing.normalize(mats, norm='l2', 
                                axis=int(mats.shape[0] == 1), copy=False)
                        vecs = mats.toarray().ravel()
                        #debug.debug_here()
                    else:
                        cols = column[locs]
                        try:
                            cols.data *= idfs
                            cols = preprocessing.normalize(cols, norm='l2', 
                                        axis=int(cols.shape[0] == 1), copy=False)
                            for i, row in enumerate(mats):
                                debug.print_dot(i, verbose)
                                rowi = sparse.csc_matrix(row.toarray() * idfs)
                                
                                rowi = preprocessing.normalize(rowi, norm='l2', 
                                            axis=int(rowi.shape[0] == 1), copy=False)
                                #vecs[i] = rowi * cols
                                res = (rowi * cols).toarray().ravel()
                                assert len(res) == 1
                                vecs[i] = res[0]
                        except Exception as e:
                            errors.GetRelatedWarning(e.__repr__(), self.logger)
                
                else:
                    cols = column[locs].toarray().ravel()
                    cols *= numpy.power(idfs, 2)
                    vecs = mats * cols
                
                #return vecs#vec.toarray().ravel()
                return vecs.toarray().ravel()
        
        def bm25(column, matrix, idf, suffix=""):
            with debug.Timer(suffix, None, verbose, self.logger):
                try:
                    locs = column.nonzero()[0]
                    #if not locs:
                    if len(locs) == 0:
                        return numpy.zeros(matrix.shape[0], dtype=float)
                    cols = column[locs].toarray().ravel()
                    if idf.shape[1] == 1:
                        idfs = idf[locs].toarray() .ravel()
                    else:
                        idfs = idf[:,locs].toarray().ravel()#.transpose()
                    #cols.data *= idfs.data
                    
                    lengths = numpy.array(doc_store.get_tokens_count(locs.tolist(), suffix, verbose))
                    avdl = numpy.mean(lengths)
                    
                    b = 0.75
                    k = 1.6
                    
                    mats = matrix[:,locs]
                    
                    numerator = (mats * (k+1)).toarray()
                    denominator = numpy.array(mats + k * (1 - b + (b * lengths / avdl)))
                    #vecs = numpy.array(numerator/denominator).ravel()
                    vecs = numpy.sum(numerator/denominator, axis=1)
                    
                    if len(vecs) != len(indices):
                        debug.debug_here()
                    
                except Exception as e:
                    errors.GetRelatedWarning(e.__repr__(), self.logger)
                    return numpy.zeros(matrix.shape[0], dtype=float)
                
                return vecs
        
        msg = "Date boost %.2f\tTitle boost %.2f\tAbstract boost %.2f" % \
                (self.date_boost, self.title_boost, self.abstract_boost)
        msg += "\tNGRAM boost " + str(self.ngram_boost)
        msg += "\tRetrieval Type " + self.retrieval_type
        
        doc_store = self._engine._doc_store
        
        result = {}
        
        with debug.Timer(msg, None, verbose, self.logger):
            if self.retrieval_type in ['TFIDF', 'BM25']:
                if self.retrieval_type == 'TFIDF':
                    idf_method = ""
                    sim_func = tfidf
                else:
                    idf_method = "_bm25"
                    sim_func = bm25
                
                result['final'] = numpy.zeros(len(source_indices), dtype=float)
                #result['final'] = sparse.csc_matrix((len(indices),1), dtype=float)
                
                for i, ngram in enumerate(botnee_config.NGRAMS.keys()):
                    ngstr = '_%d' % ngram
                    
                    res = get_data("", idf_method, ngstr)
                    
                    #vec = sim_func(res[0], res[2], res[3], "") * ngram
                    vec = sim_func(res[0], res[2], res[3], "") * self.ngram_boost[i]
                    
                    result['coln' + ngstr] = res[0]
                    result['sufn' + ngstr] = res[1]
                    result['matn' + ngstr] = res[2]
                    result['idfn' + ngstr] = res[3]
                    
                    result['vec' + ngstr] = vec
                    try:
                        result['final'] = result['final'] + vec
                    except:
                        debug.debug_here()
                    
                #vec_orig = vec.copy()
                dvn = numpy.zeros(len(source_indices), dtype=float)
                #dvn = sparse.csc_matrix((len(indices),1), dtype=float)
                title_vec = numpy.zeros(len(source_indices), dtype=float)
                #title_vec = sparse.csc_matrix((len(indices),1), dtype=float)
                
                if self.title_boost > 0:
                    for ngram in botnee_config.NGRAMS.keys():
                        ngstr = '_%d' % ngram
                        title_data = get_data("_title", idf_method)
                        title_vec = sim_func(title_data[1], title_data[2], title_data[3], "_title")
                    
                    result['title_vec'] = title_vec
                    result['final'] = result['final'] * (1 - self.title_boost)
                    result['final'] = result['final'] + title_vec * self.title_boost
                
                if self.date_boost > 0:
                    result = self.get_dates(self.filters.guids, verbose)
                    
                    date_vec = numpy.zeros(len(source_indices), dtype=float)
                    
                    for idx, (target_index, dateval) in enumerate(result):
                        date_vec[idx] = dateval.toordinal()
                    
                    #newest_date = max(date_vec) #date_vec[0]
                    #oldest_date = min(date_vec) #date_vec[-1]
                    
                    today = datetime.date.today()
                    
                    newest_date = today.toordinal()
                    oldest_date = datetime.date(today.year-10, 
                                                today.month,
                                                today.day).toordinal()
                    
                    date_vec -= oldest_date
                    date_vec /= newest_date
                    
                    dvn = sparse.csr_matrix(numpy.power(date_vec, 1))
                    dvn = preprocessing.normalize(dvn, norm='l2', axis=1, copy=False).toarray().ravel()
                    
                    result['date_vec'] = dvn
                    result['final'] = result['final'] * (1 - self.date_boost)
                    result['final'] = result['final'] + dvn * self.date_boost
                
                return result
    
    def get_matrix(self, verbose=False):
        ''' 
        return the similarity matrix for the given guids 
        SLOW VERSION: Uses existing similarity code in a loop. Would be much 
        faster to do matrix multiplication (TODO)
        '''
        
        with debug.Timer(None, None, verbose, self.logger):
            
            valid_indices = self.get_valid_indices()
            n = len(valid_indices)
            
            matrix = numpy.zeros((n,n), dtype=float)
            
            try:
                for ngram, ngdict in botnee_config.NGRAMS.items():
                    ngstr = "_%d" % ngram
                    
                    boost = ngdict['boost']
                    
                    mats = self._engine._matx_dict['tfidf' + ngstr][valid_indices,:]
                    
                    # randomly project??
                    
                    # inner product matrix
                    #debug.debug_here()
                    M = mats * mats.transpose() * boost
                    matrix += M.toarray()
                    
                
            except Exception as e:
                errors.GetRelatedWarning(e.__repr__(), self.logger)
                
                for i in valid_indices:
                    debug.print_dot(i, verbose)
                    result = self.calculate_similarity(valid_indices, "", i, verbose)
                    
                    vec = result['final']
                    matrix[i,:] = vec
            
            return matrix
    
    def by_guid(self, guid, num_results=10, verbose=False):
        ''' return the top n documents according to guid '''
        #self.filters.print_summary(verbose)
        
        with debug.Timer(None, None, verbose, self.logger):
            msg = "Top %d docs related to: %s" % (num_results, guid)
            debug.print_verbose(msg, verbose, self.logger)
            try:
                return self.by_index(self._engine._meta_dict['guids'][guid], 
                                     num_results, verbose)
            except KeyError:
                print "Document ID " + guid + " not found!"
                print self._engine._meta_dict['guids'][guid]
                #return (None, None, None, None) #(numpy.zeros(num_results), range(num_results))
                return {}
    
    def _pseudo_related(self, pseudo_meta_dict, pseudo_time_dict, num_results=10, verbose=False):
        """
        Performs releatedness query using pseudo_meta_dict and pseudo_time_dict,
        called by by_text, by_tokens, or by_tokens
        """
        
        with debug.Timer(None, None, verbose, self.logger):
            reindex = False
            try:
                vector_space_model(pseudo_meta_dict, self._engine._data_dict, 
                                self._engine._matx_dict, 
                               pseudo_time_dict, self._engine._doc_store, 
                               reindex, self._engine._job_server, verbose)
            except errors.ProcessError as e:
                errors.GetRelatedWarning(e.__repr__(), self.logger)
                #debug.debug_here()
                #raise e
                return {}
            
            valid_indices = self.get_valid_indices(verbose)
            if not valid_indices:
                return {}
            
            try:
                result = self.calculate_similarity(valid_indices, "pseudo_", 0, verbose)
            except Exception as e:
                errors.GetRelatedWarning(e.__repr__(), self.logger)
            #    debug.debug_here()
                return {}
            
            indices = numpy.argsort(result['final'], axis=0)[::-1]
            scores = result['final'][indices]
            
            zeros = numpy.argwhere(scores==0).ravel()
            if len(zeros) > 0:
                first_zero = zeros[0]
                
                if first_zero < num_results + 1:
                    msg = 'Only %d positive results' % (first_zero)
                    debug.print_verbose(msg, verbose, self.logger)
                    num_results = first_zero - 1
            
            rng = range(0, num_results)
            
            result['scores'] = scores[rng,].ravel()
            result['indices'] = indices[rng,].ravel()
            
            for ngstr in ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
                result['scores' + ngstr] = result['vec' + ngstr][indices][rng,].ravel()
            
            for sub_res in ['title', 'abstract', 'date']:
                if sub_res + '_scores' in result:
                    result[sub_res + '_scores'] = \
                        result[sub_res + '_vec'][indices][rng,].ravel()
            
            try:
                result['indices'] = numpy.array(valid_indices)[indices]
            except Exception as e:
                raise errors.GetRelatedError(str(e), self.logger)
            
            msg = "Scores: " + str(result['scores'])
            debug.print_verbose(msg, verbose, self.logger)
            msg = "Indices: " + str(result['indices'])
            debug.print_verbose(msg, verbose, self.logger)
            
            return result

    
    
    def by_text(self, title, abstract, body, num_results=10, verbose=False):
        ''' return the top n documents according to input text '''
        #self.filters.print_summary(verbose)
        
        #pdoc, pdata = process.process_pseudo_doc(meta_dict, data_dict, text)
        with debug.Timer(None, None, verbose, self.logger):
            pseudo_meta_dict = MetaDict({}, verbose, False)
            pseudo_time_dict = TimeDict()
            process_raw_text(title, abstract, body, 
                                   self._engine._meta_dict, 
                                   self._engine._data_dict, 
                                   pseudo_meta_dict, verbose)
            
            return self._pseudo_related(pseudo_meta_dict, pseudo_time_dict, num_results, verbose)
    
    def by_tokens(self, tokens_dict, num_results=10, verbose=False):
        ''' return the top n documents according to input tokens dict '''
        
        with debug.Timer(None, None, verbose, self.logger):
            pseudo_meta_dict = MetaDict({}, verbose, False)
            pseudo_time_dict = TimeDict()
            process_raw_tokens(tokens_dict, 
                                   self._engine._meta_dict, 
                                   self._engine._data_dict, 
                                   pseudo_meta_dict, verbose)
            
            return self._pseudo_related(pseudo_meta_dict, pseudo_time_dict, num_results, verbose)
    
    def by_index(self, index, num_results=10, verbose=False):
        ''' return the top n documents according to index'''
        #self.filters.print_summary(verbose)
        
        with debug.Timer(None, None, verbose, self.logger):
            str_rel = "Top %d docs related to: %d" % (num_results, index)
            debug.print_verbose(str_rel, verbose, self.logger)
            # Load in the tfidf matrix
            #tfidf = files.load_tfidf()
            
            # calculate inner product
            #v = numpy.inner(tfidf, tfidf[index].transpose())
            if index < 0 or index >= self._engine._meta_dict['n_docs']:
                debug.print_verbose('Index out of range', verbose, self.logger)
                return None
            
            valid_indices = self.get_valid_indices()
            if not valid_indices:
                return None
            
            num_results = min(num_results, len(valid_indices)-1)
            
            #vec = tfidf * tfidf[index].transpose()
            result = self.calculate_similarity(valid_indices, "", index, verbose)
            #(vec, vec_orig, title_vec, date_vec, coln, sufn) = result
            
            # sort
            indices = numpy.argsort(result['final'], axis=0)[::-1]
            scores = result['final'][indices]
            
            zeros = numpy.argwhere(scores==0).ravel()
            if len(zeros) > 0:
                first_zero = zeros[0]
                
                if first_zero < num_results + 1:
                    msg = 'Only %d positive results' % (first_zero)
                    debug.print_verbose(msg, verbose, self.logger)
                    num_results = first_zero - 1
            
            rng = range(1, num_results + 1)
            
            result['scores'] = scores[rng,].ravel()
            result['indices'] = indices[rng,].ravel()
            
            for ngstr in ["_%d" % ng for ng in botnee_config.NGRAMS.keys()]:
                result['scores' + ngstr] = result['vec' + ngstr][indices][rng,].ravel()
            
            for sub_res in ['title', 'abstract', 'date']:
                if sub_res + '_scores' in result:
                    result[sub_res + '_scores'] = \
                        result[sub_res + '_vec'][indices][rng,].ravel()
            
            try:
                result['indices'] = numpy.array(valid_indices)[indices]
            except Exception as e:
                raise errors.GetRelatedError(str(e), self.logger)
            #bscores = vec_orig[indices][0:num_results,].ravel()
            #tscores = title_vec[indices][0:num_results,].ravel()
            #dscores = date_vec[indices][0:num_results,].ravel()
            
            msg = "Scores: " + str(result['scores'])
            debug.print_verbose(msg, verbose, self.logger)
            msg = "Indices: " + str(result['indices'])
            debug.print_verbose(msg, verbose, self.logger)
            
            #extra = (bscores, tscores, dscores, coln, sufn)
            
            return result #(scores, indices, extra)

    
    def format_matrix_summary(self, matrix, stream, verbose=False):
        """
        Takes the values of the matrix and formats them for the screen or file
        summary is a stream object (file or string)
        """
        with debug.Timer(None, None, verbose, self.logger):
            valid_indices = self.get_valid_indices()
            
            # Title line
            #summary = ","
            #for i in valid_indices:
            #    summary += ",%d" % i
            #summary += "\n"
            
            guids = self._engine._meta_dict['guids']
            
            #debug.debug_here()
            
            #for i in valid_indices:
            for i, indexi in enumerate(valid_indices):
                debug.print_dot(i, verbose)
                
                guidi = guids[:indexi]
                
                #summary += "%d,%s" % (i, guid)
                
                for j, indexj in enumerate(valid_indices):
                    #if i < j:
                    #    continue
                    guidj = guids[:indexj]
                    
                    item = u"%s,%s,%.8f" % (guidi, guidj, matrix[i,j])
                    #print item
                    
                    stream.write(item + "\n")
    
    def print_summary(self, score, index, num_results=10, verbose=False):
        """
        Prints the list of dictionaries to the screen
        """
        summary = self.get_summary_as_list(score, index, num_results)
        print_verbose(self.format_summary(summary), verbose, self.logger)
        summary = [
                "%20s: %.2f" % ("Title boost", self.title_boost),
                "%20s: %.2f" % ("Abstract boost", self.abstract_boost),
                "%20s: %.2f" % ("Date boost", self.date_boost)
                        ]
        for item in summary:
            debug.print_verbose(item, verbose, self.logger)
    
    def format_summary(self, summary):
        """
        Takes a summary as a list of dictionaries and returns a formatted string
        """
        string = ''
        for atom in summary:
            for (key,value) in atom.iteritems():
                if key in ['failed', 'operation','tokens']:
                    continue
                try:
                    string = string + key + ": " + str(value) + '\n'
                except Exception as e:
                    if type(value) is bson.ObjectId:
                        pass
                    print type(key), type(value)
                    print key, value
                    pass
            string = string + '\n'
        return string
    
    
    def get_summary_as_list(self, results, num_results=10, verbose=False):
        """
        Returns a list of dictionaries of results
        """
        summary = []
        
        #(scores, idxs, extra) = results
        
        #(bscores, tscores, dscores, coln, sufn) = extra
        
        scores = results['scores']
        idxs = results['indices']
        
        for i, score in enumerate(scores):
            if i >= num_results:
                break
            
            index = idxs[i]
            #bscore = bscores[i]
            #tscore = tscores[i]
            #dscore = dscores[i]
            
            #with debug.Timer(None, None, verbose, self.logger):
            fields={'_id':1, 'title':1, 'url':1, 
                    'publication': 1, 'publication-date': 1,
                    'journal_section': 1, 'article_type': 1,
                    }
            
            for ngram in botnee_config.NGRAMS.keys():
                ngstr = '_%d' % ngram
                fields.update({
                        'tf' + ngstr: 1,
                        'tf_title' + ngstr: 1,
                        })
            
            try:
                guid = self._engine._meta_dict['guids'][:index]
            except KeyError as e:
                raise e
            except TypeError as e:
                raise e
            
            doc = self._engine._doc_store.get_by_guid(guid, fields)[0]
            
            doc['extra'] = u""
            doc['extra'] += "<br/>GUID: %s"         % guid
            doc['extra'] += "<br/>Publication: %s"  % doc['publication']
            doc['extra'] += "<br/>Section: %s"      % doc['journal_section']
            doc['extra'] += "<br/>Article Type: %s" % doc['article_type']
            doc['extra'] += "<br/>Total Score %6f"  % score
            
            
            if botnee_config.DEBUG:
                for ngram in botnee_config.NGRAMS.keys():
                    ngstr = '_%d' % ngram
                    doc['extra'] += "<br/>&nbsp;NGRAM %d" % ngram
                    doc['extra'] += "<br/>&nbsp;Score %.6f" % (results['scores' + ngstr][i])
                    
                    for sub_res in ['title', 'abstract', 'date']:
                        if sub_res + '_score' in results:
                            doc['extra'] += "<br/>&nbsp;%s %.6f" % \
                                (sub_res.title(), results[sub_res + '_score'][i])
                    #(score, bscore[ngram-1], tscore, dscore)
                    
                    coln = results['coln' + ngstr]
                    idfn = results['idfn' + ngstr]
                    
                    top_tf = self.get_top_terms(doc, '', ngram, coln, idfn)
                    doc['extra'] += "<br/>&nbsp;Top terms (body): %s" % str(top_tf)
                    
                    if self.title_boost > 0.0:
                        coln = results['sufn' + ngstr]
                        top_tf_title = self.get_top_terms(doc, '_title', ngram, coln, idfn)
                        doc['extra'] += "<br/>&nbsp;Top terms (title): %s" % str(top_tf_title)
                    
                    if self.abstract_boost > 0.0:
                        coln = results['sufn' + ngstr]
                        top_tf_abstract = self.get_top_terms(doc, '_abstract', ngram, coln, idfn)
                        doc['extra'] += "<br/>&nbsp;Top terms (abstract): %s" % str(top_tf_abstract)
            
            summary.append(doc)
            
        return summary
    
    def get_top_terms(self, doc, suffix, ngram, coln, idfn):
        ngstr = "_%d" % ngram
        #dictionary = self._engine._meta_dict['dictionary']
        guids = self._engine._meta_dict['guids']
        tokens_map_inv = self._engine._meta_dict['tokens_map_inv' + ngstr]
        
        doc_store = self._engine._doc_store
        
        if idfn is None:
            # Assume tfidf is precalculated
            idfn = self._engine._data_dict['idf' + ngstr]
        else:
            idfn = idfn.toarray().ravel()
        
        #tfd = doc['tf' + suffix + ngstr]['data']
        tfd = numpy.array(doc['tf' + suffix + ngstr]['data'], dtype=float).ravel()
        tfi = doc['tf' + suffix + ngstr]['indices']
        if any(tfd) and coln is not None:
            # mask out terms not in column
            #tfd *= coln[tfi].toarray().ravel()
            coln_div = coln/coln
            tfd *= coln_div[tfi].toarray().ravel()
        
        stf = numpy.argsort([tfd]).ravel()[::-1]
        
        max_items = min(len(tfd.nonzero()[0]), 10)
    
        #debug.debug_here()
        
        #numpy.log(n_docs/tf[:,551].sum())
        #numpy.log(n_docs/tf[:,10544].sum())
        #numpy.log(n_docs/tf[:,35639].sum())
        
        rlist = []
        for i in range(0, max_items):
            try:
                rlist.append((tokens_map_inv[tfi[stf[i]]], \
                        "%d, %.2f" % (tfd[stf[i]], idfn[tfi[stf[i]]]) ))
            except Exception as e:
                errors.GetRelatedWarning(e.__repr__(), self.logger)
        
        #debug.debug_here()
        return rlist
