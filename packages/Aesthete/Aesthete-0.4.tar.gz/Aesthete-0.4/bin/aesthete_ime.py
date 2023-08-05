#!/usr/bin/env python

"""Testing this

.. moduleauthor:: Phil Weir
"""

import uuid
import matplotlib
import time
matplotlib.use('GtkAgg')
import os, math, sys, getopt, string
import cProfile
from aesthete import *
import random
import aesthete.paths as paths
import aesthete.tablemaker as tablemaker
from gtk import gdk
import threading
import cairo, gtk, gobject
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as mpl_Canvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as mpl_Navbar
import pylab
from PIL import Image
from aesthete.glypher.Widget import GlyphBasicGlypher as GBG
from aesthete.glypher.Glypher import Glypher as G
from aesthete.glancer.Glancer import Glancer
from aesthete.gluer.Gluer import Gluer
import aesthete.aesspreadsheet as aesspreadsheet
import aesthete.aespythonconsole as aespythonconsole
from aesthete.glypher.GlyphMaker import GlyphMaker as GM
import aesthete.help_browser as help_browser
from aesthete.utils import debug_print, set_debug_print

def filter_func(f, u) :
    debug_print(f['groups'])
    return True

class Aesthete (gtk.Window, aobject.AObject):

    __gsignals__ = { "key-press-event" : "override",
                     'window-state-event' : 'override' }

    terminal_pid = 0
    active_plot = None
    concise_property_notebook = True
    show_logger = False
    show_welcome = False
    debug_print_on = False
    maximize_on_start = False

    def add_icons(self) :
        icon_factory = gtk.IconFactory()

        icon_names = ('glancer', 'glypher', 'gridder')

        for icon_name in icon_names :
            stock_id = 'aes-'+icon_name

            source = gtk.IconSource()
            source.set_filename(
                paths.get_share_location() + 'images/icons/aesthete/' + icon_name + '.svg')
            icon_set = gtk.IconSet()
            icon_set.add_source(source)
            icon_factory.add(stock_id, icon_set)

        icon_factory.add_default()

    def plot_source(self, glypher, aname) :
        glancer = Glancer(self.get_aenv())
        glancer.source_action(aname)

    _full_screen_window = None
    def toggle_full_screen(self) :
        fullscreen = bool(self.get_window().get_state() & \
                          gtk.gdk.WINDOW_STATE_FULLSCREEN)
        toolbar = self.ui_manager.get_widget("/ToolBar")
        view_notebook = aobject.get_object_dictionary().get_viewnotebook()
        if fullscreen :
            self.unfullscreen()
            toolbar.show()
            self._full_screen_window.hide()
            if self.notebook.get_parent() :
                self.notebook.get_parent().remove(self.notebook)
            self.left_vpnd.pack1(self.notebook)
            self.left_vpnd.show()
            view_notebook.set_tab_pos(gtk.POS_TOP)
        else :
            self.fullscreen()
            toolbar.hide()
            self.left_vpnd.hide()
            if self.notebook.get_parent() :
                self.notebook.get_parent().remove(self.notebook)
            self._full_screen_window.add(self.notebook)
            self._full_screen_window.show()
            view_notebook.set_tab_pos(gtk.POS_LEFT)

        self.focus_to_view_notebook()

    def __init__(self):
        gtk.Window.__init__(self)
        env = aobject.Env(logger = alogger.get_new_logger(), toplevel = self)
        aobject.AObject.__init__(self, "Aesthete", env, show = False)

        self.log(1, "=== Welcome to Aesthete ===")

        self.add_icons()

        aobject.get_object_dictionary().connect("add", lambda o,s,r : self.change_property('active_plot', s)\
            if r=='Plot' else 0)

        self.setup_window()

        #GM(env=self.get_aenv())
        #GBG(env=self.get_aenv())
        #Gluer(self.get_aenv())
        Glancer(self.get_aenv())
        glypher = G(env=self.get_aenv())

        if not os.path.exists(paths.get_user_location()+'welcomed') :
            self.show_welcome = True
        if self.show_welcome :
            dialog = gtk.Dialog('Welcome to Aesthete!', self,
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            vbox = dialog.get_content_area()
            info_head_labl = gtk.Label()
            info_head_labl.set_markup('<b>Glypher Tip</b>')
            vbox.pack_start(info_head_labl, False)
            info_labl = gtk.Label()
            info_labl.set_line_wrap(True)
            info_labl.set_size_request(600, -1)
            info_labl.set_markup("""
<i>Aesthete</i> is split up into a number of modules. One module in particular
takes a little bit of getting used to, though we feel it's worthwhile!

<i>Glypher</i> is the visual equation editing framework and computer algebra
frontend. In simpler terms, it's a GUI for sympy. <i>Glypher</i> is a little
misleading though; it looks like a basic text entry window, but as a cunningly
disguised equation editor, it's a little more complex.

<u>An equation in Glypher is a tree of components</u>. When you're in the Glypher
window itself, you start with a 1-element "SpaceArray". You can insert a
word, or equation here, but remember that pressing Space will add an element
to this top-level array, so don't try and space out your equation this way!
This strict structure makes entry of commands easy and unambiguous.

For example, entering "E x p a n d <i>Space</i> x + 3 <i>Right</i> <i>Right</i> ^ 2" will
give you a two element top-level SpaceArray. The first element is an
instruction, the second, its argument. Next press Return and you should see
the familiar binomial expansion!

As well as remembering Space has a specific meaning, you should also remember
that, instead of explicit bracketing, <i>Aesthete</i> gets your drift by
operating on (squaring, multiplying, etc.) whatever expression is currently
enclosed in blue Caret brackets. <i>Aesthete</i> will show brackets if it
feels the need to avoid <i>visual</i> ambiguity, but they're always there
implicitly. Trying to insert a parenthesis will bring up a tip explaining this.

So, that should give you a gist to get you started. Fiddle around and you should
find quite a number of possibilities, each of which we're gradually getting
around to documenting...
""")
            vbox.pack_start(info_labl)
            noshow_hbox = gtk.HBox()
            noshow_chbn = gtk.CheckButton()
            noshow_hbox.pack_start(noshow_chbn, False)
            noshow_hbox.pack_start(gtk.Label('Don\'t show this again'))
            vbox.pack_start(noshow_hbox, False)
            vbox.show_all()
            try :
                dialog.get_widget_for_response(gtk.RESPONSE_ACCEPT).grab_focus()
            except :
                dialog.get_action_area().get_children()[0].grab_focus()
            dialog.run()
            dialog.destroy()
            if noshow_chbn.get_active() :
                with open(paths.get_user_location()+'welcomed', 'w') as f :
                    f.write(details.get_version())
                    f.write(str(time.time()))
            
        #plot_window = plotter.get_new_plot_window(comp, plotref, runA, runB, timeA, timeB, left1, fabien_file, plateside, vertices, left2)
        if self.get_maximize_on_start() :
            self.maximize()
        self._full_screen_window = gtk.Window()
        self._full_screen_window.set_transient_for(self)
        self._full_screen_window.set_opacity(0.8)
        self._full_screen_window.hide()
    
        self.focus_to_view_notebook()

    def __del__(self) :
        aobject.AObject.__del__(self)

    def focus_to_view_notebook(self) :
        view_notebook = aobject.get_object_dictionary().get_viewnotebook()
        if view_notebook.get_n_pages() > 0 :
            view_notebook.get_nth_page(view_notebook.get_current_page()).grab_focus()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { 'active_plot' : [self.change_active_plot, self.get_active_plot, True], \
             'concise_property_notebook' : [self.change_concise_property_notebook, self.get_concise_property_notebook, True], \
             'show_logger' : [self.change_show_logger, self.get_show_logger, True], \
             'debug_print' : [self.change_debug_print, self.get_debug_print, True], \
             'maximize_on_start' : [self.change_maximize_on_start,
                                    self.get_maximize_on_start, True], \
				 'show_welcome' : [self.change_show_welcome, self.get_show_welcome, True] } 
    #BEGIN PROPERTIES FUNCTIONS
    def get_active_plot(self, val=None): return (self.active_plot.get_aname() if self.active_plot != None else '') if val==None else val
    def change_active_plot(self, aname):
        plot = aobject.get_object_from_dictionary(aname)
        if (plot != None and plot.get_aname_root() == 'AesMPLFrame') : self.active_plot = plot
    def get_concise_property_notebook(self, val=None) :
        return self.concise_property_notebook if val==None else str(val)=='True'
    def change_concise_property_notebook(self, val) :
        aobject.get_object_dictionary().set_concise_notebook(val)
        self.concise_property_notebook = val
    def get_show_logger(self, val=None) :
        return self.show_logger if val==None else str(val)=='True'
    def change_show_logger(self, val) :
        if self.logger_view :
            self.logger_view.show() if val else self.logger_view.hide()
        self.show_logger = val
    def get_show_welcome(self, val=None) :
        return self.show_welcome if val==None else str(val)=='True'
    def change_show_welcome(self, val) :
        if self.show_welcome :
            with open(paths.get_user_location()+'welcomed', 'w') as f :
                    f.write(details.get_version())
                    f.write(str(time.time()))
        elif os.path.exists(paths.get_user_location()+'welcomed') :
            os.remove(paths.get_user_location()+'welcomed')
        self.show_welcome = val
    def get_debug_print(self, val=None) :
        return self.debug_print_on if val==None else str(val)=='True'
    def change_debug_print(self, val) :
        self.debug_print_on = val
        set_debug_print(val)
    def get_maximize_on_start(self, val=None) :
        return self.maximize_on_start if val==None else str(val)=='True'
    def change_maximize_on_start(self, val) :
        self.maximize_on_start = val
    #END PROPERTIES FUNCTIONS

    def do_window_state_event(self, event) :
        maximized = bool(self.get_window().get_state() & gtk.gdk.WINDOW_STATE_MAXIMIZED)
        if maximized != self.get_maximize_on_start() :
            self.set_preference('maximize_on_start', maximized)

    def to_action_panel(self, window) :
        old_window = self.action_panel.get_children()[0]
        if old_window is not None :
            self.action_panel.remove(old_window)
            old_window.hide()
        self.action_panel.add(window)
        self.action_panel.set_label(window.aes_title)
        window.show()

    def do_print(self) :
        po = gtk.PrintOperation()
        po.connect("begin-print", self.begin_print)
        po.connect("draw-page", self.draw_page)
        res = po.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, self)
    
    def get_preferences_window(self) :
        tm = tablemaker.PreferencesTableMaker()
        tm.append_row("Concise property notebook", self.aes_method_check_button('concise_property_notebook'))
        tm.append_row("Show logger window", self.aes_method_check_button('show_logger'))
        tm.append_row("Show welcome dialogue on startup", self.aes_method_check_button('show_welcome'))
        tm.append_row("Print debug output",
                      self.aes_method_check_button('debug_print'))
        win = tm.make_table()
        return win

    def do_preferences_response(self, dlog, resp) :
        pass
    def do_preferences(self, w) :
        win = gtk.Dialog("Aesthete Preferences", self, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                           (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        win.vbox.pack_start(self.get_preferences_window(), False, False)
        win.connect("response", self.do_preferences_response)
        win.show_all()
        win.set_size_request(300, 200)
        win.run()
        win.destroy()
    
    def begin_print(self, op, ct) :
        op.set_n_pages(1)
    def draw_page(self, op, pc, pn) :
        if pn > 0 : return
        aobject.get_active_object().print_out(op, pc, pn)

    def explain_no_modules(self, what, missing) :
        dia = gtk.Dialog("Missing package", self)
        dia.pack_start(gtk.Label(what + ' requires the following package(s): ' + missing))
        dia.show()
        
    def setup_window(self) :
        #self.connect("logger", self.logger.get_new_signal_to_logger("Aesthete"))
        self.connect("destroy", lambda w : gtk.main_quit())

        main_vbox = gtk.VBox()
        hbox = gtk.HBox()
        vbox = gtk.VBox()

        ui_manager = aobject.ui_manager
        self.ui_manager = ui_manager
        accel_group = ui_manager.get_accel_group()
        self.add_accel_group(accel_group)

        spreadsheet = lambda w : aesspreadsheet.AesSpreadsheet(self.get_aenv()) \
                if aesspreadsheet.have_gtksheet else \
                self.explain_no_module('Spreadsheet', 'gtksheet')
        actiongroup = gtk.ActionGroup('Actions')
        actions = []
        add_actions = [ \
            ('File', None, '_File'),
            ('View', None, '_View'),
            ('Tools', None, '_Tools'),
            ('Sources', None, 'Sources'),
            ('Help', None, '_Help'),
            ('Print', gtk.STOCK_PRINT, '_Print', None, None, lambda w : self.do_print()),
            ('Contents', gtk.STOCK_HELP, '_Contents', 'F1', None, lambda w : help_browser.launch_help()),
            ('Quit', gtk.STOCK_QUIT, '_Quit', '<Alt>F4', None, lambda w : gtk.main_quit()),
            ('Fullscreen', gtk.STOCK_FULLSCREEN, '_Full screen', 'F11', None,
                lambda w : self.toggle_full_screen()),
            ('Glypher', 'aes-glypher', '_Glypher', None, 'New Glypher', lambda w : G(env=self.get_aenv())),
            ('GlyphMaker', gtk.STOCK_FIND_AND_REPLACE, '_GlyphMaker', None, 'New GlyphMaker', lambda w : GM(env=self.get_aenv())),
            ('Plot', 'aes-glancer', '_Plot',
                None, 'New Plot Window', lambda w :
                Glancer(self.get_aenv())), 
            ('Console', 'aes-python-console', 'Console',
                None, 'New Python Console',
                lambda w :  aespythonconsole.AesPythonConsole(self.get_aenv())),
            ('Spreadsheet', 'aes-gridder', 'Spreadsheet',
                None, 'New Spreadsheet Window',
                lambda w :  aesspreadsheet.AesSpreadsheet(self.get_aenv())),
            ('Preferences', gtk.STOCK_PREFERENCES, 'Pref_erences', None, 'Set Aesthete preferences', self.do_preferences),
            ('Import', gtk.STOCK_OPEN, '_Import Source...',
                None, 'New Source',
                lambda w : sims.SourceImporter.run_chooser(self.get_aenv())),
            ('Recent', gtk.STOCK_OPEN, '_Recent',
                None, 'Recently used sources', None)
            ]
        for tup in add_actions :
            action = gtk.Action(tup[0], tup[2], None, tup[1])
            if len(tup) >= 6 and tup[5] is not None :
                action.connect("activate", tup[5])
            actiongroup.add_action(action)

        ui_manager.insert_action_group(actiongroup, 0)
        ui_manager.add_ui_from_string("""
            <menubar name="MenuBar">
                <menu action="File">
                    <menuitem action="Print"/>
                    <menuitem action="Quit"/>
                </menu>
                <menu action="View">
                    <menuitem action="Fullscreen"/>
                </menu>
                <menu action="Tools">
                    <menuitem action="Glypher"/>
                    <menuitem action="GlyphMaker"/>
                    <menuitem action="Plot"/>
                    <menuitem action="Spreadsheet"/>
                    <separator/>
                    <menuitem action="Console"/>
                    <separator/>
                    <menuitem action="Preferences"/>
                </menu>
                <menu action="Sources">
                    <menuitem action="Import"/>
                    <menuitem action="Recent"/>
                </menu>
                <menu action="Help">
                    <menuitem action="Contents"/>
                </menu>
            </menubar>
            <toolbar name="ToolBar">
                <toolitem action="Glypher"/>
                <toolitem action="GlyphMaker"/>
                <toolitem action="Plot"/>
                <toolitem action="Spreadsheet"/>
                <separator/>
                <toolitem action="Import"/>
                <toolitem action="Print"/>
                <separator/>
                <toolitem action="Preferences"/>
                <toolitem action="Contents"/>
            </toolbar>
            """)
        menubar = ui_manager.get_widget("/MenuBar")
        main_vbox.pack_start(menubar, False, True, 0)
        toolbar = ui_manager.get_widget("/ToolBar")
        main_vbox.pack_start(toolbar, False, True, 0)

        recent_sources = ui_manager.get_widget("/MenuBar/Sources/Recent")
        recent_sources_rcmu = \
            gtk.RecentChooserMenu(gtk.recent_manager_get_default())
        recent_sources_rcfi = gtk.RecentFilter()
        recent_sources_rcfi.add_group('aesthete-sources')
        #recent_sources_rcmu.add_filter(recent_sources_rcfi)
        recent_sources.set_submenu(recent_sources_rcmu)
        recent_sources_rcmu.connect('item-activated',
            lambda c : sims.load_from_file(c.get_current_uri(),
                                           c.get_current_item().get_display_name(),
                                           self.get_aenv()))

        sources_trvw = sims.make_source_treeview()
        sources_trvw.set_size_request(100, 0)
        sources_trvw.set_tooltip_column(1)
        sources_vbox = gtk.VBox()
        sources_vbox.pack_start(sources_trvw)
        sources_butt = gtk.Button("Update")
        sources_butt.connect("clicked", lambda o : sims.reload_sources(ness=True))
        sources_vbox.pack_start(sources_butt, False, False)
        sources_vbox.show_all()
        hbox.pack_end(sources_vbox, False)
        
        #plotter.connect("logger", self.logger.get_new_signal_to_logger("Plot Window"))
        view_notebook = aobject.get_object_dictionary().view_notebook
        vbox.pack_start(view_notebook)
        view_notebook.show()
        
        logger_view = self.get_alogger().get_new_logger_view()
        logger_view.show_all()
        
        notebook = gtk.Notebook()
        notebook.append_page(logger_view, gtk.Label("Logger"))
        notebook.show_all()
        vbox.pack_start(notebook)
        self.logger_view = notebook
        if not self.get_show_logger() : notebook.hide()
        
        vbox.show()
        hbox.pack_end(vbox)

        left_vpnd = gtk.VPaned()
        self.left_vpnd = left_vpnd
        #property_frame = gtk.Frame("Objects")
        #property_frame.set_shadow_type(gtk.SHADOW_IN)
        property_notebook = aobject.get_object_dictionary().get_notebook()
        property_notebook.show()
        self.notebook = property_notebook
        #property_frame.add(property_notebook)
        #property_frame.show()

        action_panel = gtk.Frame("Action Panel")
        action_panel.to_action_panel = self.to_action_panel
        self.env.action_panel = action_panel # Sets action panel for all objects inheriting this env
        action_panel.set_shadow_type(gtk.SHADOW_IN)
        action_panel.set_size_request(0, 100)
        self.action_panel = action_panel
        #action_panel_vbox = gtk.VBox()
        #action_panel_vbox.pack_start(action_panel, False)
        #action_panel_vbox.show()
        action_panel.show()
        #left_vpnd.pack1(property_frame, True, True)
        left_vpnd.pack1(property_notebook, False, False)
        left_vpnd.pack2(action_panel, True)
        left_vpnd.show()
        hbox.pack_start(left_vpnd, False)

        hbox.show()

        status = aobject.get_status_bar()
        status.show()
    
        main_vbox.pack_start(hbox)
        main_vbox.pack_start(status, False)
        main_vbox.show()
        self.add(main_vbox)

    def do_key_press_event(self, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        #if keyname == "w" and (event.state & gtk.gdk.CONTROL_MASK) :
        #    gtk.main_quit()            
        gtk.Window.do_key_press_event(self, event)

optlist, args = getopt.getopt(sys.argv[1:], 'F:VIOQDARSPd:n:m:r:')

left1 = False
left2 = False
vertices = False
plateside = False
wave = False
plotref = False
comp = False
fabien_file = None
invert = False

if len(args) > 2 : comp = True

for arg,val in optlist:
    if arg == "-D":
        comp = True
    if arg == "-R":
        plotref = True
    if arg == "-F":
        fabien_file = val
    if arg == "-Q":
        left2 = True

runA = args[0] if len(args)>0 else None
runB = None
timeA = float(args[1]) if len(args)>1 else 0
timeB = timeA
if comp :
    runB = args[2]
    timeB = float(args[3]) if len(args)>3 else timeA

window = Aesthete()
#window.set_size_request(-1, 700)
window.present()
window.set_icon_from_file(paths.get_share_location()+'images/great_wave/great_wave.svg')
window.set_title(details.get_name() + ' : ' + details.get_description())
#window.maximize()
#cProfile.run('gtk.main()')
gtk.main()

