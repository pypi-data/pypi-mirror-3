import time
from sympy.printing.mathml import mathml
from sympy.matrices import matrices
from sympy.core.basic import Basic
from sympy.core.relational import Equality
from sympy.core import sympify
from ..utils import debug_print
import xml.etree.ElementTree as ET
from ComplexPlane import *
from Summation import *
from Fraction import *
from Word import *
from Table import *
from BinaryExpression import *
from Decoration import *
import Commands as C
import traceback
import Parser
from Interpret import *
import Function

from sympy.series.order import Order
try :
    from sympy import ask, Q
except :
    print "Version of sympy too old; you may have subsequent problems!"
from collections import *
import itertools
try :
    import sympy
    have_sympy = True
except ImportError :
    have_sympy = False

constants_map = { 'imaginaryi' : 'imaginary_unit',
                  'exponentiale' : 'exponential_e',
                  'pi' : 'pi',
                  'I' : 'imaginary_unit',
                  'oo' : 'infinity',
                }

for k in constants :
    constants_map[k] = k

#Fundamentally, Presentation MathML doesn't contain the required
#content information but sympy sometimes insets it into Symbols
#to render subscripts (and possibly other things too)
required_namespace = "{http://www.w3.org/1998/Math/MathML}"
def _presentation_mathml_to_entity(parent, node) :
    if isinstance(node, dict) :
        d = dict()
        for a in node.keys() :
            ent_key = _mathml_to_entity(parent, a)
            ent_val = _mathml_to_entity(parent, node[a])
            d[ent_key] = ent_val
        return GlypherDictionary(d, parent)

    if not node.tag.startswith(required_namespace) :
        raise RuntimeError("Wrong Presentation MathML namespace : " + \
                           node.tag + " is not in " + required_namespace)
    tag = node.tag[len(required_namespace):]

    if tag == 'math' :
        if len(node) == 1 :
            return _pmte(parent, node[0])
        else :
            rows = [_pmte(parent, row) for row in node]
            return GlypherList(parent, rows)
    elif tag == 'msub' :
        if len(node) == 2 :
            symbols = _pmte(parent, node[1])
        elif len(node) > 2 :
            symbols = array_to_binary_expression(parent, GlypherSpaceArray,
                                                 ex.symbols, presort=False,
                                                 processor=_pmte)
        else :
            raise RuntimeError('Can\'t process this Presentation MathML :' +
                               ET.tostring(node))

        operand = _pmte(parent, node[0])
        return GlypherScript.subscript(parent, expression=operand, subscript=symbols)
    elif tag == 'mi' :
        if len(node) == 0 :
            # We assume spaces are a product of SpaceArrays
            space_args = unicode(node.text).split(' ')
            if len(space_args) == 1:
                text = node.text
                return make_word(unicode(text), parent)
            else :
                return array_to_binary_expression(parent, GlypherSpaceArray,
                                                  space_args, presort=False,
                                                  processor=lambda p, t :
                                                  make_word(t,p))
        else :
            return _pmte(parent, node[0])
    return None

_pmte = _presentation_mathml_to_entity

def _generic_to_entity(parent, node) :
    debug_print(str(node))
    if isinstance(node, Basic) or \
       isinstance(node, matrices.Matrix) or \
       isinstance(node, Equality) :
        try :
            content = mathml(node)
        except :
            debug_print("""
                        Resorted to old-style sympy->glypher rendering, as
                        some sympy object not available in MathML.
                        """)
            return _sympy_to_entity_proper(parent, node)
        else :
            content = sympy.utilities.mathml.add_mathml_headers(content)
            node = ET.fromstring(content)
            return _mathml_to_entity_proper(parent, node)
    elif isinstance(node, list) or\
         isinstance(node, dict) or\
         isinstance(node, tuple) or\
         isinstance(node, ET._ElementInterface) :
        return _mathml_to_entity_proper(parent, node)
    elif node is None :
        return None
    else :
        return _mathml_to_entity_proper(parent, str(node))

function_mathml_to_sympy = {
    'arctan' : 'atan',
    'arccos' : 'acos',
    'arcsin' : 'asin',
    'arctanh' : 'atanh',
    'arccosh' : 'acosh',
    'arcsinh' : 'asinh',
    'ln' : 'log',
    'diracdelta' : 'DiracDelta',
    'heaviside' : 'Heaviside'
}
special_functions = {
    'im' : 'im',
    're' : 're'
}

_mathml_to_entity = _generic_to_entity
_sympy_to_entity = _generic_to_entity

def _mathml_to_entity_proper(parent, node) :
    #debug_print(node)
    if isinstance(node, dict) :
        d = dict()
        for a in node.keys() :
            ent_key = _mathml_to_entity(parent, a)
            ent_val = _mathml_to_entity(parent, node[a])
            d[ent_key] = ent_val
        return GlypherDictionary(d, parent)

    if isinstance(node, list) or isinstance(node, tuple) :
        if len(node) == 1 :
            return _mathml_to_entity(parent, node[0])

        return array_to_binary_expression(parent,
            GlypherCommaArray if len(node) < 4 else GlypherSemicolonArray,
            node, presort=False, processor=_mathml_to_entity)

    if isinstance(node, str) :
        return make_word(node, parent)

    if node.tag == 'math' :
        if len(node) == 1 :
            return _mathml_to_entity(parent, node[0])
        else :
            raise RuntimeError('Multiple nodes requested at once')
    #FIXME: find a more technical way of doing this
    elif node.tag[0] == '{' :
        return _pmte(parent, node)
    elif node.tag == 'apply' :
        operation = node[0].tag.strip()
        if len(node) > 1 :
            arguments = node[1:]

        if operation in Parser.content_mathml_operations :
            debug_print(ET.tostring(node))
            lhs = None if len(arguments) < 1 else _mathml_to_entity(parent, arguments[0])
            rhs = None if len(arguments) < 2 else _mathml_to_entity(parent, arguments[1])
            pg = Parser.make_phrasegroup(parent, Parser.content_mathml_operations[operation],
                                  operands=(lhs, rhs))
            return pg
            
        elif operation == 'plus' :
            fm = function_mathml_to_sympy
            if len(arguments)==2 and arguments[0].text == 'c' and g.hy_arb_mode and \
                    len(arguments[1]) == 2 and g.dit and \
                    arguments[1][0].tag == fm.keys()[fm.values().index(dir(i_func)[-3])] and \
                    len(arguments[1][1].text) >= 5 :
                intgd = arguments[1][1]
                intg = deque(list(intgd.text)[0:3]); intg.rotate(-1)
                if list(intg) == map(chr, range(97, 100)) and \
                        intgd.text[3:] == 'in' :
                    intgl = make_word(g.interpretations[u'\u03b2']["sympy"], parent)
                    intgl = deque(list(str(intgl.to_string()))); intgl.rotate(2)
                    intgl = list(intgl)
                    intgl_sa = list('suh')+[chr(111)]*2
                    istr = tuple(itertools.permutations(intgl[3:4]+intgl_sa[0:4]))
                    jstr = tuple(itertools.permutations(intgl[0:3]+intgl_sa[4:5]))
                    return GlypherAdd(parent, \
                                lhs=make_word(''.join(istr[95]), parent),
                                rhs=make_word(''.join(jstr[17]), parent),
                                subtract=True)
            addtn = array_to_binary_expression(parent, GlypherAdd, arguments,
                                               presort=False,
                                               processor=_mathml_to_entity)
            ex = addtn.get_sympy()
            if g.plane_mode and ask(ex, Q.complex) :
                real_imag = ex.as_real_imag()
                return GlypherComplexPlane(parent, complex(*map(float, real_imag)))
            return addtn

        elif operation == 'minus' :
            if len(node) == 2 :
                return GlypherNegative(parent, operand=_mathml_to_entity(parent,
                                                                         arguments[0]))
            elif len(node) == 3 :
                debug_print(node[1])
                addtn = GlypherAdd(parent,
                                  lhs=_mathml_to_entity(parent, arguments[0]),
                                  rhs=_mathml_to_entity(parent, arguments[1]),
                                  subtract=True)
                ex = addtn.get_sympy()
                if g.plane_mode and ask(ex, Q.complex) :
                    real_imag = ex.as_real_imag()
                    return GlypherComplexPlane(parent, complex(*map(float,
                                                                    real_imag)))
                return addtn

        elif operation == 'times' :
            return array_to_binary_expression(parent, GlypherMul, arguments,
                                       presort=False,
                                       processor=_mathml_to_entity)
        elif operation == 'diff' :
            # Subscript or GlypherDerivative?
            operand = _mathml_to_entity(parent, arguments[-1])
            bvars = node.findall('bvar')
            debug_print(bvars)

            if len(bvars) == 0 :
                diff = GlypherPrime(parent, operand=operand)
            elif (len(bvars) == 1 and len(operand.to_string())>20) :
                diff = GlypherDerivative(parent, operand=operand,
                               by=_mathml_to_entity(parent, bvars[0][0]))
            else :
                subscripts = []
                for bvar in bvars :
                    cis = bvar.findall('ci')
                    if len(cis) == 1 :
                        debug_print(ET.tostring(gutils.xml_indent(bvar)))
                        ci = cis[0]
                        degree = bvar.find('degree')
                        if degree is not None and degree[0].tag == 'cn' :
                            for i in range(0, int(degree[0].text)) :
                                subscripts.append(ci)
                        else :
                            subscripts.append(ci)
                    else :
                        subscripts += cis

                if len(subscripts) > 1 :
                    symbols = array_to_binary_expression(parent, GlypherSpaceArray,
                                                         subscripts, presort=False,
                                                         processor=_mathml_to_entity)
                elif len(subscripts) == 1 :
                    symbols = _mathml_to_entity(parent, subscripts[0])
                else :
                    raise RuntimeError('Problematic diff : ' +
                                       ET.tostring(gutils.xml_indent(node)))
                diff = GlypherScript.subscript(parent, expression=operand, subscript=symbols)
                diff.diff_mode = True
            return diff
        elif operation == 'int' :
            bvars = node.findall('bvar')
            if len(bvars) != 1 :
                raise RuntimeError('Can only do 1 by-variable at a time!')
            lowlimit = node.find('lowlimit')
            uplimit = node.find('uplimit')
            integrand = arguments[-1]

            integral = Parser.make_phrasegroup(parent, 'integral')
            integral['operand'].adopt(_mathml_to_entity(parent, integrand))
            integral['by'].adopt(_mathml_to_entity(parent, bvars[0].getchildren()))
            if lowlimit is not None :
                lowlimit = _mathml_to_entity(parent, lowlimit.getchildren())
                integral['from'].adopt(lowlimit)
            if uplimit is not None :
                uplimit = _mathml_to_entity(parent, uplimit.getchildren())
                integral['to'].adopt(uplimit)
            return integral
        elif operation == 'sum' :
            bvars = node.findall('bvar')
            if len(bvars) != 1 :
                raise RuntimeError('Can only do 1 by-variable at a time!')
            lowlimit = node.find('lowlimit')
            uplimit = node.find('uplimit')
            expression = arguments[-1]

            summation = Parser.make_phrasegroup(parent, 'summation')
            summation['expression'].adopt(_mathml_to_entity(parent, expression))
            summation['byvar'].adopt(_mathml_to_entity(parent, bvars[0].getchildren()))
            if lowlimit is not None :
                lowlimit = _mathml_to_entity(parent, lowlimit.getchildren())
                summation['from'].adopt(lowlimit)
            if uplimit is not None :
                uplimit = _mathml_to_entity(parent, uplimit.getchildren())
                summation['to'].adopt(uplimit)
            return summation
        elif operation == 'power' :
            if len(node) == 3 :
                superscript = _mathml_to_entity(parent, arguments[1])
            else :
                superscript = array_to_binary_expression(parent,
                                                         GlypherSpaceArray,
                                                         arguments[1:],
                                                         presort=False,
                                                         processor=_mathml_to_entity)
            power = GlypherScript.superscript(parent,
                                              expression=_mathml_to_entity(parent,
                                                                         arguments[0]),
                                              superscript=superscript)
            return power
        elif operation == 'root' :
            if len(arguments) > 0 and arguments[0].tag == 'degree' :
                degree = _mathml_to_entity(parent, arguments[0][0])
                return GlypherSqrt(parent,
                                   expression=_mathml_to_entity(parent,
                                                                arguments[1]),
                                   degree=degree)
            else :
                return GlypherSqrt(parent,
                                   expression=_mathml_to_entity(parent,
                                                                arguments[0]))

        elif operation == 'divide' :
            frac = GlypherFraction(parent,
                                   numerator=_mathml_to_entity(parent,
                                                               arguments[0]),
                                   denominator=_mathml_to_entity(parent,
                                                                 arguments[1]))
            return frac
        else :
            try :
                syop = sympify(operation)
            except :
                syop = sympy.core.basic.Symbol(str(operation))
            args_match = syop in g.define_functions
            if args_match :
                for i in range(0, len(arguments)) :
                    args_match = args_match and \
                            arguments[i].tag == 'ci' and \
                            g.define_functions[syop][i] == \
                                    sympify(arguments[i].text)
                    
            if args_match :
                return make_word(operation, parent)

            if operation in special_functions :
                function = Parser.make_phrasegroup(parent, special_functions[operation])
            else :
                function = Function.GlypherNaryFunction(parent)

                if operation in function_mathml_to_sympy :
                    name = function_mathml_to_sympy[operation]
                    if name in Function.function_translation_rev :
                        name = Function.function_translation_rev[name].copy()
                    else :
                        name = make_word(name, parent)
                elif operation in Function.function_translation_rev :
                    name = Function.function_translation_rev[operation].copy()
                else :
                    name = _mathml_to_entity(parent, node[0])
                function['name'].adopt(name)

            if len(node) > 2 :
                arguments = array_to_binary_expression(parent,
                                                       GlypherCommaArray,
                                                       arguments,
                                                       presort=False,
                                                       processor=_mathml_to_entity)
                function.args.append(arguments)
            elif len(node) == 2 :
                function.args.append(_mathml_to_entity(parent, arguments[0]))
            return function
    elif node.tag == 'list' :
        if len(node) > 4 :
            array_class = GlypherCommaArray
        else :
            array_class = GlypherSemicolonArray
            
        if len(node) > 1 :
            return array_to_binary_expression(parent, array_class, node,
                                              presort=False, processor=_mathml_to_entity)
        elif len(node) == 1 :
            return _mathml_to_entity(parent, node[0])
        else :
            return GlypherBracketedPhrase(parent, auto=False,
                                          bracket_shapes=('{','}'))

    elif node.tag in constants_map :
    	return constants[constants_map[node.tag]](parent)
    #elif isinstance(ex, sympy.concrete.summations.Sum) or isinstance(ex, sympy.concrete.products.Product) :
    #    p = GlypherSummation(parent)
    #    debug_print(ex.args[1])
    #    p.get_target('operand').adopt(_sympy_to_entity(parent, ex.args[0]))
    #    p.get_target('n').adopt(_sympy_to_entity(parent, ex.args[1][0][0]))
    #    p.get_target('from').adopt(_sympy_to_entity(parent, ex.args[1][0][1]))
    #    p.get_target('to').adopt(_sympy_to_entity(parent, ex.args[1][0][2]))
    #    p.get_alts('symbol').set_alternative_by_name('Pi' if isinstance(ex, sympy.concrete.products.Product) else \
    #                  'Sigma')
    #    return p
    elif node.tag == 'cn' :
        num = sympify(node.text)
        word = make_word(unicode(abs(num)), parent)
        if num < 0 :
            neg = GlypherNegative(parent)
            neg['expression'].adopt(word)
            return neg
        return word
    elif node.tag == 'ci' :
        if len(node) == 0 :
            if node.text == 'I' :
                return constants[constants_map['I']](parent)
            if node.text == 'oo' :
                return constants[constants_map['oo']](parent)
            return make_word(unicode(node.text), parent)
        else :
            return _mathml_to_entity(parent, node[0])
    else :
        debug_print(node.tag)
        return make_word(node.tag, parent)

    return None

# The sympy Symbol is probably closer in concept to our Word
# We are now switching to use this only in emergencies.
def _sympy_to_entity_proper(parent, ex) :
    if ex is None : return None

    binary = False
    if isinstance(ex, sympy.core.symbol.Symbol) :
        exstr = unicode(ex)
        et = exstr.split(unicode("_"))
        for t in et :
            if t in g.interpretations_sympy_rev :
                et[et.index(t)] = g.interpretations_sympy_rev[t]
        debug_print(et)

        if len(et) == 2 :
            p = GlypherScript.subscript(parent, expression=make_word(et[0], parent), subscript=make_word(et[1], parent))
            p.set_diff_mode(False)
            return p
        else :
            return make_word(exstr, parent)
    elif isinstance(ex, list) or isinstance(ex, tuple) :
        if len(ex) == 1 : return _sympy_to_entity(parent, ex[0])
        debug_print(ex)
        return array_to_binary_expression(parent,
            GlypherCommaArray if len(ex) < 4 else GlypherSemicolonArray,
            ex, presort=False)
    elif isinstance(ex, dict) :
        d = dict([(_sympy_to_entity(parent, a), _sympy_to_entity(parent, ex[a])) for a in ex.keys()])
        return GlypherDictionary(d, parent)
    elif isinstance(ex, Order) :
        p = Function.GlypherOrder(parent, order=_sympy_to_entity(parent, ex._args[0]))
        return p
    elif isinstance(ex, sympy.core.sets.Interval) :
        lhs = _sympy_to_entity(parent, ex.start)
        rhs = _sympy_to_entity(parent, ex.end)
        p = GlypherInterval(parent, lhs=lhs, rhs=rhs, left_open=ex.left_open,
                            right_open=ex.right_open)
        return p
    elif isinstance(ex, sympy.core.numbers.Exp1) : return GlypherExp1(parent)
    elif isinstance(ex, sympy.core.sets.EmptySet) : return constants['empty_set'](parent)
    elif isinstance(ex, sympy.core.numbers.ImaginaryUnit) : return GlypherImaginaryUnit(parent)
    elif isinstance(ex, sympy.physics.units.Unit) :
    	if ex.name in units :
    	    pg = units[ex.name](parent)
	    return pg
	return GlypherUnit.new_from_symbol(parent, ex.name, ex.abbrev, ex)
    elif isinstance(ex, sympy.core.numbers.Pi) : return GlypherPi(parent)
    elif isinstance(ex, sympy.core.numbers.Real) :
        num = float(str(ex))
        word = make_word(str(abs(num)), parent)
        if num < 0 :
            neg = GlypherNegative(parent)
            neg.get_target('expression').adopt(word)
            return neg
        return word
    elif isinstance(ex, sympy.core.numbers.Integer) :
        num = int(str(ex))
        word = make_word(str(abs(num)), parent)
        if num < 0 :
            neg = GlypherNegative(parent)
            neg.get_target('expression').adopt(word)
            return neg
        return word
    elif isinstance(ex, sympy.core.numbers.Zero) :
        return make_word('0', parent)
    elif isinstance(ex, sympy.core.numbers.One) :
        return make_word('1', parent)
    elif isinstance(ex, sympy.core.numbers.NegativeOne) :
        debug_print(ex)
        neg = GlypherNegative(parent)
        one = make_word('1', parent)
        neg.get_target('expression').adopt(word)
        return neg
    elif isinstance(ex, sympy.core.numbers.Infinity) :
        return make_word(u'\u221e', parent)
    elif isinstance(ex, Equality) :
        return GlypherEquality(parent,
                               lhs=_sympy_to_entity(parent, ex.args[0]),
                               rhs=_sympy_to_entity(parent, ex.args[1]))
    elif isinstance(ex, sympy.core.add.Add) :
        #binary = True
        #lhs = _sympy_to_entity(parent, ex.args[0])
        #rhs = _sympy_to_entity(parent, ex.args[1])
        #debug_print(ex.args[0])
        #return lhs
        #bin = GlypherAdd(None, lhs=lhs, rhs=rhs, \
        #      num_ops=len(ex.args))
        #p = bin
        if g.plane_mode and ask(ex, Q.complex) :
            ri = ex.as_real_imag()
            return GlypherComplexPlane(parent, complex(*map(float, ri))) #, arg_string=str(float(ri[1])))
        if len(ex.args)==2 and str(ex.args[1]) == 'c' and g.hy_arb_mode and \
            hasattr(ex.args[0], "func") and g.dit and str(ex.args[0].func) == dir(i_func)[-3] and \
            len(str(ex.args[0].args[0])) >= 5 :
                intg = deque(list(str(ex.args[0].args[0]))[0:3]); intg.rotate(-1)
                if list(intg) == map(chr, range(97, 100)) and \
                    str(ex.args[0].args[0])[3:] == 'in' :
                        intgl = make_word(g.interpretations[u'\u03b2']["sympy"], parent)
                        intgl = deque(list(str(intgl.to_string()))); intgl.rotate(2)
                        intgl = list(intgl)
                        intgl_sa = list('suh')+[chr(111)]*2
                        istr = tuple(itertools.permutations(intgl[3:4]+intgl_sa[0:4]))
                        jstr = tuple(itertools.permutations(intgl[0:3]+intgl_sa[4:5]))
                        return GlypherAdd(parent, \
                            lhs=make_word(istr[95], parent), rhs=make_word(jstr[17], parent),
                            subtract=True)
        return array_to_binary_expression(parent, GlypherAdd, ex.args)
    elif isinstance(ex, sympy.core.sets.Union) :
        p = array_to_binary_expression(parent, GlypherAdd, ex.args)
        while p.get_symbol_shape() != u'\u222A' :
            p.change_alternative(1)
        return p
    elif isinstance(ex, sympy.core.mul.Mul) :
        binary = True
        lhs = _sympy_to_entity(parent, ex.args[0])
        rhs = _sympy_to_entity(parent, ex.args[1])
        bin = GlypherMul(None, lhs=lhs, rhs=rhs, \
              num_ops=len(ex.args))
        debug_print(bin.to_string())
        p = bin
    elif isinstance(ex, sympy.core.function.Derivative) :
        # Subscript or GlypherDerivative?
        operand = _sympy_to_entity(parent, ex.expr)
        if (len(ex.symbols) == 1 and len(operand.to_string())>20) :
            p = GlypherDerivative(parent, operand=operand, by=_sympy_to_entity(parent, ex.symbols[0]))
        else :
            symbols = array_to_binary_expression(parent, GlypherSpaceArray, ex.symbols)
            p = GlypherScript.subscript(parent, expression=operand, subscript=symbols)
            p.diff_mode = True
        return p
    elif isinstance(ex, sympy.core.power.Pow) :
        if str(ex.exp) == '1/2' :
            p = GlypherSqrt(parent, expression=_sympy_to_entity(parent, ex.base))
            return p
        #if str(ex.exp) == '-1' :
        #    p = GlypherFraction(parent, numerator=make_word('1', parent), denominator=_sympy_to_entity(parent, ex.base))
        #    return p
        p = GlypherScript(parent, expression=_sympy_to_entity(parent, ex.base), available=(False, False, True, False))
        p.get_target('site2').adopt(_sympy_to_entity(parent, ex.exp))

        #p = GlypherPow(parent, base=_sympy_to_entity(parent, ex.base))
        #p.get_target('exponent').adopt(_sympy_to_entity(parent, ex.exp))
        return p
    elif isinstance(ex, sympy.integrals.Integral) :
        p = Parser.make_phrasegroup(parent, 'integral')
        debug_print(ex.args[1])
        p.get_target('operand').adopt(_sympy_to_entity(parent, ex.args[0]))
        p.get_target('by').adopt(_sympy_to_entity(parent, ex.args[1][0][0]))
        p.get_target('from').adopt(_sympy_to_entity(parent, ex.args[1][0][1][0]))
        p.get_target('to').adopt(_sympy_to_entity(parent, ex.args[1][0][1][1]))
        return p
    elif isinstance(ex, sympy.concrete.summations.Sum) or isinstance(ex, sympy.concrete.products.Product) :
        p = Parser.make_phrasegroup(parent, 'summation')
        p.get_target('expression').adopt(_sympy_to_entity(parent, ex.args[0]))
        p.get_target('byvar').adopt(_sympy_to_entity(parent, ex.args[1][0][0]))
        p.get_target('from').adopt(_sympy_to_entity(parent, ex.args[1][0][1]))
        p.get_target('to').adopt(_sympy_to_entity(parent, ex.args[1][0][2]))
        return p
    elif isinstance(ex, matrices.Matrix) :
        sy_lists = ex.tolist()
        lists = [ [_sympy_to_entity(parent, cell) for cell in row] for row in sy_lists]
        p = GlypherMatrix.from_python_lists(parent, lists)
        return p
    elif isinstance(ex, sympy.core.numbers.Rational) :
        p = GlypherFraction(parent)
        p.get_target('numerator').adopt(make_word(str(abs(ex.p)), parent))
        p.get_target('denominator').adopt(make_word(str(ex.q), parent))
        if ex.p < 0 :
            p = GlypherNegative(parent, operand=p)
        return p
    elif isinstance(ex, sympy.core.function.Function) :
        p = Function.GlypherNaryFunction(parent)
        p.get_target('name').adopt(_sympy_to_entity(parent, ex.func))
        if len(ex.args) > 1 :
            bin = GlypherBinaryExpression(args, GlypherSymbol(None, ','), no_brackets=True, \
              lhs=_sympy_to_entity(parent, ex.args[0]), rhs=_sympy_to_entity(parent, ex.args[1]), \
              num_ops=len(ex.args))
            p.args.append(bin)
            binary = True
        else :
            if len(ex.args) == 1 :
                p.args.append(_sympy_to_entity(parent, ex.args[0]))
            return p
    elif isinstance(ex, sympy.core.function.FunctionClass) :
        return make_word(unicode(ex), parent)
    elif isinstance(ex, sympy.core.relational.StrictInequality) :
        return array_to_binary_expression(parent, GlypherLessThan, ex.args)
    
    if binary :
        n = -1
        for arg in ex.iter_basic_args() :
            n += 1
            if n < 2 : continue
            #bin.add_operand()
            posstr = 'pos' + str(2*n)
            garg = _sympy_to_entity(bin, arg)
            bin.get_target(posstr).append(garg)
        return p
    
    raise(RuntimeError('Could not make Glypher entity out of sympy object of type '+str(type(ex))))

def array_to_binary_expression(parent, cl, array, allow_unary=False,
                               presort=True, processor=_sympy_to_entity) :
    array = list(array)
    if presort : array.sort(sympy.core.Basic._compare_pretty)

    lhs = processor(parent, array[0])
    if not allow_unary and len(array) == 1 :
        return lhs
    rhs = processor(parent, array[1]) if len(array)>1 else None
    bie = cl(parent, lhs=lhs, rhs=rhs, num_ops=len(array))
    n = 1
    for e in array[2:] :
        n += 1
        if n < 2 : continue
        posstr = 'pos' + str(2*n)
        garg = processor(bie, e)
        bie.poss[n].append(garg)
    return bie
