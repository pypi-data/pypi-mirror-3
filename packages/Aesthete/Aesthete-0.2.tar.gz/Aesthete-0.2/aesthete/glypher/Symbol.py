import glypher as g
import traceback
import Renderers
from Entity import *

class GlypherSymbol(GlypherEntity) :
    title = "GlypherSymbol"
    info_text = '''
Usually a single unicode characters, this is the basic graphical unit.
<i>Not to be confused with sympy Symbols</i>, which correspond more closely to
<b>Words</b>
        '''

    mid = None
    shape = u'\u25A3'
    ink = False
    def alt_to_ent(self, a) :
        return GlypherSymbol(self.get_parent(), a)
    def get_italic(self) : return self.get_p('italic')
    def set_italic(self, italic, quiet=False) :
        self.set_p('italic', italic)
        self.set_redraw_required()
        if not quiet : self.recalc_bbox()
    def get_shape(self) : return self.shape       #def get_shape(self) : return self.get_p('shape')
    def set_shape(self, shape) :
        self.shape = unicode(shape) #def set_shape(self, shape) : self.set_p('shape', shape)
        self.set_redraw_required()
    def get_ink(self) : return self.ink           #def get_ink(self) : return self.get_p('ink')
    def set_ink(self, ink) :
        self.ink = ink        #def set_ink(self, ink) : self.set_p('ink', ink)
        self.set_redraw_required()
    def get_mid(self) : return self.mid
    def set_mid(self, mid) :
        self.mid = mid
        self.set_redraw_required()

    rendering = None

    def check_combination(self, shape) :
        cmb = self.to_string() + unicode(shape)
        chg = cmb in g.combinations
        if chg :
            self.set_shape(g.combinations[cmb])
            self.recalc_bbox()
        return chg

    def get_xml(self, name = None, top = True, targets = None, full = False) :
        root = GlypherEntity.get_xml(self, name, top)
        root.set('shape', str(self.get_shape()))
        root.set('ink', str(self.get_ink()))
        return root
    def __init__(self, parent, shape, area = (0,0,0,0), code = None, text = None, align = ('c','m'), italic = None, bild = False, ink = False) :
        GlypherEntity.__init__(self, parent)
        self.add_properties({'align' : ('c', 'm'), 'italic' : g.get_default_italic_for_shape(shape),
                     'mid' : 0.5, 'have_alternatives' : True})

        self.topline = area[1]
        self.baseline = area[3]
        self.set_align(align)
        self.set_ink(ink)
        if italic is not None :
            self.set_italic(italic, True)
        self.set_shape(shape)
        
        self.mes.append('symbol')
        self.set_ref_width(area[2] - area[0])
        self.set_ref_height(area[3] - area[1])
        self.recalc_basebox()
        self.config[0].reset()
        pos = (self.config[0].bbox[0], self.config[0].bbox[3])
        self.old_bbox = [pos[0], pos[1], pos[0], pos[1]]

        self.recalc_bbox()

    def to_string(self, mode = "string") :
        if not self.get_visible() : return unicode("")
        elif self.get_blank() : return unicode(" ")

        uc = u'\u25a1'
        try :
            uc = unicode(self.get_shape())
        except UnicodeDecodeError :
            raise(RuntimeError('Could not change ' + self.get_shape() + ' to unicode'))
        return unicode(self.get_shape())

    def recalc_basebox(self, config = None, only_recalc_self = False) :
        b = self.config[0].get_bbox()
        mid = self.get_mid()
        if mid is None : mid = (b[3]-b[1])*0.5
        self.config[0].basebox = (b[0], (b[0]+b[2])*0.5, b[2], b[1], b[3]-mid, b[3])

    def get_caret_position(self, inside=False) :
        return GlypherEntity.get_caret_position(self, inside=inside, pos=[self.config[0].bbox[2], self.config[0].bbox[3]])
    def cast(self, shape, size, pos, code = None, align = ('l','b'), italic = None, bild = False, ink = False) :
        self.set_italic(g.get_default_italic_for_shape(shape) if italic is None else italic, quiet=True)
        self.set_shape(shape)
        self.set_align(align)
        self.set_ink(ink)

        self.rendering = Renderers.find_rendering(shape, code, italic=self.get_italic(), bold=self.get_ip('bold'))

        (rh,rw,mid) = self.rendering.draw(self.get_scaled_font_size(),\
            ink=ink, italic=self.get_italic(), bold=self.get_ip('bold'), font_name=self.get_ip('font_name'))
        #(rh,rw,mid) = self.rendering.draw(size, ink=ink)
        self.set_mid(mid)
        p = self.padding
        #rh += p[1]+p[3]
        #rw += p[0]+p[2]
        self.set_ref_width(rw)
        self.set_ref_height(rh)
        #if align[0] == 'l' :
        #    self.ref_bbox[0] = pos[0]
        #    self.ref_bbox[2] = pos[0] + rw
        #elif align[0] == 'c' :
        #    self.ref_bbox[0] = pos[0] - rw/2
        #    self.ref_bbox[2] = pos[0] + rw/2
        #else :
        #    self.ref_bbox[0] = pos[0] - rw
        #    self.ref_bbox[2] = pos[0]

        #if align[1] == 'b' :
        #    self.ref_bbox[3] = pos[1]
        #    self.ref_bbox[1] = pos[1] - rh
        #elif align[1] == 'm' :
        #    self.ref_bbox[1] = pos[1] - rh/2
        #    self.ref_bbox[3] = pos[1] + rh/2
        #else :
        #    self.ref_bbox[1] = pos[1]
        #    self.ref_bbox[3] = pos[1] + rh
        #self.ref_bbox = list(self.bbox)
    
    def recalc_bbox(self, quiet=False, old_bbox=None) :
        if self.get_shape() is None : return
        self.cast(self.get_shape(), self.get_scaled_font_size(), self.get_anchor(), \
            None, self.get_align(), self.get_italic(), None, self.get_ink())
        #traceback.print_stack()
        GlypherEntity.recalc_bbox(self, quiet=quiet)

        # Sort out zero-width symbols (we really should be able to handle these)
    
    def draw(self, cr) :
        if self.draw_offset != (0,0) :
            cr.translate(*self.draw_offset)
        self.draw_topbaseline(cr, (0,1,1))
        if not self.get_visible() or self.get_blank() : return
        #if self.get_scaled_font_size() != self.size : #TODO: find a more efficient way of doing this
        #    self.size = self.get_scaled_font_size()
            #self.cast(self.shape, self.get_scaled_font_size(), self.loc, self.text, None, self.align, self.italic)
        #debug_print(self.format_me())

        if g.show_rectangles :
            colour = (0.8,0.8,0.8)
        elif self.in_selected() :
            colour = (0.8, 0.2, 0.2)
        else :
            colour = self.get_rgb_colour()

        if not self.rendering :
            self.cast(self.get_shape(), self.get_scaled_font_size(), self.get_anchor(), \
                None, self.get_align(), self.get_italic(), None, self.get_ink())
        self.rendering.draw(self.get_scaled_font_size(), cr, self.config[0].bbox[0]+self.padding[0], self.config[0].bbox[1]+self.padding[1],\
            colour=colour,\
            ink=self.get_ink(), italic=self.get_italic(), bold=self.get_ip('bold'), font_name=self.get_ip('font_name'))
        if g.show_rectangles :
            cr.save()
            cr.set_source_rgba(0.5,0.5,1.0,0.2)
            cr.rectangle(self.config[0].bbox[0], self.config[0].bbox[1], self.config[0].bbox[2]-self.config[0].bbox[0], self.config[0].bbox[3]-self.config[0].bbox[1])
            cr.stroke()
            cr.set_source_rgba(0.5, 0.0, 1.0, 0.4)
            cr.move_to(self.config[0].basebox[0]-5, self.config[0].basebox[4])
            cr.line_to(self.config[0].basebox[2]+5, self.config[0].basebox[4])
            for i in (0,2) :
                cr.move_to(self.config[0].basebox[i], self.config[0].basebox[4]-2)
                cr.line_to(self.config[0].basebox[i], self.config[0].basebox[4]+2)
            cr.move_to(self.config[0].basebox[0]-5, self.config[0].basebox[3])
            cr.line_to(self.config[0].basebox[2]+5, self.config[0].basebox[3])
            cr.move_to(self.config[0].basebox[0]-5, self.config[0].basebox[5])
            cr.line_to(self.config[0].basebox[2]+5, self.config[0].basebox[5])
            cr.stroke()
            cr.restore()
        if self.draw_offset != (0,0) :
            cr.translate(-self.draw_offset[0], -self.draw_offset[1])

    def change_alternative(self, dir) :
        alts = g.find_alternatives(self.get_shape())
        if alts == None :
            if self.included() :
                return self.get_parent().change_alternative(dir)
            else :
                return False
        ind = alts[0].index(self.get_shape())
        self.set_shape(alts[0][(len(alts[0]) + ind + dir)%len(alts[0])])
        self.recalc_bbox()
        return True

    def draw_alternatives(self, cr) :
        if not self.get_visible() : return

        a = g.find_alternatives(self.get_shape(), generate_altbox=True)
        if a is None : return
        alts, altbox = (a[0], a[1])
        #cr.save()
        #cr.set_line_width(2.0)
        #cr.set_source_rgba(1.0,1.0,1.0)
        #cr.rectangle(self.config[0].bbox[0]-4, self.config[0].bbox[1]-4, self.config[0].bbox[2]-self.config[0].bbox[0]+8, self.config[0].bbox[3]-self.config[0].bbox[1]+8)
        #cr.fill_preserve()
        #cr.set_source_rgb(0.7,0.7,0.7)
        #cr.stroke()
        cr.save()
        cr.translate(self.config[0].bbox[2]+self.get_local_offset()[0]+20, self.config[0].bbox[1]+self.get_local_offset()[1])
        if alts != None : altbox.draw(cr, anchor=(0,0),\
            size=self.get_scaled_font_size(), rgb_colour=self.get_rgb_colour(), active=self.get_shape())
        cr.restore()
        #self.draw(cr)
        #cr.restore()
