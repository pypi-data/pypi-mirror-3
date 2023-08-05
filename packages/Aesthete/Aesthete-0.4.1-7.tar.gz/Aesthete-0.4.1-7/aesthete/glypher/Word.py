import glypher as g
import Dynamic
import sympy
import re
import draw
from Phrase import *
from PhraseGroup import *
from Symbol import *
from sympy import physics, sympify
from sympy.core.symbol import Symbol as sySymbol
from sympy.core.basic import Basic
from sympy.core.numbers import *
from sympy.core.sets import *
import Parser
import Decoration

class GlypherWord (GlypherPhrase) :
    title = "Word"
    info_text = '''
Basic conceptual unit - combination of unicode characters (GlypherSymbols)
together representing a sympy Symbol
        '''
    defined_function = False
    defined_symbol = False
    let_function = False
    let_matrix = False
    wildcard = False

    def is_function(self) :
        return self.defined_function or self.let_function 

    def set_auto_italicize(self, auto_italicize) : self.set_p('auto_italicize', auto_italicize)
    def get_auto_italicize(self) : return self.get_p('auto_italicize')

    def __init__(self, parent, area = (0,0,0,0)) :
        GlypherPhrase.__init__(self, parent, area)
        self.mes.append('word')
        self.add_properties({'auto_italicize' : True, 'wordlike' : True})

    def split(self, position) :
        area = (self.config[0].bbox[0], self.get_topline(), self.config[0].bbox[2], self.get_baseline())
        wanc = area[0]
        word1 = GlypherWord(self.get_up(), area)
        word2 = GlypherWord(self.get_up(), area)
        ents = self.get_entities()
        bboxes = [ent.config[0].bbox[0] for ent in ents]
        i = 0
        for ent in ents :
            ent.orphan()
            if bboxes[i]-wanc < position : word1.append(ent, quiet = True)
            else : word2.append(ent, quiet = True)
            i += 1
        word1.recalc_bbox()
        word2.recalc_bbox()
        if len(word1.get_entities()) == 0 : return (None,word2)
        elif len(word2.get_entities()) == 0 : return (word1,None)
        return (word1, word2)

    # We assume that, if a word is not leading with a number, it shouldn't be considered as such
    def is_leading_with_num(self) : return self.is_num()

    def is_num(self) : return all_numbers.match(self.to_string())

    def is_roman(self) : return all_roman.match(self.to_string())

    def to_latex(self) :
        if not self.get_visible() : return ""
        elif self.get_blank() : return " "

        me_str = self.to_string()
        if me_str in g.interpretations :
            me_str = g.interpretations[me_str]["latex"]
        return str(me_str)

    #def _get_symbol_string(self, sub = True) :
    #    if self.is_num() :
    #        return None

    #    return GlypherPhrase._get_symbol_string(sub=sub)

    def get_sympy(self, sub = True, ignore_func = False) :
        if self.let_function and not ignore_func and \
                self.get_sympy(ignore_func=True) in g.let_functions :
            name = self.get_sympy(ignore_func=True)
            return g.let_functions[name]
        elif self.defined_function and not ignore_func and \
                self.get_sympy(ignore_func=True) in g.define_functions :
            name = self.get_sympy(ignore_func=True)
            args = g.define_functions[name]
            f = Dynamic.Function(str(self.to_string()))
            return f(*args)
        elif self.let_matrix and not ignore_func and \
                self.get_sympy(ignore_func=True) in g.let_matrices :
            name = self.get_sympy(ignore_func=True)
            return g.let_matrices[name]

        me_str = self._get_symbol_string(sub)
        if self.is_num() :
            sym = sympify(self.to_string())
        else :
            sym = sySymbol(str(me_str))
            if sub and sym in g.var_table :
                sym = g.var_table[sym]

        if sym in g.define_symbols and not ignore_func :
            sym = g.define_symbols[sym]

        return sym
            #return sySymbol(self.to_string("sympy"))

    def get_symbol_extents(self) :
        if len(self.get_entities()) == 0 :
            return (self.config[0].bbox[0], self.config[0].bbox[2])

        extents = [self.get_entities()[0].config[0].bbox[0],
                   self.get_entities()[0].config[0].bbox[2]]

        for sym in self.get_entities() :
            ie = sym.config[0].bbox
            if ie[0] < extents[0] :
                extents[0] = ie[0]
            if ie[2] > extents[1] :
                extents[1] = ie[2]

        return extents

    def draw(self, cr) :
        try :
            if self.get_visible() and not self.get_blank() and \
                self.get_sympy(sub=False, ignore_func=True) in g.var_table :
                cr.save()
                cr.set_source_rgba(1.0,0.8,0,0.5)
                #cr.rectangle(self.config[0].bbox[0], self.config[0].bbox[1],
                #             self.get_width(), self.get_height())
                area = (self.config[0].bbox[0],
                        self.config[0].bbox[2],
                        self.config[0].bbox[1],
                        self.config[0].bbox[3])
                draw.trace_rounded(cr, area, 7)
                cr.fill()
                cr.restore()
        except :
            pass

        GlypherPhrase.draw(self, cr)

    def process_key(self, name, event, caret) :
        mask = event.state
        if name == 'Return' and \
                self.included() and \
                self.get_sympy(sub=False, ignore_func=True) in g.var_table :
            sy = self.get_sympy(sub=False, ignore_func=True)
            new_pg = interpret_sympy(self.get_parent(), g.var_table[sy])
            self.get_parent().exchange(self, new_pg)
            return True
        
        return GlypherPhrase.process_key(self, name, event, caret)

    def _adjust_bbox(self, bbox) :
        '''
        Override this to expand (or contract) bbox after it has been set by
        contained elements.
        '''

        for sym in self.get_entities() :
            ie = sym.get_ink_extent()
            if ie is None :
                continue
            if ie[0] < bbox[0] :
                bbox[0] = ie[0]
            if ie[1] > bbox[2] :
                bbox[2] = ie[1]

    def child_change(self) :
        '''Runs a few checks to see what kind of Word we now have.'''

        GlypherPhrase.child_change(self)

        # Check whether we have a collapsible combination
        if self.to_string() in g.combinations :
            new_sym = GlypherSymbol(self, g.combinations[self.to_string()])
            self.empty()
            self.adopt(new_sym)

        # Check whether we have a special combination
        if self.to_string() in g.specials and self.included() :
            pg = Parser.make_phrasegroup(self.get_parent(),
                                         g.specials[self.to_string()])
            self.get_parent().exchange(self, pg)
            self.set_recommending(pg)
            return

        try :
            symp = self.get_sympy(ignore_func=True)
        except :
            symp = None

        # If we have a Let function, show it up
        if symp and isinstance(symp, Basic) and \
                symp in g.let_functions :
            if not self.let_function :
                self.let_function = True
                self.set_bold(True)
                self.set_rgb_colour((0.5, 0.2, 0.5))
        # If we have a Define function, show it up
        elif symp and isinstance(symp, Basic) and \
                symp in g.define_functions :
            if not self.defined_function :
                self.defined_function = True
                self.set_bold(True)
                self.set_rgb_colour((0.2, 0.4, 0.4))
        # If we have a Let matrix, show it up
        elif symp and isinstance(symp, Basic) and \
                symp in g.let_matrices :
            if not self.let_matrix :
                self.let_matrix = True
                self.set_bold(True)
        elif symp and isinstance(symp, Basic) and \
                    symp in g.define_symbols and \
                    isinstance(g.define_symbols[symp], Dynamic.Wild) :
            if not self.wildcard :
                self.wildcard = True
                self.set_rgb_colour((0.8, 0.6, 0.0))
        elif symp and isinstance(symp, Basic) and \
                symp in g.define_symbols :
            if not self.defined_symbol :
                self.defined_symbol = True
                self.set_rgb_colour((0.4, 0.4, 0.4))
        # Otherwise, cancel those settings
        elif self.defined_function or self.let_function or self.wildcard or \
                self.defined_symbol :
            self.defined_function = False
            self.let_function = False
            self.set_bold(False)
            self.set_rgb_colour(None)

        if self.get_auto_italicize() :
         if len(self.entities) > 1 and self.is_roman() :
            for e in self.entities :
                if e.get_italic() : e.set_italic(False)
         else :
            for e in self.entities :
                if not e.get_italic() and all_roman.match(e.to_string()) :
                    e.set_italic(True)

    def set_italic(self, italic) :
        for e in self.entities :
            if e.get_italic() is not italic :
                e.set_italic(italic)

    def decorate(self, cr) :
        #self.draw_topbaseline(cr)
        if not self.get_visible() : return
        #if self.active and self.shows_active :
        if g.additional_highlighting and self.get_attached() and self.get_shows_active() :
            cr.save()
            #cr.set_line_width(4.0)
            #cr.rectangle(self.bbox[0]-2, self.bbox[1]-2, self.bbox[2]-self.bbox[0]+4, self.bbox[3]-self.bbox[1]+4)
            cr.move_to(self.config[0].bbox[0]-2, self.config[0].bbox[3]+2)
            draw.draw_blush( cr, self.config[0].bbox[2]-self.config[0].bbox[0]+4, (0.5,0.5,0.5), 8)
            #cr.line_to(self.config[0].bbox[2]+2, self.config[0].bbox[3]+2)
            #cr.set_source_rgba(0.5, 0.5, 0.5, 0.6)
            #cr.stroke()
            cr.restore()
        elif self.get_attached() or (len(self.get_entities()) > 1 and not self.is_num()) :
            cr.save()
            #cr.set_line_width(4.0)
            cr.move_to(self.config[0].bbox[0]+2, self.config[0].bbox[3]-2)
            #draw_blush( cr, self.config[0].bbox[2]-self.config[0].bbox[0]+4, (0.7,0.9,0.7), 2)
            cr.line_to(self.config[0].bbox[2]-2, self.config[0].bbox[3]-2)
            col = (0.7, 0.7, 0.9, 1.0) if self.get_attached() else (0.7, 0.9, 0.7, 1.0)
            cr.set_source_rgba(*col)
            cr.stroke()
            cr.restore()

alternatives = {
    1 : ('planck', 'hbar'),

    2 : ('second', 'millisecond', 'microsecond', 'nanosecond', 'picosecond'),
    3 : ('gee','gram', 'kilogram', 'microgram', 'milligram'),
    4 : ('liter', 'milliliter', 'centiliter', 'decaliter'),
    5 : ('meter', 'kilometer', 'u0', 'mole', 'micron', 'millimeter', 'centimeter'),
    6 : ('ampere',),
    7 : ('kelvin',),
    8 : ('speed_of_light', 'candela'),
    9 : ('hertz',),
    10: ('newton',),
    11: ('exp1', 'e0'),
    12: ('G',),
    }
alternatives_keys = {
    'h' : 1, 's' : 2, 'g' : 3, 'l' : 4, 'm' : 5,
    'A' : 6, 'K' : 7, 'C' : 8, 'H' : 9, 'N' : 10,
    'e' : 11,'G' : 12,
    }
alternatives_current_defaults = {}

class GlypherConstant(GlypherPhraseGroup) :
    get_sympy_code = None
    value = None
    toolbox = None

    @classmethod
    def parse_element(cls, parent, root, names, targets, operands, recommending, lead,
                  add_entities, am = None, top = True, args=None) :
        ent = cls(parent, GlypherSymbol(parent, root.find('symbol').text))
        return ent

    def get_sympy(self) :
        if self.get_sympy_code is not None :
            return Dynamic.eval_for_sympy(self, self.get_sympy_code)
        return self.value

    def __init__(self, parent, entity) :
        GlypherPhraseGroup.__init__(self, parent, [], area=[0,0,0,0])
        self.set_rgb_colour((0.5, 0.5, 0.8))
        self.mes.append('constant')
        self.add_properties({'enterable' : False,
                             'have_alternatives' : False})
        self.suspend_recommending()
        self.append(entity)
        #self.set_default_entity_xml()

constants = {}
class GlypherConstant_(GlypherConstant) :
    value = None
    symbol = None
    me = None
    constant_have_alternatives = False

    parse_element = None

    def __init__(self, parent) :
        GlypherPhraseGroup.__init__(self, parent)
        self.set_rgb_colour((0.5, 0.5, 0.8))
        self.mes.append('constant')
        if self.me is not None :
            self.mes.append(self.me)
        self.add_properties({'enterable' : False,
                             'have_alternatives' :
                             self.constant_have_alternatives})
        self.suspend_recommending()
        if self.symbol is not None :
            self.append(GlypherEntity.xml_copy(parent, self.symbol))
        self.set_default_entity_xml()

    def change_alternative(self, dir = 1) :
        ret = GlypherPhrase.change_alternative(self, dir=dir)
        if ret:
            for ind in alternatives :
                alts = alternatives[ind]
                if self.mes[-1] in alts :
                    i = alternatives_current_defaults[ind]
                    alternatives_current_defaults[ind] = (i+dir) % len(alts)
                    break

        return ret

    @classmethod
    def new_from_symbol(cls, name, symbol, value, italicize=False,
                        cat="Constants", alternatives_cat=None) :
        new_sym = GlypherSymbol(None, symbol, italic=italicize)
        return cls.new_from_entity(name, new_sym, value, cat=cat,
                                   alternatives_cat=alternatives_cat)

    @classmethod
    def new_from_symbol_sub(cls, name, symbol, sub,
            value, italicize=False, it_sub=None, cat="Constants",
                            alternatives_cat=None) :
        if it_sub is None :
            it_sub = italicize
        new_sym = GlypherSymbol(None, symbol, italic=italicize)
        new_sub = GlypherSymbol(None, sub, italic=it_sub)
        new_dec = Decoration.GlypherScript.subscript(None, area=(0,0,0,0),
            expression=new_sym, subscript=new_sub)
        return cls.new_from_entity(name, new_dec, value, cat=cat,
                                   alternatives_cat=alternatives_cat)

    @classmethod
    def new_from_entity(cls, name, symbol, value, cat="Constants",
                        alternatives_cat=None) :
        if cat is not None :
            toolbox = {'symbol' : symbol.to_string(),
                           'category' : cat,
                           'priority' : None,
                           'shortcut' : None }
        else :
            toolbox = None
        new_dict = {'me':name, 'value':value, 'symbol':symbol,
                    'toolbox':toolbox,'altname':name,'alternatives_cat':alternatives_cat}
        new_sym = type('GlypherConstant_'+str(name), (cls,object,), new_dict)

        for alts in alternatives :
            alts = alternatives[alts]
            if name in alts :
                new_sym.constant_have_alternatives = True
                new_sym.alternatives = alts
                new_sym.altname = name
        g.add_phrasegroup_by_class(name, new_sym, alt_cat=alternatives_cat)
        return new_sym

constants['planck'] = GlypherConstant_.new_from_symbol('planck', 'h',
                                                      physics.units.planck,
                                                      italicize=True,
                                                      cat="Physical Constants",
                                                      alternatives_cat='planck')
constants['hbar'] = GlypherConstant_.new_from_symbol( 'hbar', u'\u0127',
                                                    physics.units.hbar,
                                                    italicize=True,
                                                    cat="Physical Constants",
                                                    alternatives_cat='planck')
constants['speed_of_light'] = GlypherConstant_.new_from_symbol( 'speed_of_light',
                                                              'c',
                                                              physics.units.speed_of_light,
                                                              italicize=True,
                                                              cat="Physical Constants")
constants['G'] = GlypherConstant_.new_from_symbol( 'G', 'G',
                                                 physics.units.speed_of_light,
                                                 italicize=True,
                                                 cat="Physical Constants")
constants['gee'] = GlypherConstant_.new_from_symbol( 'gee', 'g',
                                                   physics.units.speed_of_light,
                                                   italicize=True,
                                                 cat="Physical Constants",
                                                   alternatives_cat="gram")
constants['e0'] = GlypherConstant_.new_from_symbol_sub( 'e0', 'e', '0',
                                                      physics.units.e0,
                                                      italicize=True,
                                                 cat="Physical Constants")
constants['u0'] = GlypherConstant_.new_from_symbol_sub( 'u0', u'\u03BC', '0',
                                                      physics.units.u0,
                                                      italicize=True,
                                                 cat="Physical Constants")
constants['Z0'] = GlypherConstant_.new_from_symbol_sub( 'Z0', 'Z', '0',
                                                      physics.units.Z0,
                                                      italicize=True,
                                                 cat="Physical Constants")

constants['exp1'] = GlypherConstant_.new_from_symbol( 'exp1',
                                                    'e',Exp1(),
                                                    italicize=False,
                                                   cat="Mathematical Constants")
constants['exponential_e'] = GlypherConstant_.new_from_symbol( 'exp1', 'e',
                                                             Exp1(),
                                                             italicize=False,
                                                   cat="Mathematical Constants")
constants['empty_set'] = GlypherConstant_.new_from_symbol(
                                                                  'empty_set',
                                                                  u'\u2205',
                                                                  EmptySet(),
                                                                  italicize=False,
cat="Sets")

#constants['complex'] = GlypherConstant_.new_from_symbol(
#                                                                  'Complex',
#                                                                  u'\u2102',
#                                                                  Exp1(),
#                                                                  italicize=False)
#        (u'\u2102', '\\Complex'), \
#        (u'\u2124', '\\Integer'), \
#        (u'\u2115', '\\Natural'), \
#        (u'\u211A', '\\Rational'), \
#        (u'\u211D', '\\Real'), \

constants['infinity'] = GlypherConstant_.new_from_symbol(
                                       'infinity',
                                       u'\u221e',
                                       Infinity(),
    italicize=False,
                                                   cat="Mathematical Constants")
constants['imaginary_unit'] = GlypherConstant_.new_from_symbol(
                                       'imaginary_unit',
                                       'i',
                                       ImaginaryUnit(),
    italicize=False,
    cat="Complex")

constants['realR'] = GlypherConstant_.new_from_symbol(
                                       'realR',
                                       u'\u211D',
                                       None, italicize=False,
cat="Sets")

constants['rationalQ'] = GlypherConstant_.new_from_symbol(
                                       'rationalQ',
                                       u'\u211A',
                                       None, italicize=False,
cat="Sets")

constants['complexC'] = GlypherConstant_.new_from_symbol(
                                       'complexC',
                                       u'\u2102',
                                       None, italicize=False,
cat="Sets")

units = {}
class GlypherUnit_(GlypherConstant_) :
    value = None

    def __init__(self, parent) :
        GlypherConstant_.__init__(self, parent)
        self.set_rgb_colour((0.5, 0.8, 0.6))
        self.suspend_recommending()

def auto_make_unit(name, symbol, cat=None, alternatives_cat=None) :
  units[name] = GlypherUnit_.new_from_symbol(name, symbol,
                                            physics.units.__dict__[name],
                                            cat=cat,
                                            alternatives_cat=alternatives_cat)

auto_make_unit('meter', 'm', cat="Units", alternatives_cat="meter")
auto_make_unit('gram', 'g', cat="Units", alternatives_cat="gram")
auto_make_unit('second', 's', cat="Units", alternatives_cat="second")
auto_make_unit('ampere', 'A', cat="Units")
auto_make_unit('kelvin', 'K', cat="Units")
auto_make_unit('mole', u'\u33d6', cat="Units")
auto_make_unit('candela', u'\u33c5', cat="Units")
auto_make_unit('liter', u'\u2113', cat="Units", alternatives_cat="liter")

auto_make_unit('hertz', u'\u3390', cat="Units")
auto_make_unit('newton', 'N', cat="Units")

auto_make_unit('millisecond', u'\u33b3', alternatives_cat='second')
auto_make_unit('microsecond', u'\u33b2', alternatives_cat='second')
auto_make_unit('nanosecond', u'\u33b1', alternatives_cat='second')
auto_make_unit('picosecond', u'\u33b0', alternatives_cat='second')

auto_make_unit('kilogram', u'\u338f', alternatives_cat='gram')
auto_make_unit('microgram', u'\u338d', alternatives_cat='gram')
auto_make_unit('milligram', u'\u338e', alternatives_cat='gram')

auto_make_unit('milliliter', u'\u3396', alternatives_cat='liter')
#auto_make_unit('decaliter', 'dl')

auto_make_unit('kilometer', u'\u339e', alternatives_cat='meter')
auto_make_unit('micron', u'\u339b', alternatives_cat='meter')
auto_make_unit('millimeter', u'\u339c', alternatives_cat='meter')
auto_make_unit('centimeter', u'\u339d', alternatives_cat='meter')

def make_word(string, parent, area = (0,0,0,0), auto_italicize=True) :
    '''Make a Word from a string.'''

    string = unicode(string)
    word = GlypherWord(parent, area)
    word.set_auto_italicize(auto_italicize)

    for l in string :
        word.append(GlypherSymbol(word, l))

    return word

all_numbers = None
all_roman = None
def word_init() :
    global all_numbers, all_roman
    all_numbers = re.compile(g.is_floating_point_num_regex)
    all_roman   = re.compile('[A-Za-z]')

import Interpret
def interpret_sympy(p, sy) :
    return Interpret.interpret_sympy(p, sy)

g.add_phrasegroup_by_class('constant', GlypherConstant)
