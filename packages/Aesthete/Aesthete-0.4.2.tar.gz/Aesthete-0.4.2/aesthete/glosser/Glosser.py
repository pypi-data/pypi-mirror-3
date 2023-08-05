import gtk
import tarfile
from matplotlib.backends.backend_cairo import RendererCairo
import pangocairo
from aobject.utils import *
import pango
import gobject
from .. import glypher
import copy
from lxml import etree
import cairo
from aobject import aobject
from aobject.paths import *
from ..tablemaker import *

import rsvg
import StringIO
from TextView import *
from Glancer import *
from Glypher import *
from Containers import *

GLOSSER_PRESENTATION = True
GLOSSER_DESIGN = False

layout_bgcolor = { GLOSSER_PRESENTATION : (0.,0.,0.),
                   GLOSSER_DESIGN : (1.,1.,.8) }
widget_types = {
            'textview' : ('Text', gtk.STOCK_JUSTIFY_FILL, GlosserTextView,
                        lambda s : render_stock(s,gtk.STOCK_JUSTIFY_FILL)),
            'glyphentry' : ('Equation', 'aes-glypher', GlosserGlyphEntry,
                            lambda s : render_stock(s,'aes-glypher')),
            'glancer' : ('Plot', 'aes-glancer', GlosserGlancer,
                         lambda s : render_stock(s,'aes-glancer')),
            'vbox' : ('VBox', gtk.STOCK_GO_DOWN, GlosserVBox,
                         lambda s : render_stock(s,gtk.STOCK_GO_DOWN)),
            'bullets' : ('VBox', gtk.STOCK_SORT_ASCENDING, GlosserBullets,
                         lambda s : render_stock(s,gtk.STOCK_SORT_ASCENDING)) }

aname_root_to_ty = {}
for ty in widget_types.keys() :
    aname_root_to_ty[widget_types[ty][2].__name__] = ty

def _make_lambda_iw(obj, w) :
    return lambda b : obj.insert_widget(w)

def _px_to_float(px_str) :
    w = px_str
    if w.endswith('px') :
        f = float(w[:-2])
    else :
        f = float(w)
    return f
GLOSSER_SPRONK_CELL_NORMAL = 0
GLOSSER_SPRONK_CELL_OPEN = 1
GLOSSER_SPRONK_CELL_CLOSE = 2
GLOSSER_SPRONK_CELL_INITIAL = 3
GLOSSER_SPRONK_CELL_FINAL = 4

glosser_spronk_cell_colours = {\
        GLOSSER_SPRONK_CELL_OPEN : ('#DDDDDD', '#FFDDAA'),
        GLOSSER_SPRONK_CELL_INITIAL : ('#BBBBBB', '#FFAA00'),
        GLOSSER_SPRONK_CELL_NORMAL : ('#BBBBBB', '#FFAA00'),
        GLOSSER_SPRONK_CELL_FINAL : ('#BBBBBB', '#FFAA00'),
        GLOSSER_SPRONK_CELL_CLOSE : ('#DDDDDD', '#FFDDAA')}
class GlosserSpronkCellRenderer(gtk.GenericCellRenderer) :
    __gproperties__ = {
        "text": (gobject.TYPE_STRING, "text", "text", "", gobject.PARAM_READWRITE),
        "active": (gobject.TYPE_BOOLEAN, "active", "active", False, gobject.PARAM_READWRITE),
        "special": (gobject.TYPE_INT, "special", "special",0,4,
                    GLOSSER_SPRONK_CELL_NORMAL, gobject.PARAM_READWRITE),
    }

    def __init__(self) :
        self.__gobject_init__()
        self.spronk_font_face = cairo.ToyFontFace("Linux Libertine 8")

    def do_set_property(self, pspec, value) :
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec) :
        return getattr(self, pspec.name)

    def on_render(self, window, widget, background_area, cell_area, expose_area,
                  flags) :
        cr = window.cairo_create()
        
        cr.save()
        cr.translate(cell_area.x, cell_area.y)

        cr.rectangle(0, 0, cell_area.width, cell_area.height)
        colour = gtk.gdk.Color(\
            glosser_spronk_cell_colours[self.special][1 if self.active else 0])
        colour_list = [colour.red_float,
                       colour.green_float,
                       colour.blue_float,
                       1.]

        colour_list[3] = .5
        cr.set_source_rgba(*colour_list)
        cr.fill()
        colour_list[3] = 1.

        if self.special == GLOSSER_SPRONK_CELL_OPEN :
            cr.move_to(cell_area.width/2, cell_area.height)
            cr.rel_line_to(-10, 0)
            cr.rel_line_to(10, -cell_area.height)
            cr.rel_line_to(10, cell_area.height)
            cr.close_path()
            colour_list[3] = 1.
            cr.set_source_rgba(*colour_list)
            cr.fill()
        elif self.special == GLOSSER_SPRONK_CELL_CLOSE :
            cr.move_to(cell_area.width/2, 0)
            cr.rel_line_to(-10, 0)
            cr.rel_line_to(10, cell_area.height)
            cr.rel_line_to(10, -cell_area.height)
            cr.close_path()
            cr.set_source_rgba(*colour_list)
            cr.fill()
        elif self.special == GLOSSER_SPRONK_CELL_INITIAL :
            cr.move_to(cell_area.width/2,cell_area.height)
            cr.arc(cell_area.width/2, cell_area.height, 10, 3.14159, 0)
            cr.close_path()
            cr.set_source_rgba(*colour_list)
            cr.fill()
        elif self.special == GLOSSER_SPRONK_CELL_FINAL :
            cr.move_to(cell_area.width/2,0)
            cr.arc(cell_area.width/2, 0, 10, 0, 3.14159)
            cr.close_path()
            cr.set_source_rgba(*colour_list)
            cr.fill()
        elif self.special == GLOSSER_SPRONK_CELL_NORMAL :
            cr.rectangle(cell_area.width/2-10, 0, 20, cell_area.height)
            cr.set_source_rgba(*colour_list)
            cr.fill()

        cr.restore()

    line_height = 100
    def on_get_size(self, widget, cell_area=None):
        x = 0
        y = 0

        if cell_area is not None :
            x = cell_area.x
            y = cell_area.y

        w = 30
        h = 10

        return (x, y, w, h)

gobject.type_register(GlosserSpronkCellRenderer)

class GlosserSlideCellRenderer(gtk.GenericCellRenderer) :
    __gproperties__ = {
        "slide": (gobject.TYPE_PYOBJECT, "slide", "Slide", gobject.PARAM_READWRITE),
    }

    def __init__(self) :
        self.__gobject_init__()
        self.slide = None
        self.spronk_font_face = cairo.ToyFontFace("Linux Libertine 5")

    def do_set_property(self, pspec, value) :
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec) :
        return getattr(self, pspec.name)

    def on_render(self, window, widget, background_area, cell_area, expose_area,
                  flags) :
        cr = window.cairo_create()
        
        cr.save()
        cr.translate(cell_area.x, cell_area.y)

        if self.slide is None :
            return

        ci = self.slide.thumb
        if cr is not None and ci is not None :
            spnum = len(self.slide.spronks)
            if spnum > 0:
                cr.save()
                mid = ci.get_height()/2
                cr.set_source_rgb(.5,.5,.5)
                if spnum > 6 :
                    text = str(len(self.slide.spronks))
                    cr.set_font_face(self.spronk_font_face)
                    cr.set_font_size(8.)
                    for i in range(0, len(text)) :
                        cr.move_to(0, mid-4*len(text)+8*i)
                        cr.show_text(text[i])
                else :
                    cr.save()
                    for i in range(0, spnum) :
                        cr.move_to(0, mid-3*spnum+6*i)
                        cr.rel_line_to(0, 6)
                        cr.rel_line_to(3, -3)
                        cr.close_path()
                        cr.fill()
                    cr.restore()
                cr.restore()
            cr.save()
            cr.translate(5, 0)
            cr.set_source_surface(ci, 0, 0)
            cr.paint()
            cr.restore()
        cr.restore()

    line_height = 100
    def on_get_size(self, widget, cell_area=None):
        x = 0
        y = 0

        if cell_area is not None :
            x = cell_area.x
            y = cell_area.y

        if self.slide is None or self.slide.thumb is None :
            w = self.line_height
            h = self.line_height
        else :
            w = int(self.slide.thumb.get_width())
            h = int(self.slide.thumb.get_height())

        return (x, y, w, h)

        #ims = self.main_phrase.cairo_cache_image_surface
gobject.type_register(GlosserSlideCellRenderer)


def _fill_text(root, nodeid, text) :
    node = root.xpath('//*[@id=\'%s\']'%nodeid)

    if len(node) != 1 :
        return
        #raise RuntimeError('Malformed template SVG :'+\
        #                   ' Expected 1 id to be '+nodeid)

    node = node[0]

    #for child in node :
    #    node.remove(child)

    #text_node = _make_text_tag()
    text_node = node[0]
    text_node.text = text
    node.append(text_node)

def _make_text_tag() :
    el = etree.Element('tspan', role='line')
    return el

class GlosserLayout(gtk.Layout) :
    __gsignals__ =     { \
                "expose-event" : "override", \
                 "button-press-event" : "override",\
                 "button-release-event" : "override",\
                "scroll-event" : "override",\
                "size-allocate" : "override",\
            }
    handle = None
    width = None
    height = None
    line_num = 0
    line_indicators = ()
    default_height = 100.
    lines = None

    def do_size_allocate(self, allocation) :
        gtk.Layout.do_size_allocate(self, allocation)
        self._resize_to_allocation(allocation)

    def __init__(self, presentation=False):
        gtk.Layout.__init__(self)

        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.add_events(gtk.gdk.SCROLL_MASK)

        self.pilcrow_font_face = cairo.ToyFontFace("Linux Libertine 20")
        self.am_presentation = presentation

    def do_expose_event(self, event):
        cr = self.get_bin_window().cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.get_bin_window().get_size())

    def get_rat(self) :
        al = self.get_allocation()
        swidth = al.width
        sheight = al.height
        twidth = self.width
        theight = self.height
        rath = sheight/float(theight)
        ratw = swidth/float(twidth)
        rat = min(rath, ratw)
        if self.show_decoration :
            rat *= 0.8
        return rat

    def translate_dist(self, d, rev=False) :
        rat = self.get_rat()
        if rev :
            d /= rat
        else :
            d *= rat

        return d

    def translate_dim(self, w, h) :
        rat = self.get_rat()

        w *= rat
        h *= rat

        return w, h

    def translate_body_pos(self, x, y, rev=False) :
        if not rev :
            x += self.body_x
            y += self.body_y
        pos = self.translate_pos(x, y, rev=rev)
        if rev :
            pos = (pos[0]-self.body_x, pos[1]-self.body_y)
        return pos

    def translate_pos(self, x, y, rev=False) :
        al = self.get_allocation()
        swidth = al.width
        sheight = al.height
        twidth = self.width
        theight = self.height
        rat = self.get_rat()

        if rev :
            x -= .5*(swidth-rat*twidth)
            y -= .5*(sheight-rat*theight)
            x /= rat
            y /= rat
        else :
            x *= rat
            y *= rat
            x += .5*(swidth-rat*twidth)
            y += .5*(sheight-rat*theight)

        return x, y

    def draw(self, cr, swidth, sheight):
        cr.save()
        cr.set_source_rgb(*layout_bgcolor[self.am_presentation])
        cr.rectangle(0, 0, swidth, sheight); cr.fill()

        if self.handle is not None :
            rat = self.get_rat()
            twidth = self.width
            theight = self.height
            #rat = swidth/float(twidth)
            #if self.show_decoration :
            #    rat *= 0.8
            cr.translate(0.5*(swidth-rat*twidth),
                         0.5*(sheight-rat*theight))
            cr.scale(rat, rat)

            if self.show_decoration :
                blurrad = 2.
                for i in range(1,10) :
                    cr.rectangle(-blurrad*i,-blurrad*i,twidth+2*blurrad*i,theight+2*blurrad*i)
                    cr.set_source_rgba(0.,0.,0.,0.5/float(i))
                    cr.fill()

            self.handle.render_cairo(cr)

            if self.show_decoration :
                y = 0
                i = 0
                current_y = None
                current_height = None
                for line in self.lines :
                    cr.set_source_rgba(0.85,0.85,0.85,1.)
                    cr.rectangle(self.body_x-13, self.body_y+y, 10., line[1].h)
                    cr.fill()

                    if i == self.line_num :
                        current_y = y
                        current_height = line[1].h

                    y += line[1].h
                    i += 1

                if current_y is None :
                    current_y = y

                if self.current_widget is not None :
                    cr.set_source_rgba(0.5,0.5,0.5,1.)
                    cr.rectangle(self.body_x-18,
                                 self.body_y+self.current_widget.y, 5,
                                 self.current_widget.h)
                    cr.fill()

                rx, ry = (self.body_x-13, self.body_y+current_y)

                if current_height is not None :
                    linear_gradient = cairo.LinearGradient(rx, ry, rx,
                                                           ry+current_height)
                    linear_gradient.add_color_stop_rgba(0, 0.85, 0.85, 0.85, 1.)
                    linear_gradient.add_color_stop_rgba(0.25, 0.7, 0.7, 0.7, .8)
                    linear_gradient.add_color_stop_rgba(0.75, 0.7, 0.7, 0.7, .8)
                    linear_gradient.add_color_stop_rgba(1, 0.85, 0.85, 0.85, 1.)
                else :
                    current_height = self.default_height
                    linear_gradient = cairo.LinearGradient(rx, ry, rx,
                                                           ry+current_height)
                    linear_gradient.add_color_stop_rgba(0, 0.85, 0.85, 0.85, 1.)
                    linear_gradient.add_color_stop_rgba(0.5, 0.7, 0.7, 0.7, .2)
                    linear_gradient.add_color_stop_rgba(1, 0.85, 0.85, 0.85, 0.)

                cr.set_source(linear_gradient)

                cr.rectangle(rx, ry, 10., current_height)
                cr.fill()
        
                cr.move_to(self.body_x-30, self.body_y+current_y)
                cr.set_source_rgba(0.8,0.8,0.8,1.)
                cr.set_font_face(self.pilcrow_font_face)
                cr.set_font_size(20.)
                cr.show_text(u'\u00b6')
                #cr.set_source_rgba(0.4,0.4,0.4,1.)
                i = 0
                for ind in self.line_indicators :
                    cr.save()
                    cr.translate(self.body_x-35,
                                 self.body_y+current_y+\
                                 i*20)

                    if isinstance(ind, gtk.gdk.Pixbuf) :
                        cr.set_source_pixbuf(ind, 0, 0)
                        cr.paint()
                        cr.stroke()
                    else :
                        cr.move_to(4, 20)
                        cr.show_text(ind)
                    cr.restore()
                    i += 1

                #cr.set_source_rgba(0.8,0.8,0.8,1.)
                #cr.set_line_width(10.)
                #cr.move_to(self.body_x-8, self.body_y+current_y)
                #cr.rel_line_to(0, current_height)
                #cr.stroke()
        
        cr.restore()

    def do_button_press_event(self, event) :
        return False

    def do_button_release_event(self, event) :
        return False

    def do_scroll_event(self, event) :
        return False

    def _resize_to_allocation(self, allocation=None) :
        pass

class GlosserSlide(aobject.AObject) :
    title = None
    num = None
    thumb = None
    lines = None
    spronks = None
    variant = 'basic'

    def aes_get_parameters(self) :
        return {'num' : self.get_num()}

    def pre_spronk(self) :
        for l in self.lines :
            l[1].initial_spronk()
            if l[1].container :
                for w in l[1].contained :
                    w.initial_spronk()

    def execute_all_spronks(self) :
        self.pre_spronk()
        for n in range(0, len(self.spronks)) :
            self.execute_spronk(n)

    def execute_spronk(self, num, reverse=False) :
        n = 1 if reverse else 0
        for action_pair in self.spronks[num] :
            if action_pair[n] is not None :
                action_pair[n]()

    def add_to_spronk(self, num, action, reverse=None) :
        for l in range(len(self.spronks), num+1) :
            self.spronks.append([])
        self.spronks[num].append((action, reverse))

    def remove_from_spronks(self, action) :
        for spronk in self.spronks :
            for action_pair in spronk :
                if action == action_pair[0] :
                    spronk.remove(action_pair)

    #PROPERTIES
    def get_auto_aesthete_properties(self):
        return {
            'num' : (int,),
            'title' : (str,),
            'variant' : (str,),
        }
    #BEGIN PROPERTIES FUNCTIONS
    def get_title(self) :
        return self.title if self.title is not None else ''
    def change_title(self, val) :
        self.title = val if val != "" else None
        self.reload()
    def change_variant(self, val) :
        self.variant = val
        self.reload()
    #END PROPERTIES FUNCTIONS

    def reload(self) :
        self.reload_slide(self.num, change_current=False)

    def __init__(self, num, variant, reload_slide, variant_lsto, env=None) :
        self.reload_slide = reload_slide
        self.num = num
        self.lines = []
        self.spronks = []
        self.variant_lsto = variant_lsto
        aobject.AObject.__init__(self, name_root='GlosserSlide',
                                 env=env,
                                 view_object=False,
                                 elevate=False)
        self.set_variant(variant)
        self.action_panel = self.make_action_panel()

    def render_widgets_to_cairo(self, cr, ignore_spronks=True) :
        cr.save()
        for l in self.lines :
            cr.save()
            cr.translate(l[1].x, l[1].y)
            l[1].presentation_draw(cr, 1., ignore_spronks=ignore_spronks)
            cr.restore()
        cr.restore()

    def remove_line(self, n) :
        self.lines[n][1].remove_from_layouts()
        self.lines.remove(self.lines[n])

    def insert_line(self, n, ty, widget, line_height, alignment) :
        self.lines.insert(n, [ty, widget, line_height, alignment])

    def set_title(self, title='') :
        self.change_property('title', title)
    def get_num(self) :
        return self.num

    def set_thumb(self, thumb) :
        self.thumb = thumb
    def get_thumb(self) :
        return self.thumb

    def fill_in_xml(self, xml) :
        root = xml.getroot()

        title_text = self.title
        if title_text is None : title_text = '[NO TITLE]'
        _fill_text(root, 'glosser_title', title_text)

        num_text = str(self.get_num()+1)
        _fill_text(root, 'glosser_number', num_text)

    def make_action_panel(self) :
        win = gtk.VBox()
        line_table_maker = PreferencesTableMaker()
        line_table_maker.append_row("Title",
                                    self.aes_method_entry_update("title"))

        variant_cmbo = gtk.ComboBox(self.variant_lsto)
        variant_crtx = gtk.CellRendererText()
        variant_cmbo.pack_start(variant_crtx, True)
        variant_cmbo.add_attribute(variant_crtx, 'text', 1)
        line_table_maker.append_row('Variant',
                                    variant_cmbo)
        self.aes_method_automate_combo(variant_cmbo, 'variant', 0)

        win.aes_title = "Slide %s" % self.get_num()
        win.pack_start(line_table_maker.make_table())
        win.show_all()
        return win

class GlosserBasic(gtk.VBox) :
    complete_widgets_list = None
    presentation = None

    def go_previous(self) :
        self.set_slide(self.slides.index(self.current_slide)-1)
    def go_next(self) :
        self.set_slide(self.slides.index(self.current_slide)+1)
    def go_first(self) :
        self.set_slide(0)
    def go_last(self) :
        self.set_slide(len(self.slides)-1)

    def do_key_release_event(self, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        
        if m_control and not m_alt and not m_shift :
            if keyname == 'Home' :
                self.go_first()
                return True
            if keyname == 'End' :
                self.go_last()
                return True
        if keyname == 'Page_Up' :
            self.go_previous()
        if keyname == 'Page_Down' :
            self.go_next()
        if keyname == 'Escape' and self.presentation is not None :
            self.get_parent().unfullscreen()
            self.get_parent().hide()
            self.presentation.grab_focus()
            return True

        return False

    __gsignals__ =     { \
                 "key-release-event" : "override",\
            }
    slide_list = None
    
    default_template = 'basic'
    current_slide = None
    current_xml = None
    current_variant = ""

    template = None

    conference = None
    date = None
    institute = None
    presenter = None

    def set_current_line_alignment(self, al) :
        if self.current_line in range(0, len(self.current_slide.lines)) :
            self.current_slide.lines[self.current_line][3] = al
            self.do_widget_pos_update(self, None)

    def __init__(self, layout=None, template=template, slides=None, complete_widgets_list=None):
        gtk.VBox.__init__(self)
        if layout is None :
            layout = GlosserLayout()
        self.layout = layout
        self.connect_after("size-allocate", self.do_widget_pos_update)
        self.set_property("can-focus", True)

        self.add_events(gtk.gdk.KEY_RELEASE_MASK)

        if template is None :
            template = { 'name' : self.default_template }
        self.template = template

        if complete_widgets_list is None :
            complete_widgets_list = []
        self.complete_widgets_list = complete_widgets_list

        if slides is None :
            self.slides = []
        else :
            self.slides = slides

        self.layout.show_decoration = False

        self.pack_start(self.layout)

        self.grab_focus()

        self.set_slide(0)

        self.show_all()

    def do_widget_pos_update(self, widget, req) :
        if self.current_slide is None :
            return 

        y = 0
        for l in self.current_slide.lines :
            widget = l[1]
            #new_pos = map(int,self.layout.translate_pos(
            #        self.template['body']['x'],
            #        self.template['body']['y']+y))
            if l[3] == 'left' :
                offset = 0
            elif l[3] == 'centre' :
                offset = self.template["body"]["width"]-widget.w
                offset *= 0.5
            elif l[3] == 'right' :
                offset = self.template["body"]["width"]-widget.w
            #new_pos[0] += int(offset)
            #new_x, new_y = map(int,self.layout.translate_pos(new_pos[0],
            #                                               new_pos[1],
            #                                         rev=True))
            #new_x, new_y = self.template["body"]["x"], self.template["body"]["y"]+y
            new_x = int(offset)
            new_y = y

            #offset = self.layout.translate_pos(body_x, body_y+y)
            if abs(new_x-widget.x) > 5 or abs(new_y-widget.y) > 5:
                widget.move(new_x, new_y)

            #if widget.current_offset[subwidget] != \
            #        offset or\
            #   widget.current_scaling[subwidget] != \
            #        self.layout.translate_dist(1) or \
            #  (widget.x, widget.y) != (new_x,new_y) :
            #    widget.offset(subwidget, *offset)
            #    widget.rescale(subwidget, self.layout.translate_dist(1))
            #    widget.move(new_x, new_y)

            y += widget.h


    def set_template_variant_xml(self, variant, force=False) :
        if variant == self.current_variant and not force :
            return
        self.current_variant = variant
        self.current_xml = copy.deepcopy(self.template['variants'][variant]['xml'])

        root = self.current_xml.getroot()
        body_node = root.xpath('//*[@id=\'glosser_body\']')

        if len(body_node) != 1 :
            raise RuntimeError('Malformed template SVG :'+\
                               ' Expected one "rect" id to be glosser_body')

        body_node = body_node[0]
        
        body = { 'x' : _px_to_float(body_node.get('x')),
                 'y' : _px_to_float(body_node.get('y')),
                 'width' : _px_to_float(body_node.get('width')),
                 'height' : _px_to_float(body_node.get('height')) }
        self.template['body'] = body

        body_node.getparent().remove(body_node)

    def set_slide(self, n=None, change_current=True, xml=None) :
        have_changed = False
        old_slide = self.current_slide
        if n is not None :
            if n < 0 or n >= len(self.slides) :
                return
            slide = self.slides[n]
            if change_current and slide != self.current_slide :
                have_changed = True
                self.current_slide = slide
        else :
            slide = self.current_slide

        # Even if we do not want to change TO this slide, we may still need to
        # update it
        change_current = change_current or slide==self.current_slide

        if slide is None :
            return

        n = slide.num

        if self.current_xml is None :
            return

        self.set_template_variant_xml(slide.variant)

        if xml is None :
            if change_current :
                xml = self.current_xml
            else :
                xml = copy.deepcopy(self.current_xml)

        slide.fill_in_xml(xml)

        root = xml.getroot()

        conf_text = self.conference
        if conf_text is None : conf_text = ''
        _fill_text(root, 'glosser_conference', conf_text)
        _fill_text(root, 'glosser_total', str(len(self.slides)))

        attributes = ['presenter', 'institute', 'date', 'conference']
        for attribute in attributes :
            val = self.__getattribute__(attribute)
            if val is None :
                val = ''
            _fill_text(root, 'glosser_'+attribute, str(val))
        
        _fill_text(root, 'glosser_date_big', self.date)
        _fill_text(root, 'glosser_presenter_institute', "%s (%s)" % (\
                                            self.presenter,
                                            self.institute))

        if have_changed and self.presentation is None and self.get_aenv() is not None and \
                self.get_aenv().action_panel is not None :
            self.get_aenv().action_panel.to_action_panel(slide.action_panel)
        if change_current :

            h = self.template['body']['height']

            if old_slide != self.current_slide :
                if old_slide is not None :
                    for line in old_slide.lines :
                        line[1].remove_from_layouts()

                for line in slide.lines :
                    widget = line[1]
                    line[1].restore_to_layouts()

            slide.pre_spronk()

            self.do_widget_pos_update(self, None)

        self.redraw(slide, xml, change_current=change_current)

    def redraw(self, slide=None, xml=None, change_current=True) :
        if slide is None :
            slide = self.current_slide

        if xml is None :
            self.set_template_variant_xml(slide.variant)
            xml = self.current_xml

        if xml is not None and \
                slide is not None :
            svg = StringIO.StringIO()
            xml.write(svg)
            handle = rsvg.Handle()
            handle.write(svg.getvalue())
            handle.close()

            if change_current :
                self.layout.width = self.template['width']
                self.layout.height = self.template['height']
                self.layout.handle = handle
                #self.layout.line_num = self.current_line
                self.layout.lines = slide.lines
                #self.layout.current_widget = self.current_widget
                #if self.current_line < len(slide.lines) :
                #    ty = slide.lines[self.current_line][0]
                #    self.layout.line_indicators = \
                #        [ widget_types[ty][3](self.get_style())]
                #    if self.current_widget is not None and self.current_widget != slide.lines[self.current_line][1]:
                #        ty = self.current_widget.ty
                #        self.layout.line_indicators.append(widget_types[ty][3](self.get_style()))
                #else :
                #    self.layout.line_indicators = ( u'\u273c', )
                self.layout.body_x = self.template['body']['x']
                self.layout.body_y = self.template['body']['y']
                self.layout.body_w = self.template['body']['width']
                self.layout.body_h = self.template['body']['height']

            self.layout.queue_draw()

class GlosserPresentation(GlosserBasic) :
    presentation = None
    current_spronk = 0

    def go_first(self) :
        self.set_slide(0)
        self.current_spronk = 0
    def go_last(self) :
        self.set_slide(len(self.slides)-1)
        self.current_slide.execute_all_spronks()
        self.current_spronk = len(self.current_slide.spronks)

    def go_previous(self) :
        if self.current_spronk == 0 :
            self.set_slide(self.slides.index(self.current_slide)-1)
        else :
            self.current_spronk -= 1
            self.current_slide.execute_spronk(self.current_spronk, reverse=True)
    def go_next(self) :
        if self.current_spronk == len(self.current_slide.spronks) :
            if self.current_slide == self.slides[-1] :
                return
            else :
                self.set_slide(self.slides.index(self.current_slide)+1)
                self.current_spronk = 0
        else :
            self.current_slide.execute_spronk(self.current_spronk, reverse=False)
            self.current_spronk += 1

    def do_key_release_event(self, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        debug_print(keyname)
        
        if keyname == 'Escape' :
            self.get_parent().unfullscreen()
            self.get_parent().hide()
            self.presentation.grab_focus()
            return True

        return GlosserBasic.do_key_release_event(self, event)

    def __init__(self, slides=None, template=None, complete_widgets_list=None, presentation=None):
        self.presentation = presentation
        layout = GlosserLayout(presentation=GLOSSER_PRESENTATION)
        GlosserBasic.__init__(self, layout=layout, template=template, slides=slides,
                              complete_widgets_list=complete_widgets_list)

class Glosser(GlosserBasic, aobject.AObject) :
    current_widget = None
    #def change_current_line(self, n=None) :
    #    ret = GlosserBasic.change_current_line(self, n=n)

    #    if not ret :
    #        return False

    #    if n < len(self.current_slide.lines) :
    #        self.change_current_widget(self.current_slide.lines[n][1])

    #    self.redraw()

    from_spronk = None
    def update_spronk_strip(self) :
        if self.current_slide is None :
            return

        slide = self.current_slide

        self.spronk_buffer.clear()

        w = self.current_widget

        cwh = w is None or w.initial_hide

        self.spronk_buffer.insert(0, (GLOSSER_SPRONK_CELL_OPEN, not cwh, u'\u21c8'))
        
        self.spronk_buffer.insert(1, (GLOSSER_SPRONK_CELL_INITIAL, not cwh, 'Initial'))

        l = 2
        for spronk in slide.spronks :
            colour = '#BBBBBB'
            for action_pair in spronk :
                action = action_pair[0]
                if w and action == w.show :
                    cwh = False
                if w and action == w.hide :
                    cwh = True
            if not cwh :
                colour = '#FFAA00'

            text = ''

            ty = GLOSSER_SPRONK_CELL_NORMAL if len(slide.spronks)+1 > l else \
                 GLOSSER_SPRONK_CELL_FINAL
            self.spronk_buffer.insert(l, (ty, not cwh, text))
            l += 1

        post_colour = '#DDDDDD'

        if not cwh :
            post_colour = '#FFDD00'

        self.spronk_buffer.insert(l, (GLOSSER_SPRONK_CELL_CLOSE, not cwh, u'\u21ca'))

        self.slide_list_trvw.queue_draw()

    current_widget = None
    def change_current_line(self, n=None) :

        if self.current_slide is None :
            self.current_line = 0
            return False

        if n is None :
            n = self.current_line

        if n > len(self.current_slide.lines) :
            n = len(self.current_slide.lines)
        elif n < 0 :
            n = 0

        self.current_line = n

        if self.get_current_widget_in_line() is None :
            self.change_current_widget(None)
        elif self.get_current_widget_in_line() == -1 :
            self.change_current_widget(self.current_slide.lines[n][1])

        self.redraw()

    def get_current_widget_in_line(self) :
        if self.current_slide is None :
            return None
        if 0 > self.current_line or len(self.current_slide.lines) <=  self.current_line:
            return None
        if self.current_widget == self.current_slide.lines[self.current_line][1] :
            return -1
        if not self.current_slide.lines[self.current_line][1].container :
            return -1
        if self.current_widget not in self.current_slide.lines[self.current_line][1].contained:
            return -1
        return self.current_slide.lines[self.current_line][1].contained.index(self.current_widget)

    current_line = 0
    def change_current_widget(self, widget) :
        if widget == self.current_widget :
            return

        if widget.slide != self.current_slide :
            return

        self.current_widget = widget
        self.update_spronk_strip()

        if widget is not None :
            widget.design_widget.grab_focus()

            win = widget.get_action_panel()
            if win is not None and self.presentation is not None and self.get_aenv() is not None and \
                        self.get_aenv().action_panel is not None :
                self.get_aenv().action_panel.to_action_panel(win)

    def do_key_release_event(self, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        
        if m_control and not m_alt and not m_shift :
            if keyname == 'Down' :
                widpos = self.get_current_widget_in_line()

                if widpos is None :
                    self.change_current_line(self.current_line+1)
                else :
                    line_widget = self.current_slide.lines[self.current_line][1]
                    if not line_widget.container or widpos == len(line_widget.contained)-1 :
                        self.change_current_line(self.current_line+1)
                    else :
                        self.change_current_widget(line_widget.contained[widpos+1])
                        self.redraw()
                #if self.current_line < 0 or \
                #   self.current_line >= len(self.current_slide.lines) :
                #    self.change_current_line(self.current_line+1)
                #if line_widget.container and len(line_widget.contained) > 0 :
                #    if self.current_widget is None :
                #        self.current_widget = line_widget.contained[0]
                #        self.redraw()
                #    elif line_widget.contained[-1] == self.current_widget :
                #        self.change_current_line(self.current_line+1)
                #    else :
                #        self.current_widget = \
                #            line_widget.contained[1+
                #            line_widget.contained.index(self.current_widget)]
                #        self.redraw()
                #else :
                #    self.change_current_line(self.current_line+1)
                return True
            elif keyname == 'Up' :
                widpos = self.get_current_widget_in_line()

                if widpos is None or widpos == -1 :
                    self.change_current_line(self.current_line-1)
                else :
                    line_widget = self.current_slide.lines[self.current_line][1]
                    if widpos == 0 :
                        self.change_current_widget(line_widget)
                        self.redraw()
                    else :
                        self.change_current_widget(line_widget.contained[widpos-1])
                        self.redraw()
                #if self.current_line < 0 or \
                #   self.current_line >= len(self.current_slide.lines) :
                #    self.change_current_line(self.current_line-1)
                #line_widget = self.current_slide.lines[self.current_line][1]
                #if line_widget.container and len(line_widget.contained) > 0 :
                #    if self.current_widget is None :
                #        self.change_current_line(self.current_line-1)
                #    elif line_widget.contained[0] == self.current_widget :
                #        self.current_widget = None
                #        self.redraw()
                #    else :
                #        self.current_widget = \
                #            line_widget.contained[-1+
                #            line_widget.contained.index(self.current_widget)]
                #        self.redraw()
                #else :
                #    self.change_current_line(self.current_line-1)
                #return True
            elif keyname == 'BackSpace' :
                self.remove_current_line()
                return True

        return GlosserBasic.do_key_release_event(self, event)

    def remove_current_line(self) :
        if self.current_line in range(0,len(self.current_slide.lines)) :
            self.complete_widgets_list.remove(self.current_slide.lines[self.current_line][1])
            self.current_slide.remove_line(self.current_line)
        self.change_current_line()
        self.set_slide()

    def __del__(self) :
        aobject.AObject.__del__(self)

    #PROPERTIES
    def get_auto_aesthete_properties(self):
        return {
            'conference' : (str,(aobject.AOBJECT_CAN_NONE,)),
            'date' : (str,(aobject.AOBJECT_CAN_NONE,)),
            'presenter' : (str,(aobject.AOBJECT_CAN_NONE,)),
            'institute' : (str,(aobject.AOBJECT_CAN_NONE,)),
            'template' : (str,),
        }
    #BEGIN PROPERTIES FUNCTIONS
    def get_template(self, val=None) :
        return self.template['name'] if self.template is not None else ''
    def change_template(self, val) :
        if val == '' :
            val = None
        self.set_template(val)
    def change_date(self, val) :
        if val == '' :
            self.date = None
        else :
            self.date = val
            self.presentation_instance.date = val
        self.set_slide()
    def change_presenter(self, val) :
        if val == '' :
            self.presenter = None
        else :
            self.presenter = val
            self.presentation_instance.presenter = val
        self.set_slide()
    def change_institute(self, val) :
        if val == '' :
            self.institute = None
        else :
            self.institute = val
            self.presentation_instance.institute = val
        self.set_slide()
    def change_conference(self, val) :
        if val == '' :
            self.conference = None
        else :
            self.conference = val
            self.presentation_instance.conference = val
        self.set_slide()
    #END PROPERTIES FUNCTIONS

    def make_action_panel(self) :
        win = gtk.VBox()
        line_table_maker = PreferencesTableMaker()
        line_table_maker.append_row("Conf",
                                    self.aes_method_entry_update("conference"))
        line_table_maker.append_row("Presenter",
                                    self.aes_method_entry_update("presenter"))
        line_table_maker.append_row("Date",
                                    self.aes_method_entry_update("date"))
        line_table_maker.append_row("Institute",
                                    self.aes_method_entry_update("institute"))

        template_cmbo = gtk.ComboBox(template_lsto)
        template_crtx = gtk.CellRendererText()
        template_cmbo.pack_start(template_crtx, True)
        template_cmbo.add_attribute(template_crtx, 'text', 1)
        line_table_maker.append_row("Template", template_cmbo)
        self.aes_method_automate_combo(template_cmbo, 'template', 0)

        win.aes_title = "Presentation"
        win.pack_start(line_table_maker.make_table())
        win.show_all()

        return win

    def __init__(self, slides=None, complete_widgets_list=None, env=None):
        self.slide_list = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_PYOBJECT)

        self.variant_lsto = gtk.ListStore(str, str)

        self.template = {'name':self.default_template}

        if complete_widgets_list is None :
            complete_widgets_list = []
        self.complete_widgets_list = complete_widgets_list



        if slides is None :
            self.slides = []
        else :
            self.slides = slides
        self.layout = GlosserLayout(presentation=GLOSSER_DESIGN)

        self.presentation_instance = GlosserPresentation(slides=self.slides,
                                                         template=self.template,
                                             complete_widgets_list=complete_widgets_list,
                                             presentation=self)
        self.presentation_window = gtk.Window()
        self.presentation_window.add(self.presentation_instance)
        self.presentation_instance.show_all()
        self.presentation_window.hide()

        gtk.VBox.__init__(self)

        aobject.AObject.__init__(self, name_root="Glosser", env=env,
                                 view_object=True,
                                 elevate=True)

        self.connect_after("size-allocate", self.do_widget_pos_update)
        self.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.presentation_window.connect_after("show", lambda w : (w.fullscreen(), w.grab_focus()))

        self.layout.show_decoration = True

        self.set_template()
        #self.new_slide(0, 'basic')

        toolbar = gtk.Toolbar()

        present_tbut = gtk.ToolButton('aes-glosser')
        present_tbut.connect("clicked", lambda w :(\
                             self.presentation_instance.go_first(),
                             self.presentation_window.show()))
        toolbar.insert(present_tbut, -1)

        pdf_tbut = gtk.ToolButton(gtk.STOCK_SAVE_AS)
        pdf_tbut.connect("clicked", lambda w :\
                             self.run_chooser())
        toolbar.insert(pdf_tbut, -1)

        toolbar.insert(gtk.SeparatorToolItem(), -1)


        for w in widget_types :
            wt = widget_types[w]
            new_tbut = gtk.ToolButton(wt[1])
            new_tbut.set_tooltip_text(wt[0])
            new_tbut.connect('clicked', _make_lambda_iw(self, w))
            toolbar.insert(new_tbut, -1)

        toolbar.insert(gtk.SeparatorToolItem(), -1)

        left_tbut = gtk.ToolButton(gtk.STOCK_JUSTIFY_LEFT)
        left_tbut.connect("clicked", lambda w : \
                          self.set_current_line_alignment('left'))
        toolbar.insert(left_tbut, -1)
        centre_tbut = gtk.ToolButton(gtk.STOCK_JUSTIFY_CENTER)
        centre_tbut.connect("clicked", lambda w : \
                          self.set_current_line_alignment('centre'))
        toolbar.insert(centre_tbut, -1)
        right_tbut = gtk.ToolButton(gtk.STOCK_JUSTIFY_RIGHT)
        right_tbut.connect("clicked", lambda w : \
                          self.set_current_line_alignment('right'))
        toolbar.insert(right_tbut, -1)

        self.pack_start(toolbar, False)

        self.layout_hbox = gtk.HBox()

        self.spronk_buffer = gtk.ListStore(int, bool, str)
        spronk_strip = gtk.TreeView(self.spronk_buffer)
        spronk_strip.connect("row-activated", self.do_spronk_strip_row_activated)
        spronk_strip.get_selection().connect("changed",
                                          self.do_spronk_strip_selection_changed)
        spronk_strip.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        spronk_column = gtk.TreeViewColumn('Spronk')
        spronk_strip.append_column(spronk_column)
        spronk_tvcr = GlosserSpronkCellRenderer()
        spronk_column.pack_start(spronk_tvcr, True)
        spronk_column.add_attribute(spronk_tvcr, 'special', 0)
        spronk_column.add_attribute(spronk_tvcr, 'active', 1)
        spronk_column.add_attribute(spronk_tvcr, 'text', 2)

        self.layout_hbox.pack_start(self.layout)
        self.layout_hbox.pack_start(spronk_strip, False)

        self.pack_start(self.layout_hbox)

        self.grab_focus()

        self.set_slide(0)
        self.presentation_instance.set_slide(0)

        self.show_all()

        self.action_panel = self.make_action_panel()
        if self.get_aenv() is not None :
            self.get_aenv().action_panel.to_action_panel(self.action_panel)

    old_sel = None
    old_old_sel = None
    def do_spronk_strip_selection_changed(self, selection) :
        if self.current_slide is None or self.current_widget is None :
            return

        self.old_old_sel = self.old_sel
        self.old_sel = selection.get_selected_rows()

    def do_spronk_strip_row_activated(self, spronk_strip, path, column) :
        if self.current_slide is None :
            return
        spronks = self.current_slide.spronks

        if self.old_old_sel is not None :
            selected_rows = self.old_old_sel[1]
        else :
            selected_rows = spronk_strip.get_selection().get_selected_rows()[1]

        if len(selected_rows) == 1 and path == (0,) :
            spronks.insert(0, [])
        elif len(selected_rows) == 1 and path == (len(spronks)+2,):
            spronks.insert(len(spronks), [])
        elif self.current_widget is not None :

            self.current_slide.remove_from_spronks(self.current_widget.show)
            self.current_slide.remove_from_spronks(self.current_widget.hide)

            self.current_widget.initial_hide = ((0,) not in selected_rows and \
                                                (1,) not in selected_rows )
            debug_print(self.current_widget.initial_hide)
            current_hide = self.current_widget.initial_hide
            
            for l in range(0, len(self.current_slide.spronks)) :
                if (((l+2,) in selected_rows) == current_hide) :
                    if current_hide :
                        self.current_slide.add_to_spronk(l,
                                                  self.current_widget.show,
                                                  self.current_widget.hide)
                        current_hide = False
                    else :
                        self.current_slide.add_to_spronk(l,
                                                  self.current_widget.hide,
                                                  self.current_widget.show)
                        current_hide = True
        self.update_spronk_strip()
        debug_print(path)
    def do_widget_size_allocate(self, widget, req) :
        line = widget.line
        line[2] = self.layout.translate_dist(req.height, rev=True)

        self.redraw()

    line_max = 5
    def insert_widget(self, ty, slide_num=None) :
        if slide_num is not None :
            slide = self.slides[slide_num]
        else :
            slide = self.current_slide

        if self.template is None or slide is None :
            return
        w = self.template['body']['width']
        h = self.template['body']['height']

        widget = widget_types[ty][2](slide,
                                     self.layout,
                                     self.presentation_instance.layout,
                                     env=self.get_aenv())
        for sw in widget.subwidgets :
            sw.modify_bg(gtk.STATE_NORMAL,
                         gtk.gdk.Color(self.template['params']['bgcolor']))
        self.complete_widgets_list.append(widget)
        self.absorb_properties(widget, as_self=False)
        design_widget = widget.subwidgets[GLOSSER_WIDGET_DESIGN]
        #design_widget.set_property('width-request', int(self.layout.translate_dist(w)))
        line_height = h/self.line_max

        if self.current_line < len(slide.lines) and \
           slide.lines[self.current_line][1].container :
            cntr = slide.lines[self.current_line][1]
            cntr.append(widget)
            self.change_current_widget(widget)
        else :
            slide.insert_line(self.current_line,
                                       ty,
                                       widget,
                                       line_height,
                                       'left')
            widget.line = slide.lines[self.current_line]
            self.change_current_widget(widget)
        widget.connect_after("redraw-request", lambda w :
                             self.redraw(thumb_only=True))
        self.set_slide()

        #self.do_widget_size_allocate(widget, design_widget.allocation)
        #self.do_widget_pos_update(self, None)
        design_widget.grab_focus()

        return widget

    def new_slide(self, num, variant) :
        num = int(num)
        self.slides.insert(num, GlosserSlide(num,
                                             variant=variant,
                                             reload_slide=self.set_slide,
                                             variant_lsto=self.variant_lsto,
                                             env=self.get_aenv()))
        self.absorb_properties(self.slides[num], as_self=False)
        self.slide_list.append((num+1, self.slides[num],))
        self.slides[num].reload()
        self.set_slide(num)
        self.presentation_instance.set_slide(num)
        return self.slides[num]

    def set_slide(self, n=None, change_current=True, xml=False) :

        self.presentation_instance.set_slide(n,
                                                 change_current=change_current)
        GlosserBasic.set_slide(self, n=n, change_current=change_current)

        if change_current :
            self.update_spronk_strip()
            self.change_current_line()

    def run_chooser(self, env = None) :
        chooser = gtk.FileChooserDialog(title="Export PDF",
                                        parent=self.get_toplevel(),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))

        chooser.set_default_response(gtk.RESPONSE_OK)

        resp = chooser.run()

        if resp == gtk.RESPONSE_OK :
            filename = chooser.get_filename()
            chooser.destroy()
        else :
            chooser.destroy()
            return
        
        self.render_to_pdf(filename)

    def render_to_pdf(self, filename) :
        pdfsurface = cairo.PDFSurface(filename,
                                   int(self.template['width']),
                                   int(self.template['height']))
        pdf_cr = cairo.Context(pdfsurface)

        for slide in self.slides :
            self.set_template_variant_xml(slide.variant)
            xml = copy.deepcopy(self.current_xml)
            self.presentation_instance.set_slide(n=self.slides.index(slide),
                           xml=xml,
                           change_current=False)
            slide.pre_spronk()

            for n in range(0, len(slide.spronks)+1) :
                pdf_cr.save()
                svg = StringIO.StringIO()
                xml.write(svg)
                handle = rsvg.Handle()
                handle.write(svg.getvalue())
                handle.close()

                handle.render_cairo(pdf_cr)
                pdf_cr.translate(self.template["body"]["x"],
                                   self.template["body"]["y"])
                slide.render_widgets_to_cairo(pdf_cr, ignore_spronks=False)
                pdf_cr.restore()
                pdf_cr.show_page()

                if n < len(slide.spronks) :
                    slide.execute_spronk(n)

    thumb_rat = .2
    def redraw(self, slide=None, xml=None, change_current=True, thumb_only=False) :

        if not thumb_only :
            self.presentation_instance.redraw(slide, xml, change_current=False)

        if slide is None :
            slide = self.current_slide
        if xml is None :
            self.set_template_variant_xml(slide.variant)
            xml = self.current_xml

        if xml is not None and \
                slide is not None :
            svg = StringIO.StringIO()
            xml.write(svg)
            handle = rsvg.Handle()
            handle.write(svg.getvalue())
            handle.close()

            thumb_rat = self.thumb_rat
            thumb = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                       int(self.template['width']*thumb_rat),
                                       int(self.template['height']*thumb_rat))
            thumb_cr = cairo.Context(thumb)
            thumb_cr.scale(thumb_rat, thumb_rat)
            handle.render_cairo(thumb_cr)
            thumb_cr.translate(self.template["body"]["x"],
                               self.template["body"]["y"])

            slide.render_widgets_to_cairo(thumb_cr)
            thumb.flush()
            slide.set_thumb(thumb)

            if change_current and not thumb_only :
                self.layout.width = self.template['width']
                self.layout.height = self.template['height']
                self.layout.handle = handle
                self.layout.line_num = self.current_line
                self.layout.lines = slide.lines
                self.layout.current_widget = self.current_widget
                if self.current_line < len(slide.lines) :
                    ty = slide.lines[self.current_line][0]
                    self.layout.line_indicators = \
                        [ widget_types[ty][3](self.get_style())]
                    if self.current_widget != slide.lines[self.current_line][1]:
                        ty = self.current_widget.ty
                        self.layout.line_indicators.append(widget_types[ty][3](self.get_style()))
                else :
                    self.layout.line_indicators = ( u'\u273c', )
                self.layout.body_x = self.template['body']['x']
                self.layout.body_y = self.template['body']['y']
                self.layout.body_w = self.template['body']['width']
                self.layout.body_h = self.template['body']['height']

            self.slide_list_trvw.queue_draw()
            self.layout.queue_draw()

    def _slide_to_action_panel(self) :
        if self.current_slide is None :
            return
        self.get_aenv().action_panel.to_action_panel(self.current_slide.action_panel)

    def _remake_slide_menu(self) :
        children = self.new_slide_menu.get_children()
        for r in range(1, len(children)) :
            self.new_slide_menu.remove(children[r])

        if self.template is None or 'variants' not in self.template :
            return

        for variant in self.template['variants'] :
            variant_settings = self.template['variants'][variant]
            new_variant_butt = gtk.MenuItem()
            new_variant_butt.add(self.template['variants'][variant]['sample'])
            new_variant_butt.set_tooltip_text(variant_settings['title'])
            new_variant_butt.connect('activate',
                                     variant_settings['new_slide'])
            self.new_slide_menu.append(new_variant_butt)

        self.new_slide_menu.show_all()

    def aes_add_a(self, aname_root, **parameters) :
        if aname_root == 'GlosserSlide' :
            return self.new_slide(parameters['num'], 'basic')
        elif aname_root in aname_root_to_ty :
            return self.insert_widget(aname_root_to_ty[aname_root],
                                      slide_num=int(parameters["on_slide"]))

        return aobject.AObject.aes_add_a(self, aname_root, **parameters)

    def get_method_window(self) :
        vbox = gtk.VBox()

        butt_hbox = gtk.HBox()
        new_slide_butt = gtk.ToggleButton()
        new_slide_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_NEW,
                                                    gtk.ICON_SIZE_BUTTON))

        new_slide_butt.set_tooltip_text("New slide")
        new_slide_menu = gtk.Menu()
        new_slide_menu.attach_to_widget(new_slide_butt, None)
        new_slide_butt.connect("button_press_event", lambda w, e :\
            new_slide_menu.popup(None, None, None, e.button, e.time) \
                if not w.get_active() else \
            new_slide_menu.popdown())

        new_slide_menu.set_title('New Slide')
        self.new_slide_menu = new_slide_menu
        new_slide_menu.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))

        new_slide_labl = gtk.Label()
        new_slide_labl.set_markup('<b>New...</b>')
        new_slide_meni = gtk.MenuItem()
        new_slide_meni.add(new_slide_labl)
        new_slide_menu.append(new_slide_meni)

        self._remake_slide_menu()

        settings_butt = gtk.Button()
        settings_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES,
                                                    gtk.ICON_SIZE_BUTTON))
        slide_settings_butt = gtk.Button()
        slide_settings_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_PAGE_SETUP,
                                                    gtk.ICON_SIZE_BUTTON))

        if self.get_aenv() is not None and \
                self.get_aenv().action_panel is not None :
            settings_butt.connect('clicked', lambda b : \
                self.get_aenv().action_panel.to_action_panel(self.action_panel))
            slide_settings_butt.connect('clicked', lambda b : \
                self._slide_to_action_panel())
        else :
            win = gtk.Window()
            win.add(action_panel)
            win.hide()
            settings_butt.connect('clicked', lambda b : win.show())
        butt_hbox.pack_start(settings_butt, False)
        butt_hbox.pack_start(slide_settings_butt, False)

        butt_hbox.pack_start(new_slide_butt, False)

        vbox.pack_start(butt_hbox, False)
        vbox.pack_start(gtk.Label('Slides'), False)
        slide_list_trvw = gtk.TreeView(self.slide_list)
        slide_list_cllr = GlosserSlideCellRenderer()
        slide_list_num_cllr = gtk.CellRendererText()
        slide_list_num_tvcl = gtk.TreeViewColumn('#', slide_list_num_cllr)
        slide_list_num_tvcl.add_attribute(slide_list_num_cllr, 'text', 0)
        slide_list_tvcl = gtk.TreeViewColumn('Slide', slide_list_cllr)
        slide_list_tvcl.add_attribute(slide_list_cllr, 'slide', 1)
        slide_list_trvw.append_column(slide_list_num_tvcl)
        slide_list_trvw.append_column(slide_list_tvcl)
        slide_list_scrw = gtk.ScrolledWindow()
        slide_list_scrw.add_with_viewport(slide_list_trvw)
        slide_list_scrw.set_size_request(-1, 300)
        self.slide_list_trvw = slide_list_trvw

        slide_list_trvw.connect('row-activated', self._set_slide_from_trvw)

        vbox.pack_start(slide_list_scrw)
        vbox.show_all()
        return vbox

    def _set_slide_from_trvw(self, tv, pa, col) :
        it = self.slide_list.get_iter(pa)
        self.set_slide(self.slide_list.get_value(it, 0)-1)

    def _make_new_slide_lambda(self, variant) :
        return lambda c: self.new_slide(len(self.slides), variant)

    def set_template(self, template_name=None, variant='basic') :
        if template_name is None :
            template_name = self.default_template

        self.template['name'] = template_name

        self.template['tar'] = tarfile.open(\
            get_share_location()+'templates/glosser/'+template_name+'.tgz', 'r')
        self.template['params_xml'] = \
            etree.parse(self.template['tar'].extractfile('parameters.xml'))

        self.template['params'] = {}
        params = ['bgcolor']
        root = self.template['params_xml'].getroot()

        param_root = root.find('params')
        for p in params :
            node = param_root.find(p)
            self.template['params'][p] = node.text.strip()

        self.variant_lsto.clear()

        variants_root = root.find('variants')
        self.template['variants'] = {}
        for variant_node in variants_root :
            self.template['variants'][variant_node.tag] = {
                'title' : variant_node.get('title'),
                'filename' : variant_node.text.strip(),
                'new_slide' : self._make_new_slide_lambda(variant_node.tag),
            }
            var_dict = self.template['variants'][variant_node.tag]
            fobj = var_dict['filename']
            fobj = self.template['tar'].extractfile(fobj)
            file_contents = fobj.read()

            var_dict['xml'] =\
                etree.ElementTree(etree.fromstring(file_contents))

            loader = gtk.gdk.PixbufLoader('svg')
            loader.write(file_contents)
            loader.set_size(50, 50)
            loader.close()

            var_dict['sample'] =\
                    gtk.image_new_from_pixbuf(loader.get_pixbuf())

            self.variant_lsto.append((variant_node.tag,
                                      var_dict['title']))

        if not self.presentation :
            self._remake_slide_menu()

        basic_xml = self.template['variants']['basic']['xml']

        w = basic_xml.getroot().get('width')
        self.template['width'] = _px_to_float(w)
        h = basic_xml.getroot().get('height')
        self.template['height'] = _px_to_float(h)

        self.set_template_variant_xml(variant, force=True)

        for w in self.complete_widgets_list :
            for sw in w.subwidgets :
                sw.modify_bg(gtk.STATE_NORMAL,
                             gtk.gdk.Color(self.template['params']['bgcolor']))

        # Redraw thumbs
        for n in range(0, len(self.slides)) :
            self.set_slide(n, change_current=False)

        # Update slide in view
        self.set_slide()

all_templates = {}
template_files = os.listdir(get_share_location()+'templates/glosser/')
template_lsto = gtk.ListStore(str, str, str)

for t in template_files :
    if t.endswith('.tgz') :
        template_name = t[:-4]
        all_templates[template_name] = {}

        tar = tarfile.open(\
            get_share_location()+'templates/glosser/'+template_name+'.tgz', 'r')
        params_xml = \
            etree.parse(tar.extractfile('parameters.xml'))

        root = params_xml.getroot()
        param_root = root.find('params')
        for node in param_root :
            all_templates[template_name][node.tag] = node.text.strip()

        template_lsto.append((template_name,
                              all_templates[template_name]['title'],
                              all_templates[template_name]['description'],))

aobject.aname_root_catalog['Glosser'] = Glosser
