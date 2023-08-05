import os, math, sys, getopt, string
import pango
import random
from gtk import gdk
from ..tablemaker import PreferencesTableMaker
import threading
import cairo, gtk, gobject
import matplotlib
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_cairo import RendererCairo
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as mpl_Canvas
from matplotlib.backends.backend_gtkcairo import NavigationToolbar2Cairo as mpl_Navbar
from matplotlib import cm
import pylab
from PIL import Image
from ..aobject import *
from ..glypher.Widget import GlyphEntry
from ..glypher.Parser import parse_phrasegroup

class GlancerLine(AObject) :
    line = None
    plot = None
    source = None

    def get_useful_vars(self) :
        return {
                 'line' : 'mpl Line',
               }

    def replot(self) :
        self._line_from_source()

    def _line_from_source(self) :
        if self.source is None :
            return

        x_range = self.axes.get_xlim() if self.source.needs_x_range else None
        values = self.source.source_get_values(multi_array=True, x_range=x_range)[0]
        points = values['values']
        series = values['x']
        dim = self.source.source_get_max_dim()
        trans = [series, points]

        if self.line is None :
            self.line = self.axes.plot(trans[0], trans[1])[0]
        else :
            self.line.set_xdata(trans[0])
            self.line.set_ydata(trans[1])
        self.axes.figure.canvas.draw()

    def __init__(self, plot, line = None, source = None, env=None,
                 read_series=False, axes = None, aname="GlancerLine"):

        self.read_series = read_series
        self.axes = axes

        if line is None and source is not None :
            self.source = source
            self._line_from_source()
        elif source is None and line is not None :
            self.line = line
        else :
            raise RuntimeError('Must specify one of line and source for Line')

        self.plot = plot
        self.source = source
        AObject.__init__(self, aname, env, elevate = False)

        self.set_aesthete_xml(self.source.get_aesthete_xml())
        self.change_property("label", "$$"+self.source.get_aname_nice()+"$$")

    def __del__(self) :
        AObject.__del__(self)

    def redraw(self) :
        self.plot.do_legend()
        self.line.figure.canvas.draw()
    
    def self_remove(self, parent_remove = True) :
        if (parent_remove) : self.plot.lines.remove(self); self.plot.check_legend()
        if self.line in self.line.axes.lines :
            self.line.axes.lines.remove(self.line)

        self.aes_remove()
        if (parent_remove) : self.redraw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { 'label' : [self.change_label, self.get_label, True],
             'marker' : [self.change_marker, self.get_marker, True],
             'linewidth' : [self.change_linewidth, self.get_linewidth, True],
             'colour' : [self.change_colour, self.get_colour, True],
             'source' : [None, self.get_source, True],
             'markersize' : [self.change_markersize, self.get_markersize, True],
             'markevery' : [self.change_markevery, self.get_markevery, True],
             'markerfacecolor' : [self.change_markerfacecolor, self.get_markerfacecolor, True],
             'alpha' : [self.change_alpha, self.get_alpha, True],
             'zorder' : [self.change_zorder, self.get_zorder, True],
             'visible' : [self.change_visible, self.get_visible, True],
             'aa' : [self.change_aa, self.get_aa, True],
             'linestyle' : [self.change_linestyle, self.get_linestyle, True],
             'solid-capstyle' : [self.change_solid_capstyle, self.get_solid_capstyle, True],
             'solid-joinstyle' : [self.change_solid_joinstyle, self.get_solid_joinstyle, True],
             'dash-capstyle' : [self.change_dash_capstyle, self.get_dash_capstyle, True],
             'dash-joinstyle' : [self.change_dash_joinstyle,
                                 self.get_dash_joinstyle, True] }
    #BEGIN PROPERTIES FUNCTIONS
    def get_label(self, val=None): return self.line.get_label() if val==None else val
    def get_marker(self, val=None): return self.line.get_marker() if val==None else val
    def get_linewidth(self, val=None): return self.line.get_linewidth() if val==None else float(val)
    def get_colour(self, val=None):
        return mpl_to_tuple(self.line.get_color()) \
        if val==None else string_to_float_tup(val)
    def get_source(self, val=None) : return self.source if val==None else val
    def get_markersize(self, val=None): return self.line.get_markersize() if val==None else float(val)
    def get_markevery(self, val=None): return self.line.get_markevery() \
            if val==None else (1 if val is None else int(val))
    def get_markerfacecolor(self, val=None):
        return mpl_to_tuple(self.line.get_markerfacecolor()) \
        if val==None else string_to_float_tup(val)
    def get_alpha(self, val=None): return self.line.get_alpha() if val==None else float(val)
    def get_zorder(self, val=None): return self.line.get_zorder() if val==None else float(val)
    def get_visible(self, val=None): return self.line.get_visible() if val==None else (val=='True')
    def get_aa(self, val=None): return self.line.get_aa() if val==None else (val=='True')
    def get_linestyle(self, val=None): return self.line.get_linestyle() if val==None else val
    def get_solid_capstyle(self, val=None): return self.line.get_solid_capstyle() if val==None else val
    def get_solid_joinstyle(self, val=None): return self.line.get_solid_joinstyle() if val==None else val
    def get_dash_capstyle(self, val=None): return self.line.get_dash_capstyle() if val==None else val
    def get_dash_joinstyle(self, val=None): return self.line.get_dash_joinstyle() if val==None else val

    def change_label(self, val) : self.line.set_label(val); self.set_aname_nice(val); self.plot.do_legend(); self.redraw()
    def change_colour(self, val) : self.line.set_color(val); self.redraw()
    def change_marker(self, val) : self.line.set_marker(val); self.redraw()
    def change_linewidth(self, val) : self.line.set_linewidth(val); self.redraw()
    def change_markersize(self, val) : self.line.set_markersize(val); self.redraw()
    def change_markevery(self, val) : self.line.set_markevery(val); self.redraw()
    def change_markerfacecolor(self, val) : self.line.set_markerfacecolor(val); self.redraw()
    def change_alpha(self, val) : self.line.set_alpha(val); self.redraw()
    def change_zorder(self, val) : self.line.set_zorder(val); self.redraw()
    def change_visible(self, val) : self.line.set_visible(val); self.redraw()
    def change_aa(self, val) : self.line.set_aa(val); self.redraw()
    def change_linestyle(self, val) : self.line.set_linestyle(val); self.redraw()
    def change_solid_capstyle(self, val) : self.line.set_solid_capstyle(val); self.redraw()
    def change_solid_joinstyle(self, val) : self.line.set_solid_joinstyle(val); self.redraw()
    def change_dash_capstyle(self, val) : self.line.set_dash_capstyle(val); self.redraw()
    def change_dash_joinstyle(self, val) : self.line.set_dash_joinstyle(val); self.redraw()

    #END PROPERTIES FUNCTIONS
    def set_label_for_button(self, button, obj=None) :
        if obj is not None :
            rep = obj.get_arepr()
            if isinstance(rep, ET.ElementTree) :
                button.remove(button.get_child())
                ge = GlyphEntry()
                #pg = parse_phrasegroup(ge.main_phrase, rep, top=True)
                #ge.main_phrase.empty()
                #ge.main_phrase.adopt(pg)
                ge.set_xml(rep)
                ge.show()
                button.add(ge)
                return
            text = obj.get_aname_nice()

        if obj is not None :
            button.set_label(text)
        #button.get_child().props.ellipsize = pango.ELLIPSIZE_END
        button.get_child().modify_fg(gtk.STATE_NORMAL,
                         gtk.gdk.Color(*self.get_colour()))
        if obj is not None :
            button.set_tooltip_text(text)
    def get_method_window(self) :
        #frame = gtk.Frame(self.source)
        hbox = gtk.HBox()
        config_butt = gtk.Button(self.get_aname_nice()+'...')
        config_butt.set_relief(gtk.RELIEF_NONE)
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,o))
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,o))
        hbox.pack_start(config_butt)
        remove_butt = gtk.Button(); remove_butt.add(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_SMALL_TOOLBAR))
        remove_butt.connect("clicked", lambda o : self.self_remove())
        hbox.pack_start(remove_butt, False)

        win = gtk.VBox()
        nb = gtk.Notebook()

        line_table_maker = PreferencesTableMaker()
        line_table_maker.append_row("Label",
                                    self.aes_method_entry_update("label", "Set"))
        line_table_maker.append_row("Colour",
                self.aes_method_colour_button("colour", "Set line colour"))
        line_table_maker.append_row("Thickness",
                self.aes_method_entry("linewidth",
                     wait_until_parsable_float=True))
        line_table_maker.append_row("Alpha",
                self.aes_method_entry_update("alpha", "Set"))
        line_table_maker.append_row("Z order",
                self.aes_method_entry_update("zorder", "Set"))
        line_table_maker.append_row("Visible",
                self.aes_method_toggle_button("visible", onoff=('On','Off')))
        line_table_maker.append_row("Antialiased",
                self.aes_method_toggle_button("aa", onoff=('On','Off')))
        nb.append_page(line_table_maker.make_table(), gtk.Label("General"))

        marker_table_maker = PreferencesTableMaker()
        marker_table_maker.append_row("Marker",
                self.aes_method_entry_update("marker", "Set"))
        marker_table_maker.append_row("Size",
                self.aes_method_entry_update("markersize", "Set"))
        marker_table_maker.append_row("Freq",
                self.aes_method_entry_update("markevery", "Set"))
        marker_table_maker.append_row("Colour",
                self.aes_method_colour_button("markerfacecolor", "Set marker colour"))
        nb.append_page(marker_table_maker.make_table(), gtk.Label("Marker"))

        style_table_maker = PreferencesTableMaker()
        style_table_maker.append_row("Line Style",
                self.aes_method_entry_update("linestyle", "Set"))
        style_table_maker.append_row("Solid Cap",
                self.aes_method_entry_update("solid-capstyle", "Set"))
        style_table_maker.append_row("Solid Join",
                self.aes_method_entry_update("solid-joinstyle", "Set"))
        style_table_maker.append_row("Dash Cap",
                self.aes_method_entry_update("dash-capstyle", "Set"))
        style_table_maker.append_row("Dash Join",
                self.aes_method_entry_update("dash-joinstyle", "Set"))
        nb.append_page(style_table_maker.make_table(), gtk.Label("Style"))

        win.pack_start(nb, False)

        if self.source is not None:
            win.pack_start(gtk.HSeparator(), False)
            update_hbox = gtk.HBox()
            update_labl = gtk.Label()
            update_labl.set_markup("from source <b>"+\
                self.source.get_aname_nice()+\
                "</b>")
            update_labl.set_alignment(1.0, 0.5)
            update_hbox.pack_start(update_labl)
            update_butt = gtk.Button()
            update_butt.add(gtk.image_new_from_stock(gtk.STOCK_REFRESH,
                                                     gtk.ICON_SIZE_BUTTON))
            update_butt.connect("clicked", lambda e : self.replot())
            update_hbox.pack_start(update_butt, False)
            win.pack_start(update_hbox, False)

        self.connect("aesthete-property-change",
                     lambda o, p, v, a : self.set_label_for_button(config_butt))

        win.show_all()

        if self.env and self.env.action_panel :
            win.hide()
            win.aes_title = "Configure line"
            config_butt.connect("clicked", lambda o : self.env.action_panel.to_action_panel(win))
        else :
            config_win = gtk.Window()
            config_win.set_title("Configure line")
            remove_butt = gtk.Button("Close"); remove_butt.connect("clicked", lambda o : config_win.hide())
            win.pack_start(remove_butt)
            config_win.add(win)
            config_win.hide()
            config_butt.connect("clicked", lambda o : config_win.show())
        hbox.show_all()
        #frame.add(win)

        return hbox

class GlancerLine3D(GlancerLine) :
    def __init__(self, plot, line = None, source = None, env=None,
                 read_series=False, axes = None, aname="GlancerLine3D"):
        GlancerLine.__init__(self, plot, line=line, source=source, env=env,
                 read_series=read_series, axes=axes, aname=aname)

    def _line_from_source(self) :
        if self.source is None :
            return

        x_range = self.axes.get_xlim() if self.source.needs_x_range else None
        values = self.source.source_get_values(multi_array=True, x_range=x_range)[0]

        points = values['values']
        series = values['x']
        dim = self.source.source_get_max_dim()
        if dim <3 :
            points = (points,)
        trans = [series, points]

        trans = (trans[0], trans[1][0], 0 if dim < 3 else trans[1][1])
        self.line = self.axes.plot(*trans)[0]
        # Can't replot as no set_zdata :(
        self.axes.figure.canvas.draw()

class GlancerSurface(AObject) :
    line = None
    plot = None
    source = None

    def get_useful_vars(self) :
        return {
                 'line' : 'mpl Poly3DCollection',
               }

    def replot(self) :
        self._line_from_source()

    def __init__(self, plot, line = None, source = None, env=None,
                 read_series=False, axes = None, aname="GlancerSurface"):

        self.read_series = read_series
        self.axes = axes

        if line is None and source is not None :
            self.source = source
            self._line_from_source()
        elif source is None and line is not None :
            self.line = line
        else :
            raise RuntimeError('Must specify one of line and source for Surface')

        self.plot = plot
        self.source = source
        AObject.__init__(self, aname, env, elevate = False)

    def __del__(self) :
        AObject.__del__(self)

    def redraw(self) :
        self.plot.do_legend()
        self.line.figure.canvas.draw()
    
    def self_remove(self, parent_remove = True) :
        if (parent_remove) : self.plot.lines.remove(self); self.plot.check_legend()
        if self.line in self.line.axes.lines :
            self.line.axes.lines.remove(self.line)

        self.aes_remove()
        if (parent_remove) : self.redraw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { 'label' : [self.change_label, self.get_label, True],
             'linewidth' : [self.change_linewidth, self.get_linewidth, True],
             'source' : [None, self.get_source, True],
             'alpha' : [self.change_alpha, self.get_alpha, True],
             'zorder' : [self.change_zorder, self.get_zorder, True],
             'visible' : [self.change_visible, self.get_visible, True],
             'linestyle' : [self.change_linestyle, self.get_linestyle, True]}
    #BEGIN PROPERTIES FUNCTIONS
    def get_label(self, val=None): return self.line.get_label() if val==None else val
    def get_marker(self, val=None): return self.line.get_marker() if val==None else val
    def get_linewidth(self, val=None): return self.line.get_linewidth() if val==None else float(val)
    def get_source(self, val=None) : return self.source if val==None else val
    def get_alpha(self, val=None): return self.line.get_alpha() if val==None else float(val)
    def get_zorder(self, val=None): return self.line.get_zorder() if val==None else float(val)
    def get_visible(self, val=None): return self.line.get_visible() if val==None else (val=='True')
    def get_linestyle(self, val=None): return self.line.get_linestyle() if val==None else val

    def change_label(self, val) : self.line.set_label(val); self.set_aname_nice(val); self.plot.do_legend(); self.redraw()
    def change_linewidth(self, val) : self.line.set_linewidth(val); self.redraw()
    def change_alpha(self, val) : self.line.set_alpha(val); self.redraw()
    def change_zorder(self, val) : self.line.set_zorder(val); self.redraw()
    def change_visible(self, val) : self.line.set_visible(val); self.redraw()
    def change_linestyle(self, val) : self.line.set_linestyle(val); self.redraw()

    #END PROPERTIES FUNCTIONS
    def set_label_for_button(self, button, obj=None) :
        if obj is not None :
            rep = obj.get_arepr()
            if isinstance(rep, ET.ElementTree) :
                 debug_print('1')
                 return
            text = obj.get_aname_nice()

        if obj is not None :
            button.set_label(text)
        button.get_child().props.ellipsize = pango.ELLIPSIZE_END
        button.get_child().modify_fg(gtk.STATE_NORMAL,
                         gtk.gdk.Color(*self.get_colour()))
        if obj is not None :
            button.set_tooltip_text(text)
    def get_method_window(self) :
        #frame = gtk.Frame(self.source)
        hbox = gtk.HBox()
        config_butt = gtk.Button(self.get_aname_nice()+'...')
        config_butt.set_relief(gtk.RELIEF_NONE)
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,o))
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,o))
        hbox.pack_start(config_butt)
        remove_butt = gtk.Button(); remove_butt.add(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_SMALL_TOOLBAR))
        remove_butt.connect("clicked", lambda o : self.self_remove())
        hbox.pack_start(remove_butt, False)

        win = gtk.VBox()
        nb = gtk.Notebook()

        line_table_maker = PreferencesTableMaker()
        line_table_maker.append_row("Label",
                                    self.aes_method_entry_update("label", "Set"))
        line_table_maker.append_row("Thickness",
                self.aes_method_entry("linewidth",
                     wait_until_parsable_float=True))
        line_table_maker.append_row("Alpha",
                self.aes_method_entry_update("alpha", "Set"))
        line_table_maker.append_row("Z order",
                self.aes_method_entry_update("zorder", "Set"))
        line_table_maker.append_row("Visible",
                self.aes_method_toggle_button("visible", onoff=('On','Off')))
        nb.append_page(line_table_maker.make_table(), gtk.Label("General"))

        style_table_maker = PreferencesTableMaker()
        style_table_maker.append_row("Line Style",
                self.aes_method_entry_update("linestyle", "Set"))
        nb.append_page(style_table_maker.make_table(), gtk.Label("Style"))

        win.pack_start(nb, False)

        if self.source is not None:
            win.pack_start(gtk.HSeparator(), False)
            update_hbox = gtk.HBox()
            update_labl = gtk.Label()
            update_labl.set_markup("from source <b>"+\
                self.source.get_aname_nice()+\
                "</b>")
            update_labl.set_alignment(1.0, 0.5)
            update_hbox.pack_start(update_labl)
            update_butt = gtk.Button()
            update_butt.add(gtk.image_new_from_stock(gtk.STOCK_REFRESH,
                                                     gtk.ICON_SIZE_BUTTON))
            update_butt.connect("clicked", lambda e : self.replot())
            update_hbox.pack_start(update_butt, False)
            win.pack_start(update_hbox, False)

        self.connect("aesthete-property-change",
                     lambda o, p, v, a : self.set_label_for_button(config_butt))

        win.show_all()

        if self.env and self.env.action_panel :
            win.hide()
            win.aes_title = "Configure line"
            config_butt.connect("clicked", lambda o : self.env.action_panel.to_action_panel(win))
        else :
            config_win = gtk.Window()
            config_win.set_title("Configure line")
            remove_butt = gtk.Button("Close"); remove_butt.connect("clicked", lambda o : config_win.hide())
            win.pack_start(remove_butt)
            config_win.add(win)
            config_win.hide()
            config_butt.connect("clicked", lambda o : config_win.show())
        hbox.show_all()
        #frame.add(win)

        return hbox
    def _line_from_source(self) :
        if self.source is None :
            return

        x_range = self.axes.get_xlim() if self.source.needs_x_range else None
        y_range = self.axes.get_ylim()
        values = self.source.source_get_values(multi_array=True,
                                               x_range=x_range,
                                               y_range=y_range)[0]

        points = values['values']
        xs = values['x']
        ys = values['y']
        self.line = self.axes.plot_surface(xs, ys, points, rstride=1, cstride=1,
                                          cmap=cm.jet)
        # Can't replot as no set_zdata :(
        self.axes.figure.canvas.draw()
