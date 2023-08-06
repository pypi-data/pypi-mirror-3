"""
Script that loads in MetaDict and DataDict and saves them out in json format.
If botnee_config.META_DICT_TYPE (and DATA) are both 'marshal', this will
translate the files from marshal to json format.
"""

import os

from botnee import botnee_config
from botnee.process.meta_dict import MetaDict
from botnee.process.data_dict import DataDict

INPUT_FORMAT = 'marshal'
OUTPUT_FORMAT = 'json'

botnee_config.DATA_DICT_STORE_TYPE = INPUT_FORMAT
botnee_config.META_DICT_STORE_TYPE = INPUT_FORMAT

md = MetaDict()

md.format = OUTPUT_FORMAT
md.filename = os.path.join(botnee_config.DATA_DIRECTORY, OUTPUT_FORMAT, 'meta_dict' + botnee_config.SUFFIX) + '.dat'

md.flush()

dd = DataDict()

dd.format = OUTPUT_FORMAT
dd.filename = os.path.join(botnee_config.DATA_DIRECTORY, OUTPUT_FORMAT, 'data_dict' + botnee_config.SUFFIX) + '.dat'

dd.flush()
