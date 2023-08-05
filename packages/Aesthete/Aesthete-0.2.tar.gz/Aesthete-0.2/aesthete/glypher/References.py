import glypher as g
from sympy.matrices import matrices
import copy
import draw
import gutils
from ..utils import debug_print
from PhraseGroup import *

ac = gutils.array_close
fc = gutils.float_close

class GlypherResponseReference(GlypherBracketedPhrase) :
    def __init__(self, parent, resp_code = None) :
        GlypherBracketedPhrase.__init__(self, parent, bracket_shapes=('[',']'), auto=False)
        self.mes.append('reference')
        self.mes.append('response_reference')
        if resp_code is not None :
            resp_code = make_word(resp_code, self)
            self.get_target('expression').adopt(resp_code)
        self.set_recommending(self["expression"])
        debug_print(self.IN().is_enterable())
        self.set_rgb_colour([0.5, 0, 0])

    def process_key(self, keyname, event, caret) :
        mask = event.state

        if keyname == 'Return'  :
            r = self.get_target('expression').get_repr()
            if self.included() and r is not None :
                new_me = g.get_response(r)
                new_me = GlypherEntity.xml_copy(new_me)
                self.suspend_recommending()
                self.get_parent().exchange(self.OUT(), new_me)
                self.set_recommending(new_me.get_recommending())
        else :
            return GlypherPhraseGroup.process_key(self, keyname, mask, caret)

        return True

    
    def get_sympy(self) :
        r = self.get_target('expression').get_repr()
        debug_print(r)
        if r is not None :
            d = g.get_response(r)
            if d :
                sy = d.get_sympy()
                if sy is None :
                    raise GlypherTargetPhraseError(self["expression"].IN(), "Did not evaluate to simple expression")
                return sy
        raise GlypherTargetPhraseError(self["expression"].IN(), "Need valid address.")

class GlypherRangeReference(GlypherBracketedPhrase) :
    sheet = None

    def get_pow_options(self) :
        return ('elementwise', 'python')

    def __init__(self, parent, resp_code = None) :
        GlypherBracketedPhrase.__init__(self, parent,
                                        bracket_shapes=(u'\u27e8',u'\u27e9'),
                                        auto=False)
        self.mes.append('reference')
        self.mes.append('range_reference')

        self["expression"].set_font_size_scaling(0.6)
        self["expression"].IN().set_p('align_as_entity', True)
        from_phrase = GlypherPhrase(self)
        to_phrase = GlypherPhrase(self)
        self["expression"].adopt(from_phrase)
        self["expression"].append(to_phrase, row=1)

        self["expression"].IN().set_enterable(False)
        self.add_target(from_phrase, "from")
        self.add_target(to_phrase, "to")
        self.ignore_targets.append('expression')

        self.set_recommending(self["from"].IN())
        self.set_rgb_colour([0.5, 0.3, 0])
    
    def get_sympy(self) :
        self.sheet = self.get_main_phrase_property('spreadsheet')
        debug_print(self.sheet)
        if not self.sheet :
            return None

        r = self["from"].get_sympy()
        debug_print(r)
        try :
            s = self["to"].get_sympy()
        except :
            s = None

        if r is not None :
            if s is not None :
                r0, c0 = r
                r1, c1 = s
                mat = []
                for i in range(c0, c1+1) :
                    row = []
                    for j in range(r0, r1+1) :
                        row.append(self.sheet.get_sympy_val(j, i))
                    mat.append(row)
                debug_print(mat)
                return matrices.Matrix(mat)
            else :
                d = self.sheet.get_sympy_val(int(r[0]), int(r[1]))
                return d

g.phrasegroups['response_reference'] = GlypherResponseReference
g.phrasegroups['range_reference'] = GlypherRangeReference
