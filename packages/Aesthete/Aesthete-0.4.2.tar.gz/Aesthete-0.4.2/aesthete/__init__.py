"""
Test
"""

import os
import aobject.paths as paths
from aobject.utils import *

paths.try_make_subdir('')
paths.try_make_subdir('glypher')
paths.try_make_subdir('glypher/phrasegroups')
paths.try_make_subdir('glypher/snippets')
paths.try_make_subdir('glypher/formulae')

#def try_make_subdir(subdir) :
#    loc = paths.get_user_location() + subdir
#
#    if os.path.exists(loc) :
#        return
#
#    try :
#        os.mkdir(loc)
#    except OSError as e:
#        debug_print(str(e))
