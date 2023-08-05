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

def separate(join, caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) == 3 and args[1].to_string() == u'wrt' :
        wrt = args[2]
        sym = wrt.get_sympy()
        if not isinstance(sym, Dynamic.Symbol) :
            return "WRT not a sympy symbol (usu. a GlypherWord or subscripted Word)"

        op = Dynamic.together if join else Dynamic.apart 
        return interpret_sympy(None, op(args[0].get_sympy(), sym))
    elif join and len(args) == 1 :
        return interpret_sympy(None, Dynamic.together(args[0].get_sympy()))

    return "Wrong arguments"

def plot(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) == 1 :
        ret = Plot.make_plot(args[0], caret)
    elif len(args) == 3 and args[1].to_string() == u'for' and \
            args[2].am('elementof') and\
            args[2].poss[1].get_entities()[0].am('interval') :
        interval = args[2].poss[1].get_entities()[0]
        debug_print(interval.format_me())
        ret = Plot.make_plot(args[0], caret,
                             (args[2].poss[0].get_sympy(),
                              interval.get_lhs().get_sympy(),
                              interval.get_rhs().get_sympy()))

        #ret = Plot.make_plot(args[0], caret)
    else :
        return "Wrong arguments"

    return make_word('Plotted' if ret else 'Could not plot', None)

def let(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) >2 and args[1].to_string() == u'be':
        func = args[0]
        sym = func.get_sympy()
        if not isinstance(sym, Dynamic.Symbol) :
            return "LHS not a sympy symbol (usu. a GlypherWord or subscripted Word)"


        if args[2].to_string() in (u'wildcard', u'wild', u'w') :
            excl = {}
            if len(args) == 5 and args[3].to_string() == u'excluding' :
                sy = args[4].get_sympy()
                excl['exclude'] = sy if isinstance(sy, list) else [sy]

            debug_print(excl)

            g.define_symbols[sym] = \
                Dynamic.Wild(str(func._get_symbol_string(sub)), **excl)
            return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                     rhs=GlypherEntity.xml_copy(None, args[0]))

        if args[2].to_string() in (u'indexed', u'tensor', u'I') :
            shape = {}
            if len(args) == 4 :
                sy = args[3].get_sympy()
                shape['shape'] = sy if isinstance(sy, list) else [sy]

            g.define_symbols[sym] = \
                Dynamic.IndexedBase(str(func._get_symbol_string(sub)), **shape)
            return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                     rhs=GlypherEntity.xml_copy(None, args[0]))

        if args[2].to_string() in (u'index', u'i') :
            shape = {}
            if len(args) == 4 :
                sy = args[3].get_sympy()
                shape['range'] = sy

            g.define_symbols[sym] = \
                Dynamic.Idx(str(func._get_symbol_string(sub)), **shape)
            return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                     rhs=GlypherEntity.xml_copy(None, args[0]))

        return "Don't know that type"

    if len(args) != 1 :
        return "Too many arguments without 'be'"

    eq = args[0]
    if eq.am('binary_expression') and eq.get_symbol_shape() == '=' :
        lhs = eq['pos0']
        rhs = eq['pos2']
        if len(lhs.get_entities()) != 1 or len(rhs.get_entities()) != 1 :
            return "LHS or RHS wrong length"
        lhs = lhs.get_entities()[0]

        rhs = rhs.get_entities()[0]

        try :
            lhs_sym = lhs.get_sympy()
        except :
            lhs_sym = None

        if isinstance(lhs_sym, Dynamic.Symbol) :
            if rhs.am('matrix') :
                g.let_matrices[lhs_sym] = rhs.get_sympy()

                return GlypherSpaceArray(None, lhs=make_word('Defined', None), rhs=lhs.copy())

            if rhs.am('function') :
                func_sym = rhs['name'].get_sympy()
                if func_sym != lhs_sym :
                    return "Expect function name to match declared function"

                if not isinstance(func_sym, Dynamic.Symbol) :
                    return "Function name not a sympy symbol (usu. a GlypherWord or subscripted Word)"

                for arg in rhs.get_args() :
                    if not isinstance(arg.get_sympy(), Dynamic.Symbol) :
                        return "All arguments should give Sympy symbols"

                g.define_functions[func_sym] = rhs.get_sympy_args()

                return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                         rhs=rhs['name'].get_entities()[0].copy())

        if lhs.am('function') :
            func_sym = lhs['name'].get_sympy()
            if not isinstance(func_sym, Dynamic.Symbol) :
                return "Function name not a sympy symbol (usu. a GlypherWord or subscripted Word)"

            for arg in lhs.get_args() :
                if not isinstance(arg.get_sympy(), Dynamic.Symbol) :
                    return "All arguments should give Sympy symbols"

            g.let_functions[lhs['name'].get_sympy()] = \
                Dynamic.Lambda(lhs.get_sympy_args(), rhs.get_sympy())
            return GlypherSpaceArray(None, lhs=make_word('Defined', None), rhs=lhs.copy())

    elif eq.am('elementof') :
        contained_in = eq['pos2'].get_entities()[0]
        if contained_in.am('realR' ) :
            assumptions = { 'real' : True }
        elif contained_in.am('complexC' ) :
            assumptions = { 'complex' : True }
        elif contained_in.am('rationalQ' ) :
            assumptions = { 'rational' : True }
        else :
            raise RuntimeError('Unrecognized set')

        g.define_symbols[eq['pos0'].get_sympy()] = \
                Dynamic.Symbol(str(eq['pos0'].get_entities()[0]._get_symbol_string(sub)),
                                         **assumptions)

        return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                 rhs=eq['pos0'].get_entities()[0].copy())

    return "Need e.g. function with Word as name for LHS"

def match(caret, *args) :
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


def unlet(caret, *args) :
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
                                   rhs=make_word('declared', None))

    return GlypherSpaceArray(None, lhs=make_word('Undeclared', None),
                             rhs=GlypherEntity.xml_copy(None, func))

def define(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    func = args[0]

    if func.am('function') :
        func_sym = func['name'].get_sympy()
        if not isinstance(func_sym, Dynamic.Symbol) :
            return "Function name not a sympy symbol (usu. a GlypherWord or subscripted Word)"

        for arg in func.get_args() :
            if not isinstance(arg.get_sympy(), Dynamic.Symbol) :
                return "All arguments should give Sympy symbols"

        g.define_functions[func_sym.get_sympy()] = func.get_sympy_args()

        return GlypherSpaceArray(None, lhs=make_word('Defined', None),
                                 rhs=func['name'].get_entities()[0].copy())

    return "Did not fit a known Define format"

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
    if not isinstance(sym, Dynamic.Symbol) :
        return "LHS not a sympy symbol (usu. a GlypherWord or subscripted Word)"

    #sym = sympy.Symbol(str(lhs.to_string()))
    g.var_table[sym] = rhs.get_entities()[0].get_sympy()
    lhs = lhs.copy(); lhs.orphan(); lhs.set_parent(None)
    return make_phrasegroup(None, 'equality', (lhs, interpret_sympy(None,
                                                                    g.var_table[sym])))

def unset_equal(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 1 :
        return "Too many arguments"

    sym = args[0]
    symp = sym.get_sympy(sub=False)
    debug_print(g.var_table[symp])
    if not isinstance(symp, Dynamic.Symbol) or symp not in g.var_table :
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
    
    if isinstance(args[2].get_sympy(), Dynamic.Function) :
        if not args[0].am('equality') :
            return "Need equality as first argument"

        for_sym = args[2].get_sympy()

        sy = Dynamic.dsolve(args[0]['pos0'].get_sympy()-args[0]['pos2'].get_sympy(), args[2].get_sympy())
    else :
        if not (args[0].am('equality') or \
            args[0].am('semicolon_array') or args[0].am('comma_array')) :
            return "Need equality or array as first argument"
    
        sy = Dynamic.solve(args[0].get_sympy(), args[2].get_sympy())
    
    debug_print(sy)
    return interpret_sympy(None, sy)

def diff(caret, *args) :
    args = get_arg_innards(args)
    if isinstance(args, str) : return args

    if len(args) != 3 or args[1].to_string() != 'by' :
        return "Wrong arguments"

    return interpret_sympy(None, args[0].get_sympy().diff(args[2].get_sympy()))

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
