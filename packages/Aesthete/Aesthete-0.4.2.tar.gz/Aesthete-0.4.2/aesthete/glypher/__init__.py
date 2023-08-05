"""
Glypher subpackage
"""

__all__ = ['Glypher', 'GlyphEntry', 'GlyphMaker']

import os
import shutil
import lxml.etree as ET
from xml.parsers.expat import ExpatError
from aobject.paths import *
from aobject.utils import debug_print
import glypher as g
from Parser import add_phrasegroup_tree, add_formula_tree, load_shortcuts
from Function import function_init
from Word import word_init, make_word
import Widget

g.import_interpretations()
g.import_combinations()
g.import_specials()

formula_files = map(lambda e : get_share_location()+'formulae/'+e,
                 os.listdir(get_share_location()+'formulae'))
formula_files += map(lambda e : get_user_location()+'glypher/formulae/'+e,
                 os.listdir(get_user_location()+'glypher/formulae'))
for u in formula_files :
    try :
        tree = ET.parse(u)
        name = tree.getroot().get('name').lower()
        add_formula_tree(name, tree)
    except (ExpatError, ET.XMLSyntaxError) as e :
        debug_print("WARNING : Could not parse formula '%s', continuing without: %s" % (u, e))

file_sets = (map(lambda e : get_share_location()+'defs/'+e,
                 os.listdir(get_share_location()+'defs')),
             map(lambda e : get_user_location()+'glypher/phrasegroups/'+e,
                 os.listdir(get_user_location()+'glypher/phrasegroups')))

user = False
for file_set in file_sets :
    for u in file_set :
        try :
            tree = ET.parse(u)
            name = tree.getroot().tag.lower()
            add_phrasegroup_tree(name, tree, user=user, latex=tree.getroot().get('latex_name'))
        except (ExpatError, ET.XMLSyntaxError) as e :
            debug_print("WARNING : Could not parse PG '%s', continuing without: %s" % (u, e))
        user = True

word_init()
function_init()

shortcut_default_file = get_share_location()+'shortcuts.default.xml' 
load_shortcuts(shortcut_default_file)
shortcut_file = get_user_location()+'glypher/shortcuts.xml' 
if not os.path.exists(shortcut_file) :
    shutil.copyfile(shortcut_default_file,
                    shortcut_file)
load_shortcuts(shortcut_file)
