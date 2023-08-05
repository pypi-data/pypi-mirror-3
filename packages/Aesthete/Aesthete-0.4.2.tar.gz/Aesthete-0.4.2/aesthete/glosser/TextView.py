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

#class GlosserTextView_via_widget(gtk.TextView, GlosserWidget) :
#    initial_font_size = 25
#    def __init__(self, env=None) :
#        self.design_widget = self
#        self.presentation_widget =\
#           GlosserPresentationWidget(pres_text_view,
#                                     self.allocation.x,
#                                     self.allocation.y,
#                                    self.allocation.width,
#                                   self.allocation.height)
#        gtk.TextView.__init__(self)
#        GlosserWidget.__init__(self, name_root='GlosserTextView',
#                                 env=env)
#        self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
#        pres_text_view = gtk.TextView(self.get_buffer())
#        pres_text_view.modify_font(pango.FontDescription(\
#            "Linux Libertine %d"%int(self.initial_font_size)))
#        self.get_buffer().connect_after("changed", lambda w :\
#                                        self.emit("redraw-request"))
#    def rescale(self, rat) :
#        GlosserWidget.rescale(self, rat)
#        self.modify_font(pango.FontDescription(\
#            "Linux Libertine %d"%int(self.initial_font_size*rat)))
#    def presentation_draw(self, cr, scaling=None) :
#        return self.presentation_widget.draw(cr, scaling)

class GlosserTextView(GlosserWidget) :
    ty = 'textview'
    initial_font_size = 25

    def get_auto_aesthete_properties(self) :
        d = GlosserWidget.get_auto_aesthete_properties(self)
        d.update({'text' : (str,), 'font' : (str,)})
        return d

    def get_font(self) :
        return self.font_desc.to_string()

    def make_action_panel(self) :
        textview_table_maker = PreferencesTableMaker()
        textview_table_maker.append_row("Font",
            self.aes_method_font_button('font'))

        win = textview_table_maker.make_table()
        win.aes_title = "Glancer View"
        win.show_all()

        return win

    def change_font(self, val) :
        self.font_desc = pango.FontDescription(val)
        self.rescale_action(GLOSSER_WIDGET_DESIGN,
                            self.current_scaling[GLOSSER_WIDGET_DESIGN])
        self.presentation_widget.font_desc = self.font_desc
        self.presentation_widget.queue_draw()

    def __init__(self, slide, design_layout, presentation_layout, env=None) :
        self.font_desc = pango.FontDescription(\
            "Linux Libertine %d"%int(self.initial_font_size))
        self.design_widget = gtk.TextView()
        #self.design_widget.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.presentation_widget =\
           GlosserPresentationTextView(self.design_widget.get_buffer(),
                                       self.font_desc,
                                     self.design_widget.allocation.x,
                                     self.design_widget.allocation.y,
                                    self.design_widget.allocation.width,
                                   self.design_widget.allocation.height)
        GlosserWidget.__init__(self,
                               slide,
                               design_layout,
                               presentation_layout,
                               name_root='GlosserTextView',
                                 env=env)
        self.design_widget.get_buffer().connect_after("changed", lambda w :\
                                         self.emit("redraw-request"))

        self.action_panel = self.make_action_panel()
        self.design_widget.connect("focus-in-event", lambda w, e :
            self.get_aenv().action_panel.to_action_panel(self.action_panel))

    def get_text(self) :
        w = self.design_widget.get_buffer()
        return w.get_text(w.get_start_iter(), w.get_end_iter())
    def change_text(self, val) :
        self.design_widget.get_buffer().set_text(val)
    def rescale_action(self, subwidget, rat) :
        debug_print(self.initial_font_size*rat)
        if subwidget == GLOSSER_WIDGET_PRESENTATION :
            self.subwidgets[subwidget].rescale(rat)
        elif subwidget == GLOSSER_WIDGET_DESIGN :
            fd = pango.FontDescription(self.font_desc.to_string())
            fd.set_size(int(fd.get_size()*rat))
            self.subwidgets[subwidget].modify_font(fd)
    def do_presentation_draw(self, cr, scaling=None) :
        return self.presentation_widget.draw(cr, scaling)

class GlosserPresentationTextView(gtk.DrawingArea) :
    x = 0
    y = 0
    __gsignals__ = { "expose-event" : "override" }
    scaling = 1
    draw_fn = None
    def __init__(self, text_buffer, font_desc, x, y, w, h) :
        self.text_buffer = text_buffer
        self.font_desc = font_desc
        gtk.DrawingArea.__init__(self)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rescale(1)
    def rescale(self, rat=None) :
        if rat is None :
            rat = self.scaling
        self.scaling = rat
    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, self.scaling)
    def draw(self, cr, scaling) :
        cr.scale(scaling, scaling)
        cr.move_to(0, 0)
        pcr = pangocairo.CairoContext(cr)
        layout = pcr.create_layout()
        layout.set_font_description(self.font_desc)
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        s = self.text_buffer.get_start_iter()
        e = self.text_buffer.get_end_iter()
        layout.set_text(self.text_buffer.get_text(s, e))
        pcr.show_layout(layout)

