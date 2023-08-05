import glypher as g
import time
import copy
from ..utils import debug_print
from PhraseGroup import *
import sympy.functions.elementary.exponential as i_func
from sympy import Mul as sympy_mul
from sympy import Pow as sympy_power
from sympy.core.numbers import NegativeOne as sympy_negone

from gutils import float_cmp as fcmp

#nary_sympy_exprs = (u'+',u'-',u',',u' ',u'*', u'\u00B7', u'\u00D7', u';')

class GlypherNegative(GlypherPhraseGroup) :
    associative = False

    def __init__(self, parent, area = (0,0,0,0), operand = None) :
        GlypherPhraseGroup.__init__(self, parent, [], area)
        self.mes.append('negative')
        self.set_bodmas_level(100)

        neg = GlypherPhrase(self); sign = GlypherSymbol(neg, '-'); neg.adopt(sign)
        neg.set_enterable(False); neg.set_attachable(False)

        expr = GlypherBracketedPhrase(self)
        #expr = GlypherPhrase(self)
        expr.set_collapse_condition(lambda : not (len(expr.get_entities())==1 and expr.get_entities()[0].am('add')))
        #expr.set_bodmas_sensitivity(0)

        self.append(neg)
        self.append(expr)
        self.set_lead(expr, GLYPHER_PG_LEAD_ALL)

        self.add_target(expr, 'expression')
        self.set_rhs_target('expression')
        expr.set_deletable(3)
        #self.set_expr('expression')

        if operand is not None :
            self.get_target('expression').adopt(operand)
    
    def get_sympy(self) :
        # apparently how sympy renders negative numbers
        debug_print(self.get_target('expression').get_sympy())
        return sympy_mul(sympy_negone(), self.get_target('expression').get_sympy())

    _orphaning = None
    def make_simplifications(self) :
        """Absorb an inner suffix into this one."""

        if self.included() and self._orphaning is None :
            if len(self['expression']) == 1 and \
               self['expression'].get_entities()[0].am('negative') and \
               len(self['expression'].get_entities()[0]['expression'])==1 :
                p = self.get_parent()
                p.suspend_recommending()
                neg = self['expression'].get_entities()[0]['expression'].get_entities()[0]
                self._orphaning = neg
                neg.orphan()
                p.exchange(self, neg)
                self._orphaning = None
                p.resume_recommending()

class GlypherCumulativeSuffix(GlypherPhraseGroup) :
    suffix_shape = None

    def is_wordlike(self) :
        if not self.included() :
            return self.get_p('wordlike')

        wordlike = len(self["operand"]) == 1 and self["operand"][0].is_wordlike()
        
        old_wordlike = self.get_p('wordlike')
        if wordlike != old_wordlike :
            self.set_p('wordlike', wordlike) #FIXME: gotta be a better way of doing this
            self.child_change()
        return wordlike

    def child_change(self) :
        GlypherPhraseGroup.child_change(self)
        self.is_wordlike()

    def __init__(self, parent, shape, operand = None) :
        GlypherPhraseGroup.__init__(self, parent)
        self.mes.append('cumulative_suffix')

        self.set_bodmas_level(100)
        self.suffix_shape = shape

        op_phrase = GlypherBracketedPhrase(self)
        self.append(op_phrase)
        self.add_target(op_phrase, 'operand')
        self.set_lhs_target('operand')
        op_phrase.set_deletable(3)

        suffix_phrase = GlypherPhrase(self)
        self.suffix_phrase = suffix_phrase
        suffix_phrase.set_enterable(False)
        suffix_phrase.set_attachable(False)
        self.add_suffix()

        self.append(suffix_phrase)

        if operand is not None :
            self['operand'].adopt(operand)

        self.set_recommending(self)

    def set_lhs(self, lhs) :
        GlypherPhraseGroup.set_lhs(self, lhs)
        self.set_recommending(self)

    def add_suffix(self) :
        new_suffix = GlypherSymbol(self.suffix_phrase,
                                   self.suffix_shape)
        self.suffix_phrase.append(new_suffix)

    _orphaning = None
    def make_simplifications(self) :
        """Absorb an inner suffix into this one."""

        if self.included() and self._orphaning is None :
            operand_tgt = self["operand"]
            # Check whether we have exactly one of us as operand
            if len(operand_tgt) == 1 and \
                    operand_tgt[0].am('cumulative_suffix') and \
                    operand_tgt[0].suffix_shape == self.suffix_shape :
                operand = operand_tgt[0]
                
                # Ensure we don't trigger a loop
                self._orphaning = operand

                self.suspend_recommending()

                # Get the internal entit(ies)
                operand.orphan()
                operand["operand"].elevate_entities(operand_tgt)

                # Check the internal suffix count
                n = len(operand.suffix_phrase)

                # Add another visual suffix
                for i in range(0, n) :
                    self.add_suffix()

                self.resume_recommending()

                # Reset _orphaning for next occasion
                self._orphaning = None

class GlypherPrime(GlypherCumulativeSuffix) :
    def __init__(self, parent, operand = None) :
        GlypherCumulativeSuffix.__init__(self, parent, u'\u2032', operand)
        self.mes.append('prime')

    def get_sympy(self) :
        '''Return nth derivative of operand.'''

        # Get core expression
        ex = self['operand'].get_sympy()

        # Ensure this is the type of thing we're looking for
        if not hasattr(ex, "func") or len(ex.args) != 1 :
            raise GlypherTargetPhraseError(self,
                'Need to provide a differentiable function of a single variable.')

        # Differentiate as many times as there are primes
        by = ex.args[0]
        for level in range(0, len(self.suffix_phrase)) :
            ex = sympy.core.function.diff(ex, by)

        return ex

class GlypherBinaryExpression(GlypherPhraseGroup) :
    also_adopt_symbol_shapes = ()
    def set_symbol_shape(self, symbol_shape) : self.set_p('symbol_shape', symbol_shape)
    def get_symbol_shape(self) : return self.get_p('symbol_shape')
    def set_associative(self, associative) : self.set_p('associative', associative)
    def get_associative(self) : return self.get_p('associative')
    def set_op_count(self, op_count) : self.set_p('op_count', op_count)
    def get_op_count(self) : return self.get_p('op_count')
    def set_use_space(self, use_space) : self.set_p('use_space', use_space)
    def get_use_space(self) : return self.get_p('use_space')
    def set_allow_unary(self, allow_unary) : self.set_p('allow_unary', allow_unary)
    def get_allow_unary(self) : return self.get_p('allow_unary')

    syms = None
    poss = None
    poser = None
    p_sort = lambda s,x,y : fcmp(x.config[0].get_bbox()[0], y.config[0].get_bbox()[0])

    def make_new_symbol(self) :
        #sym = self.ref_symbol.copy()
        sym = GlypherSymbol(self, self.get_symbol_shape())
        sym.orphan()
        return sym

    def _set_pos_properties(self, pos) :
        pos.set_deletable(2) # Send delete requests for rhs to me
        if self.poser is GlypherBODMASBracketedPhrase :
            pos.no_bracket.add('pow')
            pos.set_bodmas_sensitivity(self.get_bodmas_level())
        
    _suspend_change_check = False
    def check_combination(self, shape) :
        chg = False

        if self._suspend_change_check :
            return False

        self._suspend_change_check = True
        for sym in self.syms :
            chg = chg or self.syms[sym].get_entities()[0].check_combination(shape)
        self._suspend_change_check = False

        return chg

    def get_xml(self, name = None, top = True, targets = None, full = False) :
        root = GlypherPhraseGroup.get_xml(self, name, top, targets, full)
        if self.get_p('variable_ops') :
            root.set('num_ops', str(self.get_op_count()))
        return root
        
    _suspend_change_alternative = False
    def change_alternative(self, dir = 1) :
        if self._suspend_change_alternative :
            return False

        self._suspend_change_alternative = True
        k= len(self.syms)
        success = False
        sym_ind = 1 if self.get_use_space() else 0
        syms = [self.ref_symbol] + \
               [self.syms[self.syms.keys()[i]].get_entities()[sym_ind] for i in range(0, k)]
        for sym in syms :
            #sb = sym.get_entities()[0]
            success = sym.change_alternative(dir) or success

        debug_print(self.ref_symbol.to_string())
        self.set_symbol_shape(self.ref_symbol.to_string())

        self._suspend_change_alternative = False

        if not success and self.included() :
            return self.get_parent().change_alternative(dir)
        return success

    def __init__(self, parent, symbol, area = (0,0,0,0), lhs = None, rhs = None, allow_unary = False, no_brackets = False,
            num_ops = 2, use_space = False, default_shortening = True,
                 variable_ops=False) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'pos0')
        self.mes.append('binary_expression')

        self.add_properties({'op_count' : 1, 'associative' : False, 'use_space' : False, 'allow_unary' : False,
                             'symbol_shape' : u'\u00ae', 'use_space' : False,
                             'bodmas_level' : 0, 'breakable' : True,
                             'auto_ascend' : True, 'variable_ops' : False })
        self.set_use_space(use_space)
        self.set_p('variable_ops', variable_ops)

        self.syms = {}; self.poss = {}
        self.set_allow_unary(allow_unary)
        self.poser = GlypherPhrase if no_brackets else GlypherBracketedPhrase
        self.default_shortening = default_shortening

        self.characteristics.append('_bodmasable')
        self.set_symbol_shape(symbol.to_string())
        self.ref_symbol = symbol.copy()
        self.set_associative(g.get_associative(self.get_symbol_shape()))
        bodmas_level = g.get_bodmas(self.get_symbol_shape())
        self.set_bodmas_level(bodmas_level)

        pos0 = self.poser(self); pos0.name = 'pos0'
        self._set_pos_properties(pos0)
        self.add_target(pos0, 'pos0')
        self.poss[0] = pos0
        self.set_lhs_target('pos0')
        self.append(pos0, align=('l','m'))

        if lhs is not None :
            self.get_target('pos0').adopt(lhs)

        self.set_recommending(pos0)

        if (not allow_unary) or num_ops > 1 or rhs is not None :
            for i in range(1, num_ops) :
                self.append_operand()
                debug_print(i)
            debug_print(num_ops)
            self.set_rhs_target('pos2')

            if rhs is not None :
                self.set_rhs(rhs)
                if lhs is None :
                    self.set_recommending(self.get_target('pos0').IN())
            else :
                if lhs is None :
                    self.set_recommending(self.get_target('pos0').IN())
                else :
                    self.set_recommending(self.get_target('pos2').IN())

    def get_args(self) :
        tgts = [self.get_target('pos'+str(2*p)) for p in self.poss.keys()]
        tgts = filter(lambda t : len(t.entities)==1, tgts)
        return [tgt.get_entities()[0] for tgt in tgts]

    def _get_sympy_args(self) :
        return [a.get_sympy() for a in self.get_args()]

    def _reorder_pos_arrays(self) :
        p_sort = self.p_sort
        ns = self.syms.values(); np = self.poss.values()
        ns.sort(p_sort)
        np.sort(p_sort)
        for i in range(0,len(self.poss)) :
            posname = 'pos'+str(2*i)
            self.poss[i] = np[i]
            self.poss[i].set_name(posname)
            self.target_phrases[posname] = self.poss[i].IN()
            if i > 0 :
                self.syms[i] = ns[i-1]
                self.syms[i].set_name('sym'+str(2*i-1))
                debug_print(self.syms[i].config[0].bbox)

    def _move_along_one(self, from_pos) :
        offset = self.poss[self.get_op_count()-1].config[0].bbox[2] - self.poss[self.get_op_count()-2].config[0].bbox[2]
        for i in range(from_pos, self.get_op_count()) :
            self.poss[i].translate(offset, 0, quiet=True)
            self.syms[i].translate(offset, 0, quiet=True)
        self.recalc_bbox()
        self._reorder_pos_arrays()
    def add_operand(self, after = None) :
        ret = self.append_operand()
        if after is not None and after < self.get_op_count()-2 :
            old_pos = self.syms[after+1].config[0].bbox[0]
            self._move_along_one(after+1)
            to_start = self.syms[self.get_op_count()-1].config[0].bbox[0] - old_pos
            #debug_print(self.syms[self.op_count-1].config[0].bbox)
            #debug_print(self.syms[after].config[0].bbox)
            self.syms[self.get_op_count()-1].translate(-to_start, 0, quiet=True)
            self.poss[self.get_op_count()-1].translate(-to_start, 0, quiet=True)
            self._reorder_pos_arrays()
        self.recalc_bbox()
        debug_print(self.get_op_count())
        return ret
        #offset = self.poss[self.op_count-1].config[0].bbox[2] - self.poss[self.op_count-2].config[0].bbox[2]
        #to_start = self.syms[self.op_count-1].config[0].bbox[0] - self.syms[after+1].config[0].bbox[0]
        #for i in range(after+1, self.op_count-1) :
        #    self.poss[i].translate(offset, 0, quiet=True)
        #    self.syms[i].translate(offset, 0, quiet=True)
        #self.syms[self.op_count-1].translate(-to_start, 0, quiet=True)
        #self.poss[self.op_count-1].translate(-to_start, 0, quiet=True)
        #return ret

        #if after != None and after < self.op_count - 1 :
        #    posold = self.poss[self.op_count-1]
        #    symold = self.syms[self.op_count-1]
        #    if posold.am('bracketed_phrase') : posold.suspend_collapse_checks()
        #    posold.empty()
        #    symold.empty()
        #    #debug_print(after)
        #    #debug_print(self.op_count)
        #    for m in range(after+1, self.op_count-1) :
        #        nm = self.op_count-2+after+1 - m
        #        debug_print(nm)
        #        posnew = self.poss[nm]
        #        posnew.suspend_collapse_checks()
        #        symnew = self.syms[nm]
        #        #debug_print(posold.entities)
        #        #debug_print(posold.to_string())
        #        #posold.elevate_entities(posnew)
        #        posnew.elevate_entities(posold)
        #        #posnew.empty()
        #        #posold.append(GlypherSymbol(None, 'r'))
        #        symnew.elevate_entities(symold)
        #        if posold.am('bracketed_phrase') : posold.resume_collapse_checks()
        #        posold = posnew; symold = symnew
        #    symbol = self.make_new_symbol()
        #    sym = self.syms[after+1]
        #    sym.adopt(symbol)
        #    sym.set_enterable(False)
        #    sym.set_attachable(False)
        #    pphr = self.poss[after+1]
        #    #self.add_target(pphr, 'pos'+str(2*after+2))
        #    return pphr
        #return ret
            
    _example_sym = None
    _example_pos = None
    def append_operand(self) :
        if len(self.syms) > 0 and \
           not self.get_p('variable_ops') :
            return None
        self.set_op_count(self.get_op_count()+1)
        index = 2*(self.get_op_count()-1)
        sname = 'sym'+str(index-1)
        pname = 'pos'+str(index)
        debug_print(pname)
        #pds = {}
        #pds[sname] = { 'x' : index-1 , 'y' : 0, 'fs' : 1, 'ls' : 1, 'a' : ('l','m'), 'g' : GlypherPhrase }
        #pds[pname]   = { 'x' : index   , 'y' : 0, 'fs' : 1, 'ls' : 1, 'a' : ('l','m'), 'g' : GlypherBODMASBracketedPhrase }
        ##debug_print(self.phrases)
        #for name in pds : self.append_phrase_to_group(name, pds[name])
        #if self._example_sym is None :
        sphr = GlypherPhrase(self)
        symbol = self.make_new_symbol()
        sphr.adopt(symbol)

        if self.default_shortening :
            sphr.hide()

        if self.get_use_space() :
            space = GlypherSpace(self, (0.02,0))
            sphr.append(space)
            if not self.default_shortening :
                space.hide()
        self._example_sym = sphr
        sphr.set_enterable(False); sphr.set_attachable(False)
        #sphr = self._example_sym.copy()
        #if self._example_pos is None :
        pphr = self.poser(self)
        self._set_pos_properties(pphr)
        self._example_pos = pphr
        #pphr = self._example_pos.copy()

        #if self.op_count == 3 : s = GlypherSymbol(self, 'X'); self.append(s)
        #else :

        self.syms[self.get_op_count()-1] = sphr
        self.poss[self.get_op_count()-1] = pphr
        self.add_target(pphr, pname)
        self.append(sphr, align=('l','m')); sphr.set_name(sname)
        self.append(pphr, align=('l','m')); pphr.set_name(pname)
        #debug_print(self.phrases)
        #pphr.set_bodmas_sensitivity(self.bodmas_level)
        #sphr.set_enterable(False)
        #sphr.set_attachable(False)
        #pphr.set_deletable(2) # Send delete requests for rhs to me
        #get_caret().enter_phrase(self.get_phrase('pos2').expr())
        #g.suggest(self.get_phrase(pname).IN())
        return pphr
    
    def remove_operand(self, n) :
        debug_print(n)
        if n==0 :
            posold = self.get_target('pos0')
            posold.empty()
            posnew = self.get_target('pos2')
            symnew = self.syms[1]
            if symnew.to_string() == '-' :
                neg = GlypherNegative(posold)
                posold.adopt(neg)
                posnew.elevate_entities(neg)
            else :
                posnew.elevate_entities(posold)
            symnew.empty()
            posold = posnew; symold = symnew
            n += 1
        else :
            posold = self.get_target('pos'+str(2*n))
            symold = self.syms[n]
            symold.empty(); posold.empty()
        for m in range(n+1, self.get_op_count()) :
            posnew = self.get_target('pos'+str(2*m))
            symnew = self.syms[m]
            debug_print(symnew.config[0].bbox)
            posnew.elevate_entities(posold)
            symnew.elevate_entities(symold)
            posold = posnew; symold = symnew
        self.remove(self.poss[self.get_op_count()-1], override_in=True)
        if self.get_op_count() > 1 : self.remove(self.syms[self.get_op_count()-1])
        self.set_op_count(self.get_op_count() - 1)
        del self.syms[self.get_op_count()]
        del self.poss[self.get_op_count()]
        del self.target_phrases['pos'+str(2*self.get_op_count())]
        debug_print(self.get_op_count())
        debug_print(self.to_string())
    
    _orphaning = None
    def make_simplifications(self) :
        if self.included() :
         if not self.get_p('variable_ops') :
             return
         for n in range(0, self.get_op_count()) :
            pos = 'pos' + str(2*n)
            if pos not in self.target_phrases : return
            ents = self.get_target(pos).get_entities()
            if self.get_associative() and \
                len(ents) == 1 and ents[0].am('binary_expression') and \
                (ents[0].get_symbol_shape() == self.get_symbol_shape() or\
                 ents[0].get_symbol_shape() in self.also_adopt_symbol_shapes) \
                and ents[0].get_op_count() == 2 and ents[0].included() and self._orphaning == None :
                debug_print('HI')
                self._orphaning = ents[0]; e = ents[0]
                lhs_e = e.get_target('pos0')
                rhs_e = e.get_target('pos2')
                if lhs_e.OUT().am('bracketed_phrase') : lhs_e.OUT().suspend_collapse_checks()
                if rhs_e.OUT().am('bracketed_phrase') : rhs_e.OUT().suspend_collapse_checks()
                debug_print(n)
                newpos = self.add_operand(n)
                lhs_e.elevate_entities(self.get_target(pos), adopt=True)
                rhs_e.elevate_entities(newpos, adopt=True)
                e.orphan()
                self.set_recommending(self.get_target('pos'+str(2*(n+1))).IN())
                self._orphaning = None
                #debug_print(self.entities_by_name())
                #debug_print([e.format_me() for e in self.entities])
                #debug_print(get_caret().enter_phrase(newpos.expr(), at_start=True))

    # TODO: Creating and deleting moves fractionally (1px right)
    def delete(self, sender=None, if_empty=True) :
        if self.get_op_count() == 1 :
            return GlypherPhraseGroup.delete(self, sender=sender)

        if sender != None :
            tps = self.target_phrases.keys()
            for phrn in tps :
                if self.get_target(phrn).OUT() == sender :
                    loc = int(phrn[3])/2
                    self.remove_operand(loc)
                    if loc > 0 :
                        debug_print(loc)
                        self.set_recommending(self.get_target('pos'+str((loc-1)*2)).IN())
        if not self.get_allow_unary() : self.check_release_last(sender)
    
    def check_release_last(self, sender=None) :
        # correct for multiple
        if self.get_op_count() == 1 :
            parent = self.get_up()
            self.get_target('pos0').elevate_entities(parent, to_front=True)
            GlypherPhraseGroup.delete(self, sender=sender)
            debug_print('h')
            self.feed_up()
            debug_print('g')
            return parent

class GlypherBinaryRowExpression(GlypherBinaryExpression) :
    p_sort = lambda s,x,y : fcmp(x.config[0].row, y.config[0].row)

    def __init__(self, parent, symbol, area = (0,0,0,0), lhs = None, rhs = None, allow_unary = False, no_brackets = False,
            num_ops = 2, use_space = False) :
        GlypherBinaryExpression.__init__(self, parent, symbol, area=area, lhs=lhs, rhs=rhs,
            allow_unary=allow_unary, no_brackets=no_brackets, num_ops=num_ops,
                                         use_space=use_space, variable_ops=True)
        for i in range(1, self.get_op_count()) :
            self.add_row(i)
            j=i
            for s in (self.poss[i], self.syms[i]) :
                for c in s.config :
                    s.config[c].row = j
                j-=1
        self.recalc_bbox()
        debug_print(unicode("\n").join([s.format_me() for s in self.syms.values()]))

    def _move_along_one(self, from_pos) :
        for i in range(from_pos, self.get_op_count()) :
            for s in (self.poss[i], self.syms[i]) :
                for c in s.config :
                    s.config[c].row += 1
        self.recalc_bbox()
        self._reorder_pos_arrays()
    def add_operand(self, after = None) :
        ret = self.append_operand()
        if after is not None and after < self.get_op_count()-2 :
            old_pos = self.syms[after+1].config[0].row
            i = self.get_op_count()-1; j=old_pos
            for s in (self.poss[i], self.syms[i]) :
                for c in s.config :
                    s.config[c].row = j
                j-=1
            self._move_along_one(after+1)

            self.recalc_bbox()
            delta = self.syms[i].config[0].bbox[0] - self.poss[i-1].config[0].bbox[2]
            self.syms[i].translate(-delta, 0, quiet=True)

            self._reorder_pos_arrays()
            self.recalc_bbox()

        return ret
    def append_operand(self) :
        ret = GlypherBinaryExpression.append_operand(self)
        self.add_row(self.get_op_count()-1)
        i=self.get_op_count()-1; j=i
        for s in (self.poss[i], self.syms[i]) :
            for c in s.config :
                s.config[c].row = j
                debug_print(j)
            j-=1
        self.recalc_bbox()
        delta = self.syms[i].config[0].bbox[0] - self.poss[i-1].config[0].bbox[2]
        self.syms[i].translate(-delta, 0, quiet=True)
        self.recalc_bbox()
        return ret

class GlypherSemicolonArray(GlypherBinaryRowExpression) :
    def __init__(self, parent, area = (0,0,0,0), lhs = None, rhs = None, subtract = False, num_ops = 2) :
        symbol = GlypherSymbol(None, ';')
        GlypherBinaryRowExpression.__init__(self, parent, symbol, area, lhs=lhs, rhs=rhs, num_ops=num_ops,\
            allow_unary=False, no_brackets=True)
        self.mes.append('semicolon_array')

    def get_sympy(self) :
        return self._get_sympy_args()

class GlypherAdd(GlypherBinaryExpression) :
    def __init__(self, parent, area = (0,0,0,0), lhs = None, rhs = None, subtract = False, num_ops = 2) :
        symbol = GlypherSymbol(None, '+') if not subtract else GlypherSymbol(None, '-')
        GlypherBinaryExpression.__init__(self, parent, symbol, area, lhs=lhs,
                                         rhs=rhs, num_ops=num_ops,
                                         variable_ops=True)
        self.mes.append('add')

    def _set_pos_properties(self, pos) :
        GlypherBinaryExpression._set_pos_properties(self, pos)
        if issubclass(self.poser, GlypherBracketedPhrase) :
            pos.no_bracket.add('function')
            pos.no_bracket.add('script')
            pos.no_bracket.add('fraction')
            pos.no_bracket.add('mul')
            pos.no_bracket.add('negative')

    def _get_sympy_args(self) :
        signed_args = [self.get_target('pos0').get_sympy()]
        for i in range(1, self.get_op_count()) :
            if self.syms[i].to_string() == '-' :
                signed_args.append(\
                    sympy_mul(\
                        sympy_negone(),\
                        self.get_target('pos'+str(2*i)).get_sympy()))
            else :
                signed_args.append(self.get_target('pos'+str(2*i)).get_sympy())
        return signed_args

    def get_sympy(self) :
        args = self._get_sympy_args()
        total = args[0]

        shape = self.get_symbol_shape()

        if shape == u'\u222A' :
            for arg in args[1:] :
                total = total.union(arg)
        elif shape == u'\u2229' :
            for arg in args[1:] :
                total = total.intersect(arg)
        else :
            for arg in args[1:] :
                total += arg

        return total
        #return sympy.core.add.Add(*self._get_sympy_args())

    _orphaning = None
    def make_simplifications(self) :
        GlypherBinaryExpression.make_simplifications(self)
        if self._orphaning is not None :
            return

        for i in range(1, self.get_op_count()) :
            sym = 'sym' + str(2*i-1)
            pos = 'pos' + str(2*i)
            if i not in self.poss : return
            ents = self.get_target(pos).get_entities()
            syml = self.syms[i].get_entities() if i in self.syms else (1,)
            if len(ents) == 1 and ents[0].am('negative') and self._orphaning not in (ents[0], syml[0]):
                self._orphaning = ents[0]
                e = ents[0]
                e.orphan()
                e.get_target('expression').elevate_entities(self.get_target(pos), adopt=True)
                self._orphaning = syml[0]
                s = syml[0]
                st = s.to_string()
                #debug_print(s.to_string())
                s.orphan()
                #debug_print(s.to_string())
                #debug_print(s.to_string() == '+')
                self.syms[i].adopt(GlypherSymbol(self.syms[i],\
                    '-' if st == '+' else '+'))
                self.set_recommending(self.get_target(pos))
                self._orphaning = None
        for i in range(0, self.get_op_count()) :
            sym = 'sym' + str(2*i-1)
            pos = 'pos' + str(2*i)
            if i not in self.poss : return
            ents = self.get_target(pos).get_entities()
            syml = self.syms[i+1].get_entities() if i+1 in self.syms else (1,)
            if len(ents) == 1 and ents[0].am('add') and \
                    self._orphaning not in (ents[0], syml[0]) and \
                    ents[0].get_symbol_shape() == '-' and \
                    len(ents[0].syms) == 1 :
                self._orphaning = ents[0]
                e = ents[0]
                lhs_e = e.get_target('pos0')
                rhs_e = e.get_target('pos2')
                if lhs_e.OUT().am('bracketed_phrase') :
                    lhs_e.OUT().suspend_collapse_checks()
                if rhs_e.OUT().am('bracketed_phrase') :
                    rhs_e.OUT().suspend_collapse_checks()

                newpos = self.add_operand(i)
                lhs_e.elevate_entities(self.get_target(pos), adopt=True)
                rhs_e.elevate_entities(newpos, adopt=True)
                e.orphan()

                self._orphaning = None

                s = self.syms[i+1].get_entities()[0]
                self._orphaning = s
                st = s.to_string()
                s.orphan()
                self.syms[i+1].adopt(GlypherSymbol(self.syms[i+1],\
                    '-' if st == '+' else '+'))
                self._orphaning = None

                self.set_recommending(self.get_target('pos'+str(2*(i+1))).IN())

class GlypherLessThan(GlypherBinaryExpression) :
    def __init__(self, parent, lhs=None, rhs=None, num_ops = 2) :
        eq_symbol = GlypherSymbol(parent, "<")
        GlypherBinaryExpression.__init__(self, parent, symbol=eq_symbol, lhs=lhs, rhs=rhs, no_brackets=True, num_ops=num_ops)
        self.mes.append('less_than')

    def get_sympy(self) :
        if self.get_symbol_shape() == '<' :
            rel_holds = True
            args = self._get_sympy_args()
            for i in range(1, len(args)) :
                rel_holds += sympy.relational.Lt(args[i-1], args[i])
        elif self.get_symbol_shape() == u'\u220A' :
            debug_print("Not evaluable")

        return rel_holds

class GlypherGreaterThan(GlypherBinaryExpression) :
    def __init__(self, parent, lhs=None, rhs=None, num_ops = 2) :
        eq_symbol = GlypherSymbol(parent, ">")
        GlypherBinaryExpression.__init__(self, parent, symbol=eq_symbol, lhs=lhs, rhs=rhs, no_brackets=True, num_ops=num_ops)
        self.mes.append('greater_than')

    def get_sympy(self) :
        rel_holds = True
        args = self._get_sympy_args()
        for i in range(1, len(args)) :
            rel_holds += sympy.relational.Gt(args[i-1], args[i])
        return rel_holds

class GlypherEquality(GlypherBinaryExpression) :
    def __init__(self, parent, lhs=None, rhs=None, num_ops = 2) :
        eq_symbol = GlypherSymbol(parent, "=")
        GlypherBinaryExpression.__init__(self, parent, symbol=eq_symbol, lhs=lhs, rhs=rhs, no_brackets=True, num_ops=num_ops)
        self.mes.append('equality')

    def get_sympy(self) :
        return sympy.relational.Eq(self.get_target('pos0').get_sympy(), self.get_target('pos2').get_sympy())

class GlypherCommaArray(GlypherBinaryExpression) :
    def __init__(self, parent, lhs=None, rhs=None, num_ops = 2) :
        comma_symbol = GlypherSymbol(parent, ",")
        GlypherBinaryExpression.__init__(self, parent, symbol=comma_symbol,
                                         lhs=lhs, rhs=rhs, no_brackets=True,
                                         num_ops=num_ops, variable_ops=True)
        self.mes.append('comma_array')
    
    def get_sympy(self) :
        return self._get_sympy_args()

class GlypherRowVector(GlypherBracketedPhrase) :
    be = None
    def __init__(self, parent, lhs=None, rhs=None, num_ops = 2) :
        be = GlypherCommaArray(None, lhs, rhs, num_ops)
        GlypherBracketedPhrase.__init__(self, parent, auto=False, expr=be)
        self.mes.append('row_vector')
        self.set_enterable(False)
        self.set_recommending(be.get_recommending())

    def get_sympy(self) :
        return sympy.matrix.Matrix(self.be._get_sympy_args())

# NEEDS LATER VERSION OF SYMPY
class GlypherFiniteSet(GlypherBracketedPhrase) :
    be = None
    def __init__(self, parent, lhs=None, rhs=None) :
        self.be = GlypherCommaArray(None, lhs, rhs)
        GlypherBracketedPhrase.__init__(self, parent, auto=False, expr=self.be)
        self.mes.append('interval')
        self.set_bracket_shapes(('{','}'))
        self.set_enterable(False)
        self.set_recommending(self.be.get_recommending())

    def get_sympy(self) :
        finite_set = sympy.core.FiniteSet(*self.be._get_sympy_args())
        return finite_set

class GlypherInterval(GlypherBracketedPhrase) :
    be = None
    def __init__(self, parent, lhs=None, rhs=None, left_open=True,
                 right_open=True) :
        self.be = GlypherCommaArray(None, lhs, rhs, 2)
        GlypherBracketedPhrase.__init__(self, parent, auto=False, expr=self.be)
        self.mes.append('interval')

        bracket_pair = ( '(' if left_open else '[', ')' if right_open else ']' )
        self.set_bracket_shapes(bracket_pair)
        self.set_enterable(False)
        self.set_recommending(self.be.get_recommending())

    def set_lhs(self, lhs) :
        self.be.set_lhs(lhs)

    def set_rhs(self, rhs) :
        self.be.set_rhs(rhs)

    bracket_pairs = ( ('(',')'), ('[',')'), ('[',']'),('(',']') )
    def change_alternative(self, dir = 1) :
        ind = self.bracket_pairs.index(self.get_bracket_shapes())
        debug_print((ind,self.get_bracket_shapes()))
        ind += dir
        ind = (ind+len(self.bracket_pairs))%len(self.bracket_pairs)
        self.set_bracket_shapes(self.bracket_pairs[ind])
        return True

    def get_sympy(self) :
        l, r = self.be._get_sympy_args()
        lo, ro = self.get_bracket_shapes()
        lo = lo == '('
        ro = ro == ')'
        interval = sympy.core.Interval(l, r, lo, ro)
        return interval

class GlypherSideFraction(GlypherBinaryExpression) :
    def __init__(self, parent, lhs=None, rhs=None) :
        solidus_symbol = GlypherSymbol(parent, "/")
        GlypherBinaryExpression.__init__(self, parent, symbol=solidus_symbol,
                                         lhs=lhs, rhs=rhs, no_brackets=False)
        self.mes.append('side_fraction')

    def get_sympy(self) :
        return sympy_mul(self.get_target('pos0').get_sympy(),\
            sympy_power(self.get_target('pos2').get_sympy(), -1))

    def _set_pos_properties(self, pos) :
        GlypherBinaryExpression._set_pos_properties(self, pos)
        if issubclass(self.poser, GlypherBracketedPhrase) :
            pos.no_bracket.add('function')
            pos.no_bracket.add('script')

class GlypherSpaceArray(GlypherBinaryExpression) :
    stop_for_binary_expression_exceptions = ()
    def __init__(self, parent, width = 0.5, num_ops = 2, lhs = None, rhs = None, spacing = 0.1) :
        space_symbol = GlypherSpace(parent, (spacing,0.4))
        #space_symbol = make_word(' ',self)
        GlypherBinaryExpression.__init__(self, parent, symbol=space_symbol,
                                         allow_unary=True, no_brackets=True,
                                         num_ops=num_ops, lhs=lhs, rhs=rhs,
                                         variable_ops=True)
        self.add_properties({'allow_unary' : True, 'symbol_shape' : ' ', 'no_brackets' : True, 'num_ops' : 2})
        self.mes.append('space_array')

    def get_sympy(self) :
        return self._get_sympy_args()

class GlypherMul(GlypherBinaryExpression) :
    also_adopt_symbol_shapes = (u'*', u'\u00B7', u'\u00D7', u'')
    _shortening = False
    def set_shortened(self, shortened) : self.set_p('shortened', shortened)
    def get_shortened(self) : return self.get_p('shortened')
    def make_new_symbol(self) :
        sy = GlypherBinaryExpression.make_new_symbol(self)
        sy.set_rgb_colour((0.8, 0.8, 0.8))
        return sy

    def __init__(self, parent, area = (0,0,0,0), lhs = None, rhs = None, num_ops = 2) :
        symbol = GlypherSymbol(None, u'\u00B7')
        GlypherBinaryExpression.__init__(self, parent, symbol, area, lhs, rhs,
                                         num_ops=num_ops, use_space=True,
                                         variable_ops=True)
        self.add_properties({'breakable' : False, 'wordlike' : True,
                             'associative' : True})
        self.mes.append('mul')

    def _set_pos_properties(self, pos) :
        GlypherBinaryExpression._set_pos_properties(self, pos)
        if issubclass(self.poser, GlypherBracketedPhrase) :
            pos.no_bracket.add('function')
            pos.no_bracket.add('script')
            pos.no_bracket.add('fraction')

    def get_sympy(self) :
        args = self._get_sympy_args()
        total = args[0]
        for arg in args[1:] :
            total *= arg
        return total
        #return sympy.core.mul.Mul(*self._get_sympy_args())
        #return sympy.core.mul.Mul(*(a.get_sympy() for a in self._get_sympy_args()))
        
    _orphaning = None
    def make_simplifications(self) :
        GlypherBinaryExpression.make_simplifications(self)
        
        nents = 0
        for i in range(0, self.get_op_count()) :
            pos = 'pos' + str(2*i)
            if i in self.poss : nents += len(self.get_target(pos).get_entities())
        if nents <= 1 : return

        if self.included() :
         for i in range(0, self.get_op_count()) :
            #debug_print(self.op_count)
            pos = 'pos' + str(2*i)
            if i not in self.poss : return
            ents = self.get_target(pos).get_entities()
            #debug_print(self.phrases.keys())
            if self._orphaning == None and \
                len(ents) == 1 and ents[0].am('negative') and\
                len(ents[0]['expression'].get_entities()) > 0 :
                    debug_print('Found *(-a)')
                    p = self.get_up()
                    self._orphaning = p
                    self.suspend_recommending()
                    nexpr = ents[0].get_target('expression')
                    if len(nexpr.get_entities())==1 and \
                           nexpr.get_entities()[0].am('word') and \
                        len(nexpr.get_entities()[0].get_entities())==1 and \
                           nexpr.get_entities()[0].get_entities()[0].am('symbol') and \
                           nexpr.get_entities()[0].get_entities()[0].to_string() == '1' :
                        self.remove_operand(i)
                    else :
                        e = ents[0]
                        nt = nexpr.get_entities()[0]
                        if nt.am('fraction') : 
                            debug_print((nt.get_scaled_font_size(), nt.config[0].bbox))
                            debug_print((e.get_scaled_font_size(), e.config[0].bbox))
                        e.orphan()
                        if nt.am('fraction') : 
                            debug_print((nt.get_scaled_font_size(), nt.config[0].bbox))
                            debug_print((e.get_scaled_font_size(), e.config[0].bbox))
                        nexpr.elevate_entities(self.get_target(pos).IN())

                    if (self.get_parent() != None and self.get_parent().am('negative')) :
                        q = p.get_parent()
                        p.orphan()
                        p.elevate_entities(q, adopt=True)
                    else :
                        self.orphan()
                        n = GlypherNegative(p)
                        n.get_target('expression').adopt(self)
                        p.adopt(n)
                        debug_print(p.to_string())
                    self.check_release_last()
                    self._orphaning = None
                    self.resume_recommending()
                    #self.set_recommending(t)
        if not self._shortening and not self._orphaning :
         for i in range(0, self.get_op_count()-1) :
            posi  = 'pos' + str(2*i)
            posi1 = 'pos' + str(2*(i+1))
            if i not in self.poss or (i+1) not in self.poss : return
            entsi  = self.get_target(posi ).get_entities()
            entsi1 = self.get_target(posi1).get_entities()
            if len(entsi) == 0 or len(entsi1) == 0 : continue
            self._shortening = True
            self.set_shortened(True)
            #if entsi[0].am('word') :
            if should_shorten_mul(entsi[0], entsi1[0]) :
                if self.syms[i+1].get_entities()[0].get_visible() :
                    self.syms[i+1].get_entities()[0].hide()
                    self.syms[i+1].get_entities()[1].show()
                if self.included() : self.get_parent().child_change()
            else :
                if not self.syms[i+1].get_entities()[0].get_visible() :
                    self.syms[i+1].get_entities()[0].show()
                    debug_print(self.get_use_space())
                    debug_print(self.syms[i+1].get_entities())
                    debug_print(self.format_me())
                    self.syms[i+1].get_entities()[1].hide()
                self.set_shortened(False)
                if self.included() : self.get_parent().child_change()
            self._shortening = False
        self.consistency_check_sub_poses()

def should_shorten_mul(ent1, ent2) :
    # never contract if the second term is a number
    if not ent2.get_p('auto_contract_premultiplication') or ent2.is_leading_with_num() : return False

    word1 = (ent1.am('word') and not ent1.is_num()) or ent1.am('constant') or ent1.am('unit')
    word2 = (ent2.am('word') and not ent2.is_num()) or ent2.am('constant') or ent2.am('unit')
    shorten =          (ent1.am('word') and ent1.is_num()) and not (ent2.am('word') and ent2.is_num()) # num and not-num
    shorten = shorten or (word1 and word2)  # word and word
    shorten = shorten or (ent1.am('script') or ent2.am('script')) # two powers/scripts/etc.
    shorten = shorten or (ent1.am('bracketed_phrase') and ent2.am('bracketed_phrase')) # two bracketed phrases
    shorten = shorten or (ent1.am('binary_expression') or ent2.am('binary_expression')) # this should be bracketed!
    shorten = shorten or (ent1.am('fraction') and not ((ent2.am('word') and ent2.is_num())\
        or ent2.am('side_fraction') or ent2.am('fraction'))) # fraction and not-(number or fraction)
    shorten = shorten or (ent2.am('unit')) # unit on right
    return shorten and len(ent1.get_entities()) > 0

def is_short_mul(test) : return isinstance(test, GlypherMul) and test.get_shortened()

g.phrasegroups['negative'] = GlypherNegative
g.phrasegroups['add'] = GlypherAdd
g.phrasegroups['mul'] = GlypherMul
g.phrasegroups['comma_array'] = GlypherCommaArray
g.phrasegroups['semicolon_array'] = GlypherSemicolonArray
g.phrasegroups['space_array'] = GlypherSpaceArray
g.phrasegroups['prime'] = GlypherPrime
g.phrasegroups['side_fraction'] = GlypherSideFraction
g.phrasegroups['interval'] = GlypherInterval
g.phrasegroups['finite_set'] = GlypherFiniteSet
g.phrasegroups['greater_than'] = GlypherGreaterThan
g.phrasegroups['less_than'] = GlypherGreaterThan
g.phrasegroups['equality'] = GlypherEquality
g.phrasegroups['prime'] = GlypherPrime
