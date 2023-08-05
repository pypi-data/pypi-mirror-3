from Entity import *
import gutils
from sympy.core.sympify import SympifyError

ac = gutils.array_close
fc = gutils.float_close

class GlypherMirror(GlypherEntity) :
    tied_to = None

    def to_string(self, mode = "string") : return self.tied_to.to_string(mode);

    def __init__(self, parent = None, tied_to = None) :
        GlypherEntity.__init__(self, parent)
        self.add_properties({'tied_to': None})
        self.set_always_recalc(True)
        self.mes.append('mirror')
        self.config[0].bbox[0] = 0
        self.config[0].bbox[3] = 1
        self.set_ref_width(1)
        self.set_ref_height(1)
        self.set_attachable(False)
        self.set_tied_to(tied_to)
        self.recalc_bbox()
    
    def recalc_bbox(self, quiet = False) :
        self.set_tied_to(self.get_p('tied_to'))
        chg1 = self.cast()
        chg2 = GlypherEntity.recalc_bbox(self, quiet=quiet)
        return chg1 or chg2

    def set_tied_to(self, entity) :
        self.tied_to = entity
        if self.tied_to == self.get_p('tied_to') :
            return
        self.set_p('tied_to', entity)
        debug_print(entity.format_me() if entity is not None else None)
        self.recalc_bbox()

    def cast(self) :
        old_rw = self.get_ref_width()
        old_rh = self.get_ref_height()

        self.set_ref_width(self.tied_to.get_width())
        self.set_ref_height(self.tied_to.get_height())

        return not fc(old_rw, self.get_ref_width()) or not fc(old_rh, self.get_ref_height())

    def get_xml(self, name = None, top = True, targets = None, full = False) :
        root = GlypherEntity.get_xml(self, name, top, full=full)
        root.set('tied_to', self.tied_to.get_name())
        return root

    def draw(self, cr) :
        if not self.get_visible() or self.get_blank() :
            return

        cr.save()
        bb = self.config[0].bbox
        cr.translate(bb[0]-self.tied_to.config[0].bbox[0],
                     bb[1]-self.tied_to.config[0].bbox[1])
        self.tied_to.draw(cr)
        cr.restore()

def make_mirror(parent, original) :
    new_mirror = GlypherMirror(parent, original)
    original.add_cousin(new_mirror)
    return new_mirror
