import glypher as g
from Word import *
from PhraseGroup import *
from Symbol import *
from Fraction import *
import sympy

class GlypherDerivative(GlypherPhraseGroup) :

    def get_sympy(self) :
        return self.get_target('operand').get_sympy().diff(self.get_target('by').get_sympy())

    def __init__(self, parent, area = (0,0,0,0), operand = None, by = None) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'operand')
        self.mes.append('derivative')

        fr = GlypherFraction(self)
        fr.get_target('numerator').enterable = False
        fr.get_target('numerator').adopt(GlypherSymbol(fr, 'd', italic=False))
        den = fr.get_target('denominator')
        den.enterable = False
        den.adopt(GlypherSymbol(fr, 'd', italic=False))
        by_phrase = GlypherPhrase(den)
        den.append(by_phrase)
        self.add_target(by_phrase, 'by')
        fr.highlight_group = False
        fr.set_attachable(False)
        fr.set_deletable(3)
        fr.name = 'derivative'
        self.adopt(fr)

        op = GlypherPhrase(None)
        op.name = 'operand'
        self.add_target(op, 'operand')
        self.append(op)
        op.set_deletable(3)

        if operand is not None :
            op.adopt(operand)
        if by is not None :
            by_phrase.adopt(by)

        self.set_recommending(by_phrase)

class GlypherSummation(GlypherPhraseGroup) :
    bodmas_level = 100
    si_cell = None

    #def get_basebox(self) :
    #    if self.si_cell :
    #            return self.si_cell.get_basebox()
    #    else :
    #        return GlypherPhraseGroup.get_basebox(self)

    #def get_baseboxes(self) :
    #    bb = GlypherPhraseGroup.get_baseboxes(self)
    #    bb[0] = self.get_basebox()
    #    return bb

    def get_sympy(self) :
        if self.get_alt('symbol').shape == u'\u03A0' :
            return sympy.concrete.products.Product(self.get_target('operand').get_sympy(),\
            (self.get_target('n').get_sympy(), self.get_target('from').get_sympy(), self.get_target('to').get_sympy()))
        if self.get_alt('symbol').shape == u'\u03A3' :
            return sympy.concrete.summations.Sum(self.get_target('operand').get_sympy(),\
            (self.get_target('n').get_sympy(), self.get_target('from').get_sympy(), self.get_target('to').get_sympy()))

    def __init__(self, parent, area = (0,0,0,0), operand = None) :
        GlypherPhraseGroup.__init__(self, parent, [], area, 'operand')

          # Make sure that appending doesn't bring the left edge forward
          #old_left = self.old_bbox[0]
          #adj = self.get_adj(ind)
          #if pd['n'] == 'col1' : adj = 10
          #debug_print(adj)
          #glyph.translate(adj, 0)
          #if self.bbox[0] > old_left : self.bbox[0] = old_left

        self.mes.append('summation')
        self.enterable = False
        self.highlight_group = True

        col0 = GlypherPhraseGroup(None, [])
        self.append(col0, override_in=True)
        self.add_phrase(col0, 'col0')
        col0.enterable = False
        col0.set_attachable(False)
        col0.set_deletable(3)
        col0.set_keep_min_row_height(False)
        col0.highlight_group = False

        si_cell = GlypherPhrase(None); col0.append(si_cell, row=0)
        si_alts = self.add_alts(si_cell, 'symbol')
        col0.add_phrase(si_cell, 'row0')
        #si_cell.set_padding(1, -8)
        #si_cell.set_padding(3, -8)
        #si_cell.set_padding(2, 8)
        #si_cell.set_enterable(False)
        si_cell.set_attachable(False)
        si_cell.set_size_scaling(1.5)
        si_cell.set_keep_min_row_height(False)
        self.set_lead(si_cell, GLYPHER_PG_LEAD_VERT)

        Sigma = GlypherSymbol(col0, u'\u03A3', area, ink=True)
        Pi    = GlypherSymbol(col0, u'\u03A0', area, ink=True)
        Sigma.name = 'Sigma';    si_alts.append(Sigma)
        Pi.name = 'Pi';        si_alts.append(Pi)

        op = GlypherPhrase(None)
        self.add_target(op, 'operand'); self.add_phrase(op, 'operand')
        self.append(op, override_in=True)
        op.set_deletable(3)

        #n = GlypherSymbol(col0, 'n', area, align=('c','m'))
        n_phrase = GlypherPhrase(col0)
        self.add_target(n_phrase, 'n')
        #n = make_word('n', n_phrase); n.align=('c','m')
        n_phrase.set_padding(2, 2)
        #n_phrase.adopt(n)
        eq = GlypherSymbol(col0, '=', area, align=('c','m'))
        #eq.set_padding(2, 2)
        from_phrase = GlypherPhrase(col0)
        self.add_target(from_phrase, 'from')

        fr_cell = GlypherPhrase(None); col0.append(fr_cell, row=1)
        col0.add_phrase(fr_cell, 'row-1')
        fr_cell.adopt(n_phrase)
        fr_cell.append(eq)
        fr_cell.append(from_phrase)
        fr_cell.enterable = False
        fr_cell.set_attachable(False)
        fr_cell.set_keep_min_row_height(False)
        fr_cell.set_size_scaling(0.6)
        col0.set_row_align(1, 'c')

        to_phrase = GlypherPhrase(None)
        self.add_target(to_phrase, 'to')

        to_cell = GlypherPhrase(None); col0.append(to_cell, row=-1)
        col0.add_phrase(to_cell, 'row1')
        to_cell.set_keep_min_row_height(False)
        to_cell.adopt(to_phrase)
        to_cell.enterable = False
        to_cell.set_attachable(False)
        to_cell.set_size_scaling(0.6)
        col0.set_row_align(-1, 'c')

        col0.set_padding(2, 4)

        op.set_row_redirect(GLYPHERDIRECTION_DOWN, self.get_target('from'))
        op.set_row_redirect(GLYPHERDIRECTION_UP  , self.get_target('to'))

        if operand is not None :
            op.adopt(operand)

        self.set_recommending(op)
