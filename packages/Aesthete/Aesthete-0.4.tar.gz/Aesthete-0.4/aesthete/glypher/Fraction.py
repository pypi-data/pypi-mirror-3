import glypher as g
from Word import *
from PhraseGroup import *
from Symbol import *
from Spacer import *
from Function import *
import BinaryExpression
import sympy
from sympy.core import sympify
        
class GlypherFraction(GlypherPhraseGroup) :
    bodmas_level = 0
    row0 = None
    vin = None

    def recalc_basebox(self) :
        GlypherPhraseGroup.recalc_basebox(self)
        if self.vin :
            l = self.config[0].get_basebox()
            m = self.vin.config[0].get_basebox()
            self.config[0].basebox = (l[0], l[1], l[2], l[3], m[4], l[5])

    def get_sympy(self) :
        return sympy.core.mul.Mul(self.get_target('numerator').get_sympy(),\
            sympy.core.power.Pow(self.get_target('denominator').get_sympy(), -1))
    
    def to_string(self, mode = "string") :
        if not 'numerator' in self.target_phrases or not 'denominator' in self.target_phrases : return '/'
        return self.get_target('numerator').to_string(mode) + '/' + self.get_target('denominator').to_string(mode)

    def __init__(self, parent, area = (0,0,0,0), numerator = None, denominator = None) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'row0')

          # Make sure that appending doesn't bring the left edge forward
          #old_left = self.old_bbox[0]
          #adj = self.get_adj(ind)
          #if pd['n'] == 'col1' : adj = 10
          #debug_print(adj)
          #glyph.translate(adj, 0)
          #if self.bbox[0] > old_left : self.bbox[0] = old_left

        self.mes.append('fraction')

        de_cell = GlypherPhrase(self, align=('c','m'))
        self.append(de_cell, row=1); self.add_phrase(de_cell, 'row1')
        de_cell.set_deletable(2)
        de_cell.set_enterable(False)
        self.add_target(de_cell, 'denominator')
        self.set_rhs_target('denominator')
        de_cell.set_font_size_scaling(0.6)
        #de_cell.set_line_size_scaling(0.6)
        self.set_row_align(1, 'c')

        nu_cell = GlypherPhrase(self, align=('c','m'))
        self.append(nu_cell, row=-1); self.add_phrase(nu_cell, 'row-1')
        nu_cell.set_deletable(2)
        nu_cell.set_enterable(False)
        #nu_cell.set_attachable(False)
        self.add_target(nu_cell, 'numerator')
        self.set_lhs_target('numerator')
        nu_cell.set_font_size_scaling(0.6)
        #nu_cell.set_line_size_scaling(0.6)
        self.set_row_align(-1, 'c')

        vinculum = GlypherHorizontalLine(None, length=10, thickness=0.04)
        vinculum.align=('c','m')
        vinculum.set_tied_to(self)
        ## I think LaTeX just takes the max, but this looks quite nice
        ## until full compatibility is being implemented
        #lc = lambda : \
        #    0.5*(nu_cell.width()+de_cell.width()) \
        #    if de_cell.width() < nu_cell.width() else \
        #    de_cell.width()
        #vinculum.length_calc = lc
        #vinculum.set_padding(1, 4)
        #vinculum.set_padding(3, 4)

        vi_cell = GlypherPhrase(self, align=('c','m')); self.row0 = vi_cell
        self.append(vi_cell, row=0); self.add_phrase(vi_cell, 'row0')
        vi_cell.set_deletable(2)
        vi_cell.set_enterable(False)
        vi_cell.set_attachable(False)
        vi_cell.adopt(vinculum)
        vi_cell.set_horizontal_ignore(True)
        vi_cell.set_always_recalc(True)
        self.set_lead(vi_cell, GLYPHER_PG_LEAD_VERT)
        self.vin = vinculum

        self.set_recommending(self["numerator"])
        if numerator is not None :
            nu_cell.adopt(numerator)
            self.set_recommending(self["denominator"])
        if denominator is not None :
            de_cell.adopt(denominator)


    def delete(self, sender = None, if_empty = True) :
        if len(self.get_target('numerator').entities) \
            + len(self.get_target('denominator').entities) == 0 \
            or not if_empty :
             GlypherPhraseGroup.delete(self, if_empty=False)

    _orphaning = None
    def make_simplifications(self) :
        if not 'numerator' in self.target_phrases : return
        num_e = self.get_target('numerator').get_entities()
        debug_print(num_e)
        if len(num_e) > 0 : debug_print(num_e[0].to_string())
        if self.included() and len(num_e) == 1 and num_e[0].am('negative') and len(num_e[0].get_entities())>0:
          debug_print('Found (-m)/n')
          p = self.get_parent()
          self._orphaning = p

          q = num_e[0]
          q.orphan()
          q["expression"].IN().elevate_entities(self.get_target('numerator'))
          self.set_recommending(self['numerator'])

          self.orphan()
          n = BinaryExpression.GlypherNegative(p)
          n.get_target('expression').adopt(self)
          p.adopt(n)
          self._orphaning = None

    def child_change(self) :
        GlypherPhraseGroup.child_change(self)
        self.make_simplifications()
        
a_half = sympify("1/2")
class GlypherSqrt(GlypherCompoundPhrase) :
    bodmas_level = 0
    degree = None

    def get_sympy(self) :
        return sympy.core.power.Pow(self.get_target('expression').get_sympy(),
                              a_half if not self.degree else \
                              self.degree.get_sympy())
    
    def to_string(self, mode = "string") :
        return unicode('sqrt(')+self.IN().to_string(mode)+unicode(')')

    _altering = False
    ex_cell = None
    sqrt = None
    def child_altered(self, child = None) :
        GlypherCompoundPhrase.child_altered(self, child)
        if self.ex_cell and self.sqrt and not self._altering :
            b = self.sqrt
            s = self.ex_cell

            sc = (s.config[0].bbox[3]-s.config[0].bbox[1])
            bc = (b.config[0].bbox[3]-b.config[0].bbox[1])
            if not fc(sc, bc) :
                if b.config[0].get_changes() != "" :
                    raise(RuntimeError('Rescaling sqrt for an un-reset sqrt bounding box'))
                self._altering = True
                b.set_font_size_scaling((sc/bc)*b.get_size_scaling())
                self._altering = False

    #FIXME: Note that degree is fixed (as this is a CompoundPhrase)
    def __init__(self, parent, area = (0,0,0,0), expression = None,
                 degree = None) :
        GlypherCompoundPhrase.__init__(self, parent, [], area)
        #FIXME: Misnomer!
        self.mes.append('square_root')

        if degree is not None :
            degree_pos = GlypherPhrase(self)
            degree_pos.set_size_scaling(0.5)
            degree_pos.set_enterable(False)
            degree_pos.set_attachable(False)
            right_mid = GlypherSpace(self, dims=(0.1,0.1))#GlypherVerticalSpacer(self, tied_to=expr, scaling=1.4)
            right_mid.set_attachable(False)
            degree_side = GlypherPhrase(self)
            degree_side.append(right_mid, row=0)
            degree_side.append(degree_pos,  row=-1)
            degree_side.set_enterable(False)
            degree_side.set_attachable(False)
            degree_pos.append(degree)
            self.append(degree_side)
            self.degree = degree_pos
        
        sq_cell = GlypherPhrase(self, align=('c','m'))
        self.append(sq_cell)
        sq_cell.set_enterable(False)
        sqrt_sym  = GlypherSymbol(sq_cell, u'\u221A', area, ink=True, italic=False)
        sqrt_sym.name = '\sqrt'; sq_cell.append(sqrt_sym)
        self.sqrt = sq_cell

        ex_cell = GlypherPhrase(self, align=('c','m'))
        ex_cell.set_p('align_as_entity', True)
        self.append(ex_cell)
        expr = GlypherPhrase(self)
        ex_cell.append(expr)
        self.ex_cell = ex_cell
        self.add_target(expr, 'expression')

        line = GlypherHorizontalLine(None, length=10, thickness=0.05, thickness_too=True)
        line.align=('c','m')
        line.set_tied_to(expr)
        ## I think LaTeX just takes the max, but this looks quite nice
        ## until full compatibility is being implemented
        #lc = lambda : \
        #    0.5*(nu_cell.width()+de_cell.width()) \
        #    if de_cell.width() < nu_cell.width() else \
        #    de_cell.width()
        #vinculum.length_calc = lc
        #vinculum.set_padding(1, 4)
        #vinculum.set_padding(3, 4)

        ex_cell.append(line, row=-1)
        line.set_vertical_ignore(False)
        debug_print(ex_cell.format_loc())
        line.set_horizontal_ignore(True)
        debug_print(ex_cell.format_loc())
        line.set_always_recalc(True)
        debug_print(ex_cell.format_loc())
        debug_print(ex_cell.format_entities())

        self.set_expr("expression")

        if expression is not None :
            expr.adopt(expression)

        self.set_recommending(self["expression"])

    def show_decoration(self) :
        return True

g.phrasegroups['fraction'] = GlypherFraction
g.phrasegroups['square_root'] = GlypherSqrt
