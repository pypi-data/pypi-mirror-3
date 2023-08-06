"""
Simple global function for parsing JSON queries containing tokens
"""

import json
import debug

from botnee import debug
from botnee import errors

def json_token_parser(text, verbose=False, logger=None):
    with debug.Timer(None, None, verbose, logger):
        tokens_dict = {}
        
        if len(text) == 0:
            return tokens_dict
        
        try:
            tokens_dict.update(json.loads(text))
        except Exception as e:
            errors.GetRelatedWarning(e.__repr__(), logger)
            #debug.debug_here()
            return tokens_dict
            #return handler500(request)
        
        #debug.debug_here()
        
        for key, value in tokens_dict.items():
            if key[:-1] != "tokens_":
                msg = 'Unknown key [%s] in tokens dict' % key
                errors.GetRelatedWarning(msg, web_logger)
                return tokens_dict
                #return handler500(request)
            
            ngram = int(key[-1])
            
            if ngram == 1:
                # unigrams
                if all(type(x)==unicode for x in value):
                    tokens_dict[key] = [value]
                elif all(type(x)==list for x in value):
                    pass
                else:
                    msg = 'Incorrect type in tokens dict (%d)' % ngram
                    errors.GetRelatedWarning(msg, web_logger)
                    #debug.debug_here()
                    return tokens_dict
                    #return handler500(request)
            else:
                # ngrams
                if all(len(x)==ngram for x in value) and \
                    all(type(y)==unicode for x in value for y in x):
                    tokens_dict[key] = [value]
                elif all(len(y)==ngram for x in value for y in x) and \
                    all(type(z)==unicode for x in value for y in x for z in y):
                    pass
                else:
                    msg = 'Incorrect type in tokens dict (%d)' % ngram
                    errors.GetRelatedWarning(msg, web_logger)
                    #debug.debug_here()
                    return tokens_dict
                    #return handler500(request)
    return tokens_dict

