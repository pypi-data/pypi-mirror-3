import os, math, sys, getopt, string
import pango
import random
from gtk import gdk
from ..tablemaker import PreferencesTableMaker
from ..paths import get_user_home
import threading
import cairo, gtk, gobject
import matplotlib
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_cairo import RendererCairo
import pylab
from PIL import Image
from ..aobject import *
from Pie import GlancerPie
from Plot import GlancerPlot
from Plot3d import GlancerPlot3D

def add_icons() :
    icon_factory = gtk.IconFactory()

    icon_names = ('plot2d', 'pie', 'plot3d')

    for icon_name in icon_names :
        stock_id = 'aes-glancer-'+icon_name

        source = gtk.IconSource()
        source.set_filename(
            paths.get_share_location() + 'images/icons/glancer/' + icon_name + '.svg')
        icon_set = gtk.IconSet()
        icon_set.add_source(source)
        icon_factory.add(stock_id, icon_set)

    icon_factory.add_default()

class Glancer(gtk.Frame, AObject) :
    __gsignals__ = { "expose-event" : "override", "loaded-sim" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ( gobject.TYPE_STRING,)),
             }
    fig = None
    read_series = True

    def savefig(self) :
        '''Save image of figure to file.'''

        chooser = gtk.FileChooserDialog(\
                      title="Save Image", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_current_folder(get_user_home())
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_current_name('.png')
        resp = chooser.run()
        self.grab_focus()

        if resp == gtk.RESPONSE_OK :
            filename = chooser.get_filename()
            chooser.destroy()
        else :
            chooser.destroy()
            return

        self.fig.savefig(filename, format='png')

    def set_ui(self) :
        self.ui_action_group = gtk.ActionGroup('GlancerActions')
        self.ui_action_group.add_actions([('GlancerMenu', None, 'Glancer'),
            ('GlancerSaveImage', None, 'Save image', None, None,
                lambda w : self.savefig()),
                                         ])
        self.ui_ui_string = '''
            <ui>
                <menubar name="MenuBar">
                    <menu action="GlancerMenu">
                        <menuitem action="GlancerSaveImage"/>
                    </menu>
                </menubar>
            </ui>
        '''

    def __init__(self, env=None):
        gtk.Frame.__init__(self)

        vbox = gtk.VBox()
        self.fig = matplotlib.pyplot.figure()
        self.plotter = None

        self.frame = gtk.Frame()
        vbox.pack_start(self.frame)
        vbox.show_all()
        self.add(vbox)

        self.set_size_request(0, 200)

        self.source_action = lambda s :\
            self.load_series(get_object_from_dictionary(s))

        AObject.__init__(self, "Glancer", env, view_object = True)
        self.set_aname_nice("Glancer" + (" ("+str(self.get_aname_num())+")" if self.get_aname_num()>1 else ""))

    def load_series(self, source, series = None, vals = None):
        if self.plotter is None :
            dims = source.source_get_max_dim()
            if dims == 3:
                self.new_plotter(GlancerPlot3D)
            else :
                self.new_plotter(GlancerPlot)

        self.plotter.load_series(source, series=series, vals=vals)

        self.elevate()
        self.queue_draw()

    def new_plotter(self, plotter) :
        self.check_clear()
        if self.plotter is not None :
            self.frame.remove(self.frame.get_child())
            self.plotter.aes_remove()
            del self.plotter
        self.fig.clear()
        self.plotter = plotter(self.fig, queue_draw=lambda : self.queue_draw(), env=self.get_aenv())
        self.absorb_properties(self.plotter, as_self = False)
        self.frame.add(self.plotter.canvas)
        self.frame.show_all()
        self.queue_draw()

    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.window.get_size())

    def print_out(self, op, pc, pn) :
        w = pc.get_width(); h = pc.get_height()
        w1, h1 = self.plotter.canvas.get_width_height()
        r = 1
        if w/h > w1/h1 : w = h*w1/h1; r = h/h1
        else : h = w*h1/w1; r = w/w1
        print w, h
        print w1, h1
        print r
        #op.cancel()

        c = pc.get_cairo_context()
        c.scale(r, r)
        renderer = RendererCairo (self.plotter.canvas.figure.dpi)
        renderer.set_width_height (w1, h1)
        renderer.gc.ctx = pc.get_cairo_context()
        self.plotter.canvas.figure.draw (renderer)

    def draw(self, cr, swidth, sheight):
        if self.plotter is not None :
            self.plotter.canvas.draw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return { }
    #BEGIN PROPERTIES FUNCTIONS
    #END PROPERTIES FUNCTIONS

    def replot_all(self) :
        for line in self.lines :
            line.replot()

    def get_method_window(self) :
        win = gtk.VBox()
        icon_table = gtk.Table(3, 1)
        win.pack_start(icon_table)

        new_butt = gtk.ToggleButton()
        new_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_NEW,
                                                       gtk.ICON_SIZE_BUTTON))
        new_butt.set_tooltip_text("New plot")
        icon_table.attach(new_butt, 0, 1, 0, 1)
        new_menu = gtk.Menu()
        new_menu.attach_to_widget(new_butt, None)
        new_butt.connect("button_press_event", lambda w, e :\
            new_menu.popup(None, None, None, e.button, e.time) \
                if not w.get_active() else \
            new_menu.popdown())

        new_menu.set_title('New Plot')
        new_menu.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 65535, 65535))

        new_labl = gtk.Label()
        new_labl.set_markup('<b>New...</b>')
        new_meni = gtk.MenuItem()
        new_meni.add(new_labl)
        new_menu.append(new_meni)

        plot_butt = gtk.MenuItem()
        plot_butt.add(gtk.image_new_from_stock('aes-glancer-plot2d',
                                                       gtk.ICON_SIZE_BUTTON))
        plot_butt.set_tooltip_text("New 2D plot")
        plot_butt.connect("activate", lambda o : self.new_plotter(GlancerPlot))
        new_menu.append(plot_butt)

        pie_butt = gtk.MenuItem()
        pie_butt.add(gtk.image_new_from_stock('aes-glancer-pie',
                                                       gtk.ICON_SIZE_BUTTON))
        pie_butt.set_tooltip_text("New pie chart")
        pie_butt.connect("activate", lambda o : self.new_plotter(GlancerPie))
        new_menu.append(pie_butt)

        plot_butt = gtk.MenuItem()
        plot_butt.add(gtk.image_new_from_stock('aes-glancer-plot3d',
                                                       gtk.ICON_SIZE_BUTTON))
        plot_butt.set_tooltip_text("New 3D plot")
        plot_butt.connect("activate", lambda o : self.new_plotter(GlancerPlot3D))
        new_menu.append(plot_butt)

        new_menu.show_all()

        sim_butt = gtk.Button()
        sim_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX,
                                                    gtk.ICON_SIZE_BUTTON))
        sim_butt.set_tooltip_text("Plot from currently selected Source")
        sim_butt.set_sensitive(get_object_dictionary().selected_source \
                               is not None)
        icon_table.attach(sim_butt, 1, 2, 0, 1)
        sim_butt.connect("clicked", lambda o : self.load_from_sim(\
                            get_object_dictionary().selected_source))
        get_object_dictionary().connect(\
            'aesthete-selected-source-change',
            lambda tr : sim_butt.set_sensitive(True))

        win.set_border_width(5)
        win.show_all()

        return win

    def check_clear(self, force = False) :
        if self.plotter is not None :
            self.plotter.check_clear(force=force)

    def load_from_sim(self, aname) :
        if aname == None or aname == 'None' or aname == '' : return
        sim = get_object_from_dictionary(aname)

        self.check_clear()
        dim = sim.source_get_max_dim()

        if len(values) == 1 :
            self.load_series(sim)
        else :
            for point_set in values :
                points = point_set['values']
                series = range(0, len(points[0]))
                if dim > 1 :
                    trans = zip(*points)
                    if not self.read_series : trans[0] = series
                else :
                    trans = [series, points]
                self.load_series(None, trans[0], trans[1])

add_icons()
