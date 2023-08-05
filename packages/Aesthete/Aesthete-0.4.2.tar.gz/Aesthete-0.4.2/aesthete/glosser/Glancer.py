import gtk
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

from aobject.aobject import *
import rsvg
import StringIO

from GlosserWidget import *

class GlosserGlancer(GlosserWidget) :
    ty = "glancer"
    glancer = None

    #PROPERTIES
    def get_auto_aesthete_properties(self):
        return {
            'glancer' : (str, (AOBJECT_CAN_NONE,)),
            'dpi' : (int,),
        }
    #BEGIN PROPERTIES FUNCTIONS
    def get_dpi(self) :
        return self.design_widget.dpi
    def change_dpi(self, val) :
        self.design_widget.dpi = val
        self.design_widget.check_canvas_size()
        self.emit('redraw-request')

    def change_glancer(self, val) :
        if val == '' :
            val = None

        if val != self.glancer :
            if self.glancer is not None :
                glancer = aobject.get_object_from_dictionary(self.glancer)
                glancer.plotter.canvas.disconnect(self.glancer_conn)
                glancer.plotter.canvas.disconnect(self.glancer_changed_conn)
            elif val is not None :
                glancer = aobject.get_object_from_dictionary(val)
                self.glancer_conn =\
                    glancer.plotter.canvas.connect("size-allocate", lambda w, e:
                                     self.design_widget.check_canvas_size())
                self.glancer_changed_conn =\
                    glancer.plotter.canvas.connect("event", lambda w, e:
                                     self.design_widget.set_recache_queue())

        self.glancer = val
        self.design_widget.glancer = val
        self.design_widget.check_canvas_size()
        self.design_widget.queue_draw()
        self.presentation_widget.queue_draw()
        self.emit('redraw-request')
    #END PROPERTIES FUNCTIONS

    def set_glancer(self, glancer) :
        self.change_property('glancer', glancer)
        self.rescale(1, self.current_scaling[1])

    def __init__(self, slide, design_layout, presentation_layout, env=None) :
        self.design_widget = GlosserPresentationGlancer()
        self.presentation_widget =\
            GlosserPresentationImage(self.do_presentation_draw)
        self.design_widget.connect("focus-in-event", lambda w, e :
            self.get_aenv().action_panel.to_action_panel(self.action_panel))

        GlosserWidget.__init__(self,
                               slide,
                               design_layout,
                               presentation_layout,
                               name_root='GlosserGlancer',
                                 env=env)
        self.action_panel = self.make_action_panel()

    def make_action_panel(self) :
        win = gtk.VBox()
        line_table_maker = PreferencesTableMaker()

        glancer_cmbo = gtk.ComboBox(\
            aobject.get_object_dictionary().get_liststore_by_am('Glancer') ) 
        glancer_cllr = gtk.CellRendererText(); glancer_cmbo.pack_start(glancer_cllr) 
        self._glancer_cmbo = glancer_cmbo
        glancer_cmbo.add_attribute(glancer_cllr, 'text', 1) 
        glancer_cmbo.connect("changed", lambda o : \
            self.set_glancer(glancer_cmbo.get_active_text()))

        line_table_maker.append_row("Plot", glancer_cmbo)

        line_table_maker.append_row("DPI", self.aes_method_entry_update('dpi'))

        win.aes_title = "Glancer View"
        win.pack_start(line_table_maker.make_table())
        win.show_all()
        return win

    def rescale_action(self, subwidget, rat) :
        if subwidget == GLOSSER_WIDGET_PRESENTATION :
            self.presentation_widget.rescale(rat)

    def do_presentation_draw(self, cr, scaling=None, final=False) :
        cr.scale(1/self.current_scaling[1], 1/self.current_scaling[1])
        self.design_widget.presentation_draw(cr, final=final)

    def get_action_panel(self) :
        return self.action_panel

class GlosserPresentationGlancer(gtk.DrawingArea) :
    __gsignals__ = { "expose-event" : "override", "key-release-event" : "override" ,
         "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () )}
    glancer = None
    default_blank_size = 100
    basic_canvas_scaling = 1
    dpi = 30
    canvas_width = None
    canvas_height = None

    def do_key_release_event(self, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        return False

    def __init__(self, env=None) :
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.set_property("can-focus", True)

    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        self.presentation_draw(cr)

    cache = None
    def check_canvas_size(self) :
        if self.glancer is not None :
            glancer = aobject.get_object_from_dictionary(self.glancer)
            if glancer is not None and glancer.plotter is not None :
                canvas = glancer.plotter.canvas
                w1, h1 = glancer.plotter.fig.get_size_inches()
                w1 *= self.dpi*self.basic_canvas_scaling
                h1 *= self.dpi*self.basic_canvas_scaling
                if self.canvas_width != w1 or self.canvas_height != h1 :
                    self.canvas_width = w1
                    self.canvas_height = h1
                    self.set_size_request(int(self.canvas_width),
                                          int(self.canvas_height))
                    self.cache = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                    int(w1/self.basic_canvas_scaling),
                                                    int(h1/self.basic_canvas_scaling))
                    self.recache_canvas()
                    return
        else :
            self.set_size_request(self.default_blank_size, self.default_blank_size)
            self.canvas_width = None
            self.canvas_height = None

    def set_recache_queue(self) :
        self.recache_queue=True
    recache_queue = False
    def recache_canvas(self, cr=None) :
        self.recache_queue = False
        if self.glancer is not None :
            glancer = aobject.get_object_from_dictionary(self.glancer)
            if glancer is not None and glancer.plotter is not None :
                canvas = glancer.plotter.canvas
                w1, h1 = glancer.plotter.fig.get_size_inches()
                w1 *= self.dpi
                h1 *= self.dpi
                #w1, h1 = glancer.plotter.canvas.get_width_height()
                if cr is None :
                    if self.cache is None :
                        self.cache = cairo.ImageSurface(cairo.FORMAT_ARGB32, w1, h1)
                    cr = cairo.Context(self.cache)
                cr.save()
                rat = canvas.figure.dpi/float(self.dpi)
                cr.scale(1/rat, 1/rat)
                renderer = RendererCairo (canvas.figure.dpi)
                renderer.set_width_height (*canvas.get_width_height())
                renderer.gc.ctx = cr
                canvas.figure.draw (renderer)
                cr.restore()
                return
        self.cache = None

    def presentation_draw(self, cr, scaling=None, final=False) :
        if self.recache_queue == True :
            self.recache_canvas()
            self.emit("redraw-request")

        if self.glancer is not None :
            glancer = aobject.get_object_from_dictionary(self.glancer)
            if glancer is not None and glancer.plotter is not None :
                canvas = glancer.plotter.canvas
                cr.scale(self.basic_canvas_scaling, self.basic_canvas_scaling)
                if final :
                    self.recache_canvas(cr)
                else :
                    if self.cache is None :
                        self.recache_canvas()
                    cr.set_source_surface(self.cache, 0, 0)
                    cr.paint()
        else :
            cr.save()
            cr.rectangle(self.allocation.x,
                         self.allocation.y,
                         self.allocation.width,
                         self.allocation.height)
            cr.set_source_rgba(0.4, 0.4, 0.4, 1.0)
            cr.fill()
            cr.restore()
