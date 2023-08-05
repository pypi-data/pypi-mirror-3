import os, math, sys, getopt, string
import sympy
import copy
import glypher.Word as Word
from glypher.Widget import GlyphEntry, GlyphResponder
import random
from utils import debug_print
from gtk import gdk
import threading
import cairo, gtk, gobject
import matplotlib
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as mpl_Canvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as mpl_Navbar
from ipython_view import *

import pylab
from PIL import Image
import sims
import aobject

def format_obj_name (name) :
    obj = aobject.get_object_from_dictionary(name)
    return obj.get_aname_nice() + ' [' + obj.get_aname_root() + ']'

class AesPythonConsole(gtk.Frame, aobject.AObject) :
    ipython_view = None

    def __init__(self, env=None):
        gtk.Frame.__init__(self)
        aobject.AObject.__init__(self, "AesPythonConsole", env, view_object = True)
        self.set_aname_nice("Python Console " + (" ("+str(self.get_aname_num())+")" if self.get_aname_num()>1 else ""))
        self.ipython_view = IPythonView()
        cons_vbox = gtk.VBox()
        V = self.ipython_view
        # with thanks to IPython cookbook
        V.modify_font(pango.FontDescription("Mono 10"))
        V.set_wrap_mode(gtk.WRAP_CHAR)
        V.updateNamespace({'aobject' : aobject})
        V.updateNamespace({'AES' : aobject.get_object_from_dictionary})
        V.show()

        cons_vbox.pack_start(V)
        self.add(cons_vbox)

        self.source_action = lambda s :\
            V.write('AES(\''+s+'\')')

        views_hbox = gtk.HBox()
        win = gtk.VBox()
        views_hbox.pack_start(win)
        win.pack_start(gtk.Label('Objects'), False)

        s = gtk.ScrolledWindow()
        win.pack_start(s)

        dict_lsst = aobject.get_object_dictionary().get_liststore_by_am('aobject')
        dict_lsst.set_sort_column_id(1, gtk.SORT_ASCENDING)

        dict_trvw = gtk.TreeView(model=dict_lsst)

        dict_nice_crtx = gtk.CellRendererText()
        dict_nice_tvcl = gtk.TreeViewColumn('Nice Name', dict_nice_crtx)
        dict_nice_tvcl.add_attribute(dict_nice_crtx, 'text', 1)
        dict_nice_tvcl.set_expand(True)
        dict_trvw.append_column(dict_nice_tvcl)

        dict_name_crtx = gtk.CellRendererText()
        dict_name_tvcl = gtk.TreeViewColumn('Internal Name', dict_name_crtx)
        dict_name_tvcl.add_attribute(dict_name_crtx, 'text', 0)
        dict_name_tvcl.set_expand(True)
        dict_trvw.append_column(dict_name_tvcl)

        dict_trvw.connect('row-activated', lambda t, p, c : \
            self.ipython_view.write('AES(\''+\
            dict_lsst.get_value(dict_lsst.get_iter(p), 0)+'\')'))

        s.add(dict_trvw)
        s.set_size_request(-1, 200)

        win = gtk.VBox()
        views_hbox.pack_start(win)
        win.pack_start(gtk.Label('Useful Variables'))

        s2 = gtk.ScrolledWindow()
        win.pack_start(s2)

        uv_lsst = aobject.get_object_dictionary().useful_vars
        uv_lsst.set_sort_column_id(0, gtk.SORT_ASCENDING)

        uv_trvw = gtk.TreeView(model=uv_lsst)

        uv_nice_crtx = gtk.CellRendererText()
        uv_nice_tvcl = gtk.TreeViewColumn('Object', uv_nice_crtx)
        #uv_nice_tvcl.add_attribute(uv_nice_crtx, 'text', 0)
        uv_nice_tvcl.set_cell_data_func(uv_nice_crtx, lambda c, r, t, i :
            uv_nice_crtx.set_property('text', \
                format_obj_name(uv_lsst.get_value(i, 0))))
        uv_nice_crtx.set_property('ellipsize', pango.ELLIPSIZE_MIDDLE)
        uv_nice_crtx.set_property('width-chars', 30)
        uv_nice_tvcl.set_expand(True)
        uv_trvw.append_column(uv_nice_tvcl)

        uv_desc_crtx = gtk.CellRendererText()
        uv_desc_tvcl = gtk.TreeViewColumn('Variable Description', uv_desc_crtx)
        uv_desc_tvcl.add_attribute(uv_desc_crtx, 'text', 2)
        uv_desc_tvcl.set_expand(True)
        uv_trvw.append_column(uv_desc_tvcl)

        uv_trvw.connect('row-activated', lambda t, p, c : \
            self.ipython_view.write('AES(\''+\
            uv_lsst.get_value(uv_lsst.get_iter(p), 0)+'\').'+\
            uv_lsst.get_value(uv_lsst.get_iter(p), 1)))

        s2.add(uv_trvw)
        s2.set_size_request(-1, 200)

        views_hbox.show_all()

        cons_vbox.pack_start(views_hbox, False)
        self.show_all()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { }
    #BEGIN PROPERTIES FUNCTIONS
    #END PROPERTIES FUNCTIONS
    def get_method_window(self) :
        win = gtk.VBox()

        return win
