import os, math, sys, getopt, string
from aobject.utils import debug_print
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
from aobject.aobject import *
from Canvas import *
from Line import GlancerLine
from Scatter import GlancerScatter
from Legend import GlancerLegend

legend_locs = matplotlib.legend.Legend.codes    
legend_locs_rev = dict((legend_locs[k],k) for k in legend_locs)

class GlancerPlotLike(AObject) :
    fig = None
    axes = None
    canvas = None

    lines = None
    legend_object = None

    plot_over = False
    legend = True
    title = ''
    xlabel_font = ''

    grid = get_preferencer().get_preference("GlancerPlot","grid")

    if grid is None :
        grid = False

    grid_color = get_preferencer().get_preference("GlancerPlot","grid_color")

    if grid_color is None :
        grid_color = 'k'

    read_series = True

    scroll_speed = 0.1

    _xlim_changed_conn = None

    def change_time(self, time) :
        self.time = time
        for line in self.lines :
            line.set_time(time)

    def _do_xlim_changed(self, ax) :
        for line in self.lines :
            if line.source.needs_x_range and \
               line.source.current_x_range != self.axes.get_xlim() :
                line.source.source_reload()
                line.replot()

    def set_xlim(self, left=None, right=None) :
        if left is None :
            left = self.get_axes_xmin()
        if right is None :
            right = self.get_axes_xmax()
        self.axes.set_xlim(left, right)

        self.queue_draw()

    def set_ylim(self, top=None, bottom=None) :
        if top is None :
            top = self.get_axes_ymax()
        if bottom is None :
            bottom = self.get_axes_ymin()
        self.axes.set_ylim(bottom, top)
        self.queue_draw()

    def get_useful_vars(self) :
        return {
                 'axes' : 'mpl Axes',
                 'fig' : 'mpl Fig',
                 'canvas' : 'mpl Canvas',
        }

    def aes_add_a(self, aname_root, **parameters) :
        if aname_root == 'GlancerLine' :
            source = parameters['source']
            return self.load_series(source)
        if aname_root == 'GlancerLegend' :
            self.axes.legend(loc=None)
            if self.axes.legend_ is None :
                return None
            return GlancerLegend(self.axes.legend_,
                                 self.queue_draw, env=self.get_aenv()
                                 )

        return AObject.aes_add_a(self, aname_root, **parameters)

    def __init__(self, aname_root, fig, queue_draw, env=None):
        self.canvas = GlancerCanvas(fig)
        self.queue_draw = queue_draw
        self.fig = fig

        self._xlim_changed_conn = self.axes.callbacks.connect('xlim_changed',
                                                    self._do_xlim_changed)

        self.canvas.mpl_connect('scroll_event', self.do_mpl_scroll_event)
        self.canvas.mpl_connect('button_press_event', self.do_mpl_button_press_event)
        self.canvas.mpl_connect('button_release_event',
                                self.do_mpl_button_release_event)
        self.canvas.mpl_connect('motion_notify_event',
                                self.do_mpl_motion_notify_event)
        self.lines = []

        AObject.__init__(self, aname_root, env, view_object=False)
        self.time_entr = self.aes_method_entry_update('time')
        self.time_entr.show_all()

    def do_legend(self, loc = None) :
        if len(self.lines) > 0 and self.legend :
            self.axes.legend(loc=loc)

            if self.legend_object is not None :
                self.legend_object.aes_remove()
                self.legend_object = None
                self.legend_font_holder.remove(self.legend_font_holder.get_child())

            if self.axes.legend_ is None :
                return None

            self.legend_object = GlancerLegend(self.axes.legend_,
                                               self.queue_draw, env = self.get_aenv())
            self.legend_font_holder.add(\
                self.legend_object.aes_method_font_button("font",
                                                          "Set legend font"))
            self.legend_font_holder.show_all()

            self.absorb_properties(self.legend_object, as_self = False)

            if loc==None : self.emit_property_change("legend_loc")
        else : self.axes.legend_ = None
        self.canvas.draw()

    def check_legend(self) :
        if len(self.lines) == 0 and self.legend_object :
            self.legend_object.aes_remove()
            self.legend_object = None

    def check_clear(self, force = False) :
        if not self.plot_over or force :
            self.axes.clear()
            for line in self.lines :
                line.self_remove(parent_remove = False)
            self.lines = []
            self.check_legend()
            self.queue_draw()

    def update_canvas_size(self) :
        w, h = self.fig.get_size_inches()
        dpi = self.fig.get_dpi()
        h *= dpi
        w *= dpi
        self.fig.canvas.resize(int(w), int(h))
        self.fig.canvas.set_size_request(int(w), int(h))
        self.queue_draw()

    def replot_all(self) :
        for line in self.lines :
            line.replot()

class GlancerPlot(GlancerPlotLike) :
    max_dim = 2

    def __init__(self, fig, queue_draw, env=None):
        self.axes = fig.add_subplot(1,1,1)
        GlancerPlotLike.__init__(self, "GlancerPlot", fig, queue_draw, env=env)

    def load_series(self, source, series = None, vals = None):
        resolution = self.get_resolution()
        if source is None :
            mpl_line, = self.axes.plot(series, vals)
            line = GlancerLine(self, line=mpl_line, resolution=resolution,
                               env=self.get_aenv(), time=self.get_time())
        elif source.source_type() == 'line' :
            line = GlancerLine(self, source=source, axes=self.axes,
                           read_series=self.read_series,
                           resolution=resolution,
                           env=self.get_aenv(), time=self.get_time())
        else :
            line = GlancerScatter(self, source=source, axes=self.axes,
                           read_series=self.read_series,
                           env=self.get_aenv())

        self.lines.append(line)
        self.absorb_properties(line, as_self = False)

        self.do_legend()
        self.update_canvas_size()

        self.time_entr.get_parent().set_visible(source.get_time_cols() is not None)

        return line
    #PROPERTIES
    def get_auto_aesthete_properties(self) :
        return {
            'grid' : ( bool, ),
            'legend' : (bool, ),
            'grid_color' : (string_to_float_tup, ),
            'plot_over' : (bool, ),
            'title' : (str, ),
            'xmultiplier' : (float,),
            'ymultiplier' : (float,),
            'read_series' : (bool,),
            'resolution' : (int,),
            'legend_loc' : (str,),
            'axes_axis_bgcolor' : (string_to_float_tup,),
            'figure_facecolor' : (string_to_float_tup,),
            'axes_xmin' : (float,),
            'axes_xlabel' : (str,),
            'axes_xmax' : (float,),
            'axes_ymin' : (float,),
            'axes_ylabel' : (str,),
            'axes_ymax' : (float,),
            'xhide_oom' : (bool,),
            'yhide_oom' : (bool,),
            'xtick_font' : (str,),
            'ytick_font' : (str,),
            'xlabel_font' : (str,),
            'ylabel_font' : (str,),
            'title_font' : (str,),
            'size_inches' : (string_to_float_tup,),
            'subplots_region' : (string_to_float_tup,),
            'time' : (string_to_float_tup, (AOBJECT_CAN_NONE,)),
            'time_args' : (int, (AOBJECT_CAN_NONE,)),


                }
    #BEGIN PROPERTIES FUNCTIONS
    def get_subplots_region(self) :
        spp = self.fig.subplotpars
        return (spp.left, spp.bottom, spp.right, spp.top)
    def change_subplots_region(self, val) :
        self.fig.subplots_adjust(*val)
        self.queue_draw()
    def get_size_inches(self) :
        return tuple(self.fig.get_size_inches())
    def change_size_inches(self, val) :
        self.fig.set_size_inches(*val)
        self.update_canvas_size()
    def change_legend(self, val) :
        self.legend = val
        self.do_legend()
    def change_grid(self, val) :
        self.grid = val
        if self.grid : 
            self.axes.grid(color=self.grid_color)
        else : 
            self.axes.grid()
        self.queue_draw()
    def get_grid_color(self): return mpl_to_tuple(self.grid_color)
    def change_grid_color(self, val) :
        self.grid_color = val
        if self.grid :
            self.axes.grid(b=self.grid, color=val)
        self.queue_draw()
    def get_xmultiplier(self) : return 1.
    def get_ymultiplier(self) : return 1.
    def get_resolution(self) :
        if self.lines == [] :
            res_check = get_preferencer().get_preference("GlancerPlot","resolution")
            if res_check is not None :
                return int(res_check)
            else :
                return 10
        return self.lines[0].get_resolution()
    def get_legend_loc(self) :
        return (legend_locs_rev[self.legend_object.get_loc()] if self.legend_object else '')
    def get_axes_axis_bgcolor(self):
        return mpl_to_tuple(self.axes.get_axis_bgcolor())
    def get_figure_facecolor(self):
        return mpl_to_tuple(self.fig.get_facecolor())
    def get_axes_ylabel(self) : return self.axes.get_ylabel()
    def get_axes_ymin(self) : return self.axes.get_ylim()[0]
    def get_axes_ymax(self) : return self.axes.get_ylim()[1]
    def get_axes_xlabel(self) : return self.axes.get_xlabel()
    def get_axes_xmin(self) : return self.axes.get_xlim()[0]
    def get_axes_xmax(self) : return self.axes.get_xlim()[1]
    def get_xhide_oom(self) :
        return False
    def get_yhide_oom(self) :
        return False
    def get_xtick_font(self) :
        tick_props = self.axes.get_xaxis().get_major_ticks()[0].label1.get_fontproperties()
        return mpl_to_font(tick_props)
    def get_ytick_font(self) :
        tick_props = self.axes.get_yaxis().get_major_ticks()[0].label1.get_fontproperties()
        return mpl_to_font(tick_props)
    def get_xlabel_font(self) :
        label_props = self.axes.get_xaxis().get_label().get_fontproperties()
        return mpl_to_font(label_props)
    def get_ylabel_font(self) :
        label_props = self.axes.get_yaxis().get_label().get_fontproperties()
        return mpl_to_font(label_props)
    def get_title_font(self) :
        label_props = self.axes.title.get_fontproperties()
        return mpl_to_font(label_props)
    #These are exactly as Aesthete will define them...
    #def get_plot_over(self): return self.plot_over if val==None else (val=='True')
    #def change_plot_over(self, val): self.plot_over = val
    #def change_read_series(self, val) : self.read_series = val

    def change_legend_loc(self, val) : self.do_legend(loc = val)
    def change_title(self, val) :
        self.title = val
        self.axes.set_title(self.title, visible = (self.title!=''))
        self.queue_draw()
    def change_resolution(self, val) :
        for line in self.lines : 
            line.set_resolution(val)
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
        self.queue_draw()
    def change_xtick_font(self, val) : 
        ticks = self.axes.get_xaxis().get_major_ticks()
        for tick in ticks :
            font_to_mpl(tick.label1.get_fontproperties(), val)
        self.queue_draw()
    def change_xlabel_font(self, val) : 
        label_props = self.axes.get_xaxis().get_label().get_fontproperties()
        font_to_mpl(label_props, val)
        self.queue_draw()
    def change_ylabel_font(self, val) : 
        label_props = self.axes.get_yaxis().get_label().get_fontproperties()
        font_to_mpl(label_props, val)
        self.queue_draw()
    def change_title_font(self, val) : 
        label_props = self.axes.title.get_fontproperties()
        font_to_mpl(label_props, val)
        self.queue_draw()
    def change_xmultiplier(self) : self.axes.xaxis.get_major_formatter().multiplier = val; self.queue_draw()
    def change_ymultiplier(self) : self.axes.yaxis.get_major_formatter().multiplier = val; self.queue_draw()
    def change_axes_axis_bgcolor(self, val) : self.axes.set_axis_bgcolor(val); self.queue_draw()
    def change_axes_xlabel(self, val) : self.axes.set_xlabel(val); self.queue_draw()
    def change_axes_xmin(self, val) : self.set_xlim(left=val); self.queue_draw()
    def change_axes_xmax(self, val) : self.set_xlim(right=val); self.queue_draw()
    def change_axes_ylabel(self, val) : self.axes.set_ylabel(val); self.queue_draw()
    def change_axes_ymin(self, val) : self.set_ylim(bottom=val); self.queue_draw()
    def change_axes_ymax(self, val) : self.set_ylim(top=val); self.queue_draw()
    def change_figure_facecolor(self, val) : self.fig.set_facecolor(val); self.queue_draw()
    #END PROPERTIES FUNCTIONS


    def get_method_window(self) :
        #fram = gtk.Frame()
        #fram.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(1, 1, 1))
        win = gtk.VBox()
        who_algn = gtk.Alignment(0.5, 0.5)
        who_algn.set_property("top_padding", 10)
        who_hbox = gtk.HBox(spacing=5)
        who_hbox.pack_start(gtk.image_new_from_stock('aes-glancer-plot2d',
                                                     gtk.ICON_SIZE_BUTTON),
                            False)
        who_hbox.pack_start(gtk.Label("2D Plot"), False)
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
        config_vbox = self.methods_make_visual_config()
        config_vbox.aes_title = "Configure plot appearance"
        config_butt.connect("clicked", lambda o :
                            self.env.action_panel.to_action_panel(config_vbox))

        # Import Config
        legend_amtb = self.aes_method_toggle_button("legend", None,
                                                   preferencable=False)
        legend_amtb.set_image(gtk.image_new_from_stock(gtk.STOCK_JUSTIFY_RIGHT,
                                                    gtk.ICON_SIZE_BUTTON))
        legend_amtb.set_tooltip_text("Toggle legend")
        icon_table.attach(legend_amtb, 1, 2, 0, 1)
        plot_over_amtb = self.aes_method_toggle_button("plot_over", None,
                                                     preferencable=False)
        plot_over_amtb.set_image(gtk.image_new_from_stock(gtk.STOCK_DND_MULTIPLE,
                                                    gtk.ICON_SIZE_BUTTON))
        plot_over_amtb.set_tooltip_text("Toggle overlay of new plots")
        icon_table.attach(plot_over_amtb, 2, 3, 0, 1)

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
        icon_table.attach(clear_butt, 3, 4, 0, 1)
        clear_butt.connect("clicked", lambda o : self.check_clear(force=True))

        replot_butt = gtk.Button()
        replot_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH,
                                                       gtk.ICON_SIZE_BUTTON))
        replot_butt.set_tooltip_text("Replot all lines")
        replot_butt.connect("clicked", lambda o : self.replot_all())
        icon_table.attach(replot_butt, 4, 5, 0, 1)

        #fram.add(win)
        win.show_all()

        return win

    def methods_make_visual_config(self) :
        config_vbox = gtk.VBox()

        config_ntbk = gtk.Notebook()

        general_table_maker = PreferencesTableMaker()
        general_table_maker.append_heading("Title")
        general_table_maker.append_row("Text",
            self.aes_method_entry_update("title"))
        general_table_maker.append_row("Font", self.aes_method_font_button("title_font", "Set title font"))
        general_table_maker.append_heading("Geometry")
        general_table_maker.append_row("Size (in)",
            self.aes_method_tuple_entry_update("size_inches"))
        general_table_maker.append_row("Plot area",
            self.aes_method_tuple_entry_update("subplots_region"))
        general_table_maker.append_heading("Colours")
        general_table_maker.append_row("Face", self.aes_method_colour_button("figure_facecolor", "Set figure colour"))
        general_table_maker.append_row("Axes",self.aes_method_colour_button("axes_axis_bgcolor", "Axes Background Colour"))
        general_table_maker.append_heading("Detail")
        general_table_maker.append_row("Resolution",
            self.aes_method_entry_update("resolution"),
            tip="Only applies to continuous Sources")
        general_table_maker.append_heading("Grid")
        general_table_maker.append_row("Show Grid", self.aes_method_check_button("grid", None))
        general_table_maker.append_row("Grid Colour",self.aes_method_colour_button("grid_color", "Grid Colour"))
       

        config_tabl = general_table_maker.make_table()
        config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False)
        config_ntbk.append_page(config_tabl_vbox, gtk.Label("General"))

        legend_table_maker = PreferencesTableMaker()
        legend_table_maker.append_heading("Geometry")

        legend_position_cmbo = gtk.combo_box_new_text()
        for loc in legend_locs : legend_position_cmbo.append_text(loc)
        self.aes_method_automate_combo_text(legend_position_cmbo, "legend_loc")
        legend_table_maker.append_row("Position", legend_position_cmbo)

        legend_table_maker.append_heading("Appearance")
        self.legend_font_holder = gtk.Frame()
        legend_table_maker.append_row(" Font", self.legend_font_holder)

        config_tabl = legend_table_maker.make_table()
        config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False)
        config_ntbk.append_page(config_tabl_vbox, gtk.Label("Legend"))

        axes = { 'x' : "X" , 'y' : "Y" }
        for axis in axes :
            axes_table_maker = PreferencesTableMaker()
            axes_table_maker.append_heading("Labeling")
            axes_table_maker.append_row(" Label",
                self.aes_method_entry_update("axes_"+axis+"label"))
            axes_table_maker.append_row(" Axis",
                self.aes_method_font_button(axis+"label_font", "Set "+axes[axis]+" axis font"))
            axes_table_maker.append_row(" Tick", self.aes_method_font_button(axis+"tick_font", "Set "+axes[axis]+" axis font"))
            axes_table_maker.append_heading("Data Limits")
            axes_table_maker.append_row(" Minimum Value",
                self.aes_method_entry_update("axes_"+axis+"min"))
            axes_table_maker.append_row(" Maximum Value",
                self.aes_method_entry_update("axes_"+axis+"max"))

            config_tabl = axes_table_maker.make_table()
            config_tabl_vbox = gtk.VBox(); config_tabl_vbox.pack_start(config_tabl, False); 
            config_ntbk.append_page(config_tabl_vbox, gtk.Label(axes[axis]+" Axis"))

        config_vbox.pack_start(config_ntbk)
        config_vbox.show_all()
        return config_vbox

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

        if event.button == 2 or event.button == 1 :
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

        if event.button == 2 or event.button == 1:
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
