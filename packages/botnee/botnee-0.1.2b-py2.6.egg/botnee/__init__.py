#!/usr/bin/env python
"""This is the botnee package. You can run unit tests by running 
the package from the command line, e.g.:

$ python botnee

or in ipython:

>>> run botnee/__init__.py

The package is structured as follows:
------------------------------------
::

 botnee
    \- botnee_config             Configuration file
    \- debug                     some debugging helpers
    \- doc_store                 DocStore class, which deals with the mongodb meta data collection
    \- engine                    Main entry point - connects to databases and loads files
    \- errors                    Custom error handlers
    \- filters                   Class to apply filters to retrieved results
    \- get_related               Functions to retrieve related content by id, index or free text
    \- json_io                   reading of JSON files and management of mongodb connection
    \- process                   main processing engine
    |   \- data_dict                 Wrapper around standard dict for data_dict variable
    |   \- meta_dict                 Wrapper around standard dict for meta_dict variable
    |   \- text                  text processing
    |   \- vector_space_model    TF-IDF etc
    \- rss_writer                Simple RSS writer that uses WebHelpers Rss201rev2Feed
    \- standard_document_io      reading of standard document files
    \- test
    |   \- test_corpus           unit testing for the Corpus class
    |   \- test_process          unit testing for the process module
    |   \- test_standard_document_io
    |   \- test_json_io
    \- timeoutLock               class for timeout locking
    \- timer                     useful timing functions
    \- web
    |   \- manage                django management interface for web interface to botnee
    |   \- settings              django settings file
    |   \- urls                  sets up active urls
    |   \- interface
    |   |   \- models            initial loading in of data structures
    |   |   \- tests             unit tests
    |   |   \- views             code to manage view interaction (form submission etc)
    |   \- templates             html templates (landing pages)


External dependencies
---------------------
::

    IPython 
      \-Debugger 
        \-Tracer (botnee.search,botnee.debug)
    bidict (botnee.persistent_dict)
      \-bidict (botnee.process.meta_dict,botnee.doc_store,botnee.process.text,botnee.process.matrix_dict,botnee.process.vector_space_model,botnee.doc_manager_store,botnee.process.data_dict,botnee.corpus)
      \-inverted (botnee.corpus)
    botnee 
      \-START_TIME (botnee.engine)
      \-corpus 
      | \-Corpus (botnee.engine)
      \-doc_manager_store 
      | \-DocManagerStore (botnee.engine)
      \-doc_store 
      | \-DocStore (botnee.process.text,botnee.engine,botnee.process.vector_space_model)
      \-engine 
      | \-Engine (botnee.web.interface.models,botnee.get_related)
      \-get_related 
      | \-GetRelated (botnee.web.interface.models)
      \-persistent_dict 
      | \-PersistentDict (botnee.process.data_dict,botnee.process.meta_dict,botnee.process.matrix_dict)
      \-process 
      | \-data_dict 
      | | \-DataDict (botnee.process.text,botnee.corpus,botnee.engine,botnee.process.vector_space_model)
      | \-matrix_dict 
      | | \-MatrixDict (botnee.get_related,botnee.engine,botnee.process.vector_space_model)
      | \-meta_dict 
      | | \-MetaDict (botnee.process.text,botnee.corpus,botnee.get_related,botnee.engine,botnee.process.vector_space_model)
      | \-text 
      | | \-process_docs (botnee.engine)
      | | \-process_raw_text (botnee.get_related)
      | \-time_dict 
      | | \-TimeDict (botnee.process.text,botnee.corpus,botnee.get_related,botnee.engine,botnee.process.vector_space_model)
      | \-vector_space_model 
      |   \-vector_space_model (botnee.get_related,botnee.engine)
      \-standard_document 
      | \-StandardDocument (botnee.standard_document_io,botnee.doc_store,botnee.process.text,botnee.engine,botnee.doc_manager_store)
      \-timeout_lock 
      | \-TimeoutLock (botnee.web.interface.views,botnee.engine)
      \-web 
        \-interface 
          \-models 
            \-engine (botnee.web.interface.views)
            \-get_related (botnee.web.interface.views)
    bson (botnee.doc_store,botnee.get_related,botnee.doc_manager_store)
      \-code 
        \-Code (botnee.doc_store,botnee.doc_manager_store)
    dateutil 
      \-parser (botnee.standard_document_io)
    django 
      \-conf 
      | \-urls 
      |   \-defaults 
      |     \-include (botnee.web.urls)
      |     \-patterns (botnee.web.urls)
      |     \-url (botnee.web.urls)
      \-contrib 
      | \-admin (botnee.web.urls)
      \-core 
      | \-management 
      |   \-execute_manager (botnee.web.manage)
      \-db 
      | \-models (botnee.web.interface.models)
      \-forms (botnee.web.interface.views)
      \-http 
      | \-HttpResponse (botnee.web.interface.views)
      \-middleware 
      | \-gzip 
      |   \-GZipMiddleware (botnee.web.interface.views)
      \-shortcuts 
      | \-render_to_response (botnee.web.interface.views)
      \-template (botnee.web.interface.views)
      \-test 
      | \-TestCase (botnee.web.interface.tests)
      \-views 
        \-decorators 
          \-csrf 
            \-csrf_exempt (botnee.web.interface.views)
    itertools 
      \-groupby (botnee.process.vector_space_model)
    nltk (botnee.test.test_corpus)
    numpy (botnee.doc_store,botnee.process.text,botnee.engine,botnee.process.matrix_dict,botnee.process.vector_space_model,botnee.search,botnee.persistent_dict,botnee.json_io,botnee.filter_results,botnee.process.data_dict,botnee.corpus,botnee.get_related,botnee.debug)
    ordereddict (botnee.persistent_dict)
      \-OrderedDict (botnee.process.time_dict,botnee.standard_document,botnee.process.meta_dict,botnee.process.text,botnee.process.matrix_dict,botnee.process.vector_space_model,botnee.process.data_dict,botnee.corpus)
    pp (botnee.engine)
    psutil (botnee.engine)
    pymongo (botnee.doc_store,botnee.doc_manager_store)
    scipy (botnee.process.vector_space_model)
      \-sparse (botnee.doc_store,botnee.engine,botnee.process.matrix_dict,botnee.search,botnee.filter_results,botnee.process.data_dict,botnee.corpus,botnee.get_related,botnee.debug)
    setproctitle 
      \-setproctitle (botnee.web.manage,botnee)
    time 
      \-asctime (botnee.engine)
      \-localtime (botnee.engine)
      \-time (botnee.doc_store,botnee.web.interface.views,botnee.process.text,botnee.process.vector_space_model,botnee.engine,botnee.doc_manager_store,botnee.corpus,botnee.debug,botnee.test.test_corpus)
    webhelpers 
      \-feedgenerator 
        \-Rss201rev2Feed (botnee.rss_writer)


Copyright 2012 BMJGroup

The name comes from the phonetic version of 'botany' [bot-n-ee] 
since botanical nomenclature is closely linked to plant taxonomy.

Version 0.1.2
"""

#import os
#import sys
import datetime
import logging
from setproctitle import setproctitle

setproctitle('botnee-main')
#os.setprocname('botnee')

__all__ = [
    "botnee_config",
    "debug", 
    "doc_store",
    "doc_manager_store",
    "engine",
    "errors",
    "filters",
    "get_related",
    "json_io", 
    "persistent_dict",
    "process", 
    "rss_writer",
    "standard_document", 
    "standard_document_io", 
    "taxonomy", 
    "test",
    "test_harness",
    "timeout_lock",
    "timer", 
    "web",
    ]

import botnee_config

START_TIME = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

LOG_FILE = botnee_config.LOG_DIRECTORY + 'botnee_' + START_TIME + '.log'
#logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG)

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
str_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(str_format)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# import all of the modules defined in __all__
for module in __all__:
    exec "import " + module



