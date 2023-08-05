import glypher as g
import exceptions
import copy
import draw
import gutils
from ..utils import debug_print
from Phrase import *
from Symbol import *
from Spacer import *
import Parser
from sympy.series import limits
from sympy.core.sympify import SympifyError
import Dynamic
from glypher import \
    GLYPHER_PG_LEAD_ALL, \
    GLYPHER_PG_LEAD_VERT, \
    GLYPHER_PG_LEAD_HORI

ac = gutils.array_close
fc = gutils.float_close

class GlypherPhraseGroup (GlypherPhrase) :
    phrases = None
    phrase = None
    
    lead_phrase = None

    first_highlighted_pg_over_active = False
    target_phrases = None
    alts_phrases = None
    get_sympy_code = None
    to_string_code = None
    to_latex_code = None
    alternatives_cat = None

    ignore_targets = None
    
    #def to_string(self) :
    #    return '(' + self.mes[len(self.mes)-1] + '|' + '|'.join([t+'='+self.target_phrases[t].to_string() for t in self.target_phrases])

    lhs_target = None
    def set_lhs_target(self, lhs_target) :
        """Sets (or with None, unsets) the LHS target, for set_lhs."""
        
        if lhs_target is None :
            self.lhs_target = None
        elif lhs_target in self.target_phrases :
            self.lhs_target = lhs_target
        else :
            raise IndexError("lhs_target should be a target.")

    def set_lhs(self, lhs) :
        """If lhs_target is set, puts lhs there, otherwise returns False."""
        if self.lhs_target is not None :
            self[self.lhs_target].adopt(lhs)
            return True
        return False

    rhs_target = None
    def set_rhs_target(self, rhs_target) :
        """Sets (or with None, unsets) the LHS target, for set_rhs."""
        
        if rhs_target is None :
            self.rhs_target = None
        elif rhs_target in self.target_phrases :
            self.rhs_target = rhs_target
        else :
            raise IndexError("rhs_target should be a target.")

    def set_rhs(self, rhs) :
        """If rhs_target is set, puts rhs there, otherwise returns False."""
        if self.rhs_target is not None :
            self[self.rhs_target].adopt(rhs)
            return True
        return False

    def __setitem__(self, key, value) :
        """Add a new TargetPhrase called key in value."""
        self.add_target(value, key)

    def __getitem__(self, key) :
        """Retrieve a Target (or child) by key."""

        # If this is an int, then let Phrase find it, otherwise it should be a
        # string (of some sort) and a Target of ours.
        if isinstance(key, int) :
            return GlypherPhrase.__getitem__(self, key)
        elif not isinstance(key, basestring) :
            raise(TypeError("For pg[target], target must be str not " + str(type(key))))

        if key in self.target_phrases :
            return self.get_target(key)

        raise(IndexError("Target "+key+" not found in PhraseGroup"))

    # Stop looking up tree to find edit mode
    #def is_edit_mode(self) :
    #    return self.edit_mode

    # Stop upward search for all binary expressions, except SpaceArray
    stop_for_binary_expression_default = True
    stop_for_binary_expression_exceptions = ('space_array', 'equality')

    def to_latex(self) :
        if not self.get_visible() : return ""
        elif self.get_blank() : return " "

        if self.to_latex_code :
            return Dynamic.eval_for_sympy(self, self.to_latex_code)
        return GlypherPhrase.to_latex(self)
    def to_string(self, mode = "string") :
        if not self.get_visible() : return unicode("")
        elif self.get_blank() : return unicode(" ")

        if self.to_string_code :
            return Dynamic.eval_for_sympy(self, self.to_string_code)
        return GlypherPhrase.to_string(self, mode=mode)
    def get_sympy(self) :
        debug_print(self.format_me())
        if self.get_sympy_code :
            return Dynamic.eval_for_sympy(self, self.get_sympy_code)
        return GlypherPhrase.get_sympy(self)
            
    def draw_alternatives(self, cr) :
        pass
    def next_alternative(self) :
        self._alternative_in_dir(go_next=True)
    def _alternative_in_dir(self, go_next = True) :
        cat = self.alternatives_cat
        if cat is not None :
            alts = g.find_phrasegroup_alternatives(cat)
            if self.mes[-1] in alts and len(alts) > 1 :
                pos = alts.index(self.mes[-1])
                pos = (len(alts) + pos + (1 if go_next else -1)) % len(alts)
                new_name = alts[pos]
                self.parent.exchange(self, Parser.make_phrasegroup(self.parent, new_name))

    def prev_alternative(self) :
        self._alternative_in_dir(go_next=False)

    def recalc_basebox(self) :
        GlypherPhrase.recalc_basebox(self)
        pbasebox = self.config[0].get_basebox()
        if self.lead_phrase is None : return pbasebox
        b = self.lead_phrase.config[0].get_basebox()
        #if len(self.lead_phrase.get_entities()) > 0 :
        #    debug_print(self.lead_phrase.get_entities()[0].format_me())
        #    debug_print(self.lead_phrase.get_entities()[0].get_basebox())
        #    debug_print(self.lead_phrase.format_me())
        #    debug_print(b)
        #    debug_print('-'*30)
        la = self.get_p('lead_application')
        self.config[0].basebox = \
            (b[0] if la[0] else pbasebox[0],\
                 b[1] if la[1] else pbasebox[1],\
                 b[2] if la[2] else pbasebox[2],\
                 b[3] if la[3] else pbasebox[3],\
                 b[4] if la[4] else pbasebox[4],\
                 b[5] if la[5] else pbasebox[5])

    def set_lead(self, lead, application = (True,True,True,True)) :
        self.lead_phrase = lead
        self.set_p('lead_application', application)

    def get_xml(self, name = None, top = True, targets = None, full = False) :
        if targets is None :
            targets = self.target_phrases
        if full :
            root = GlypherPhrase.get_xml(self, name, top, targets=targets,
                                         full=False)
        else :
            root = ET.Element(self.get_name())
            root.set('type', self.mes[-1])
            debug_print(self.mes[-1])
        
        tgts = ET.Element('targets')
        for t in self.target_phrases :
            if t in self.ignore_targets :
                continue
            r = self.target_phrases[t].get_xml(name='target', top=False,
                                               full=False)
            r.set('name', t)
            tgts.append(r)
        if len(tgts) > 0 :
            root.append(tgts)

        if self.lhs_target is not None :
            root.set('lhs', self.lhs_target)
        if self.rhs_target is not None :
            root.set('rhs', self.rhs_target)

        return root

    def child_change(self) :
        """Called if a child changes in a non-geometric sense."""
        GlypherPhrase.child_change(self)
        if self.included() :
            self.make_simplifications()

    def make_simplifications(self) :
        pass

    def add_alts(self, phrase, name) :
        ap = make_alts_phrase()
        phrase.adopt(ap)
        self.alts_phrases[name] = ap
        return ap
    def add_target(self, phrase, name, stay_enterable = False) :
        """Add a Target, that is, a TargetPhrase which looks a bit funny and can
        be directly addressed from the PhraseGroup by a string. It sits Inside
        the passed Phrase (i.e. TP=P.IN()=TP.IN()) and, by default, should be
        indistinguishable to the end-user through the GUI."""

        if not isinstance(name, basestring) :
            raise TypeError("Target names in PGs should always be str/unicode")
        if not isinstance(phrase, GlypherPhrase) :
            raise TypeError("""
                            Only Phrases may be given to be turned into Targets
                            """)

        # Generate a TargetPhrase
        tp = make_target_phrase()

        # Ensure it will delete its parent automatically
        tp.set_deletable(2)

        # Avoid users falling into the nesting gap
        if not stay_enterable :
            phrase.set_enterable(False)

        # Put it in
        phrase.adopt(tp)

        # Add it to the dictionary
        self.target_phrases[name] = tp

        # Tell tp who the pg is
        tp.pg = self

        # Give it a name for ease of finding
        tp.set_name(name)

    def get_target(self, name) :
        return self.target_phrases[name]
    # Potentially confusing name similarity
    def get_alts(self, name) :
        return self.alts_phrases[name]
    def get_alt(self, name) :
        return self.alts_phrases[name].active_child

    def inside_a(self, what, ignore=()) :
        if self.am(what) : return self
        if self.included() and len(set(self.mes) & set(ignore))>0 :
            return self.get_parent().inside_a(what, ignore)
        return None

    def set_highlight_group(self, highlight_group) : self.set_p('highlight_group', highlight_group)
    def get_highlight_group(self) : return self.get_p('highlight_group')

    def __init__(self, parent, phrase_defs = [], area = (0,0,0,0), lead_phrase = None, phraser=None, highlight_group = True) :
        self.phrases = {}
        self.target_phrases = {}
        self.alts_phrases = {}
        self.ignore_targets = []
        GlypherPhrase.__init__(self, parent, area)
        self.add_properties({'lead_application' :(True,True,True,True,True,True),
                             })
        #self.add_properties({'local_space' : True})
        #debug_print((self,self.mes))
        self.set_highlight_group(highlight_group)
        self.mes.append('phrasegroup')
        self.set_enterable(False)
        if phraser == None : phraser = GlypherExpression if g.math_mode else GlypherPhrase
        self.phraser = phraser
        test = phraser(parent)
        self.set_p('phraser', test.mes[len(test.mes)-1] if phraser else None)
        del test

        if isinstance(phrase_defs, dict) :
         for name in phrase_defs : self.append_phrase_to_group(name, phrase_defs[name])
        else :
         for ind, pd in enumerate(phrase_defs) :
          glyph = pd['o']
          pd['x'] = ind
          self.phrases[pd['n']] = [glyph,pd]

          # Make sure that appending doesn't bring the left edge forward
          #old_left = self.old_config.bbox[0]
          debug_print(pd['n'])
          #adj = self.get_adj(ind)
          #if pd['n'] == 'col1' : adj = 10
          debug_print(adj)
          #glyph.translate(adj, 0)
          self.append(glyph, row=pd['r'] if 'r' in pd else 0, override_in=True, move=(True,True), align=pd['a'] if 'a' in pd else ('l','m'))
          #if self.config[0].bbox[0] > old_left : self.config[0].bbox[0] = old_left
          #self.feed_up()
        self.characteristics.append('_bodmasable')
    
        #def elevate_entities(self, new_parent, adopt = False, to_front = False) :
        #    #debug_print(self.lead_phrase)
        #    if self.lead_phrase is not None :
        #        return self.get_phrase(self.lead_phrase).elevate_entities(new_parent, adopt, to_front)

    def get_phrase(self, phrase) :
        return self.phrases[phrase][0]
    
    def add_phrase(self, phr, name) :
        self.phrases[name] = [phr, {'x':0}]
        phr.set_name(name)
    
    def set_child_active(self, active, desc) :
        GlypherPhrase.set_child_active(self, active, desc)
        ancs = desc.get_ancestors()

        if not active : self.first_highlighted_pg_over_active = False
        else :
            for anc in ancs :
                if anc == self and anc.get_highlight_group() : self.first_highlighted_pg_over_active = True; break
                if anc.am('phrasegroup') and anc.get_highlight_group() :
                    self.first_highlighted_pg_over_active = False; break

    def get_adj(self, loc) :
        adj = loc
        for phr in self.phrases :
            p = self.phrases[phr]
            #debug_print(p[0].to_string() + ' ' +str(p[0].config[0].bbox))
            if loc > p[1]['x'] : adj += p[0].config[0].bbox[2]-p[0].config[0].bbox[0]
        return adj

    def append_phrase_to_group(self, name, pd) :
        phraser = self.phraser
        adj = self.get_adj(pd['x'])
        if 'g' in pd : phraser = pd['g']
        pos = (self.config[0].bbox[0], self.config[0].bbox[3])
        glyph = phraser(self, (pos[0]+adj,self.get_topline()+pd['y'],pos[0]+adj,self.get_baseline()+pd['y']),\
             pd['ls'] if 'ls' in pd else 1.0,\
              pd['fs'] if 'fs' in pd else 1.0,\
              pd['a']  if 'a' in pd else (l,b))
        glyph.x_offset = adj
        glyph.y_offset = pd['y']
        self.phrases[name] = [glyph,pd]

        # Make sure that appending doesn't bring the left edge forward
        old_left = self.old_config.bbox[0]
        self.append(glyph, row=pd['r'] if 'r' in pd else 0, override_in=True, move=(True,True), align=pd['a'] if 'a' in pd else ('l','m'))
        if self.config[0].bbox[0] > old_left : self.config[0].bbox[0] = old_left
        self.feed_up()

    def decorate(self, cr) :
        self.draw_topbaseline(cr)
        if not self.get_visible() : return
        if g.additional_highlighting and self.get_attached() :
            cr.save()
            cr.move_to(self.config[0].bbox[0]-2, self.config[0].bbox[3]+2)
            draw.draw_full_blush(cr, self.config[0].bbox[2]-self.config[0].bbox[0]+4, self.config[0].bbox[3]-self.config[0].bbox[1]+4, (0.8,0.95,0.95))
            cr.set_source_rgba(0.6, 0.9, 0.9, 1.0)
            area=(self.config[0].bbox[0]-2, self.config[0].bbox[2]+2, self.config[0].bbox[1]-2, self.config[0].bbox[3]+2)
            draw.trace_rounded(cr, area, 5)
            cr.stroke()
            cr.restore()
        elif self.get_highlight_group() and self.first_highlighted_pg_over_active :
            cr.save()
            #cr.set_line_width(2.0)
            #cr.rectangle(self.config[0].bbox[0]-2, self.config[0].bbox[1]-2, self.config[0].bbox[2]-self.config[0].bbox[0]+4, self.config[0].bbox[3]-self.config[0].bbox[1]+4)
            #cr.set_source_rgba(0.9, 0.8, 0.6, 0.8)
            cr.move_to(self.config[0].bbox[0]-2, self.config[0].bbox[1]-8)
            draw.draw_inverse_blush(cr, self.config[0].bbox[2]-self.config[0].bbox[0]+4, self.config[0].bbox[3]-self.config[0].bbox[1]-2, (0.9,0.8,0.6))
            if g.stroke_mode :
                cr.fill_preserve()
                cr.set_source_rgba(0.5, 0.5, 0.4, 0.6)
                cr.stroke()
            else : cr.fill()
            cr.restore()

#if you want to run any phrase functions, you should always run through the expr() fn,
#and below is why.
class GlypherCompoundPhrase(GlypherPhraseGroup) :
    phrase_name = ''
    in_ready = False
    def __init__(self, parent, phrase_defs, area = (0,0,0,0), phrase = None, phraser = GlypherPhrase) :
        self.phrase_name = phrase
        GlypherPhraseGroup.__init__(self, parent, phrase_defs, area, phrase, phraser, highlight_group=False)
        if phrase is not None : self.set_expr(phrase)
        #self.in_ready = True
        #self.IN()._out = self
        #self.phrases[phrase][0].set_deletable(2) # Send delete requests for rhs to me
        #self.set_recommending(self.IN())
        #get_caret().enter_phrase(self.expr())

    #def IN(self) : return self.phrases[self.phrase_name][0].IN() if self.in_ready else self
    def set_expr(self, phrase) :
        self.phrase_name = phrase
        #debug_print(self.phrases)
        self.in_ready = True
        self.set_in(self.get_target(self.phrase_name))
        self.set_lead(self.get_target(phrase).IN(), GLYPHER_PG_LEAD_ALL)
        self.recalc_bbox()

class GlypherBracketedPhrase(GlypherCompoundPhrase) :
    left_bracket = None
    right_bracket = None
    is_suspend_collapse_checks = False
    collapse_condition = None

    stop_for_binary_expression_default = False
    stop_for_binary_expression_exceptions = ()

    def set_bracket_shapes(self, bracket_shapes) :
        self.suspend_recommending()
        brkt_shape = bracket_shapes[0]
        phrase = self.left_bracket
        for i in (0,1) :
            symbol = GlypherSymbol(self, brkt_shape, ink=True)
            symbol.set_attachable(False)
            phrase.IN().adopt(symbol)
            brkt_shape = bracket_shapes[1]; phrase = self.right_bracket
        self.set_p('bracket_shapes', bracket_shapes)
        self.resume_recommending()

    def get_bracket_shapes(self) :
        return self.get_p('bracket_shapes')

    def __init__(self, parent, area = (0,0,0,0), line_size_coeff = 1.0, font_size_coeff = 1.0, align = ('l','m'), no_fices = False,\
            auto = True, keep_space = False, hidden_spacing = (0,0), expr = None, bracket_shapes = ('(',')') ) :
        #pds = {}
        # pass no_fices
        #pds['left_bracket'] =    { 'x' : 0 , 'y' : 0, 'a' : ('l','m') }
        #pds['expression'] =    { 'x' : 1 , 'y' : 0, 'a' : align }
        #pds['right_bracket'] =    { 'x' : 2 , 'y' : 0, 'a' : ('l','m') }

        self.suspend_collapse_checks()
        GlypherCompoundPhrase.__init__(self, parent, [], area)
        self.no_bracket = set()
        self.set_p('no_bracket', self.no_bracket)
        self.mes.append('bracketed_phrase')

        self.no_bracket.add('fraction')
        self.no_bracket.add('symbol')
        self.no_bracket.add('square_root')
        self.no_bracket.add('matrix')
        self.no_bracket.add('reference')
        self.no_bracket.add('constant')

        self.left_bracket  = GlypherPhrase(self); self.add_phrase(self.left_bracket, 'left_bracket')
        self.right_bracket = GlypherPhrase(self); self.add_phrase(self.right_bracket, 'right_bracket')
        #self.left_space    = GlypherSpace(self, (hidden_spacing[0],1))
        #self.right_space   = GlypherSpace(self, (hidden_spacing[1],1))
        #self.left_space = GlypherSymbol(None, '-')
        #self.right_space = GlypherSymbol(None, '-')
        self.expression    = GlypherPhrase(self)
        self.expression.set_p('align_as_entity', True)
        #self.expression_out    = GlypherPhrase(self, align_as_entity=True)

        self.append(self.left_bracket,  override_in=True, move=(True,True), align=('l','m'))
        #self.append(self.left_space,    override_in=True, move=(True,True), align=('l','m'))
        self.append(self.expression)
        #self.append(self.expression_out,    override_in=True, move=(True,True), align=align)
        #self.expression_out.adopt(self.expression)
        #self.append(self.right_space,   override_in=True, move=(True,True), align=('l','m'))
        self.append(self.right_bracket, override_in=True, move=(True,True), align=('l','m'))
        #self.target_phrases['expression'] = self.expression
        self.add_target(self.expression, 'expression')
        self.set_enterable(False)
        self.set_expr('expression')
        self.set_lead(self.expression.IN(), GLYPHER_PG_LEAD_ALL)

        self.set_p('keep_space', keep_space)
        #self.left_space.hide()
        #self.right_space.hide()

        brkt_shape = bracket_shapes[0]
        phrase = self.left_bracket
        for i in (0,1) :
            phrase.set_enterable(False)
            phrase.set_attachable(False)
            phrase = self.right_bracket
        self.set_bracket_shapes(bracket_shapes)
        #if expr is not None :
        #    self.phrases['expression'][0].append(expr)
        if auto : self.set_auto_bracket(True)
        #debug_print(self.left_bracket.format_loc())
        #self.set_auto_bracket(False)
        #debug_print(self.right_bracket.format_loc())
        #debug_print(self.expression.format_loc())
        self.resume_collapse_checks()

        if expr is not None :
            self.expression.append(expr)

        self.check_collapse()
        self.set_recommending(self.get_target('expression'))
    
    def set_auto_bracket(self, auto_bracket) : self.set_p('auto_bracket', auto_bracket)
    def get_auto_bracket(self) : return self.get_p('auto_bracket')
    def set_no_bracket(self, no_bracket) : self.set_p('no_bracket', no_bracket)
    def get_no_bracket(self) : return self.get_p('no_bracket')
    def set_collapse_condition(self, collapse_condition) : self.set_p('collapse_condition', collapse_condition)
    def get_collapse_condition(self) : return self.get_p('collapse_condition')
    def set_collapsed(self, collapsed) : self.set_p('collapsed', collapsed)
    def get_collapsed(self) : return self.get_p('collapsed')
    # This ents0 arg allows us to decide should_collapse based on a different
    # entity
    def should_collapse(self, ents0 = None) :
        ents = self.get_target('expression').get_entities()
        if ents0 is None and len(ents) == 1 :
            ents0 = ents[0]
        if ents0 is not None :
            debug_print(ents0.format_me())
            while ents0.OUT().mes[-1] in ('phrase', 'target_phrase') and len(ents0) == 1 :
                ents0 = ents0[0]
        #debug_print(ents)
        # ents0.is_wordlike() or
        return len(ents) == 0 or (ents0 and \
            (len(set(ents0.mes) & self.get_no_bracket())>0 or \
             ents0.is_wordlike() or ents0.get_p('force_no_bracket')) \
            )
    def suspend_collapse_checks(self) :
        self.is_suspend_collapse_checks = True
    
    def resume_collapse_checks(self) :
        self.is_suspend_collapse_checks = False
        self.check_collapse()

    def check_collapse(self) :
        cc = self.get_collapse_condition()
        if self.get_auto_bracket() and not self.is_suspend_collapse_checks :
            if self.should_collapse() \
                or (cc and cc()) :
                    self.brackets_collapse()
            else :
                    self.brackets_restore()
    
    def brackets_collapse(self) :
            ks = self.get_p('keep_space')
            if isinstance(ks, tuple) :
                ksl = ks[0]; ksr = ks[1]
            else :
                ksl = ks; ksr = ks

            if self.left_bracket.get_visible() and not ksl : self.left_bracket.hide()#; self.left_space.show()
            if not self.left_bracket.get_blank() : self.left_bracket.blank()
            if self.right_bracket.get_visible() and not ksr : self.right_bracket.hide()#; self.right_space.show()
            if not self.right_bracket.get_blank() : self.right_bracket.blank()
            self.set_collapsed(True)

    def brackets_restore(self) :
            ks = self.get_p('keep_space')
            if isinstance(ks, tuple) :
                ksl = ks[0]; ksr = ks[1]
            else :
                ksl = ks; ksr = ks

            if not self.left_bracket.get_visible() and not ksl : self.left_bracket.show()#; self.left_space.show()
            if self.left_bracket.get_blank() : self.left_bracket.unblank()
            if not self.right_bracket.get_visible() and not ksr : self.right_bracket.show()#; self.right_space.show()
            if self.right_bracket.get_blank() : self.right_bracket.unblank()
            self.set_collapsed(False)

    def child_change(self) :
        self.check_collapse()
        GlypherCompoundPhrase.child_change(self)

    _altering = False
    def child_altered(self, child = None) :
        GlypherCompoundPhrase.child_altered(self, child)
        if self.in_ready and not self._altering and not self.is_suspend_collapse_checks : #and False :#RMV
            self._altering = True
            for b in (self.left_bracket, self.right_bracket) :
                #break
                #if not b or not b.visible : break
                if not b : break
                sc = (self.IN().config[0].basebox[5]-self.IN().config[0].basebox[3])
                #bc = b.get_scaled_font_size()
                bc = (b.config[0].basebox[5]-b.config[0].basebox[3])
                if not fc(sc, bc) :
                    if b.config[0].get_changes() != "" :
                        raise(RuntimeError('Rescaling parentheses for an un-reset bracket bounding box'))
                    b.set_font_size_scaling((sc/bc)*b.get_size_scaling())
                bc = (b.config[0].basebox[5]-b.config[0].basebox[3])
            self._altering = False

class GlypherBODMASBracketedPhrase(GlypherBracketedPhrase) :
    def set_bodmas_sensitivity(self, bodmas_sensitivity) : self.set_p('bodmas_sensitivity', bodmas_sensitivity)
    def get_bodmas_sensitivity(self) : return self.get_p('bodmas_sensitivity')

    def __init__(self, parent, area = (0,0,0,0), line_size_coeff = 1.0, font_size_coeff = 1.0, align = ('l','m'), no_fices = False) :
        GlypherBracketedPhrase.__init__(self, parent, area, line_size_coeff, font_size_coeff, align, no_fices)

    def should_collapse(self, ents0 = None) :
        # TODO: move 'expr' to 'inside'
        ents = self.IN().get_entities()
        if ents0 is None and len(ents) == 1 :
            ents0 = ents[0]
        return GlypherBracketedPhrase.should_collapse(self, ents0=ents0) or \
            (ents0 and ents0.am_c('_bodmasable') and ents0.get_bodmas_level() < self.get_bodmas_sensitivity())

    def child_change(self) :
        GlypherBracketedPhrase.child_change(self)
        self.check_collapse()
        #debug_print(self.entities[0].get_bodmas_level())

class GlypherTargetPhraseError(RuntimeError) :
    tp = None
    def __init__(self, tp, err = None) :
        self.tp = tp
        tp.set_error_note(err)
        RuntimeError.__init__(self, err)

class GlypherTargetPhrase(GlypherPhrase) :
    pg = None
    hl_anc = False
    error = False
    def __init__(self, parent, area = (0,0,0,0), line_size_coeff = 1.0, font_size_coeff = 1.0, align = ('l','m'), auto_fices = False) :
        GlypherPhrase.__init__(self, parent, area, line_size_coeff, font_size_coeff, align, auto_fices)
        self.mes.append('target_phrase')
        self.characteristics.append('_bodmasable')
        self.characteristics.append('_in_phrase')
        self.add_properties({'blank_ratio' : 0.15, 'attachable' : True,
                             'local_space' : True})

    def get_phrasegroup(self) :
        return self.pg

    def get_bodmas_level(self) :
        ents = self.get_entities()
        #debug_print(self.entities)
        if (len(ents) == 1 and ents[0].am_c('_bodmasable')) :
            return ents[0].get_bodmas_level()
        else : return 100        
        
    def decorate(self, cr) :
        if g.show_rectangles and self.show_decoration() :
            cr.save()
            cr.set_line_width(2.0)
            cr.set_source_rgba(0.5, 0.5, 0.8, 0.4)
            cr.rectangle(self.config[0].bbox[0]-2, self.config[0].bbox[1]-2, self.config[0].bbox[2]-self.config[0].bbox[0]+4, self.config[0].bbox[3]-self.config[0].bbox[1]+4)
            cr.stroke()
            cr.restore()
            
            cr.set_source_rgba(0.5, 0.5, 0.8, 1.0)
            cr.move_to(self.config[0].bbox[0]-4, self.config[0].basebox[4])
            cr.line_to(self.config[0].bbox[2]+4, self.config[0].basebox[4])
            cr.stroke()

        if not self.is_enterable() : return
        hl_anc = None
        # If this is in an unhighlighted highlight group, don't show it, otherwise if the first highlighted group is
        # above it, show it
        for anc in self.get_ancestors() :
            if anc.am('phrasegroup') :
                if anc.first_highlighted_pg_over_active : hl_anc = anc; break
                #else : hl_anc = None; break
                elif anc.get_highlight_group() : hl_anc = None; break
        self.hl_anc = hl_anc
        if not hl_anc and not self.error : return

        cr.save()
        red = 1.0 if self.error else 0.4
        cr.set_source_rgba(red, 0.4, 0.2, 0.1 if g.show_rectangles else 0.2)
        area=(self.config[0].bbox[0]-2, self.config[0].bbox[2]+2, self.config[0].bbox[1]-2, self.config[0].bbox[3]+2)
        draw.trace_rounded(cr, area, 5)
        if len(self.get_entities()) == 0 :
            cr.fill_preserve()
            cr.set_source_rgba(red, 0.4, 0.2, 0.2 if g.show_rectangles else 0.4)
        cr.stroke()
        cr.restore()

    def get_sympy(self) :
        #if len(self.IN().entities) == 0 :
        #    raise GlypherTargetPhraseError(self, "Please enter something!")

        try :
            sy = GlypherPhrase.get_sympy(self)
            self.set_error_note()
            return sy
        except GlypherTargetPhraseError :
            self.set_error_note()
            raise
        except exceptions.RuntimeError as e:
            self.set_error_note("Problem with sympy parsing : " +str(e))
            raise GlypherTargetPhraseError(self, str(e))
        except SympifyError as e:
            self.set_error_note("Sympy complained : " +str(e))
            raise GlypherTargetPhraseError(self, str(e))
        except :
            self.set_error_note("Problem with sympy parsing : " +str(sys.exc_info()[1]))
            raise GlypherTargetPhraseError(self, str(sys.exc_info()[1]))
ref_target_phrase = None
def make_target_phrase () :
    global ref_target_phrase
    if ref_target_phrase is None :
        ref_target_phrase = GlypherTargetPhrase(None)
    return copy.deepcopy(ref_target_phrase)
ref_bracketed_phrase = None
def make_bracketed_phrase () :
    global ref_bracketed_phrase
    if ref_bracketed_phrase is None :
        ref_bracketed_phrase = GlypherBracketedPhrase(None)
    return copy.deepcopy(ref_bracketed_phrase)

g.phrasegroups['phrasegroup'] = GlypherPhraseGroup
g.phrasegroups['bracketed_phrase'] = GlypherBracketedPhrase
g.phrasegroups['target_phrase'] = GlypherTargetPhrase
