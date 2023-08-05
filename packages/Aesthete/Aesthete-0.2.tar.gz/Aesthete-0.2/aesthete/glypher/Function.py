from PhraseGroup import *
import Parser
from Word import *
from BinaryExpression import *
from Decoration import *
from sympy.core.function import *
from sympy import N

auto_bracket_funcs = \
 [  'cos', 'sin', 'tan',
    'cosh', 'sinh', 'tanh',
    '1/cos', '1/sin', '1/tan',
    '1/cosh', '1/sinh', '1/tanh',
    'acos', 'asin', 'atan',
    'acosh', 'asinh', 'atanh',
    'exp', 'log' ]
function_inverses = { 'tan' : 'atan' , 'cos' : 'acos' , 'sin' : 'asin',
                      'tanh' : 'atanh' , 'cosh' : 'acosh' , 'sinh' : 'asinh' }
function_inverses_rev = dict((v,k) for k, v in function_inverses.iteritems())

function_translation_rev = {}

function_translation = {}

def function_init() :
    global function_translation_rev
    global function_translation

    gamma_function = make_word(u'\u0393', None)
    gamma_function[0].set_italic(False)
    function_translation_rev['gamma'] = gamma_function

    dirac_delta = make_word(u'\u03b4', None)
    dirac_delta[0].set_italic(False)
    function_translation_rev['DiracDelta'] = dirac_delta

    heaviside = make_word('H', None)
    function_translation_rev['Heaviside'] = heaviside

    for fn in function_translation_rev :
        r = function_translation_rev[fn].get_sympy()
        function_translation[r] = fn

# Flip to ^-1 if we find an inverse
inversify = True
class GlypherNaryFunction(GlypherPhraseGroup) :
    args = None
    argslist = None
    spacer = None
    func_colour = (0.0, 0.5, 0.0)

    def set_sympy_func(self, sympy_func) : self.set_p('sympy_func', sympy_func)
    def get_sympy_func(self) : return self.get_p('sympy_func')
    def set_resolve(self, resolve) : self.set_p('resolve', resolve)
    def get_resolve(self) : return self.get_p('resolve')

    def check_brackets(self, name) :
        if not self.args or not self.get_resolve() : return
        try :
            collapsible = (name and name.get_repr() in auto_bracket_funcs)
        except (GlypherTargetPhraseError, ValueError, TypeError) :
            collapsible = False

        #debug_print(str(name.get_sympy()))
        self.args.set_auto_bracket(collapsible)
        debug_print(collapsible)
        if not collapsible :
            self.args.brackets_restore()
        else :
            self.args.check_collapse()
        
    def __init__(self, parent, area = (0,0,0,0), expression = None, auto_bracket = False, resolve = True) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'name')
        self.set_resolve(resolve)
        self.mes.append('function')

        name = GlypherPhrase(self)
        self.add_target(name, 'name')
        self.set_lhs_target('name')
        self.append(name)
        if resolve : name.set_bold(True)

        spacer = GlypherSpace(self, (0.125,0.3))
        self.spacer = spacer

        args = GlypherBracketedPhrase(self)
        args.set_auto_bracket(auto_bracket)
        if auto_bracket :
            args.brackets_collapse()
        else :
            args.brackets_restore()

        self.add_target(args, 'args')
        self.set_rhs_target('args')
        args.set_attachable(False)
        self.args = args
        args.no_bracket.add('function')
        self.check_brackets(expression)
        args.set_deletable(2)
        self.append(spacer)
        self.append(args)
        
        if not self.args.get_collapsed() :
            spacer.hide()

        #args.collapse_condition = lambda : \
        #    len(arglist.poss[0].get_entities())==1 and\
        #    (args.should_collapse(arglist.poss[0].get_entities()[0]) or\
        #     is_short_mul(arglist.poss[0].get_entities()[0]))

        if expression :
            name.adopt(expression)
        debug_print(args.get_auto_bracket())

        self.set_recommending(args.get_target('expression'))
    
    def get_args(self) :
        if len(self.args.get_entities()) == 1 :
            if self.args.get_entities()[0].am('binary_expression') and (\
                    self.args.get_entities()[0].get_symbol_shape() == ',' or \
                    self.args.get_entities()[0].get_symbol_shape() == ';' ) :
                arglist = self.args.get_entities()[0]
                args = arglist.get_args()
            else :
                args = [self.args.get_entities()[0]]
        else :
            args = self.args.get_entities()
        return args

    def get_sympy_args(self) :
        return [arg.get_sympy() for arg in self.get_args()]

    def get_sympy(self) :
        args = self.get_sympy_args()
        try :
            if self.get_sympy_func() :
                try:
                    return self.get_sympy_func()(*args)
                except TypeError as e :  # hack to get mpmath functions working
                    new_args = []
                    for arg in args:
                        new_args.append(N(arg))
                    return self.get_sympy_func()(*new_args)
            else :
                debug_print('x')
                f = Function(str(self.get_target('name').to_string()))
                return f(*args)
        except RuntimeError as e :
            debug_print(e)
            raise GlypherTargetPhraseError(self, "Could not evaluate function : %s" % str(e))

    #check_inverse = re.compile('\(script\|expression=([^|]+)|site0=\|site1=\|site2=-1\|site3=\)')
    def child_change(self) :
        GlypherPhraseGroup.child_change(self)
        if not self.get_resolve() : return

        name = self.get_target('name')

        debug_print(name.to_string())
        try :
            name_sympy = name.get_sympy()
        except :
            name_sympy = None

        if name_sympy is not None and \
                isinstance(name_sympy, Lambda) :
            self.set_sympy_func(name_sympy)
        else :
            if name_sympy in function_translation :
                test = function_translation[name_sympy]
            else :
                try :
                    test = name.get_repr()
                except :
                    test = None
                else :
                    if test[0:2] == '1/' and len(name.get_entities())==1 and name.get_entities()[0].am('script') and test[2:] in function_inverses :
                        test = function_inverses[test[2:]]
            #test = sympy.core.sympify(test)

            if test is not None :
                func = Dynamic.get_sympy_function(test)
                if func is None :
                    func = Dynamic.get_library_function(test)
                    if func is not None :
                        self.func_colour = (0.0, 0.5, 0.5)
                else :
                    self.func_colour = (0.0, 0.5, 0.0)
    
                self.set_sympy_func(func)

        if self.get_sympy_func() :
            name.set_rgb_colour(self.func_colour)
        else :
            name.set_rgb_colour(None)

        self.check_brackets(name)

        #new_auto = name.to_string() in auto_bracket_funcs
        #if self.args and new_auto != self.args.auto_bracket :
        #    self.args.auto_bracket = new_auto
        #    self.args.check_collapse()

        if self.args and self.spacer :
            if self.args.get_collapsed() :
                self.spacer.show()
            else :
                self.spacer.hide()

        self.make_simplifications()
    
    _simplifying = False
    def make_simplifications(self) :
        if self._simplifying or not self.get_resolve() : return
        self._simplifying = True

        if len(self.get_target('name').get_entities()) == 1 :
            e = self.get_target('name').get_entities()[0]
            est = e.get_repr()
            if inversify and e.am('word') and est in function_inverses.values() :
                e.orphan()
                key = function_inverses_rev[est]
                debug_print('found inverse function')
                s = GlypherScript(self, available=(False,False,True,False))
                s.get_target('expression').append(make_word(key, s))
                s.get_target('site2').append(GlypherNegative(s,
                                                             operand=make_word('1',
                                                                                 s)))
                self.get_target('name').append(s)

        self._simplifying = False

    def delete(self, sender=None, if_empty=True) :
        parent = self.get_up()
        if self.get_resolve() and len(self.get_target('name').get_entities()) > 0 :
            self.get_target('name').elevate_entities(parent, to_front=True)
            self.feed_up()
        GlypherPhraseGroup.delete(self, sender=sender)
        return parent

class GlypherOrder(GlypherNaryFunction) :
    def __init__(self, parent, order = None) :
        O_sym = GlypherSymbol(parent, 'O', italic=False)
        O_sym.set_name('O_sym')
        GlypherNaryFunction.__init__(self, parent, expression=O_sym, resolve=False)
        self.mes.append('order')
        O_sym.set_rgb_colour((0, 0.5, 0.3))
        self.set_default_entity_xml()
        self.args.adopt(order)
    
    def get_sympy(self) :
        return sympy.series.order.Order(self.get_args()[0].get_sympy())

class GlypherSpecialFunction(GlypherNaryFunction) :
    def __init__(self, parent, what, expression, name_entity, sympy_func,
                             auto_bracket, num_args=1) :
        GlypherNaryFunction.__init__(self, parent, area=(0,0,0,0), expression=expression,
                 auto_bracket=auto_bracket, resolve=False)
        self.mes.append('special_function')
        self.mes.append(what)

        self.ignore_targets.append("name")

        xml = ET.ElementTree(name_entity.get_xml())
        name_entity = Parser.parse_phrasegroup(self["name"], xml,
                                        top=False)
        name_entity.set_rgb_colour((1.0, 0.6, 0.6))
        self["name"].adopt(name_entity)
        self["name"].set_attachable(False, children_too=True)
        self["name"].set_enterable(False, children_too=True)
        self.set_lhs_target("args")
        self.set_rhs_target(None)
        self.set_sympy_func(sympy_func)

        if num_args > 1 :
            self["args"].adopt(GlypherCommaArray(self, lhs=None, rhs=None,
                                               num_ops=num_args))
            self["args"].set_enterable(False)

# sympy_func takes form
# f(i,j,*args)
class GlypherIndexedFunction(GlypherNaryFunction) :
    def __init__(self, parent, what, expression, name_entity, sympy_func,
                              auto_bracket, num_args=1,
                              active_sites=(True,False,True,False)) :
        GlypherNaryFunction.__init__(self, parent, area=(0,0,0,0), expression=expression,
                 auto_bracket=auto_bracket, resolve=False)
        self.mes.append('indexed_function')
        self.mes.append(what)

        self.ignore_targets.append("name")

        xml = ET.ElementTree(name_entity.get_xml())
        name_entity = Parser.parse_phrasegroup(self["name"], xml,
                                        top=False)
        name_entity.set_rgb_colour((1.0, 0.6, 0.6))
        script = GlypherScript(parent, area=(0,0,0,0), expression=name_entity,
                                   available=active_sites)
        script.set_annotate(False)
        self["name"].adopt(script)
        self["name"].set_enterable(False)
        self["name"].set_attachable(False)
        script["expression"].set_attachable(False, children_too=True)
        script["expression"].set_enterable(False, children_too=True)

        sites = []
        for i in range(0,4) :
            if active_sites[i] :
                sites.append(script["site"+str(i)])
                self.add_target(script["site"+str(i)], str(i))

        self.set_lhs_target("args")
        self.set_rhs_target(None)
        self.set_sympy_func(lambda *args : \
                          sympy_func(*(tuple(map(lambda s:s.get_sympy(),sites))+args)))

        if num_args > 1 :
            self["args"].adopt(GlypherCommaArray(self, lhs=None, rhs=None,
                                               num_ops=num_args))
            self["args"].set_enterable(False)

# sympy_func takes form
# f(i,j,*args)
class GlypherTrigFunction(GlypherIndexedFunction) :
    @staticmethod
    def _eval_sympy_func(sympy_func, inv_sympy_func, i, *args) :
        if i is None :
            return sympy_func(*args)
        elif i == -1 :
            if inv_sympy_func is None :
                raise RuntimeError('Don\'t know inverse')
            else :
                return inv_sympy_func(*args)
        return sympy_func(*args)**i

    def __init__(self, parent, what, expression, name_entity, sympy_func,
                              inv_sympy_func, auto_bracket, num_args=1) :
        sympy_func_new = lambda i, *args : \
            GlypherTrigFunction._eval_sympy_func(sympy_func, inv_sympy_func, i, *args)
        GlypherIndexedFunction.__init__(self, parent, 'trig_function', expression=expression,
                 name_entity=name_entity, sympy_func=sympy_func_new,
                                        auto_bracket=auto_bracket,
                                        num_args=num_args, active_sites=(False,
                                                                        False,
                                                                         True,
                                                                         False))
        self.mes.append(what)

    _simplifying = False
    def make_simplifications(self) :
        GlypherIndexedFunction.make_simplifications(self)

        if self._simplifying :
            return

        self._simplifying = True

        debug_print(1)
        if self.included() and self.get_parent().am('target_phrase') :
            debug_print(2)
            p = self.get_parent().get_phrasegroup()
            if p.mes[-1] == 'script' and p.get_pow_mode() and \
               p.get_available() == [False, False, True, False] and \
               p.included() :
                debug_print(3)
                debug_print(p.get_parent())
                if len(p["site2"]) == 1 :
                    s = p["site2"].get_entities()[0]
                    debug_print(p.get_parent())
                    try :
                        t = self["2"].get_sympy()
                        exe = False
                        if t is None :
                            debug_print(p.get_parent())
                            s.orphan()
                            self["2"].adopt(s)
                            exe = True
                        elif s.am('word') and s.is_num() and s.get_sympy() != -1 :
                            debug_print(s.get_sympy())
                            debug_print(t)
                            t *= s.get_sympy()
                            debug_print(t)
                            s.orphan()
                            self["2"].adopt(Interpret.interpret_sympy(self, t))
                            exe = True

                        if exe :
                            self.orphan()
                            p.get_parent().exchange(p, self)
                            self.set_recommending(self["args"])
                    except RuntimeError as e:
                        debug_print(e)
                        pass
                else :
                    self.orphan()
                    p.get_parent().exchange(p, self)
                    self.set_recommending(self["2"])
        self._simplifying = False

    @classmethod
    def parse_element(cls, parent, root, names, targets, operands, recommending, lead,
                  add_entities, am=None, top=True) :
        sympy_code = root.find('sympy')
        sympy_func = Dynamic.text_to_func(sympy_code.text.strip())
        inv_sympy_code = root.find('sympy_inverse')

        if inv_sympy_code is None :
            inv_sympy_func = None
        else :
            inv_sympy_func = Dynamic.text_to_func(inv_sympy_code.text.strip())

        what = root.tag
        name_entity = make_word(root.get('name'), parent)
        auto_bracket = root.get('auto_bracket') == 'True'
        num_args = root.get('num_args')
        if num_args is None :
           num_args = 1
        else :
            num_args = int(num_args)

        fn = cls(parent, what, None, name_entity, sympy_func, inv_sympy_func, auto_bracket, num_args)

        return fn

def unicode_function_factory(what, name, sympy_func, auto_bracket=False, num_args=1,
                             auto_italicize=True) :
    maker = lambda p : GlypherSpecialFunction(p, what,
            None, make_word(name, p, auto_italicize=auto_italicize), sympy_func,
            auto_bracket=auto_bracket, num_args=num_args)
    g.phrasegroups[what] = maker
def indexed_function_factory(what, name, sympy_func, auto_bracket=False, num_args=1,
                             auto_italicize=True,
                             active_sites=(True,False,True,False)) :
    maker = lambda p : GlypherIndexedFunction(p, what,
            None, make_word(name, p, auto_italicize=auto_italicize), sympy_func,
            auto_bracket=auto_bracket, num_args=num_args,
            active_sites=active_sites)
    g.phrasegroups[what] = maker

g.phrasegroups['function'] = GlypherNaryFunction
g.phrasegroups['special_function'] = GlypherSpecialFunction
g.phrasegroups['indexed_function'] = GlypherIndexedFunction
g.phrasegroups['trig_function'] = GlypherTrigFunction
g.phrasegroups['order'] = GlypherOrder
unicode_function_factory('im', u'\u2111',
  sympy.functions.elementary.complexes.im, True)
unicode_function_factory('re', u'\u211C',
  sympy.functions.elementary.complexes.re, True)
unicode_function_factory('gamma', u'\u0393',
  sympy.functions.special.gamma_functions.gamma)
indexed_function_factory('Ylm', u'Y',
  sympy.functions.Ylm, num_args=2)
unicode_function_factory('dirac_delta', u'\u03B4',
  sympy.functions.special.delta_functions.DiracDelta)
unicode_function_factory('heaviside', u'H',
  sympy.functions.special.delta_functions.Heaviside)
Parser.parse_element_fns['trig_function'] = GlypherTrigFunction.parse_element
#g.phrasegroups['bessel_j'] = unicode_function_factory(u'J',
#  sympy.functions.special.bessel.bessel_j, active_sites=(False,False,True,False))
