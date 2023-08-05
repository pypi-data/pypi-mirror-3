from Entity import *
from Phrase import *

class GlypherSpace(GlypherEntity) :

    dims = (0,0)
    def set_dims(self, dims) : self.dims = dims; self.recalc_bbox()
    def get_dims(self) : return self.dims
    def recalc_bbox(self, quiet = False) :
        self.cast()
        #debug_print(self.ref_width)
        #debug_print(self.get_scaled_line_size())
        return GlypherEntity.recalc_bbox(self, quiet=quiet)
    
    def get_xml(self, name = None, top = True, targets = None, full = False) :
        root = GlypherEntity.get_xml(self, name, top, full=full)
        root.set('width', str(self.get_dims()[0]))
        root.set('height', str(self.get_dims()[0]))
        return root

    def cast(self) :
        self.set_ref_width(self.get_dims()[0] * (self.get_scaled_line_size() if self.as_line_height_scale else 1))
        self.set_ref_height(self.get_dims()[1] * (self.get_scaled_line_size() if self.as_line_height_scale else 1))

    def to_string(self, mode = "string") : return unicode(" ");

    def __init__(self, parent = None, dims=(0.1,0.1), as_line_height_scale = True) :
        GlypherEntity.__init__(self, parent)
        self.as_line_height_scale = as_line_height_scale

        self.config[0].bbox[0] = 0
        self.config[0].bbox[1] = 0
        self.mes.append('space')
        self.blank()
        self.set_attachable(False)
        #self.horizontal_ignore = True
        #self.vertical_ignore = True
        self.set_dims(dims)
    
    def draw(self, cr) :
        if not self.get_visible() : return
        if g.show_rectangles or not self.get_blank() :
            cr.save()
            cr.set_source_rgba(0,0,0,0.2)
            cr.rectangle(self.config[0].bbox[0]+self.padding[0], self.config[0].bbox[1]+self.padding[1],
                self.get_ref_width() - self.padding[2], self.get_ref_height()-self.padding[3])
            cr.stroke()
            cr.restore()

class GlypherVerticalSpacer(GlypherEntity) :
    length = None
    thickness = None
    def set_length(self, length) : self.set_p('length', length)
    def get_length(self) : return self.get_p('length')
    def set_thickness(self, thickness) : self.set_p('thickness', thickness)
    def get_thickness(self) : return self.get_p('thickness')
    def set_scaling(self, scaling) : self.set_p('scaling', scaling)
    def get_scaling(self) : return self.get_p('scaling')

    #def children_check(self, parent_change=False, quiet = False) :
    #    self.recalc_bbox(quiet=quiet)
    
    tied_to = None

    def to_string(self, mode = "string") : return unicode(" ");

    def __init__(self, parent = None, tied_to = None, scaling = 1.0) :
        GlypherEntity.__init__(self, parent)
        self.add_properties({'tied_to': None})
        self.set_always_recalc(True)
        self.mes.append('vertical_spacer')
        self.config[0].bbox[0] = 0
        self.config[0].bbox[1] = 0
        self.set_attachable(False)
        self.set_scaling(scaling)
        self.set_horizontal_ignore(True)
        self.set_tied_to(tied_to)
        self.recalc_bbox()
    
    def set_tied_to(self, entity) :
        self.tied_to = entity
        if self.tied_to == self.get_p('tied_to') :
            return
        self.set_p('tied_to', entity)
        self.recalc_bbox()

    def recalc_bbox(self, quiet = False) :
        self.tied_to = self.get_p('tied_to')
        self.cast()
        chg = GlypherEntity.recalc_bbox(self, quiet=quiet)
        return chg

    def cast(self) :
        if self.included() and self.tied_to :
            rh = self.tied_to.get_basebox_height() * self.get_scaling()
            for e in self.get_parent().entities :
                if e == self : continue
                rh -= e.get_height()
        else :
            rh = 10

        if rh < 0 : rh = 0
        self.set_ref_height(rh)

        self.set_ref_width(1 + self.padding[0] + self.padding[2])

    def draw(self, cr) :
        if not self.get_visible() or self.get_blank() or not g.show_rectangles : return
        cr.save()
        cr.set_source_rgb(*self.get_rgb_colour())
        cr.rectangle(self.config[0].bbox[0]+self.padding[0], self.config[0].bbox[1]+self.padding[1],
            self.get_ref_width() - self.padding[2], self.get_ref_height()-self.padding[3])
        #debug_print(self.config[0].bbox)
        cr.fill()
        cr.restore()

class GlypherHorizontalLine(GlypherEntity) :
    tied_to = None

    def set_length(self, length) : self.set_p('length', length)
    def get_length(self) : return self.get_p('length')
    def set_thickness(self, thickness) : self.set_p('thickness', thickness)
    def get_thickness(self) : return self.get_p('thickness')

    #def children_check(self, parent_change=False, quiet = False) :
    #    self.recalc_bbox(quiet=quiet)
    
    def to_string(self, mode = "string") : return "_";

    def __init__(self, parent = None, length = None, thickness = 0.05, tied_to = None, length_calc = None, thickness_too = False) :
        GlypherEntity.__init__(self, parent)
        self.add_properties({'thickness_too': False, 'tied_to': None})
        self.set_always_recalc(True)
        self.mes.append('horizontal_line')
        self.config[0].bbox[0] = 0
        self.config[0].bbox[3] = thickness
        self.set_ref_width(10 if length is None else length)
        self.set_ref_height(thickness * self.get_scaled_font_size())
        self.set_attachable(False)
        self.set_length(length)
        self.set_thickness(thickness)
        self.set_vertical_ignore(True)
        self.set_p('thickness_too', thickness_too)
        self.length_calc = length_calc
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
        #self.ref_bbox[0] = self.bbox[0]
        #self.ref_bbox[1] = self.bbox[1]
        old_rw = self.get_ref_width()
        old_rh = self.get_ref_height()

        thickness = self.get_thickness()*self.get_scaled_font_size()
        if self.tied_to is not None :
            self.set_length(self.tied_to.get_width())
            if self.get_p('thickness_too') :
                thickness = self.get_thickness()*self.tied_to.get_height()


        if self.get_length() is not None :
            rw = self.get_length()
        elif self.length_calc is not None : 
            rw = self.length_calc()
        else :
            rw = 0.3*self.get_scaled_font_size()
        rw += self.padding[0] + self.padding[2]
        self.set_ref_width(rw)

        self.set_ref_height(thickness + self.padding[1] + self.padding[3])
        return not fc(old_rw, self.get_ref_width()) or not fc(old_rh, self.get_ref_height())

    def draw(self, cr) :
        if not self.get_visible() or self.get_blank() : return
        cr.save()
        cr.set_source_rgb(*self.get_rgb_colour())
        cr.rectangle(self.config[0].bbox[0]+self.padding[0], self.config[0].bbox[1]+self.padding[1],
            self.get_ref_width() - self.padding[0] - self.padding[2], self.get_ref_height()-self.padding[1]-self.padding[3])
        cr.fill()
        cr.restore()

#FIXME: This and HL should be one class
class GlypherVerticalLine(GlypherEntity) :
    tied_to = None

    def set_length(self, length) : self.set_p('length', length)
    def get_length(self) : return self.get_p('length')
    def set_thickness(self, thickness) : self.set_p('thickness', thickness)
    def get_thickness(self) : return self.get_p('thickness')

    #def children_check(self, parent_change=False, quiet = False) :
    #    self.recalc_bbox(quiet=quiet)
    
    def to_string(self, mode = "string") : return "|";

    def __init__(self, parent = None, length = None, thickness = 0.05, tied_to = None, length_calc = None, thickness_too = False) :
        GlypherEntity.__init__(self, parent)
        self.add_properties({'thickness_too': False, 'tied_to': None})
        self.set_always_recalc(True)
        self.mes.append('vertical_line')
        self.config[0].bbox[1] = 0
        self.config[0].bbox[2] = thickness
        self.set_ref_height(10 if length is None else length)
        self.set_ref_width(thickness * self.get_scaled_font_size())
        self.set_length(length)
        self.set_thickness(thickness)
        self.set_horizontal_ignore(True)
        self.set_p('thickness_too', thickness_too)
        self.length_calc = length_calc
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
        #self.ref_bbox[0] = self.bbox[0]
        #self.ref_bbox[1] = self.bbox[1]
        old_rw = self.get_ref_height()
        old_rh = self.get_ref_width()

        thickness = self.get_thickness()*self.get_scaled_font_size()
        if self.tied_to is not None :
            self.set_length(self.tied_to.get_height())
            if self.get_p('thickness_too') :
                thickness = self.get_thickness()*self.tied_to.get_width()


        if self.get_length() is not None :
            rw = self.get_length()
        elif self.length_calc is not None : 
            rw = self.length_calc()
        else :
            rw = 0.3*self.get_scaled_font_size()
        rw += self.padding[1] + self.padding[3]
        self.set_ref_height(rw)

        self.set_ref_width(thickness + self.padding[0] + self.padding[2])
        return not fc(old_rw, self.get_ref_height()) or not fc(old_rh,
                                                               self.get_ref_width())

    def draw(self, cr) :
        if not self.get_visible() or self.get_blank() : return
        cr.save()
        cr.set_source_rgb(*self.get_rgb_colour())
        cr.rectangle(self.config[0].bbox[0]+self.padding[0], self.config[0].bbox[1]+self.padding[1],
            self.get_ref_width() - self.padding[0] - self.padding[2], self.get_ref_height()-self.padding[1]-self.padding[3])
        cr.fill()
        cr.restore()

g.phrasegroups['vertical_spacer'] = GlypherVerticalSpacer
