from Entity import *
import math

class GlypherPlane(GlypherEntity) :
    coords = (0,0)
    size = 3
    def set_coords(self, coords) : self.coords = coords
    def get_coords(self) : return self.coords
    def recalc_bbox(self, quiet = False) :
        self.cast()
        return GlypherEntity.recalc_bbox(self, quiet=quiet)
    
    def get_xml(self, name = None, top = True, targets = None) :
        root = GlypherEntity.get_xml(self, name, top)
        root.set('x', str(self.get_coords()[0]))
        root.set('y', str(self.get_coords()[0]))
        return root

    def cast(self) :
        self.set_ref_width(self.size*self.get_scaled_line_size())
        self.set_ref_height(self.size*self.get_scaled_line_size())

    def to_string(self, mode = "string") : return unicode("("+str(self.get_coords()[0])+","+str(self.get_coords()[1])+")");

    def __init__(self, parent = None, coords=(1.0,1.0), x_string = None, y_string = None) :
        GlypherEntity.__init__(self, parent)
        self.x_string = x_string
        self.y_string = y_string
        self.config[0].bbox[0] = 0
        self.config[0].bbox[1] = 0
        self.mes.append('plane')
        self.set_attachable(True)
        self.set_coords(coords)
        self.recalc_bbox()
    
    def draw(self, cr) :
        if not self.get_visible() : return
        cr.save()
        cr.set_source_rgba(0,0,0,0.2)
        l, t = [self.config[0].bbox[i]+self.padding[i] for i in (0,1)]
        cr.rectangle(l, t,
            self.get_ref_width() - self.padding[2], self.get_ref_height()-self.padding[3])
        cr.stroke()
        c1, c2 = (l+self.get_ref_width()/2, t+self.get_ref_height()/2)
        plane_radius = max(*map(abs, self.get_coords()))
        pr, pe = math.frexp(plane_radius); pe = pe*math.log(2)/math.log(10)
        plane_radius = int(pr*10 + 3)/10. * pow(10, pe)

        cr.save()
        cr.translate(c1, c2)
        s = self.get_height()/(2*plane_radius)
        cr.scale(s, -s)

        cr.set_line_width(plane_radius/20)
        cr.move_to(-plane_radius, 0)
        cr.line_to(plane_radius, 0)
        cr.stroke()
        cr.move_to(0, -plane_radius)
        cr.line_to(0, plane_radius)
        cr.stroke()

        d = self.get_coords()
        cr.set_source_rgba(0.0, 0.3, 0.3, 0.75)
        cr.set_font_size(plane_radius/5)

        mark = self.get_coords()[0]
        mark, x_string = self._coord_to_string(mark) if self.x_string is None else (mark, self.x_string)
        cr.move_to(mark, -plane_radius/20)
        cr.line_to(mark,  plane_radius/20)
        cr.move_to(mark, 2*plane_radius/20)
        cr.scale(1, -1)
        cr.show_text(x_string)
        cr.stroke()
        cr.scale(1, -1)

        mark = self.get_coords()[1]
        mark, y_string = self._coord_to_string(mark) if self.y_string is None else (mark, self.y_string)
        cr.move_to(-plane_radius/20, mark)
        cr.line_to( plane_radius/20, mark)
        cr.move_to(2*plane_radius/20, mark)
        cr.scale(1, -1)
        cr.show_text(y_string)
        cr.stroke()
        cr.scale(1, -1)

        #debug_print(plane_radius)
        cr.arc(d[0], d[1], plane_radius/30, 0, 2*math.pi)
        cr.set_source_rgb(0, 1, 0)
        cr.fill()
        cr.restore()

        cr.restore()

    def _coord_to_string(self, y) :
        if (abs(y) >= 0.01 and abs(y) < 1000) :
            if abs(y) >= 100 :
                string = ("%.0f"% y)
            elif abs(y) >= 10 :
                string = ("%.1f"% y)
            elif abs(y) >= 1 :
                string = ("%.2f"% y)
            else :
                string = ("%.3f"% y)
        else :
            string = ("%.1e" % y)
        return (float(string), string)

class GlypherComplexPlane(GlypherPlane) :
    def __init__(self, parent = None, z=complex(1.0), re_string = None, im_string = None) :
        GlypherPlane.__init__(self, parent, coords=(z.real, z.imag), x_string=re_string, y_string=im_string)
    
    def get_sympy(self) :
        z = self.get_coords()[0] + math.i*self.get_coords()[1]
        return sympy.core.sympify(str(z))
