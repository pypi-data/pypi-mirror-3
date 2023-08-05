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

try :
    import pygtksheet as gtksheet
    have_gtksheet = True
except ImportError :
    have_gtksheet = False

import pylab
from PIL import Image
import sims
import aobject

def get_sheet_child_at(sheet, r, c) :
    for child in sheet.get_children() :
        if child.attached_to_cell and child.row == r and child.col == c :
            return child
    return None

class AesSpreadsheet(gtk.Frame, aobject.AObject) :
    sheet = None
    entries = None
    current_cell = None
    suspend_activate = False

    def get_sympy_val(self, r, c) :
        if (r,c) in self.entries :
            return self.entries[(r,c)].get_sympy()
        return None
        #self.suspend_activate = True
        #t = self.sheet.cell_get_text(r, c)[0]
        #self.suspend_activate = False
        #return sympy.core.sympify(t)

    def do_sheet_activate_signal(self, sheet, r, c) :
        if self.suspend_activate :
            return

        if self.current_cell is not None :
            self.do_cell_editor_processed_line(self.cell_editor)

        self.current_cell = (r,c)
        if (r,c) not in self.entries :
            self.add_an_entry(*self.current_cell)

        entry = self.entries[(r,c)]
        debug_print(entry.get_text())
        self.cell_editor.set_xml(entry.get_xml(input_phrase=True))
        self.cell_editor.grab_focus()

    def do_cell_editor_processed_line(self, ce) :
        debug_print(ce.get_xml())
        debug_print(self.current_cell)
        if self.current_cell is None :
            return
        if not self.current_cell in self.entries :
            self.add_an_entry(*self.current_cell)

        responder = self.entries[self.current_cell]
        xml = ce.get_xml()
        responder.set_xml(xml)

    def __init__(self, env=None):
        gtk.Frame.__init__(self)
        aobject.AObject.__init__(self, "AesSpreadsheet", env, view_object = True)
        self.set_aname_nice("Spreadsheet" + (" ("+str(self.get_aname_num())+")" if self.get_aname_num()>1 else ""))

        self.entries = {}

        vbox = gtk.VBox()
        self.sheet = gtksheet.Sheet(2000, 20, "PyGtkSheet")
        sheet_scrw = gtk.ScrolledWindow()
        sheet_scrw.add(self.sheet)
        vbox.pack_start(gtk.Label("PyGtkSheet through Aes"), False, False)
        vbox.pack_start(sheet_scrw)
        self.cell_editor = GlyphEntry(evaluable=True)
        self.cell_editor.main_phrase.set_p('spreadsheet', self)
        self.cell_editor.connect("processed-line",
                                 self.do_cell_editor_processed_line)
        
        vbox.pack_start(self.cell_editor, False)
        vbox.show_all()
        new_win = gtk.Window()
        new_win.maximize()
        new_win.add(vbox)
        new_win.show_all()

        entry = self.add_an_entry(1, 1)
        entry.caret.insert_entity(Word.make_word('Hi', None))

        self.sheet.connect("activate", self.do_sheet_activate_signal)

    def add_an_entry(self, r, c) :
        test_entry = GlyphResponder(interactive=False,
                                    resize_to_main_phrase=True, evalf=True)
        test_entry.response_phrase.set_anchor_point((5, 5))
        test_entry.response_phrase.set_anchor(('l', 't'))
        test_entry.swap()
        test_entry.response_phrase.set_p('spreadsheet', self)
        test_entry.input_phrase.set_p('spreadsheet', self)
        test_entry.show_all()
        test_entry.set_font_size(15.0)
        test_entry.connect("button-press-event", lambda but, ev :
                           self.do_sheet_activate_signal(self.sheet, r, c))
        self.sheet.attach(test_entry, r, c, 0, 0, 3, 3)
        self.entries[(r,c)] = test_entry
        return test_entry

    def load_csv(self, filename):
        vals = []
        with open (filename) as f:
            #columns = f.readline().split(',')
            vals = numpy.loadtxt(f, delimiter=',', unpack = True)

        multicol = True
        try : test = vals[0][0]
        except : multicol = False

        if len(vals) == 0 : return

        if not multicol : vals = [vals]

        for i in range(0, len(vals)) :
            col = vals[i]
            for j in range(0, len(col)) :
                self.sheet.set_cell_text(j, i, str(vals[i][j]))

    def load_series(self, source, series, vals):
        pass
        #mpl_line, = self.axes.plot(series, vals)
        #line = AesMPLLine(self, mpl_line, source = source, logger = self.get_alogger())
        #self.lines.append(line)
        #self.absorb_properties(line, as_self = False)

        #line.change_property("label", source)
        #if self.legend : self.axes.legend()

        #fmtr = AesFormatter(useOffset = False, useMathText = True)
        #self.axes.xaxis.set_major_formatter(fmtr)
        #fmtr = AesFormatter(useOffset = False, useMathText = True)
        #self.axes.yaxis.set_major_formatter(fmtr)

        #self.elevate()
        #self.queue_draw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { }
    #BEGIN PROPERTIES FUNCTIONS
    #END PROPERTIES FUNCTIONS
    def get_method_window(self) :
        if not have_gtksheet : return gtk.Label("No PyGtkSheet found")
        win = gtk.VBox()

        # From Sim
        #sim_expa = gtk.Expander("From Sim"); sim_efra = gtk.Frame(); sim_expa.add(sim_efra)
        #sim_vbox = gtk.VBox()
        #sim_cmbo = gtk.combo_box_new_text()
        #self.sim_cmbo = sim_cmbo
        #self.od_add_conn = aobject.get_object_dictionary().connect(\
        #    "add", lambda o, a, r : self.methods_update_sim_cmbo() if r=="Sim" else 0)
        #self.od_rem_conn = aobject.get_object_dictionary().connect(\
        #    "remove", lambda o, a, r : self.methods_update_sim_cmbo() if r=="Sim" else 0)
        #self.methods_update_sim_cmbo()
        #sim_vbox.pack_start(sim_cmbo)
        #sim_time_hbox = gtk.HBox(); sim_time_hbox.pack_start(gtk.Label("Time"))
        #sim_time_entr = gtk.Entry(); sim_time_hbox.pack_start(sim_time_entr)
        #sim_vbox.pack_start(sim_time_hbox)
        #sim_butt = gtk.Button("Load from Sim")
        #sim_butt.connect("clicked", lambda o : self.load_from_sim(sim_cmbo.get_active_text(), sim_time_entr.get_text()))
        #sim_vbox.pack_start(sim_butt)
        #sim_efra.add(sim_vbox)
        #win.pack_start(sim_expa)

        # Load CSV
        expander = gtk.Expander("Import CSV"); ef = gtk.Frame(); expander.add(ef)
        csv_vbox = self.methods_make_load_csv()
        ef.add(csv_vbox)
        expander.show_all()

        win.pack_start(expander)
        win.show_all()
        return win

    def methods_make_load_csv(self) :
        csv_vbox = gtk.VBox()

        plotcsv_hbox = gtk.HBox()
        plotcsv_text = gtk.Entry()
        plotcsv_butt = gtk.Button("Load")
        plotcsv_hbox.pack_start(plotcsv_text); plotcsv_hbox.pack_start(plotcsv_butt)
        csv_vbox.pack_start(plotcsv_hbox)

        plotcsv_butt.connect("clicked", lambda o : self.load_csv(plotcsv_text.get_text()))
        return csv_vbox
    
    #def methods_update_sim_cmbo(self) :
    #    cmbo = self.sim_cmbo
    #    mdl = cmbo.get_model()
    #    lv = aobject.get_object_dictionary().get_objects_by_am("Sim")
    #    for row in mdl : mdl.remove(row.iter)
    #    for v in lv : cmbo.append_text(v.get_aname())
    #
    #def load_from_sim(self, aname, time) :
    #    if aname == 'None' or aname == '' : return
    #    sim = aobject.get_object_from_dictionary(aname)
    #    old_time = sim.get_time()
    #    sim.set_time(float(time))
    #    pss = sim.get_point_sets()

    #    self.check_clear()

    #    for point_set in sim.get_point_sets() :
    #        if not point_set['extent'] : continue
    #        points = point_set['point_set']
    #        trans = zip(*points)
    #        self.load_series(sim.get_aname()+":"+point_set['stem'], trans[0], trans[1])

    #    sim.set_time(old_time)
