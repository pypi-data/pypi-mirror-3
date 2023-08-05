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
import pylab
from PIL import Image
from Canvas import *
from ..aobject import *

legend_locs = matplotlib.legend.Legend.codes    
legend_locs_rev = dict((legend_locs[k],k) for k in legend_locs)

class GlancerPie(AObject) :
    fig = None
    axes = None
    canvas = None
    pie = None
    source = None

    legend_object = None
    legend = True
    title = ''

    read_series = True

    scroll_speed = 0.1

    def replot(self) :
        self._pie_from_source()

    def _pie_from_source(self) :
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

        if self.pie is None :
            self.pie = self.axes.pie(trans[1])[0]
        else :
            self.pie.set_xdata(trans[0])
            self.pie.set_ydata(trans[1])
        self.axes.figure.canvas.draw()

    def do_mpl_scroll_event(self, event) :
        '''Handle scrolling ourselves.'''

        if event.inaxes != self.axes :
            return False

        self.axes.set_autoscale_on(False)
        xl = self.axes.get_xlim()
        yl = self.axes.get_ylim()

        ec = (event.xdata, event.ydata)

        # event.step tells direction
        spd = (1+self.scroll_speed) ** (-event.step)

        # unfortunately, this seems to be the only sensible way to
        # get to the modifiers. Phrased oddly, but says do_x if we're
        # not told to only do y, and v.v.
        do_specific = event.guiEvent.state & gtk.gdk.CONTROL_MASK
        do_x = not (do_specific and (event.guiEvent.state & gtk.gdk.SHIFT_MASK))
        do_y = not (do_specific and do_x)

        if do_x :
            self.axes.set_xlim(ec[0] - (ec[0]-xl[0])*spd,
                               ec[0] - (ec[0]-xl[1])*spd)
        if do_y :
            self.axes.set_ylim(ec[1] - (ec[1]-yl[0])*spd,
                               ec[1] - (ec[1]-yl[1])*spd)


        self.queue_draw()
        return True

    _move_from = None
    _move_from_xl = None
    _move_from_yl = None
    def do_mpl_button_press_event(self, event) :
        '''Check button presses.'''

        if event.inaxes != self.axes :
            return False
        
        m_control = event.guiEvent.state & gtk.gdk.CONTROL_MASK

        if event.button == 2 :
            if m_control :
                self.axes.autoscale_view()
                self.axes.set_autoscale_on(True)
                self.queue_draw()
            else :
                self.axes.set_autoscale_on(False)
                self._move_from = (event.x, event.y)
                self._move_from_xl = self.axes.get_xlim()
                self._move_from_yl = self.axes.get_ylim()

            self.queue_draw()
            return True

        return False

    def do_mpl_button_release_event(self, event) :
        '''Check button releases.'''

        if event.button == 2 :
            self._move_from = None
            self._move_from_xl = None
            self._move_from_yl = None

            self.queue_draw()
            return True

        return False

    def do_mpl_motion_notify_event(self, event) :
        '''Check motion notifications.'''

        if event.inaxes != self.axes :
            return False

        do_specific = event.guiEvent.state & gtk.gdk.CONTROL_MASK
        do_x = not (do_specific and (event.guiEvent.state & gtk.gdk.SHIFT_MASK))
        do_y = not (do_specific and do_x)

        if self._move_from is not None :
            dx = (event.x-self._move_from[0])
            dy = (event.y-self._move_from[1])
            l,b,r,t = self.axes.bbox.extents
            el,er = self.axes.get_xlim()
            eb,et = self.axes.get_ylim()
            dx = dx*(er-el)/(r-l)
            dy = dy*(et-eb)/(t-b)

            if do_x :
                self.axes.set_xlim(self._move_from_xl[0]-dx,
                                   self._move_from_xl[1]-dx)
            if do_y :
                self.axes.set_ylim(self._move_from_yl[0]-dy,
                                   self._move_from_yl[1]-dy)

            self.queue_draw()
            return True

    def __init__(self, fig, queue_draw, env=None):
        self.queue_draw = queue_draw
        self.fig = fig
        self.canvas = GlancerCanvas(self.fig)
        self.axes = self.fig.add_subplot(1,1,1)
        self.canvas.mpl_connect('scroll_event', self.do_mpl_scroll_event)
        self.canvas.mpl_connect('button_press_event', self.do_mpl_button_press_event)
        self.canvas.mpl_connect('button_release_event',
                                self.do_mpl_button_release_event)
        self.canvas.mpl_connect('motion_notify_event',
                                self.do_mpl_motion_notify_event)
        AObject.__init__(self, "GlancerPie", env, view_object=False)

    def load_series(self, source, series=None, vals=None):
        if series is not None :
            raise RuntimeError(
                'Sorry, GlypherPie can only plot single series Sources')
        self.source = source
        self._pie_from_source()

    def redraw(self) :
        self.do_legend()
        self.figure.canvas.draw()
    
    def __del__(self) :
        get_object_dictionary().disconnect(self.sd_chg_conn)
        AObject.__del__(self)

    def do_legend(self, loc = None) :
        if len(self.lines) > 0 and self.legend :
            self.axes.legend(loc=loc)

            if self.legend_object is not None :
                self.legend_object.aes_remove()
                self.legend_object = None
            self.legend_object = GlancerLegend(self.axes.legend_, env = self.get_aenv())

            self.absorb_properties(self.legend_object, as_self = False)

            if loc==None : self.emit_property_change("legend_loc")
        else : self.axes.legend_ = None
        self.canvas.draw()

    def check_legend(self) :
        if self.legend_object :
            self.legend_object.aes_remove()
            self.legend_object = None

    def check_clear(self, force = False) :
        self.axes.clear()
        self.check_legend()
        self.queue_draw()

    #PROPERTIES
    def get_aesthete_properties(self):
        return {
             'source' : [None, self.get_source, True],
             'legend' : [self.change_legend, self.get_legend, True],
             'figure_facecolor' : [self.change_figure_facecolor, self.get_figure_facecolor, True],
             'axes_axis_bgcolor' : [self.change_axes_axis_bgcolor, self.get_axes_axis_bgcolor, True],
             'axes_xlabel' : [self.change_axes_xlabel, self.get_axes_xlabel, True],
             'axes_ylabel' : [self.change_axes_ylabel, self.get_axes_ylabel, True],
             'title_font' : [self.change_title_font, self.get_title_font, True],
             'xlabel_font' : [self.change_xlabel_font, self.get_xlabel_font, True],
             'ylabel_font' : [self.change_ylabel_font, self.get_ylabel_font, True],
             'xhide_oom' : [self.change_xhide_oom, self.get_xhide_oom, True],
             'yhide_oom' : [self.change_yhide_oom, self.get_yhide_oom, True],
             'xtick_font' : [self.change_xtick_font, self.get_xtick_font, True],
             'ytick_font' : [self.change_ytick_font, self.get_ytick_font, True],
             'xmultiplier' : [self.change_xmultiplier, self.get_xmultiplier, True],
             'ymultiplier' : [self.change_ymultiplier, self.get_ymultiplier, True],
             'read_series' : [self.change_read_series, self.get_read_series, True],
             'legend_loc' : [self.change_legend_loc, self.get_legend_loc, True],
             'title' : [self.change_title, self.get_title, True] }
    #BEGIN PROPERTIES FUNCTIONS
    def get_source(self, val=None) : return self.source if val==None else val
    def get_xmultiplier(self, val=None) : return 1. if val==None else float(val)
    def get_ymultiplier(self, val=None) : return 1. if val==None else float(val)
    def get_legend(self, val=None): return self.legend if val==None else (val=='True')
    def get_read_series(self, val=None): return self.read_series if val==None else (val=='True')
    def get_title(self, val=None): return self.title if val==None else val
    def get_legend_loc(self, val=None) :
        return (legend_locs_rev[self.legend_object.get_loc()] if self.legend_object else '')\
        if val==None else val
    def get_axes_axis_bgcolor(self, val=None):
        return mpl_to_tuple(self.axes.get_axis_bgcolor()) \
        if val==None else string_to_float_tup(val)
    def get_figure_facecolor(self, val=None):
        return mpl_to_tuple(self.fig.get_facecolor()) \
        if val==None else string_to_float_tup(val)
    def get_axes_xlabel(self, val=None) : return self.axes.get_xlabel() if val==None else val
    def get_axes_ylabel(self, val=None) : return self.axes.get_ylabel() if val==None else val
    def get_xhide_oom(self, val=None) :
        return False \
        if val==None else (val=='True')
    def get_yhide_oom(self, val=None) :
        return False \
        if val==None else (val=='True')
    def get_xtick_font(self, val=None) :
        tick_props = self.axes.get_xaxis().get_major_ticks()[0].label1.get_fontproperties()
        return mpl_to_font(tick_props) \
        if val==None else val
    def get_ytick_font(self, val=None) :
        tick_props = self.axes.get_yaxis().get_major_ticks()[0].label1.get_fontproperties()
        return mpl_to_font(tick_props) \
        if val==None else val
    def get_xlabel_font(self, val=None) :
        label_props = self.axes.get_xaxis().get_label().get_fontproperties()
        return mpl_to_font(label_props) \
        if val==None else val
    def get_ylabel_font(self, val=None) :
        label_props = self.axes.get_yaxis().get_label().get_fontproperties()
        return mpl_to_font(label_props) \
        if val==None else val
    def get_title_font(self, val=None) :
        label_props = self.axes.title.get_fontproperties()
        return mpl_to_font(label_props) \
        if val==None else val
    def change_legend_loc(self, val) : self.do_legend(loc = val)
    def change_title(self, val) :
        self.title = val
        self.axes.set_title(self.title, visible = (self.title!=''))
        self.queue_draw()
    def change_xhide_oom(self, val) : 
        self.axes.get_xaxis().major.formatter.hide_oom = val
        self.queue_draw()
    def change_yhide_oom(self, val) : 
        self.axes.get_yaxis().major.formatter.hide_oom = val
        self.queue_draw()
    def change_ytick_font(self, val) : 
        ticks = self.axes.get_yaxis().get_major_ticks()
        for tick in ticks :
            font_to_mpl(tick.label1.get_fontproperties(), val)
    def change_xtick_font(self, val) : 
        ticks = self.axes.get_xaxis().get_major_ticks()
        for tick in ticks :
            font_to_mpl(tick.label1.get_fontproperties(), val)
    def change_xlabel_font(self, val) : 
        label_props = self.axes.get_xaxis().get_label().get_fontproperties()
        font_to_mpl(label_props, val)
    def change_ylabel_font(self, val) : 
        label_props = self.axes.get_yaxis().get_label().get_fontproperties()
        font_to_mpl(label_props, val)
    def change_title_font(self, val) : 
        label_props = self.axes.title.get_fontproperties()
        font_to_mpl(label_props, val)
    def change_read_series(self, val) : self.read_series = val
    def change_xmultiplier(self, val=None) : self.axes.xaxis.get_major_formatter().multiplier = val; self.queue_draw()
    def change_ymultiplier(self, val=None) : self.axes.yaxis.get_major_formatter().multiplier = val; self.queue_draw()
    def change_legend(self, val) : self.legend = val; self.do_legend()
    def change_axes_axis_bgcolor(self, val) : self.axes.set_axis_bgcolor(val); self.queue_draw()
    def change_axes_xlabel(self, val) : self.axes.set_xlabel(val); self.queue_draw()
    def change_axes_ylabel(self, val) : self.axes.set_ylabel(val); self.queue_draw()
    def change_figure_facecolor(self, val) : self.fig.set_facecolor(val); self.queue_draw()
    #END PROPERTIES FUNCTIONS

    def replot_all(self) :
        for line in self.lines :
            line.replot()

    def get_method_window(self) :
        #fram = gtk.Frame()
        #fram.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(1, 1, 1))
        win = gtk.VBox()
        who_algn = gtk.Alignment(0.5, 0.5)
        who_algn.set_property("top_padding", 10)
        who_hbox = gtk.HBox(spacing=5)
        who_hbox.pack_start(gtk.image_new_from_stock('aes-glancer-pie',
                                                     gtk.ICON_SIZE_BUTTON),
                            False)
        who_hbox.pack_start(gtk.Label("Pie chart"), False)
        who_algn.add(who_hbox)
        win.pack_start(who_algn)

        icon_table = gtk.Table(1, 5)
        win.pack_start(icon_table)

        # Visual Config
        config_butt = gtk.Button()
        config_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_PAGE_SETUP,
                                                       gtk.ICON_SIZE_BUTTON))
        config_butt.set_tooltip_text("Appearance preferences...")
        icon_table.attach(config_butt, 0, 1, 0, 1)
        config_win = gtk.Window(); config_win.set_size_request(400, -1)
        config_win.set_title("Configure plot appearance")
        config_vbox = self.methods_make_visual_config()
        config_win.add(config_vbox); config_win.set_transient_for(self.get_aenv().toplevel)
        config_butt.connect("clicked", lambda o : config_win.show())
        config_remove_butt = gtk.Button("Close")
        config_remove_butt.connect("clicked", lambda o : config_win.hide())
        config_remove_butt.show_all()
        config_hbox = gtk.HBox(); config_hbox.show()
        config_hbox.pack_start(config_remove_butt, False, False, 5)
        config_vbox.pack_end(config_hbox, False, False, 5)

        # Import Config
        legend_amtb = self.aes_method_toggle_button("legend", None,
                                                   preferencable=False)
        legend_amtb.set_image(gtk.image_new_from_stock(gtk.STOCK_JUSTIFY_RIGHT,
                                                    gtk.ICON_SIZE_BUTTON))
        legend_amtb.set_tooltip_text("Toggle legend")
        icon_table.attach(legend_amtb, 1, 2, 0, 1)

        # From Sim
        sim_hbox = gtk.HBox()
        #sim_cmbo = gtk.ComboBox( get_object_dictionary().get_liststore_by_am('Source') )
        #sim_cllr = gtk.CellRendererText(); sim_cmbo.pack_start(sim_cllr); sim_cllr.props.ellipsize = pango.ELLIPSIZE_END;
        #sim_cmbo.add_attribute(sim_cllr, 'text', 1)
        #self.sim_cmbo = sim_cmbo
        #sim_hbox.pack_start(sim_cmbo)

        clear_butt = gtk.Button()
        clear_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR,
                                                      gtk.ICON_SIZE_BUTTON))
        clear_butt.set_tooltip_text("Clear all lines")
        icon_table.attach(clear_butt, 0, 1, 1, 2)
        clear_butt.connect("clicked", lambda o : self.check_clear(force=True))

        replot_butt = gtk.Button()
        replot_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH,
                                                       gtk.ICON_SIZE_BUTTON))
        replot_butt.set_tooltip_text("Replot all lines")
        replot_butt.connect("clicked", lambda o : self.replot_all())
        icon_table.attach(replot_butt, 1, 2, 1, 2)

        #fram.add(win)
        win.show_all()

        return win

    def methods_make_visual_config(self) :
        config_vbox = gtk.VBox()

        config_ntbk = gtk.Notebook()

        general_table_maker = PreferencesTableMaker()
        general_table_maker.append_heading("Title")
        general_table_maker.append_row("Title", self.aes_method_entry("title"))
        general_table_maker.append_row("Title Font", self.aes_method_font_button("title_font", "Set title font"))
        general_table_maker.append_heading("Colours")
        general_table_maker.append_row("Face Colour", self.aes_method_colour_button("figure_facecolor", "Set figure colour"))
        general_table_maker.append_row("Axes Background",self.aes_method_colour_button("axes_axis_bgcolor", "Axes Background Colour"))

        config_tabl = general_table_maker.make_table()
        config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False)
        config_ntbk.append_page(config_tabl_vbox, gtk.Label("General"))

        legend_table_maker = PreferencesTableMaker()
        legend_table_maker.append_heading("Geometry")

        legend_position_cmbo = gtk.combo_box_new_text()
        for loc in legend_locs : legend_position_cmbo.append_text(loc)
        self.aes_method_automate_combo_text(legend_position_cmbo, "legend_loc")
        legend_table_maker.append_row("Position", legend_position_cmbo)

        config_tabl = legend_table_maker.make_table()
        config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False)
        config_ntbk.append_page(config_tabl_vbox, gtk.Label("Legend"))

        axes = { 'x' : "X" , 'y' : "Y" }
        for axis in axes :
            axes_table_maker = PreferencesTableMaker()
            axes_table_maker.append_heading("Labeling")
            axes_table_maker.append_row(axes[axis]+" Axes Label", self.aes_method_entry("axes_"+axis+"label"))
            axes_table_maker.append_row(axes[axis]+" Axis Font", self.aes_method_font_button(axis+"label_font", "Set "+axes[axis]+" axis font"))
            axes_table_maker.append_row(axes[axis]+" Tick Font", self.aes_method_font_button(axis+"tick_font", "Set "+axes[axis]+" axis font"))
            axes_table_maker.append_row(axes[axis]+" Multiplier", self.aes_method_entry(axis+"multiplier", wait_until_parsable_float = True))

            config_tabl = axes_table_maker.make_table()
            config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False); 
            config_ntbk.append_page(config_tabl_vbox, gtk.Label(axes[axis]+" Axis"))

        config_vbox.pack_start(config_ntbk)
        config_vbox.show_all()
        return config_vbox
