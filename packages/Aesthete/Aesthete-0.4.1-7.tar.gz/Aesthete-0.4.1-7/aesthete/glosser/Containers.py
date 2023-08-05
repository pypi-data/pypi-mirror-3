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

from GlosserWidget import *

class GlosserVBox(GlosserWidget) :
    ty = "vbox"
    container = True
    contained = None

    def get_contained(self) :
        return self.contained
        
    def remove_from_layouts(self) :
        GlosserWidget.remove_from_layouts(self)
        for widget in self.contained :
            widget.remove_from_layouts()

    def restore_to_layouts(self) :
        GlosserWidget.restore_to_layouts(self)
        for widget in self.contained :
            widget.restore_to_layouts()

    def __init__(self, slide, design_layout, presentation_layout,
                 name_root='GlosserWidget', env=None) :
        if self.design_widget is None :
            self.design_widget = gtk.DrawingArea()
        if self.presentation_widget is None :
            self.presentation_widget = gtk.DrawingArea()
        self.contained = []
        GlosserWidget.__init__(self,
                               slide,
                               design_layout,
                               presentation_layout,
                                 name_root='GlosserWidget',
                                 env=env)

    def get_action_panel(self) :
        return None

    def do_presentation_draw(self, cr, scaling=None) :
        pass

    def append(self, glosser_widget) :
        self.contained.append(glosser_widget)
        glosser_widget.design_widget.connect_after("size-allocate", self.do_widget_pos_update)

    basic_offset_x = 0
    def do_widget_pos_update(self, widget, req) :
        y = 0
        layout = self.layouts[0]

        w = 0
        for widget in self.contained :
            offset = 0
            #if l[3] == 'left' :
            #    offset = 0
            #elif l[3] == 'centre' :
            #    offset = layout.body_w-widget.w
            #    offset *= 0.5
            #elif l[3] == 'right' :
            #    offset = layout.body_w-widget.w

            new_x = int(self.x+offset+self.basic_offset_x)
            new_y = self.y+y

            w = max(w, widget.w)

            if abs(new_x-widget.x) > 5 or abs(new_y-widget.y) > 5:
                widget.move(new_x, new_y)

            y += widget.h
        h = y
        self.resize(w, h)

    def presentation_draw(self, cr, scaling=None, ignore_spronks=True,
                          final=None) :
        ret = GlosserWidget.presentation_draw(self, cr, scaling=scaling,
                                              ignore_spronks=ignore_spronks,
                                              final=final)
        if not ret :
            return False

        for widget in self.subwidgets :
            if hasattr(widget, 'draw') :
                cr.save()
                widget.draw(cr, scaling)
                cr.restore()
        for widget in self.contained :
            cr.save()
            cr.translate(widget.x-self.x, widget.y-self.y)
            widget.presentation_draw(cr, scaling=scaling,
                                     ignore_spronks=ignore_spronks, final=final)
            cr.restore()

        return True

class GlosserBullet_(gtk.DrawingArea) :
    scaling = 1
    draw_fn = None
    get_contained = None

    __gsignals__ = { "expose-event" : "override"}
    def __init__(self, container, presentation=False) :
        gtk.DrawingArea.__init__(self)
        self.get_contained = container.get_contained
        self.container = container
        self.presentation = presentation
    def rescale(self, rat) :
        self.scaling = rat
        self.queue_draw()
    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self.draw(cr)
    def draw(self, cr, scaling=None) :
        if scaling is None :
            scaling = self.scaling
        cr.scale(scaling, scaling)
        cr.set_source_rgba(.5, .5, .5, 1.)

        for widget in self.get_contained() :
            if self.presentation and not widget.presentation_widget.get_visible() :
                continue
            cr.save()
            middle = int(widget.y-self.container.y+.5*widget.h)
            cr.arc(5, middle, 5, 0, 2*3.14159)
            cr.close_path()
            cr.fill()
            cr.restore()

class GlosserBullets(GlosserVBox) :
    ty = "bullets"
    def __init__(self, slide, design_layout, presentation_layout, env=None) :
        self.design_widget = GlosserBullet_(self, presentation=False)
        self.presentation_widget = GlosserBullet_(self, presentation=True)
        self.basic_offset_x = 20
        GlosserVBox.__init__(self, slide, design_layout, presentation_layout, env=env,
                             name_root='GlosserBullets')
    def rescale_action(self, subwidget, rat) :
        self.subwidgets[subwidget].rescale(rat)
    def append(self, glosser_widget) :
        GlosserVBox.append(self, glosser_widget)
        glosser_widget.presentation_widget.connect("show",
                                                   lambda w :
                                                   self.presentation_widget.queue_draw())
        glosser_widget.presentation_widget.connect("hide",
                                                   lambda w :
                                                   self.presentation_widget.queue_draw())
