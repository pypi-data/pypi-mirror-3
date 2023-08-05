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

import rsvg
import StringIO

def render_stock(style, stockid) :
    icon_set = style.lookup_icon_set(stockid)
    pixbuf = icon_set.render_icon(style,
                                  gtk.TEXT_DIR_NONE,
                                  gtk.STATE_NORMAL,
                                  gtk.ICON_SIZE_SMALL_TOOLBAR,
                                  None,
                                  None)
    return pixbuf

class GlosserWidget(aobject.AObject) :
    x = 0
    y = 0
    h = 0
    w = 0
    design_widget = None
    presentation_widget = None
    __gsignals__ = {
         "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () )}
    current_scaling = 1.
    attached = True
    suspend = False
    visible = True
    container = False

    initial_spronk_fns = None
    initial_hide = False

    def get_auto_aesthete_properties(self) :
        return {
            'x' : (float,), 'y' : (float,), 'h' : (float,), 'w' : (float,),
                }

    def aes_get_parameters(self) :
        return { 'on_slide' : self.slide.num }

    def initial_spronk(self) :
        debug_print(self.initial_hide)
        if self.initial_hide :
            self.hide()
        for fn in self.initial_spronk_fns :
            fn()

    def show(self) :
        self.presentation_widget.show()

    def hide(self) :
        self.presentation_widget.hide()

    def get_visible(self) :
        return self.visible

    def remove_from_layouts(self) :
        if not self.attached :
            return
        self.attached = False
        for i in (0,1) :
            self.layouts[i].remove(self.subwidgets[i])

    def restore_to_layouts(self) :
        if self.attached :
            return
        for i in (0,1) :
            to_pos = map(int, self.layouts[i].translate_body_pos(self.x,
                                                                 self.y))
            self.layouts[i].put(self.subwidgets[i], *to_pos)
        self.attached = True

    def __init__(self, slide, design_layout, presentation_layout, name_root='GlosserWidget', env=None) :
        aobject.AObject.__init__(self, name_root=name_root,
                                 env=env,
                                 view_object=False,
                                 elevate=False)
        self.slide = slide
        self.current_scaling = [1.,1.]
        self.layout_conn = [-1, -1]
        self.initial_spronk_fns = []
        #[presentation_layout.translate_dist(1.),
        #                        design_layout.translate_dist(1.)]
        #[presentation_layout.translate_pos(presentation_layout.body_x,presentation_layout.body_y,rev=True),
        # design_layout.translate_pos(design_layout.body_x,design_layout.body_y,rev=True)]
        self.layouts = [presentation_layout, design_layout]
        self.design_widget.connect_after("expose-event", lambda w, e :
                                  self.presentation_widget.queue_draw())
        self.subwidgets = [self.presentation_widget, self.design_widget]
        for i in (0, 1) :
            self.layout_conn[i] = self.layouts[i].connect_after("size-allocate",
                                    self.do_layout_size_allocate, i)
            self.layouts[i].put(self.subwidgets[i], 0, 0)
            self.subwidgets[i].show()
            self.move(0, 0, i)
        self.design_widget.connect("size-allocate", lambda w, a :
                                  self.update_from_design_widget())

    def move(self, x=None, y=None, subwidget=None) :
        if self.suspend :
            return
        self.suspend = True
        if x is None :
            x = self.x
        if y is None :
            y = self.y
        self.x = x
        self.y = y
        do_redraw = False
        for i in (subwidget,) if subwidget is not None else (1,0) :
            sw = self.subwidgets[i]
            self.layouts[i].handler_block(self.layout_conn[i])
            x, y = map(int, self.layouts[i].translate_body_pos(self.x,self.y))
            if self.attached and (x != sw.allocation.x or y != sw.allocation.y) :
                self.layouts[i].move(sw, x, y)
                do_redraw = True
            self.layouts[i].handler_unblock(self.layout_conn[i])
        self.suspend = False

        if do_redraw :
            self.emit("redraw-request")

    def update_from_design_widget(self) :
        if self.suspend :
            return
        al = self.design_widget.get_allocation()
        layout = self.layouts[GLOSSER_WIDGET_DESIGN]
        if al.x > 0 or al.y > 0 :
            x, y = layout.translate_body_pos(al.x, al.y, rev=True)
            self.move(x, y, subwidget=GLOSSER_WIDGET_PRESENTATION)
        if al.width > 0 or al.height > 0:
            w = layout.translate_dist(al.width, rev=True)
            h = layout.translate_dist(al.height, rev=True)
            self.resize(w, h, subwidget=GLOSSER_WIDGET_PRESENTATION)

    def move_resize(self, subwidget=None) :
        self.resize(self.w, self.h, subwidget=subwidget)
        self.move(self.x, self.y, subwidget=subwidget)

    def resize(self, w=None, h=None, subwidget=None) :
        if self.suspend :
            return
        self.suspend = True
        if w is None :
            w = self.w
        if h is None :
            h = self.h

        self.w = w
        self.h = h
        do_redraw = False

        for i in (subwidget,) if subwidget is not None else (1,0) :
            self.layouts[i].handler_block(self.layout_conn[i])
            sw = self.subwidgets[i]
            w = self.layouts[i].translate_dist(self.w)
            h = self.layouts[i].translate_dist(self.h)
            if int(w) != sw.allocation.width or int(h) != sw.allocation.height :
                sw.set_size_request(int(w), int(h))
                do_redraw = True
            self.layouts[i].handler_unblock(self.layout_conn[i])

        if do_redraw :
            self.emit("redraw-request")
        self.suspend = False

    old_origin = None
    old_rat = None
    def do_layout_size_allocate(self, layout, allocation, subwidget) :
        origin = layout.translate_body_pos(0, 0)
        rat = layout.translate_dist(1)
        if origin == self.old_origin and rat == self.old_rat :
            return
        self.old_origin = origin
        self.old_rat = rat

        if rat != self.current_scaling[subwidget] :
            self.rescale(subwidget, rat)
        else :
            self.move_resize(subwidget)

    def rescale_action(self, subwidget, rat) :
        pass

    def rescale(self, subwidget, rat) :
        if self.suspend :
            return
        self.current_scaling[subwidget] = rat
        self.move_resize(subwidget)
        self.rescale_action(subwidget, rat)

    def get_action_panel(self) :
        return None

    def presentation_draw(self, cr, scaling=None, ignore_spronks=True,
                          final=None) :
        if not ignore_spronks and not self.presentation_widget.get_visible() :
            return False

        if final is None :
            self.do_presentation_draw(cr, scaling=scaling)
        else :
            self.do_presentation_draw(cr, scaling=scaling, final=final)

        return True

class GlosserPresentationImage(gtk.DrawingArea) :
    scaling = 1
    draw_fn = None
    __gsignals__ = { "expose-event" : "override"}
    def __init__(self, draw_fn) :
        self.draw_fn = draw_fn
        gtk.DrawingArea.__init__(self)
    def rescale(self, rat) :
        self.scaling = rat
        self.queue_draw()
    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        cr.scale(self.scaling, self.scaling)
        self.draw_fn(cr, self.scaling, final=True)

GLOSSER_WIDGET_PRESENTATION = 0
GLOSSER_WIDGET_DESIGN = 1
