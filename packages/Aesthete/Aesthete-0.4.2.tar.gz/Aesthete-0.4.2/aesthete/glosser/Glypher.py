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


class GlosserGlyphEntry(GlosserWidget) :
    ty = "glyphentry"
    initial_font_size = 45

    def get_auto_aesthete_properties(self):
        return {
            'font_size' : (float,),
        }
    def get_font_size(self) :
        return self.design_widget.get_font_size()
    def change_font_size(self, val) :
        self.design_widget.set_font_size(val)

    def make_action_panel(self) :
        glyph_table_maker = PreferencesTableMaker()
        glyph_table_maker.append_row("Font size",
                                     self.aes_method_entry_update('font_size'))

        win = glyph_table_maker.make_table()
        win.aes_title = "Glancer View"
        win.show_all()

        return win

    def __init__(self, slide, design_layout, presentation_layout, env=None) :
        self.design_widget = glypher.Widget.GlyphEntry(resize_to_main_phrase=True,
                                           margins=[10,10,10,10])
        self.presentation_widget =\
           GlosserPresentationImage(self.presentation_draw)

        GlosserWidget.__init__(self,
                               slide,
                               design_layout,
                               presentation_layout,
                               name_root="GlosserGlyphEntry",
                               env=env)

        self.action_panel = self.make_action_panel()
        self.design_widget.connect("focus-in-event", lambda w, e :
            self.get_aenv().action_panel.to_action_panel(self.action_panel))

    def rescale_action(self, subwidget, rat) :
        if subwidget == GLOSSER_WIDGET_DESIGN :
            self.design_widget.set_font_size(int(self.initial_font_size)*rat)
        elif subwidget == GLOSSER_WIDGET_PRESENTATION :
            self.presentation_widget.rescale(rat)
    def do_presentation_draw(self, cr, scaling=None, final=False) :
        cr.scale(1/self.current_scaling[1], 1/self.current_scaling[1])
        self.design_widget.draw(cr,
                                self.w,
                                self.h)
