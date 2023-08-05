import os, math, sys, getopt, string
import pango
import random
from gtk import gdk
from ..tablemaker import PreferencesTableMaker
from ..utils import debug_print
import threading
import cairo, gtk, gobject
import matplotlib
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_cairo import RendererCairo
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as mpl_Canvas
from matplotlib.backends.backend_gtkcairo import NavigationToolbar2Cairo as mpl_Navbar
import pylab
from ..aobject import string_to_float_tup
from PIL import Image
from Line import GlancerLine

class GlancerScatter(GlancerLine) :
    def __init__(self, plot, line = None, source = None, env=None,
                 read_series=False, axes = None, aname="GlancerScatter"):
        GlancerLine.__init__(self, plot, line=line, source=source, env=env,
                 read_series=read_series, axes=axes, aname=aname)

    def _line_from_source(self) :
        if self.source is None :
            return

        x_range = self.axes.get_xlim() if self.source.needs_x_range else None
        values = self.source.source_get_values(multi_array=True, x_range=x_range)[0]
        points = values['values']
        series = range(0, len(points[0]))
        dim = self.source.source_get_max_dim()
        if dim > 1 :
            trans = zip(*points)
            if not self.read_series :
                trans[0] = series
        else :
            trans = [series, points]

        if self.line is None :
            if self.source.source_type() == 'line' :
                self.line = self.axes.plot(trans[0], trans[1])[0]
            else :
                self.line = self.axes.scatter(trans[0], trans[1])
        else :
            self.line.set_xdata(trans[0])
            self.line.set_ydata(trans[1])
        self.axes.figure.canvas.draw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { 'label' : [self.change_label, self.get_label, True],
             'colour' : [self.change_colour, self.get_colour, True],
             'source' : [None, self.get_source, True] }
    def get_colour(self, val=None):
        return tuple(self.line.get_facecolor().tolist()[0][0:2]) \
        if val==None else string_to_float_tup(val)
    def change_colour(self, val) : self.line.set_facecolor(val); self.redraw()

    def get_method_window(self) :
        #frame = gtk.Frame(self.source)
        hbox = gtk.HBox()
        config_butt = gtk.Button(self.get_aname_nice()+'...')
        config_butt.set_relief(gtk.RELIEF_NONE)
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,v))
        self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,v))
        hbox.pack_start(config_butt)
        remove_butt = gtk.Button(); remove_butt.add(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_SMALL_TOOLBAR))
        remove_butt.connect("clicked", lambda o : self.self_remove())
        hbox.pack_start(remove_butt, False)

        win = gtk.VBox()
        label_ameu = self.aes_method_entry_update("label", "Label")
        win.pack_start(label_ameu, False)

        colour_hbox = gtk.HBox()
        colour_label = gtk.Label("Set colour")
        debug_print(self.aesthete_properties[('colour', self.get_aname())][1]())
        colour_amcb = self.aes_method_colour_button("colour", "Face Colour")
        colour_hbox.pack_start(colour_label); colour_hbox.pack_start(colour_amcb)
        win.pack_start(colour_hbox, False)

        if self.source is not None:
            update_butt = gtk.Button("Replot")
            update_butt.connect("clicked", lambda e : self.replot())
            win.pack_start(update_butt, False)

        self.connect("aesthete-property-change",
                     lambda o, p, v, a : self.set_label_for_button(config_butt))

        win.show_all()

        if self.env and self.env.action_panel :
            win.hide()
            win.aes_title = "Configure scatter plot"
            config_butt.connect("clicked", lambda o : self.env.action_panel.to_action_panel(win))
        else :
            config_win = gtk.Window()
            config_win.set_title("Configure scatter plot")
            remove_butt = gtk.Button("Close"); remove_butt.connect("clicked", lambda o : config_win.hide())
            win.pack_start(remove_butt)
            config_win.add(win)
            config_win.hide()
            config_butt.connect("clicked", lambda o : config_win.show())
        hbox.show_all()
        #frame.add(win)

        return hbox
class GlancerScatter3D(GlancerScatter) :
    def __init__(self, plot, line = None, source = None, env=None,
                 read_series=False, axes = None, aname="GlancerScatter3D"):
        GlancerScatter.__init__(self, plot, line=line, source=source, env=env,
                 read_series=read_series, axes=axes, aname=aname)

    def _line_from_source(self) :
        if self.source is None :
            return

        x_range = self.axes.get_xlim() if self.source.needs_x_range else None
        values = self.source.source_get_values(multi_array=True, x_range=x_range)[0]

        points = values['values']
        series = range(0, len(points[0]))
        dim = self.source.source_get_max_dim()
        if dim > 1 :
            trans = zip(*points)
            if not self.read_series :
                trans[0] = series
        else :
            trans = [series, points]

        trans = (trans[0], trans[1], 0 if dim < 3 else trans[2])
        self.line = self.axes.scatter(trans[0], trans[1], trans[2])
        # Can't replot as no set_zdata :(
        self.axes.figure.canvas.draw()
