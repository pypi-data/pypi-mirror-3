import glypher as g
import sympy
import re
import draw
from Phrase import *
from Symbol import *
from sympy import physics
from sympy.core.symbol import Symbol as sySymbol
from sympy.core.basic import Basic
from sympy.core.numbers import *
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
        debug_print(bboxes)
        debug_print(position)
        i = 0
        for ent in ents :
            ent.orphan()
            if bboxes[i]-wanc < position : word1.append(ent, quiet = True)
            else : word2.append(ent, quiet = True)
            i += 1
        word1.recalc_bbox()
        word2.recalc_bbox()
        debug_print(word1.to_string())
        debug_print(word2.to_string())
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

    def _get_symbol_string(self, sub = True) :
        if self.is_num() :
            return None

        me_str = self.to_string()
        if me_str in g.sympy_specials :
            return g.sympy_specials[self.to_string()]
        #if me_str in g.interpretations :
        #    me_str = g.interpretations[me_str]["sympy"]
        return me_str

    def get_sympy(self, sub = True, ignore_func = False) :
        if self.let_function and not ignore_func and \
                self.get_sympy(ignore_func=True) in g.let_functions :
            name = self.get_sympy(ignore_func=True)
            return g.let_functions[name]
        elif self.defined_function and not ignore_func and \
                self.get_sympy(ignore_func=True) in g.define_functions :
            name = self.get_sympy(ignore_func=True)
            args = g.define_functions[name]
            f = sympy.core.function.Function(str(self.to_string()))
            return f(*args)
        me_str = self._get_symbol_string(sub)
        if me_str is None :
            sym = sympy.sympify(self.to_string())
        else :
            sym = sySymbol(str(me_str))
            if sub and sym in g.var_table :
                sym = g.var_table[sym]

        if sym in g.define_symbols and not ignore_func :
            sym = g.define_symbols[sym]

        return sym
            #return sySymbol(self.to_string("sympy"))

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

    def child_change(self) :
        '''Runs a few checks to see what kind of Word we now have.'''

        GlypherPhrase.child_change(self)

        # Check whether we have a collapsible combination
        if self.to_string() in g.combinations :
            new_sym = GlypherSymbol(self, g.combinations[self.to_string()])
            self.empty()
            self.adopt(new_sym)

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
        elif symp and isinstance(symp, Basic) and \
                    symp in g.define_symbols and \
                    isinstance(g.define_symbols[symp], sympy.core.symbol.Wild) :
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


constants = {}
class GlypherConstant(GlypherPhrase) :
    value = None

    def __init__(self, parent) :
        GlypherPhrase.__init__(self, parent)
        self.set_rgb_colour((0.5, 0.5, 0.8))
        self.mes.append('constant')
        self.add_properties({'enterable' : False})
        self.suspend_recommending()

    def change_alternative(self, dir = 1) :
        ret = GlypherPhrase.change_alternative(self, dir=dir)
	if ret:
	    for ind in alternatives :
		debug_print(ind)
	        alts = alternatives[ind]
	        if self.mes[-1] in alts :
		    debug_print((alts, self.mes[-1], ind))
		    i = alternatives_current_defaults[ind]
		    alternatives_current_defaults[ind] = (i+dir) % len(alts)
		    break

	return ret

    @classmethod
    def new_from_symbol(cls, parent, name, symbol, value, italicize=False) :
        new_sym = GlypherSymbol(parent, symbol, italic=italicize)
        return cls.new_from_entity(parent, name, new_sym, value)

    @classmethod
    def new_from_symbol_sub(cls, parent, name, symbol, sub,
            value, italicize=False, it_sub=None) :
	if it_sub is None : it_sub = italicize
        new_sym = GlypherSymbol(parent, symbol, italic=italicize)
        new_sub = GlypherSymbol(parent, sub, italic=it_sub)
	new_dec = Decoration.GlypherScript.subscript(parent, area=(0,0,0,0),
	    expression=new_sym, subscript=new_sub)
        return cls.new_from_entity(parent, name, new_dec, value)

    @classmethod
    def new_from_entity(cls, parent, name, symbol, value) :
        new_sym = cls(parent)
	new_sym.mes.append(name)
        new_sym.append(symbol)
	new_sym.value = value
	for alts in alternatives :
	    alts = alternatives[alts]
	    if name in alts :
	    	new_sym.set_have_alternatives(True)
	    	new_sym.alternatives = alts
		new_sym.altname = name
        new_sym.set_default_entity_xml()
	return new_sym

    def get_sympy(self) :
        return self.value

constants['planck'] = lambda p : GlypherConstant.new_from_symbol(p, 'planck', 'h', physics.units.planck, italicize=True)
constants['hbar'] = lambda p : GlypherConstant.new_from_symbol(p, 'hbar', u'\u0127', physics.units.hbar, italicize=True)
constants['speed_of_light'] = lambda p : GlypherConstant.new_from_symbol(p, 'speed_of_light', 'c', physics.units.speed_of_light, italicize=True)
constants['G'] = lambda p : GlypherConstant.new_from_symbol(p, 'G', 'G', physics.units.speed_of_light, italicize=True)
constants['gee'] = lambda p : GlypherConstant.new_from_symbol(p, 'gee', 'g', physics.units.speed_of_light, italicize=True)
constants['e0'] = lambda p : GlypherConstant.new_from_symbol_sub(p, 'e0', 'e', '0', physics.units.e0, italicize=True)
constants['u0'] = lambda p : GlypherConstant.new_from_symbol_sub(p, 'u0', u'\u03BC', '0', physics.units.u0, italicize=True)
constants['Z0'] = lambda p : GlypherConstant.new_from_symbol_sub(p, 'Z0', 'Z', '0', physics.units.Z0, italicize=True)
constants['exp1'] = lambda p : GlypherConstant.new_from_symbol(p, 'exp1', 'e', sympy.core.numbers.Exp1(), italicize=False)
constants['exponential_e'] = lambda p : GlypherConstant.new_from_symbol(p, 'exp1', 'e', sympy.core.numbers.Exp1(), italicize=False)
constants['empty_set'] = lambda p : GlypherConstant.new_from_symbol(p,
                                                                  'empty_set',
                                                                  u'\u2205',
                                                                  sympy.core.sets.EmptySet(),
                                                                  italicize=False)

#constants['complex'] = lambda p : GlypherConstant.new_from_symbol(p,
#                                                                  'Complex',
#                                                                  u'\u2102',
#                                                                  sympy.core.numbers.Exp1(),
#                                                                  italicize=False)
#        (u'\u2102', '\\Complex'), \
#        (u'\u2124', '\\Integer'), \
#        (u'\u2115', '\\Natural'), \
#        (u'\u211A', '\\Rational'), \
#        (u'\u211D', '\\Real'), \

constants['pi'] = lambda p : GlypherConstant.new_from_symbol(p, 'pi',
                                                             u'\u03c0',
                                                             Pi(),
                                                             italicize=False)
constants['infinity'] = lambda p : GlypherConstant.new_from_symbol(p,
                                       'infinity',
                                       u'\u221e',
                                       sympy.core.numbers.Infinity(), italicize=False)
constants['imaginary_unit'] = lambda p : GlypherConstant.new_from_symbol(p,
                                       'imaginary_unit',
                                       'i',
                                       sympy.core.numbers.ImaginaryUnit(), italicize=False)

constants['realR'] = lambda p : GlypherConstant.new_from_symbol(p,
                                       'realR',
                                       u'\u211D',
                                       None, italicize=False)

constants['rationalQ'] = lambda p : GlypherConstant.new_from_symbol(p,
                                       'rationalQ',
                                       u'\u211A',
                                       None, italicize=False)

constants['complexC'] = lambda p : GlypherConstant.new_from_symbol(p,
                                       'complexC',
                                       u'\u2102',
                                       None, italicize=False)

units = {}
class GlypherUnit(GlypherConstant) :
    value = None

    def __init__(self, parent) :
        GlypherConstant.__init__(self, parent)
        self.set_rgb_colour((0.5, 0.8, 0.6))
        self.mes.append('unit')
        self.suspend_recommending()

def auto_make_unit(name, symbol) :
  units[name] = lambda p : GlypherUnit.new_from_symbol(p, name, symbol, physics.units.__dict__[name])

auto_make_unit('meter', 'm')
auto_make_unit('kilogram', 'm')
auto_make_unit('second', 's')
auto_make_unit('ampere', 'A')
auto_make_unit('kelvin', 'K')
auto_make_unit('mole', 'mol')
auto_make_unit('candela', 'cd')

auto_make_unit('hertz', 'Hz')
auto_make_unit('newton', 'N')

auto_make_unit('millisecond', 'ms')
auto_make_unit('microsecond', u'\u03BCs')
auto_make_unit('nanosecond', 'ns')
auto_make_unit('picosecond', 'ps')

auto_make_unit('kilogram', 'kg')
auto_make_unit('gram', 'g')
auto_make_unit('microgram', u'\u03BCg')
auto_make_unit('milligram', 'mg')

auto_make_unit('liter', 'l')
auto_make_unit('milliliter', 'ml')
auto_make_unit('centiliter', 'cl')
auto_make_unit('decaliter', 'dl')

auto_make_unit('meter', 'm')
auto_make_unit('kilometer', 'km')
auto_make_unit('micron', u'\u03BCm')
auto_make_unit('millimeter', 'mm')
auto_make_unit('centimeter', 'cm')

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
