#from django.db import models

import botnee_config
from botnee.engine import Engine
#from botnee.get_related import GetRelated

# Create your models here.
engine = Engine(
              collector_directory = None, 
              verbose=botnee_config.VERBOSE, 
              parallel=botnee_config.PARALLEL, 
              recursive=botnee_config.RECURSIVE,
              force_reindex=False,
              get_data=True
              )

#get_related = GetRelated(engine)
