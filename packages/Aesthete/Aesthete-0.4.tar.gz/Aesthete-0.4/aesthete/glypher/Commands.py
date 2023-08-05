import sympy
import Plot
import copy
import Entity
from Interpret import *
from BinaryExpression import *
from PhraseGroup import *
try :
    from sympy.solvers import ode
except :
    print "Version of sympy too old; you may have subsequent problems!"

def get_arg_innards(args) :
    return args

    inns = []
    for arg in args :
        if len(arg.get_entities()) != 1 :
            return "Argument "+str(args.index(arg))+ " '"+str(arg.to_string())+"' contains multiple/zero entities"
        inns.append(arg.get_entities()[0])
    return inns

def source(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"
    
    ret = Plot.make_source(args[0], caret)

    return make_word('Successfully sourced' if ret is not None else 'Source-making unsuccessful', None)

def plot(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"
    
    ret = Plot.make_plot(args[0], caret)

    return make_word('Plotted' if ret else 'Could not plot', None)

def let(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"

    eq = args[0]
    if not eq.am('binary_expression') or eq.get_symbol_shape() != '=' :
        return "Expected equality"
    lhs = eq['pos0']
    rhs = eq['pos2']
    if len(lhs.get_entities()) != 1 or len(rhs.get_entities()) != 1 :
        return "LHS or RHS wrong length"
    lhs = lhs.get_entities()[0]

    if lhs.am('function') and len(lhs['name'].get_entities()) == 1 and \
            lhs['name'].get_entities()[0].am('word') :
        for arg in lhs.get_args() :
            if not arg.am('word') :
                return "All arguments should be Words"

        g.let_functions[lhs['name'].get_sympy()] = \
            sympy.core.function.Lambda(lhs.get_sympy_args(), rhs.get_sympy())
        return GlypherSpaceArray(None, lhs=make_word('Defined', None), rhs=lhs.copy())

def match(caret, *args) :
    debug_print("Hi")
    args = get_arg_innards(args)
    if isinstance(args, str) :
        return args

    if len(args) != 3 or args[1].to_string() != u'in' :
        return "Format for match is 'Match A in B'"

    resp = args[2].get_sympy().match(args[0].get_sympy())
    if resp is not None :
        return interpret_sympy(None, resp)
    else :
        return GlypherSpaceArray(None, lhs=make_word('No', None),
                                       rhs=make_word('match', None))


def undefine(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) :
        return args

    func = args[0]

    sy = func.get_sympy(ignore_func=True)
    if sy in g.define_symbols :
        del g.define_symbols[sy]
    elif sy in g.define_functions :
        del g.define_functions[sy]
    elif sy in g.let_functions :
        del g.let_functions[sy]
    else :
        return GlypherSpaceArray(None, lhs=make_word('Not', None),
                                   rhs=make_word('defined', None))

    return GlypherSpaceArray(None, lhs=make_word('Undefined', None),
                             rhs=GlypherEntity.xml_copy(func))

def define(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    func = args[0]

    if len(args) in (3,5) and args[1].to_string() == u'as':
        if not func.am('word') :
            return "Need Word before 'as'"

        if args[2].to_string() in (u'wildcard', u'wild', u'w') :
            excl = {}
            if len(args) == 5 and args[3].to_string() == u'excluding' :
                sy = args[4].get_sympy()
                excl['exclude'] = sy if isinstance(sy, list) else [sy]

            debug_print(excl)

            g.define_symbols[func.get_sympy()] = \
                sympy.core.symbol.Wild(str(func._get_symbol_string(sub)), **excl)
            return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                     rhs=GlypherEntity.xml_copy(args[0]))

        return "Don't know that type"

    if len(args) != 1 :
        return "Too many arguments without 'as'"

    if func.am('function') and len(func['name'].get_entities()) == 1 and \
            func['name'].get_entities()[0].am('word') :
        for arg in func.get_args() :
            if not arg.am('word') :
                return "All arguments should be Words"

        g.define_functions[func['name'].get_sympy()] = func.get_sympy_args()

        return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                 rhs=func['name'].get_entities()[0].copy())

    elif func.am('less_than') and func.get_symbol_shape() == u'\u220A' :
        contained_in = func['pos2'].get_entities()[0]
        if contained_in.am('realR' ) :
            assumptions = { 'real' : True }
        elif contained_in.am('complexC' ) :
            assumptions = { 'complex' : True }
        elif contained_in.am('rationalQ' ) :
            assumptions = { 'rational' : True }

        g.define_symbols[func['pos0'].get_sympy()] = \
                sympy.core.symbol.Symbol(str(func['pos0'].get_entities()[0]._get_symbol_string(sub)),
                                         **assumptions)

        return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                 rhs=func['pos0'].get_entities()[0].copy())

def set_equal(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"

    eq = args[0]
    if not eq.am('binary_expression') or eq.get_symbol_shape() != '=' :
        return "Expected equality"
    lhs = eq.get_target('pos0')
    rhs = eq.get_target('pos2')
    if len(lhs.get_entities()) != 1 or len(rhs.get_entities()) != 1 :
        return "LHS or RHS wrong length"
    lhs = lhs.get_entities()[0]

    sym = lhs.get_sympy()
    if not isinstance(sym, sympy.core.symbol.Symbol) :
        return "LHS not a sympy symbol (usu. a GlypherWord or subscripted Word)"

    #sym = sympy.Symbol(str(lhs.to_string()))
    g.var_table[sym] = rhs.get_entities()[0].get_sympy()
    lhs = lhs.copy(); lhs.orphan(); lhs.set_parent(None)
    return GlypherEquality(None, lhs, interpret_sympy(None, g.var_table[sym]))

def unset_equal(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"

    sym = args[0]
    symp = sym.get_sympy(sub=False)
    debug_print(g.var_table[symp])
    if not isinstance(symp, sympy.core.symbol.Symbol) or symp not in g.var_table :
        return "Unrecognized operand"
    
    del g.var_table[symp]
    return make_word('Success!', None)

def doit(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args
    g.dit = args[0].am('Integral')

    if len(args) != 1 :
        return "Too many arguments"
    return interpret_sympy(None, args[0].get_sympy().doit())

def solve(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    debug_print(map(str, args))
    if len(args) != 3 :
        return "Need 3 arguments"
    if args[1].to_string() != 'for' :
        return "Need 'for'"
    
    if isinstance(args[2].get_sympy(), sympy.core.function.Function) :
        if not args[0].am('equality') :
            return "Need equality as first argument"

        sy = ode.dsolve(args[0]['pos0'].get_sympy()-args[0]['pos2'].get_sympy(), args[2].get_sympy())
    else :
        if not (args[0].am('equality') or \
            args[0].am('semicolon_array') or args[0].am('comma_array')) :
            return "Need equality or array as first argument"
    
        sy = sympy.solvers.solve(args[0].get_sympy(), args[2].get_sympy())
    
    debug_print(sy)
    return interpret_sympy(None, sy)

def diff(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"
    return interpret_sympy(None, args[0].get_sympy().doit())

def sub(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 3 :
        return "Wrong argument number"
    if args[1].to_string() != 'into' :
        return "Incorrect syntax; don't forget 'into'"
    if not args[0].am('equality') :
        return "First argument should be an equality"

    subargs = get_arg_innards(args[0].get_args())
    if isinstance(args, str) : return subargs

    return interpret_sympy(None, args[2].get_sympy().subs(subargs[0].get_sympy(), subargs[1].get_sympy()))

def series(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) == 6 :
        if args[1].to_string() != 'about' :
            return "Incorrect syntax; don't forget 'about'"
        if args[3].to_string() != 'to' :
            return "Incorrect syntax; don't forget 'to'"
        if args[4].to_string() != 'order' :
            return "Incorrect syntax; don't forget 'order'"
        if not args[2].am('equality') :
            return "Second argument should be an equality"
        if not args[5].am('word') and args[5].is_num() :
            return "Third argument should be an integer"
        arg_about = 2; arg_order = int(args[5].to_string())
    elif len(args) == 3 and args[1].to_string() == 'about' :
        if not args[2].am('equality') :
            return "Second argument should be an equality"
        arg_about = 2; arg_order = 4
    elif len(args) == 3 :
        arg_about = 1; arg_order = int(args[2].to_string())
    elif len(args) == 2 :
        arg_about = 1; arg_order = 4
    elif len(args) == 1 :
        return interpret_sympy(None, args[0].get_sympy().expand(**g.expand))
    else :
        return "Wrong argument number"

    subargs = get_arg_innards(args[arg_about].get_args())
    if isinstance(args, str) : return subargs

    debug_print((str(args[0].get_sympy()), str(subargs[0].get_sympy()), subargs[1].get_sympy().evalf(), arg_order))
    return interpret_sympy(None, args[0].get_sympy().series(subargs[0].get_sympy(), subargs[1].get_sympy().evalf(), arg_order))

def operation_command(function, caret, *args) :
    '''Pass the remainder of a SpaceArray as a series of sympy args to a
    function.'''

    args = get_arg_innards(args)
    if isinstance(args, str) :
        return args

    sympy_args = [arg.get_sympy() for arg in args]
    sympy_resp = function(*sympy_args)

    return interpret_sympy(None, sympy_resp)

def do_substitutions_from_list(expr, csl) :
        debug_print(expr)
        if csl.am('equality') :
            subargs = get_arg_innards(csl.get_args())
            return expr.get_sympy().subs(subargs[0].get_sympy(), subargs[1].get_sympy())
        elif csl.am('comma_array') :
            subargs = get_arg_innards(csl.get_args())
            expr = expr.get_sympy()
            for a in subargs :
                if not a.am('equality') : return "Should be a comma-separated list of equalities!"
                subsubargs = get_arg_innards(a.get_args())
                debug_print(expr)
                expr = expr.subs(subsubargs[0].get_sympy(),
                                             subsubargs[1].get_sympy())
            return expr
        else :
            return "Expected an equality, or comma-separated list of equalities"
def evalf(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) == 1 :
        return interpret_sympy(None, args[0].get_sympy().evalf())
    elif len(args) == 3 and args[1].to_string() == 'at' :
        dsfl = do_substitutions_from_list(args[0], args[2])
        return interpret_sympy(None, dsfl) if isinstance(dsfl, str) else interpret_sympy(None, dsfl.evalf())
    else : return "Wrong number of arguments or need an 'at'"

def limit(caret, *args) :
    return None
