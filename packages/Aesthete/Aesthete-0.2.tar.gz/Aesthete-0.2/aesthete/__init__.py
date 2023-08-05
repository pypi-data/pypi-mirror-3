"""
Test
"""

__all__ = ["aobject", "alogger", "glypher", "glancer", "sources", "gluer", "aesspreadsheet","utils", "sims", "details"]

import os
import paths
from utils import *

def try_make_subdir(subdir) :
    loc = paths.get_user_location() + subdir

    if os.path.exists(loc) :
        return

    try :
        os.mkdir(loc)
    except OSError as e:
        debug_print(str(e))

try_make_subdir('')
try_make_subdir('glypher')
try_make_subdir('glypher/phrasegroups')
try_make_subdir('glypher/snippets')
