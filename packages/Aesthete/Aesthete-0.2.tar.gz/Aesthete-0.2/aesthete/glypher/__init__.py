"""
Glypher subpackage
"""

__all__ = ['Glypher', 'GlyphEntry', 'GlyphMaker']

import os
import shutil
import xml.etree.ElementTree as ET
import xml
from ..paths import *
import glypher as g
from Parser import add_phrasegroup_tree, load_shortcuts
from Function import function_init
from Word import word_init, make_word
import Widget

g.import_interpretations()
g.import_combinations()

user_files = map(lambda e : get_user_location()+'glypher/phrasegroups/'+e,
                 os.listdir(get_user_location()+'glypher/phrasegroups'))
for u in user_files :
    try :
        tree = ET.parse(u)
        name = tree.getroot().tag.lower()
        add_phrasegroup_tree(name, tree, latex=tree.getroot().get('latex_name'))
    except xml.parsers.expat.ExpatError :
        print "WARNING : Could not parse '%s', continuing without" % u

word_init()
function_init()

shortcut_file = get_user_location()+'glypher/shortcuts.xml' 
if not os.path.exists(shortcut_file) :
    shortcut_default_file = get_share_location()+'shortcuts.default.xml' 
    shutil.copyfile(shortcut_default_file,
                    shortcut_file)
load_shortcuts(shortcut_file)

display = Widget.GlyphDisplay()
