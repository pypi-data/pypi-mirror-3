"""
Testing of the Corpus class functions
"""

from time import time
import sys
import hashlib
import os
#import string
import glob

# botnee imports
import botnee
import botnee_config

def test_read_json(test_data):
    try:
        #test_data = {'jobjs': []}
        test_data = []

        prefix = botnee_config.DATA_DIRECTORY + 'test/json/'
        fnames = [  'gutjnl-small-test.txt',
                    'jnnp-small-test.txt',
                    'combined-small-test.txt'  ]

        for fname in fnames:
            fname = prefix + fname
            test_data.append({'jobjs': botnee.corpus.read_json(fname), 'fname': fname})

        # Get ids as dict
        for data in test_data:
            data['meta_dict']['guids'] = {}
            if isinstance(data['jobjs'], dict):
                sys.stdout.write(str(data['jobjs']['id']) + "...")
                data['meta_dict']['guids'][data['jobjs']['id']] = 0
            else:
                for i,jobj in enumerate(data['jobjs']):
                    sys.stdout.write("\n" + str(i) + ":" + str(jobj['id']) + "...")
                    data['meta_dict']['guids'][jobj['id']] = i

            # Check for uniqueness of ids
            assert len(set(data['meta_dict']['guids'].values())) == len(data['meta_dict']['guids'])
            assert len(set(data['meta_dict']['guids'].keys())) == len(data['meta_dict']['guids'])

        '''
        # Get ids as list
        for data in test_data:
            data['meta_dict']['guids'] = []
            for jobj in data['jobjs']:
                data['meta_dict']['guids'].append(jobj['id'])
        assert(len(set(data['meta_dict']['guids'])) == len(data['meta_dict']['guids']))
        '''

        result = len(test_data)==3
    except Exception as e:
        print e

        test_data = None
        result = False
        botnee.debug.debug_here()
    return (result, test_data)


def test_get_all_text(test_data):
    try:
        for data in test_data:
            data['tokens_list'] = []
            for jobj in data['jobjs']:
                text = botnee.corpus.get_all_text(jobj)
                (text, data_dict) = botnee.process.text.process_text(text)
                data['meta_dict']['tokens_list'].append(data_dict['meta_dict']['tokens'])
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)

def test_update(test_data):
    try:
        # This one was removed as it just a wrapper around botnee.process.xxx functions
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)

def test_Corpus(test_data):
    try:
        for data in test_data:
            fname = 'test/hdf5/' + hashlib.md5(str(time())).hexdigest()
            data['corpus'] = botnee.corpus.Corpus(fname)
            data['corpus'].update(data['meta_dict'], data['data_dict'], reindex=True, verbose=True)

            dtmp = data['corpus'].get_dictionary(as_bidict=True)
            assert (dtmp == data['meta_dict']['dictionary'])
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)

def test_merge_corpora(test_data):
    try:
        #for data in test_data:
        #    print [len(x) for x in data['tokens_hash']]
        assert(len(test_data)==3)
        fname = hashlib.md5(str(time())).hexdigest()

        corpus2 = botnee.corpus.Corpus('test/hdf5/' + fname)
        test_data[0]['corpus'].merge(test_data[1]['corpus'], corpus2)

        corpus2_ = test_data[2]['corpus']

        #botnee.debug.debug_here()

        # Test equality of every element
        assert(corpus2.get_dictionary(as_bidict=True) == corpus2_.get_dictionary(as_bidict=True))
        
        tokens_hash2 = corpus2.get_tokens()
        tokens_hash2_ = corpus2_.get_tokens()
        assert(tokens_hash2 == tokens_hash2_)

        ids2 = corpus2.get_guids()
        ids2_ = corpus2_.get_guids()
        assert(ids2 == ids2_)
        
        #print "WE HAVE SOME REORDERING ISSUES!"
        assert([len(x) for x in tokens_hash2] ==  [len(x) for x in tokens_hash2_])
        assert([token for tokens in tokens_hash2 for token in tokens] == [token for tokens in tokens_hash2_ for token in tokens])
        
        tf2  = corpus2.get_sparse_matrix('tf')
        tf2_ = corpus2_.get_sparse_matrix('tf')
        assert(all(tf2.data == tf2_.data))
        assert(all(tf2.indices == tf2_.indices))
        assert(all(tf2.indptr == tf2_.indptr))

        idf2 = corpus2.get_idf()
        idf2_ = corpus2_.get_idf()
        assert(max(idf2[:] - idf2_[:]) < 1e-10)


        #botnee.debug.debug_here()
        # Now create a single corpus
        
        
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)

def test_stress(test_data):
    ''' Stress test of system by merging corpora many times '''

    # Remove all files before we start
    [os.remove(f) for f in glob.glob(botnee_config.DATA_DIRECTORY + "test/hdf5/*.h5")]

    print ""
    print ""
    print "Running stress test with 10 random documents per iteration."
    print "Please indicate how many merge operations to complete: "
    x = -1
    while x==-1:
        try:
            x = int(raw_input())
        except ValueError:
            print 'Invalid Number'

    if x < 1:
        return (True, test_data)

    # nltk used to generate random words
    import nltk
    text_generator = nltk.Text(nltk.corpus.brown.words())
    text_generator.generate()

    # Generate random words
    #import nltk.corpus as nltk_corpus
    #alltext = nltk_corpus.brown.words()
    #tokens = [alltext[random.randrange(len(alltext))] for i in range(0,100)]

    verbose=True
    parallel=False

    try:
        corpus_list = []
        corpus_list.append(botnee.corpus.Corpus('test/hdf5/Merged_corpus_test_0'))
        test_data[0]['corpus'].merge(test_data[1]['corpus'], corpus_list[0])
        #corpus_list.append(test_data[2]['corpus'])
        for i in range(x):
            fname = 'test/hdf5/Merged_corpus_test_' + str(i+1)
            corpus_list.append(botnee.corpus.Corpus(fname))
            # Create a random corpus
            corpus_random = botnee.corpus.Corpus('test/hdf5/Merged_corpus_test_random_data')
            # Randomly generate text
            
            docs = []
            for j in range(10):
                random_string = ''.join([token + ' ' for token in text_generator._trigram_model.generate(100)])
                # Randomly generate ID based on text (hash)
                random_id = hashlib.md5(random_string).hexdigest()
                docs.append({'body': random_string, 'guid': random_id})
            
            
            # Call the process functions
            meta_dict = {}
            data_dict = {}
            botnee.process.text.process_docs(docs, meta_dict, True, verbose, parallel)
            tdict = botnee.process.vector_space_model.vector_space_model(meta_dict, data_dict, True, verbose, parallel)

            
            # Update in pytables
            corpus_random.update(meta_dict, data_dict, reindex=True, verbose=True)
            
            # Perform merge
            corpus_list[0].merge(corpus_random, corpus_list[1])
            
            # Delete the old object
            corpus_list[0].close()
            del corpus_list[0]
            # And remove it from disk too:
            os.remove(botnee_config.DATA_DIRECTORY + fname + "_corpus_table.h5")
            
            # And the same with the random object
            corpus_random.close()
            del corpus_random
            os.remove(botnee_config.DATA_DIRECTORY + "test/hdf5/Merged_corpus_test_random_data_corpus_table.h5")
        
        #botnee.debug.debug_here()
        result = True
    except Exception as e:
        print e
        
        result = False
        botnee.debug.debug_here()
    finally:
        # Make sure the directory is clean
        [os.remove(f) for f in glob.glob(botnee_config.DATA_DIRECTORY + "test/hdf5/*.h5")]
    return (result, test_data)


