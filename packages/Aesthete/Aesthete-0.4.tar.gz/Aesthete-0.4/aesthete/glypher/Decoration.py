import glypher as g
from sympy.matrices import matrices
from sympy.core import sympify
from Spacer import *
from PhraseGroup import *
import Table

pow_types = {
             'python' : None,
             'elementwise' : (u'\u2218', \
                              Table.matrix_hadamard_multiply)
            }

class GlypherScript(GlypherPhraseGroup) :
    left = None
    right = None

    def set_pow_mode(self, pow_mode) :
        self.set_p('pow_mode', pow_mode)
        g.pow_mode = pow_mode
        self.is_wordlike()
    def get_pow_mode(self) : return self.get_p('pow_mode')
    def set_diff_mode(self, diff_mode) :
        self.set_p('diff_mode', diff_mode)
        g.diff_mode = diff_mode
        self.is_wordlike()
    def get_diff_mode(self) : return self.get_p('diff_mode')

    def is_wordlike(self) :
        wordlike = \
            self.right and self.get_available(0) and \
            not self.get_diff_mode() and len(self["expression"].entities) == 1 and \
            self["expression"].entities[0].am("word")
        
        old_wordlike = self.get_p('wordlike')
        if wordlike != old_wordlike :
            self.set_p('wordlike', wordlike) #FIXME: gotta be a better way of doing this
            self.child_change()
        return wordlike

    pow_options = ('python')
    def child_change(self) :
        ret = GlypherPhraseGroup.child_change(self)
        if "expression" in self.target_phrases and\
           len(self["expression"].IN()) == 1 :
            inner = self["expression"].IN()[0]
            self.pow_options = inner.get_pow_options()
            
            if self.get_p('pow_type') not in self.pow_options or \
               not self.get_p('pow_type_set') :
                self.set_p('pow_type', self.pow_options[0])
        return ret

    def get_available(self, site = None) :
        rv = self.right.get_visible()
        lv = self.left.get_visible()
        if site == 0 :
            return rv and self['site0'].OUT().get_visible()
        elif site == 1 :
            return lv and self['site1'].OUT().get_visible()
        elif site == 2 :
            return rv and self['site2'].OUT().get_visible()
        elif site == 3 :
            return lv and self['site3'].OUT().get_visible()
        else :
            return [self.get_available(site) for site in range(0,4)]

    def get_xml(self, name = None, top = True, targets = None, full = False) :
        root = GlypherPhraseGroup.get_xml(self, name=name, top=top,
                                          targets=targets, full=full)
        root.set('available', ",".join(map(str,self.get_available())))
        return root

    def make_simplifications(self) :
        GlypherPhraseGroup.make_simplifications(self) 
        if len(self["expression"]) == 1 :
            self["expression"].get_entities()[0].make_simplifications()

    @classmethod
    def subscript(cls, parent, area = (0,0,0,0), expression = None, subscript = None):
        me = cls(parent, area, expression, available=(True, False, False, False))
        me.get_target('site0').adopt(subscript)
        return me

    @classmethod
    def superscript(cls, parent, area = (0,0,0,0), expression = None, superscript = None):
        me = cls(parent, area, expression, available=(False, False, True, False))
        me.get_target('site2').adopt(superscript)
        return me

    def _annotate(self, cr, bbox, text) :
        cr.save()
        cr.set_font_size(0.25*self.get_scaled_font_size())
        cr.select_font_face("sans")
        exts = cr.text_extents(text)
        cr.rectangle(bbox[0] + exts[0] - 2, bbox[1] + exts[1] - 5, exts[2] + 4, exts[3] + 4)
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        cr.stroke_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.8)
        cr.fill()
        cr.move_to(bbox[0], bbox[1] - 3)
        cr.set_source_rgb(0.8, 0, 0)
        cr.show_text(text)
        cr.restore()

    def _diff_draw(self, cr) :
        tl = self.get_target('site0')
        GlypherTargetPhrase.decorate(tl, cr)
        if self.get_annotate() and (tl.get_attached() or g.show_all_pow_diff) :
            self._annotate(cr, tl.config[0].bbox, "d/d" if self.get_diff_mode() else "|_")

    def _pow_draw(self, cr) :
        tl = self.get_target('site2')
        GlypherTargetPhrase.decorate(tl, cr)
        if self.get_annotate() and (tl.get_attached() or g.show_all_pow_diff) :
            if self.get_pow_mode() :
                pow_indicator = "**"
                pow_type = pow_types[self.get_p('pow_type')]
                if pow_type is not None :
                    pow_indicator += ":" + pow_type[0]

                self._annotate(cr, tl.config[0].bbox, pow_indicator)
            else :
                self._annotate(cr, tl.config[0].bbox, "^")
    
    def set_defaults(self) :
        self.set_pow_mode(g.pow_mode if g.pow_mode_force is None else
                          g.pow_mode_force)
        self.set_diff_mode(g.diff_mode if g.diff_mode_force is None else
                          g.diff_mode_force)
    
    def is_leading_with_num(self) :
        return self.left.get_visible() or self["expression"].is_leading_with_num()

    def get_annotate(self) : return self.get_p('annotate')
    def set_annotate(self, val) : return self.set_p('annotate', val)

    def __init__(self, parent, area = (0,0,0,0), expression = None, available = (True, True, True, True)) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'expression')
        self.mes.append('script')
        self.add_properties({'pow_type':'python', 'pow_type_set':False,
                             'annotate' : True})

        self.set_defaults()
        #FIXME: How does this translate to the XML version?
        left = GlypherPhrase(self); self.left = left; left.name = "left"
        expr = GlypherBracketedPhrase(self)
        right= GlypherPhrase(self); self.right = right; right.name = "right"
        left.set_p('always_recalc', True)
        right.set_p('always_recalc', True)

        expr.no_bracket.remove('fraction')

        self.add_target(expr, 'expression')
        self.set_lead(expr, GLYPHER_PG_LEAD_VERT)

        left.set_enterable(False)
        left.set_attachable(False)
        left.set_deletable(2)
        left.delete = lambda sender=None, if_empty=True : self.delete(sender, if_empty)
        right.set_enterable(False)
        right.set_attachable(False)
        right.set_deletable(2)
        right.delete = lambda sender=None, if_empty=True : self.delete(sender, if_empty)

        self.append(left)
        self.append(expr)
        self.append(right)

        self.set_lead(expr, GLYPHER_PG_LEAD_ALL)

        #right_mid = GlypherSpace(self, dims=(0.1,0.1)) #GlypherVerticalSpacer(self, tied_to=expr, scaling=1.4)
        right_mid = GlypherVerticalSpacer(self, tied_to=expr, scaling=1.2)
        right_mid.set_attachable(False)
        right.append(right_mid, row=0)

        #left_mid = GlypherSpace(self, dims=(0.1,0.1))#GlypherVerticalSpacer(self, tied_to=expr, scaling=1.4)
        left_mid = GlypherVerticalSpacer(self, tied_to=expr, scaling=1.4)
        left_mid.set_attachable(False)
        left.append(left_mid, row=0)
        
        right.append(self._setup_pos('site0', available=available[0]),  row=1)  #BR
        left.append (self._setup_pos('site1', available=available[1]),  row=1)  #BL
        right.append(self._setup_pos('site2', available=available[2]),  row=-1) #TR
        left.append (self._setup_pos('site3', available=available[3]),  row=-1) #TL

        self['site0'].decorate = lambda cr : self._diff_draw(cr)
        self['site2'].decorate = lambda cr : self._pow_draw(cr)
        
        # Make sure that no binary expression, particularly SpaceArrays, started
        # inside one of these sites gets passed above us.
        self['site0'].stop_for_binary_expression_default = True
        self['site2'].stop_for_binary_expression_default = True
        self['site0'].stop_for_binary_expression_exceptions = ()
        self['site2'].stop_for_binary_expression_exceptions = ()

        if not available[0] and not available[2] : right.hide()
        if not available[1] and not available[3] : left.hide()

        self.set_default_entity_xml()

        if expression :
            expr.adopt(expression)

        for i in range(0, 4) :
            pos = self.get_target('site'+str(i))
            if available[i] :
                self.set_recommending(pos)
            else :
                pos.OUT().hide()
    
    def _setup_pos(self, name, available=True) :
        pos = GlypherPhrase(self)
        pos.set_size_scaling(0.5)
        pos.set_deletable(2)
        self.add_target(pos, name)
        return pos
    
    def to_string(self, mode = "string") :
        expr = self.get_target('expression').to_string(mode)
        # Do indexing!
        if self.get_diff_mode() and self.get_available(0) :
            expr += unicode("_{") + self.get_target('site0').to_string(mode) + unicode("}")
        if self.get_pow_mode() and self.get_available(2) :
            expr += unicode("^{") + self.get_target('site2').to_string(mode) + unicode("}")
        return expr
    
    def to_latex(self) :
        expr = self.get_target('expression').to_latex()
        # Do indexing!
        if self.get_diff_mode() and self.get_available(0) :
            expr += "_{" + self.get_target('site0').to_latex() + "}"
        if self.get_pow_mode() and self.get_available(2) :
            expr += "^{" + self.get_target('site2').to_latex() + "}"
        return expr
    
    def get_sympy(self, sub = True) :
        expr = self.get_target('expression').get_sympy()
        debug_print(self.to_string())
        # Do indexing!
        if self.get_available(0) :
            if self.get_diff_mode() :
                symbol_array = self['site0'].get_sympy()
                if not isinstance(symbol_array, list) :
                    symbol_array = [symbol_array]
                for sym in symbol_array :
                    expr = sympy.core.function.diff(expr, sym)
            elif len(self["expression"].entities) == 1 :
                operand = self["expression"].entities[0]
                w_sympy = operand.get_sympy()
                debug_print(w_sympy)
                debug_print(type(w_sympy))

                if isinstance(w_sympy, sympy.core.function.Function) :
                    try :
                        args = self["site0"].get_sympy()
                    except :
                        expr = w_sympy
                    else :
                        if not isinstance(args, list) and not isinstance(args, tuple) :
                            args = (args,)

                        dict_args = dict(zip(w_sympy.args, args))
                        try :
                            expr = w_sympy(dict_args)
                        except :
                            expr = w_sympy(*args)
                elif isinstance(w_sympy, matrices.Matrix) :
                    debug_print(self["site0"].get_sympy())
                    try :
                        args = self["site0"].get_sympy()
                    except :
                        expr = w_sympy
                    else :
                        if not isinstance(args, list) and not isinstance(args, tuple) :
                            args = (args,)

                        dims = (w_sympy.rows, w_sympy.cols)
                        if len(args) == 1 :
                            if dims[0] == 1 :
                                args = (1, args[0])
                            elif dims[1] == 1 :
                                args = (args[0], 1)

                        args = map(int, args)
                        expr = w_sympy[args[0]-1, args[1]-1]
                else :
                    sym = sympy.core.symbol.Symbol(
                                  str(operand._get_symbol_string()+"_"+self["site0"].to_string()+""))

                    if sub and sym in g.var_table :
                        expr = g.var_table[sym]
                    else :
                        expr = sym

        if self.get_pow_mode() and self.get_available(2) :
            pow_mode = pow_types[self.get_p('pow_type')]
            if pow_mode is None :
                expr = expr ** self['site2'].get_sympy()
            else :
                reps = int(self['site2'].get_sympy())
                if reps < 1 :
                    raise GlypherTargetPhraseError(self['site2'].IN(),
                              "Require positive int for iterative powering")
                base = expr
                for i in range(1, reps) :
                    expr = pow_mode[1](expr, base)
            #expr = sympy.core.power.Pow(expr, self.get_target('site2').get_sympy())
        return expr

    def delete(self, sender=None, if_empty=True) :
        if sender != None :
            for i in range(0,3) :
                if sender == self.get_target('site'+str(i)).OUT() :
                    debug_print(i)
                    sender.empty()
                    sender.hide()
                    if [e.get_visible() for e in self.right.entities] == [False, False] and right.get_visible() :
                        self.right.hide()
                    if [e.get_visible() for e in self.left.entities] == [False, False] and left.get_visible() :
                        self.left.hide()
        do_del = True
        for e in self.target_phrases :
            if e == 'expression' : continue
            if self.get_target(e).OUT().get_visible() : do_del = False
        if do_del :
            parent = self.get_up()
            self.get_target('expression').elevate_entities(parent, to_front=True)
            GlypherPhraseGroup.delete(self, sender=sender)
            self.feed_up()
            return parent
    
    def _pkp(self, site) :
        if site not in self.target_phrases :
            return False

        site = self.get_target(site)
        if site.OUT() in self.right.entities and not self.right.get_visible() : self.right.show()
        if site.OUT() in self.left.entities  and not self.left.get_visible()  : self.left.show()
        site.OUT().show()
        debug_print(site.format_me())

    def process_key(self, keyname, event, caret) :
        mask = event.state

        if self['site0'].get_attached() :
            if keyname == 'Left'  : self._pkp('site1')
            if keyname == 'Up'    : self._pkp('site2')
            if keyname == 'Right' :
                self.set_diff_mode(not self.get_diff_mode())
        elif self['site1'].get_attached() :
            if keyname == 'Right' : self._pkp('site0')
            if keyname == 'Up'    : self._pkp('site3')
        elif self['site2'].get_attached() :
            if keyname == 'Left'  : self._pkp('site3')
            if keyname == 'Down'  : self._pkp('site0')
            if keyname == 'Right' :
                self.set_pow_mode(not self.get_pow_mode())
            if keyname == 'Up' :
                opt = self.pow_options.index(self.get_p('pow_type'))
                opts = len(self.pow_options)
                self.set_p('pow_type', \
                           self.pow_options[(opt+1) % opts])
                self.set_p('pow_type_set', True)
                #Trigger a redraw
                self.get_main_phrase().recalc_bbox()
        elif self['site3'].get_attached() :
            if keyname == 'Right' : self._pkp('site2')
            if keyname == 'Down'  : self._pkp('site1')
        else :
            return GlypherPhraseGroup.process_key(self, keyname, event, caret)

        return True

g.phrasegroups['script'] = GlypherScript
