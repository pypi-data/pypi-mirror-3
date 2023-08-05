import re
import sympy
from sympy.core.numbers import Infinity
from sympy.core.numbers import ImaginaryUnit
try:
    from sympy.polys.factortools import factor # 0.6.7
except:
    from sympy.polys.polytools import factor # 0.7.1
import os
import codecs
import pkg_resources


import sys, traceback
from ..utils import debug_print
from .. import paths

phrasegroups = {}

GLYPHER_PG_LEAD_ALL  = (True,True,True,True,True,True)
GLYPHER_PG_LEAD_VERT = (False,False,False,True,True,True)
GLYPHER_PG_LEAD_HORI = (True,True,True,False,False,False)

#from BinaryExpression import *
import random
import string
import Dynamic

sm_tol = 1e-5
bg_tol = 4e-2

have_pyglet = False

var_table = {}
ps_ctr = 0
stp = 72/96.0

default_line_size = 25.0
default_font_size = 10.0
default_rgb_colour = (1.0, 0.0, 0.0)

try:
    sympy_ver = pkg_resources.get_distribution("sympy").version # get version of sympy
except:
    sympy_ver = '0.6.7' # default to this if pkg_resources non-functional
if sympy_ver == '0.7.1':
    mpmath_lib = 'mpmath'
else:
    mpmath_lib = 'sympy.mpmath'

libraries = {mpmath_lib : False}
def set_library(name, mode=True) :
    if Dynamic.load_library(name, not mode) :
        libraries[name] = mode
set_library(mpmath_lib)

bbox_mode = False
stroke_mode = False
math_mode = True
show_rectangles = False
selected_colour = (0.5, 0.7, 0.9, 0.3)
plane_mode = False
def set_plane_mode(p) :
    global plane_mode
    plane_mode = p
zeros_mode = False
def set_zeros_mode(p) :
    global zeros_mode
    zeros_mode = p
pow_mode = True
pow_mode_force = None
diff_mode = False
diff_mode_force = None
def set_pow_mode_force(p) :
    global pow_mode_force
    pow_mode_force = True if p == 1 else \
                     (False if p == -1 else \
                      None)
def set_diff_mode_force(d) :
    global diff_mode_force
    diff_mode_force = True if d == 1 else \
                      (False if d == -1 else \
                       None)
show_all_pow_diff = False
def set_show_all_pow_diff(s) :
    global show_all_pow_diff
    show_all_pow_diff = s
hy_arb_mode = True
interpretations = {}
interpretations_sympy_rev = {}

expand = {'complex' : False, 'trig' : False}
def set_expand_flag(name, val) :
    expand[name] = val

# Should we cache renderings in a library?
# Note that this may lose a couple of aspects (not at the moment)
use_rendering_library = False

# Additional highlighting? Maybe more explanatory, but also more fussy
additional_highlighting = False

# Max consecutive recalcs of an individual phrase; emergency cut-off
max_recalcs = 5

# Should we check and re-check everything?
# (or expect that the bboxes don't do anything unpredictable?)
anal_retentive_mode = False
anal_retentive_mode2 = False

# Thanks to regular-expressions.info
# http://www.regular-expressions.info/floatingpoint.html
is_floating_point_num_regex = '[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'

sympy_specials = {
    u'\u221e' : Infinity(),
    'i' : ImaginaryUnit()
}

suggested_target_phrased_to = None
def suggest(phr) :
    global suggested_target_phrased_to
    suggested_target_phrased_to = phr
def get_suggest() : return suggested_target_phrased_to

#Textual renderings by mode ("string" is key)
def import_interpretations () :
    lines = []
    with codecs.open(paths.get_share_location() + "unicode/interpretations.ucd", encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) == 0 : return

    types = lines[0].split("|")
    types = [t.strip() for t in types]
    modes = lines[1].split("|")
    modes = [t.strip() for t in modes]
    for line in lines[2:] :
        if len(line) < 2 or line[0] == '#' : continue
        entries = line.split("|")
        entries = [t.strip() for t in entries]
        interpretations[entries[0]] = dict([(types[i], str(entries[i])) for i in range(1,len(types))])
        interpretations_sympy_rev[entries[1]] = entries[0]

combinations = {}
def import_combinations () :
    lines = []
    with codecs.open(paths.get_share_location() + "unicode/combinations.ucd", encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) == 0 : return

    for line in lines :
        if len(line) < 2 or line[0] == '#' : continue
        entries = line.split("|")
        entries = [t.strip() for t in entries]
        combinations[entries[0]] = entries[1]

let_functions = {}
define_functions = {}
define_symbols = {}

#blush_grad = cairo.LinearGradient(0,0.5,1,0.5)
#blush_grad.add_color_stop_rgb(0, 0, 0, 0.0)
#blush_grad.add_color_stop_rgb(1, 1, 1, 0.0)

#cm_index = {}
#def get_cm_index() :
#    if len(cm_index) == 0 :
#        lines = []
#        with codecs.open(paths.get_share_location() + "cm.ucd", encoding='utf-8') as f:
#            lines = f.readlines()
#        for line in lines :
#            if len(line) < 2 or line[0] == '#' : continue
#            entries = line.split("|")
#            entries = [t.strip() for t in entries]
#            cm_index[entries[0]] = (entries[1], entries[2], float(entries[3]), float(entries[4]))
#    return cm_index

cmu_re_letter = re.compile(u'[A-Za-z\u03b1-\u03c9]')
cmu_re_exceptions = re.compile(u'[e\u03c0]')
def get_default_italic_for_shape(shape) :
    return cmu_re_letter.match(shape) and not cmu_re_exceptions.match(shape)

import Commands as C
operation_commands = {
    'Factor' : factor,
}
commands = { 'Set' : C.set_equal, 'Differentiate' : C.diff, 'Substitute' : C.sub, 'Expand' : C.series, 'Evaluate' : C.evalf, 'Limit' : C.limit,
             'S' :   C.set_equal, 'Di' :            C.diff, 'Sub' :        C.sub,
             'Ex' :     C.series, 'E' :             C.evalf, 'Li'    : C.limit,
             'Do' :  C.doit,      'Unset' :         C.unset_equal,    'Source' :    C.source,    'Plot' :    C.plot,
             'D' :   C.doit,      'U' :             C.unset_equal,    'Sc' :        C.source,    'P' :        C.plot,
            'Solve' :    C.solve,  'Let' :          C.let,  'Define' : C.define,
             'So' :    C.solve,     'L' :           C.let,  'De' : C.define,
            'Match' : C.match,      'Undefine' :    C.undefine,
            'M' : C.match,          'Ud' :          C.undefine
       }

dit = False
response_dictionary = {}
def get_response(code) :
    if code not in response_dictionary : return None
    new_elt = response_dictionary[code].copy()
    return new_elt

def add_response(code, statement, response) :
    response_dictionary['s'+str(code)] = statement
    response_dictionary['r'+str(code)] = response

# well, dmsa
bodmas_order = [ '/', '*', '-', '+' ]
def get_bodmas(shape) :
    level = 0
    alts = find_alternatives(shape)
    if alts is None : alts = [shape]
    for x in bodmas_order :
        if x in alts : level = bodmas_order.index(x)+2
    return level # 0 if not found, (1 avoided for powers), 2 for '/' up to 4 if +
    
# well, dmsa
associative = [ '*', '+', ',', ' ', '-' ]
def get_associative(shape) :
    level = 0
    alts = find_alternatives(shape)
    if alts is None : alts = [shape]
    else : alts = alts[0]
    for x in associative :
        if x in alts : return True
    return False # 0 if not found up to 4 if +

from Alternatives import *
#Alternative for same key
alternatives = [ \
    # Latin and Greek
    ['a',u'\u03B1'],        ['A',u'\u0391'],\
    ['b',u'\u03B2'],        ['B',u'\u0392'],\
    ['c',u'\u03C2'],\
    ['d',u'\u03B4'],        ['D',u'\u0394'],\
    ['e',u'\u03B5'],        ['E',u'\u0395'],\
    ['f',u'\u03C6',u'\u03D5'],    ['F',u'\u03A6'],\
    ['g',u'\u03B3'],        ['G',u'\u0393'],\
    ['h',u'\u03B7'],        ['H',u'\u0397'],\
    ['i',u'\u03B9'],        ['I',u'\u0399'],\
    ['j',u'\u03B8'],        ['J',u'\u0398'],\
    ['k',u'\u03BA'],        ['K',u'\u039A'],\
    ['l',u'\u03BB'],        ['L',u'\u039B'],\
    ['m',u'\u03BC'],        ['M',u'\u039C'],\
    ['n',u'\u03BD'],        ['N',u'\u039D'],\
    ['o',u'\u03BF'],        ['O',u'\u039F'],\
    ['p',u'\u03C0',u'\u03D6'],    ['P',u'\u03A0'],\
    ['q',u'\u03C7'],        ['Q',u'\u03A7'],\
    ['r',u'\u03C1'],        ['R',u'\u03A1'],\
    ['s',u'\u03C3'],        ['S',u'\u03A3'],\
    ['t',u'\u03C4'],        ['T',u'\u03A4'],\
    ['u',u'\u03C5'],        ['U',u'\u03A5',u'\u03E0'],\
    ['w',u'\u03C9'],        ['W',u'\u03A9'],\
    ['x',u'\u03BE'],        ['X',u'\u039E'],\
    ['y',u'\u03C8'],        ['Y',u'\u03A8'],\
    ['z',u'\u03B6'],        ['Z',u'\u0396'],\
    # Symbols
    [u'\u00B7', u'\u00D7', '*', u'\u2217', u'\u2218'],
    ['+', u'\u222A', u'\u2227', u'\u2229'],
    ['<', u'\u2282', u'\u220A'],
]
alternatives_altboxes = {}
def find_alternatives(shape, generate_altbox=False) :
    for alt in alternatives :
        ab = alternatives_altboxes[alt[0]] if alt[0] in alternatives_altboxes else None
        if shape in alt :
            if generate_altbox and ab is None :
                ab = GlypherAltBox(alt)
                alternatives_altboxes[alt[0]] = ab
                debug_print((alt[0], ab))
            return (alt, ab)
    return None
phrasegroup_alternatives = {}

def find_phrasegroup_alternatives(cat) :
    '''Finds alternatives for a given category.'''
    debug_print(phrasegroup_alternatives)
    
    if cat in phrasegroup_alternatives :
        return phrasegroup_alternatives[cat]
    return None
