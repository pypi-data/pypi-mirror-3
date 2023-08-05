#!/usr/bin/env python

import os, math, sys, getopt, string
import random
from gtk import gdk
import threading
import cairo, gtk, gobject
import matplotlib
import numpy, numpy.fft
import scipy, scipy.interpolate, scipy.optimize
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as mpl_Canvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as mpl_Navbar
import pylab
from PIL import Image
import sims
import aobject

name = ['A', 'B']

draft = 5.0
thickness = 5.5
height = 400
width = 800
gtop = 0.8
gbottom = -0.8
gleft = 0
gright = 33

pendsy = 50

time = 0

class TimeLineWidget(mpl_Canvas) :
	__gsignals__ = { "selected-time" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)) }

	curr_time = 0
	curr_time_line = None

	curr_process_time = 0
	curr_process_time_line = None

	def __init__(self, begin, end, timestep) :
		self.timestep = timestep
		self.fig = matplotlib.pyplot.Figure()
		self.a = self.fig.add_subplot(111); self.l = self.a.axhline(0, begin, end, marker='|'); self.a.set_ylim(-0.1, 0.1)
		self.a.set_yticklabels([]); self.a.set_frame_on(False); self.fig.set_facecolor('white'); self.a.set_xlim(begin, end)
		self.fig.subplots_adjust(bottom=0.4)
		mpl_Canvas.__init__(self, self.fig)
		self.fig.canvas.mpl_connect('button_press_event', self.do_select_time)
		self.set_size_request(width, 50)
		
	def do_select_time(self, event) :
		if not event.xdata : return
		time = self.timestep*int(event.xdata/self.timestep)
		self.set_time(self, time)
		self.emit("selected-time", time)

	def set_time(self, other, time) :
		self.curr_time = time
		if self.curr_time_line : self.curr_time_line.remove()
		self.curr_time_line = self.a.axvline(time, -1, 1, linewidth=2, color='r')
		self.draw()

	def hide_process_time(self, other) :
		if self.curr_process_time_line : self.curr_process_time_line.remove()

	def set_process_time(self, other, time) :
		self.curr_process_time = time
		if self.curr_process_time_line : self.curr_process_time_line.remove()
		self.curr_process_time_line = self.a.axvline(time, -1, 1, linewidth=2, color='g')
		self.draw()

	#def do_expose_event(self, event):
	#	cr = self.window.cairo_create()
	#	cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
	#	cr.clip()
	#	self.draw(cr, *self.window.get_size())

	def draw(self):
		mpl_Canvas.draw(self)
	
#class OverTimeToolbar (gtk.Toolbar):
#	def __init__(self):

class OverTimeWidget (mpl_Canvas):
	__gsignals__ = { "expose-event" : "override", "loaded-time-series" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
				( gobject.TYPE_STRING, gobject.TYPE_FLOAT )) }
	time_series = [[],[]]
	point = 0.0
	begin = 0.0
	begin_init = 0.0
	end = 100.0
	end_init = 100.0
	clear = True
	always_fft = False
	sim = None

	def __init__(self, begin, end):
		self.fig = matplotlib.pyplot.figure()
		self.axes = self.fig.add_subplot(1,1,1)
		self.begin = begin; self.begin_init = begin
		self.end = end; self.end_init = end

		mpl_Canvas.__init__(self, self.fig)

		#self.axes.plot([0,1,2,3,4],[0,1,4,9,16])
		self.set_size_request(width, 200)
		self.fig.canvas.mpl_connect('button_press_event', self.do_extent)

	def do_extent(self, event):
		if event.button == 1 : self.begin = event.xdata
		if event.button == 2 : self.begin = self.begin_init; self.end = self.end_init
		if event.button == 3 : self.end = event.xdata
		self.load_time_series(self, self.point, 0, self.sim.get_aname(), force=True)

	def do_key_press_event(self, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		print event.key
		if keyname == "f" :
			do_fft(self, event)

	def do_write(self) :
		self.fig.savefig("overtime.png")

	def do_fft_toggle(self, other):
		self.always_fft = other.get_active()
		self.load_time_series(self, self.point, 0, self.sim.get_aname(), force=True)

	def do_fft(self):
		# ttp://docs.scipy.org/doc/numpy/reference/routines.fft.html
		n = len(self.time_series[1])
		A = numpy.fft.fft(self.time_series[1])
		A = numpy.abs(A)
		R = numpy.fft.fftfreq(n)
		line, = self.axes.plot(R[1:n/2], A[1:n/2])
		line.set_label("FFT " + self.sim.get_run() + "/" + str(self.point)+"s")
	
	def load_time_series(self, other, point, mode, aname, force=False):
		if not force and self.point == point and self.sim.get_aname() == aname : return

		self.sim = aobject.get_object_from_dictionary(aname)
		if not self.sim : self.axes.clear(); return

		self.point = point
		sim = self.sim
		#sim = sims.Sim(run, time, ['left', 'right', 'plate1'])
		begin = self.begin; end = self.end
		if mode == 0 : self.clear = True
		if mode == 1 : self.clear = False
		self.time_series = [ [], [] ]
		T = begin

		sim.set_time(T)
		point = [point, 0.0]
		pointb, pin = sim.get_point(point)
		if not pointb : return

		self.point = pointb[0]
		point = list(pointb)
		self.time_series[0].append(T)
		self.time_series[1].append(pointb[1])
		T += sim.get_timestep()
		while T < end:
			sim.set_time(T)
			pointb, pin = sim.get_point(point)
			if pointb == None : break
			self.time_series[0].append(T)
			if pointb[0] != self.point : print "WARNING : points not matching"
			self.time_series[1].append(pointb[1])
			T += sim.get_timestep()
		if self.clear : self.axes.clear()
		if self.always_fft : self.do_fft()
		else : 
			line, = self.axes.plot(self.time_series[0],self.time_series[1])
			line.set_label(sim.get_run() + "/" + str(self.point)+"s")
		self.queue_draw()
		self.emit("loaded-time-series", sim.get_run(), self.point)

	def do_expose_event(self, event):
		#mpl_Canvas.do_expose_event(self, event)
		cr = self.window.cairo_create()
		cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
		cr.clip()
		self.draw(cr, *self.window.get_size())
		self.show_all()

	def draw(self, cr, swidth, sheight):
		mpl_Canvas.draw(self)
		#dorender_cr(cr, comp, plotref, left1, left2, vertices, plateside)

def dist (a, b) :
	return math.sqrt(pow((a[0]-b[0]),2)+pow((a[1]-b[1]),2))

class PlotWidget (gtk.DrawingArea, aobject.AObject):
	__gsignals__ = { "time-series-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
				( gobject.TYPE_FLOAT, gobject.TYPE_INT, gobject.TYPE_STRING )),
			 "expose-event" : "override" , "key-press-event" : "override",
			 "scroll-event" : "override", "button-press-event" : "override",
			 "button-release-event" : "override", "motion-notify-event" : "override",
			 "change-time" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
			 "process-time" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
			 "info" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
			 "process-time-done" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()) }

	comp = False
	simlist = []
	main_sim = None
	time = 0.0
	timestep = 1.0

	begin = 0
	end = 0
	broad_plate = False
	fabien_file = None
	plotref = False
	plateside = False
	left1 = False
	left2 = False

	context_menu = None
	context_menu_root_find = None
	context_menu_measure = None
	context_menu_time_series = None
	entity_context_menu = None

	auto = False
	auto_sid = 0
	auto_delay = 200

	scroll_factor = 1.0
	scroll_center = [0.0, 0.0]

	pan_on = False
	pan_center = [0.0, 0.0]
	pan_offset = [0.0, 0.0]
	pan_dx = [0.0, 0.0]
	zoom_factor_x = 1.0
	zoom_factor_y = 1.0

	entity_move_entity = None
	entity_move_on = False
	point_select_mode = 0
	point_select_run = ''

	target = [0.0, 0.0]

	vertices = False
	wave = False

	view = [gleft, gright, gbottom, gtop]
	gview = [gleft, gright, gbottom, gtop]

	points = []
	entities = []

	def __init__(self, env = None):
		gtk.DrawingArea.__init__(self)
		aobject.AObject.__init__(self, "PlotWidget", env)
	
	def __del__(self) :
		aobject.AObject.__del__(self)

	def add_sim(self, sim) :
		if not sim : return
		index = self.simlist.append(sim)
		if self.get_main_sim() : sim.set_time(self.get_main_sim().get_time())
		else : self.change_property("main_run", sim.get_aname())
		sim.connect("aesthete-property-change", self.do_sim_property_change)
		if sim.is_valid() :
			self.log(1, "Found params for new sim [" + sim.get_aname_nice() + "]")
		else :
			self.log(0, "No params found for new sim [" + sim.get_aname_nice() + "]")
		self.queue_draw()
		self.emit_property_change("runlist")
		return index

	def remove_sim_by_aname(self, aname) :
		for sim in self.simlist :
			if sim.get_aname() == aname : self.remove_sim(sim)

	def remove_sim_by_run(self, run) :
		for sim in self.simlist :
			if sim.get_run() == run : self.remove_sim(sim)

	def remove_sim(self, sim) :
		if not sim : return
		name = sim.get_aname()
		self.simlist.remove(sim)
		#sim.aes_remove()
		#del sim
		self.emit_property_change("runlist")
		if self.main_sim == name :
			if len(self.simlist) > 0 :
				self.change_main_sim(self.simlist[0].get_aname())
			else : self.change_main_sim(None)
		self.queue_draw()
	
	def change_main_sim(self, name) :
		self.main_sim = name
		sim = self.get_main_sim()
		if sim and sim.is_valid() :
			self.timestep = sim.get_timestep()
			self.log(1, "Timestep set for new primary sim: " + str(self.timestep) + "s")
		self.emit_property_change("main_run")
		if sim : self.log(2, "Main run is now " + str(sim.get_aname_nice()))
		self.queue_draw()
	
	def get_main_sim(self) : return self.find_sim(self.main_sim) if not self.main_sim == None else None

	def find_sim(self, name) :
		for sim in self.simlist :
			if sim.get_aname() == name : return sim
		return None
	
	#BEGIN PROPERTIES
	def get_aesthete_properties(self):
		return { \
			'main_run' : [self.change_main_run, self.get_main_run, False],\
			'runlist' : [None, self.get_runlist, False],\
			'auto_delay' : [self.change_auto_delay, self.get_auto_delay, True],\
			'comp' : [self.change_comp, self.get_comp, True]
		       }
	#BEGIN PROPERTIES FUNCTIONS
	def get_runlist(self, val=None) : return ([sim.get_aname() for sim in self.simlist]) if val==None else eval(val)
	def get_main_run(self, val=None): return (self.get_main_sim().get_aname() if self.get_main_sim() else '') if val==None else val
	def get_comp(self, val=None): return self.comp if val==None else (val=='True')
	def get_auto_delay(self, val=None) : return self.auto_delay if val==None else int(val)
	def change_main_run(self, val):
		for sim in self.simlist :
			if sim.get_aname() == val : self.change_main_sim(sim.get_aname())
	def change_auto_delay(self, val) :
		self.auto_delay = val
		if (self.auto) : self.do_anim(); self.do_anim()
	def change_comp(self, val):
		self.comp = self.get_comp(val)
		self.queue_draw()
	#END PROPERTIES
	def get_method_window(self) :
		win = gtk.VBox()

		sim_hbox = gtk.HBox()
		sim_hbox.pack_start(gtk.Label("Add"))
		sim_cmbo = gtk.ComboBox( aobject.get_object_dictionary().get_liststore_by_am('Sim') )
		sim_cllr = gtk.CellRendererText(); sim_cmbo.pack_start(sim_cllr)
		sim_cmbo.add_attribute(sim_cllr, 'text', 1)
		self.sim_cmbo = sim_cmbo
		sim_cmbo.connect("changed", lambda o : ( \
			self.add_sim(aobject.get_object_from_dictionary(\
			sim_cmbo.get_active_text())),\
			sim_cmbo.set_active(-1)))
		sim_hbox.pack_start(sim_cmbo)
		win.pack_start(sim_hbox)

		remove_sim_hbox = gtk.HBox()
		remove_sim_hbox.pack_start(gtk.Label("Remove"))
		remove_sim_acmb = self.aes_method_object_combo("runlist")
		remove_sim_acmb.connect("changed", lambda o : self.remove_sim_by_aname(remove_sim_acmb.get_active_text()))
		remove_sim_hbox.pack_start(remove_sim_acmb)
		win.pack_start(remove_sim_hbox)

		speed_ameu = self.aes_method_entry_update("auto_delay", "Set")
		speed_ameu.pack_start(gtk.Label("Anim Delay"))
		win.pack_start(speed_ameu)
		win.show_all()

		return win

	def setup(self, simlist, comp, gview, vertices, wave, fabien_file = None, plateside = False, plotref = False, left1 = False, left2 = False):

		#self.simA.change_property("time", timeA); self.simB.change_property("time", timeB)
		for sim in simlist :
			self.add_sim(sim)
		if len(simlist) > 0 : self.change_property("main_run", simlist[0].get_aname())

		self.comp = comp
		if len(simlist) > 0 : self.end = self.get_main_sim().get_end()
		self.vertices = vertices
		self.wave = wave
		self.gview = gview
		self.fabien_file = fabien_file
		self.plotref = plotref; self.left1 = left1; self.left2 = left2; self.plateside = plateside

		#sims.set_siml(self.siml, self.simA, comp, self.simB)
		self.set_property("can-focus", True)
		self.add_events(gtk.gdk.KEY_PRESS_MASK | gtk.gdk.SCROLL_MASK | gtk.gdk.BUTTON_PRESS_MASK | \
				gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
		self.set_size_request(width, height)
		
		#self.change_timeA(timeA); self.change_timeB(timeB)
		self.emit("change-time", self.time)

		# Context Menu
		self.context_menu = gtk.Menu()

		#context_menu_ = gtk.MenuItem("")
		#context_menu_.connect("button-press-event", self.do_)
		#self.context_menu.add(context_menu_)

		context_menu_anim = gtk.MenuItem("Animate [Sp]")
		context_menu_anim.connect("button-press-event", self.do_anim)
		self.context_menu.add(context_menu_anim)

		context_menu_move_home = gtk.MenuItem("First [Ho]")
		context_menu_move_home.connect("button-press-event", self.do_move_home)
		self.context_menu.add(context_menu_move_home)

		context_menu_move_end = gtk.MenuItem("Last [En]")
		context_menu_move_end.connect("button-press-event", self.do_move_end)
		self.context_menu.add(context_menu_move_end)

		context_menu_speed_up = gtk.MenuItem("Faster [PgUp]")
		context_menu_speed_up.connect("button-press-event", self.do_move_speed_up)
		self.context_menu.add(context_menu_speed_up)

		context_menu_speed_down = gtk.MenuItem("Slower [PgDn]")
		context_menu_speed_down.connect("button-press-event", self.do_move_speed_down)
		self.context_menu.add(context_menu_speed_down)

		context_menu_render_frame = gtk.MenuItem("Render Frame [w]")
		context_menu_render_frame.connect("button-press-event", self.render_frame)
		self.context_menu.add(context_menu_render_frame)

		context_menu_render_anim = gtk.MenuItem("Render Animation [a]")
		context_menu_render_anim.connect("button-press-event", self.do_render_anim)
		self.context_menu.add(context_menu_render_anim)

		context_menu_separator3 = gtk.SeparatorMenuItem()
		self.context_menu.add(context_menu_separator3)

		context_menu_toggle_wavemaker = gtk.CheckMenuItem("Display Wavemaker")
		context_menu_toggle_wavemaker.connect("toggled", self.do_toggle_wavemaker)
		self.context_menu.add(context_menu_toggle_wavemaker)

		context_menu_toggle_beam = gtk.CheckMenuItem("Display Beam")
		context_menu_toggle_beam.connect("toggled", self.do_toggle_beam)
		self.context_menu.add(context_menu_toggle_beam)

		context_menu_toggle_vertices = gtk.CheckMenuItem("Display Vertices")
		context_menu_toggle_vertices.connect("toggled", self.do_toggle_vertices)
		self.context_menu.add(context_menu_toggle_vertices)

		context_menu_toggle_invert = gtk.CheckMenuItem("Invert Comparison")
		context_menu_toggle_invert.connect("toggled", self.do_toggle_invert)
		self.context_menu.add(context_menu_toggle_invert)

		context_menu_separator0 = gtk.SeparatorMenuItem()
		self.context_menu.add(context_menu_separator0)

		context_menu_clear_points = gtk.MenuItem("Clear Points [Esc]")
		context_menu_clear_points.connect("button-press-event", self.do_clear_points)
		self.context_menu.add(context_menu_clear_points)

		context_menu_root_find = gtk.MenuItem("Root Find [R]")
		context_menu_root_find.connect("button-press-event", self.do_root_find)
		self.context_menu.add(context_menu_root_find)
		self.context_menu_root_find = context_menu_root_find
		self.context_menu_root_find.set_sensitive(len(self.points)==2)

		context_menu_separator1 = gtk.SeparatorMenuItem()
		self.context_menu.add(context_menu_separator1)

		context_menu_make_entity = gtk.MenuItem("Make Entity")
		context_menu_make_entity.connect("button-press-event", self.do_make_entity)
		self.context_menu.add(context_menu_make_entity)

		context_menu_points_to_entities = gtk.MenuItem("Points to Entities")
		context_menu_points_to_entities.connect("button-press-event", self.do_points_to_entities)
		self.context_menu.add(context_menu_points_to_entities)

		context_menu_measure = gtk.MenuItem("Measure Entities [M]")
		context_menu_measure.connect("button-press-event", self.do_measure)
		self.context_menu.add(context_menu_measure)
		self.context_menu_measure = context_menu_measure
		self.context_menu_measure.set_sensitive(len(self.entities_get_active())==2)

		context_menu_entities_delete_all = gtk.MenuItem("Delete all Entities")
		context_menu_entities_delete_all.connect("button-press-event", self.do_entities_delete_all)
		self.context_menu.add(context_menu_entities_delete_all)

		context_menu_separator2 = gtk.SeparatorMenuItem()
		self.context_menu.add(context_menu_separator2)

		context_menu_time_series = gtk.MenuItem("Time Series")
		context_menu_time_series.connect("button-press-event", self.time_series_request)
		self.context_menu.add(context_menu_time_series)
		self.context_menu_time_series = context_menu_time_series
		self.context_menu_time_series.set_sensitive(len(self.points)==1)

		self.context_menu.show_all()

		# Entity Context Menu
		self.entity_context_menu = gtk.Menu()

		entity_context_menu_move = gtk.MenuItem("Move")
		entity_context_menu_move.connect("button-press-event", self.do_entity_move)
		self.entity_context_menu.add(entity_context_menu_move)

		entity_context_menu_delete = gtk.MenuItem("Delete")
		entity_context_menu_delete.connect("button-press-event", self.entity_delete)
		self.entity_context_menu.add(entity_context_menu_delete)

		self.entity_context_menu.show_all()

	def do_expose_event(self, event):
		cr = self.window.cairo_create()
		cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height )
		cr.clip()

		self.draw(cr, self.time, self.simlist, self.main_sim, *self.window.get_size())
	
	def adjust_time(self, other, time):
		self.time = time
		for sim in self.simlist : 
			if sim.is_valid() : sim.set_time(time)
		self.queue_draw()
		self.emit("change-time", self.time)
		#self.adjust_frame(self.fs*int(int(time/self.simA.get_dt()+1e-10)/self.fs))

	def update_anim(self):
		if self.get_main_sim() and self.time+self.timestep > self.end :
			end = self.get_main_sim().get_end()
			if end <= self.end :
				gobject.source_remove(self.auto_sid); self.auto = False; return False
			self.end = end

		self.adjust_time(self, self.time+self.timestep)
		self.queue_draw()
		return True

	def do_scroll_event(self, event):
		if event.direction == gtk.gdk.SCROLL_UP:
			if event.state & gtk.gdk.CONTROL_MASK :
				if event.state & gtk.gdk.SHIFT_MASK :
					self.zoom_factor_x /= 1.1
				else:
					self.zoom_factor_y /= 1.1
			else:
				self.scroll_factor *= 1.1;
				self.scroll_center = [event.x, event.y]
		if event.direction == gtk.gdk.SCROLL_DOWN:
			if event.state & gtk.gdk.CONTROL_MASK :
				if event.state & gtk.gdk.SHIFT_MASK :
					self.zoom_factor_x *= 1.1
				else :
					self.zoom_factor_y *= 1.1
			else:
				self.scroll_factor /= 1.1
		if self.scroll_factor < 1 :
			self.scroll_factor = 1
			self.pan_offset = [0.0, 0.0]
		self.queue_draw()

	def do_motion_notify_event(self, event):
		if (self.pan_on) :
			#self.pan_dx = [ event.x - self.pan_center[0], event.y - self.pan_center[1] ]
			self.pan_dx = self.distance_find(event.x - self.pan_center[0], event.y - self.pan_center[1] );
			point1 = self.point_find(event.x, event.y)
			point2 = self.point_find(self.pan_center[0], self.pan_center[1])
			self.pan_dx = [point1[0]-point2[0],point1[1]-point2[1]]
			self.redo_view()
			#self.pan_dx = [ point[0] - self.pan_center[0], point[1] - self.pan_center[1] ]
			self.queue_draw()
			#if (self.point_select_on) :
			#	self.time_series_request(event.x, event.y, self.point_select_run)
		if (self.entity_move_on) :
			loc = self.point_find(event.x, event.y)
			if event.state & gtk.gdk.CONTROL_MASK :
				loc, sim_loc = sim.get_point(loc)
				self.entity_move_entity['sim'] = sim
			self.entity_move_entity['loc'] = loc
			self.emit("info", self.format_point(loc[0],loc[1]) + " [left-click to fix, Ctrl to pin to sim]")
			self.queue_draw()

	def distance_find(self, x, y) :
		geom = self.window.get_geometry(); scwidth = geom[2]; scheight = geom[3]
		x /= self.scroll_factor
		x /= scwidth/float(width+60)
		y /= self.scroll_factor
		y /= scheight/float(height)
		origin = graph_to_plot([0, 0], self.view)
		point = plot_to_graph([x+origin[0], y+origin[1]], self.view)
		return point

	def point_lose(self, x, y) :
		geom = self.window.get_geometry(); scwidth = geom[2]; scheight = geom[3]
		point = graph_to_plot([x, y], self.view)
		point[0] +=  60.0
		point[0] *= scwidth/float(width+60)
		point[0] += -self.scroll_center[0]
		point[0] *= self.scroll_factor
		#point[0] -= self.pan_dpoint[0][0]+self.scroll_center[0]+self.pan_offset[0]
		point[1] *= scheight/float(height+20)
		point[1] *= self.scroll_factor
		point[1] += -self.scroll_center[1]
		#y -= self.pan_dx[1]+self.scroll_center[1]+self.pan_offset[1]
		# y is wrong!!
		#self.redo_view()
		return point

	def do_toggle_beam(self, other) :
		self.broad_plate = other.get_active()
		self.queue_draw()

	def do_toggle_wavemaker(self, other) :
		self.wave = other.get_active()
		self.queue_draw()

	def do_toggle_vertices(self, other) :
		self.vertices = other.get_active()
		self.queue_draw()

	def do_toggle_invert(self, other) :
		self.invert = other.get_active()
		self.queue_draw()

	def do_entity_move(self, other, event) :
		self.entity_move_on = True
		active = self.entities_get_active()
		self.entity_move_entity = active[0]

	def do_entities_delete_all(self, other, event) :
		self.entities = []
		self.queue_draw()

	def entity_delete(self, other, event) :
		for en in self.entities_get_active() : self.entities.remove(en)
		self.context_menu_measure.set_sensitive(len(self.entities_get_active())==2)
		self.queue_draw()

	def point_find(self, x, y) :
		geom = self.window.get_geometry(); scwidth = geom[2]; scheight = geom[3]
		x /= self.scroll_factor
		x -= -self.scroll_center[0]
		x /= scwidth/float(width+60)
		x -=  60.0
		#x -= self.pan_dx[0]+self.scroll_center[0]+self.pan_offset[0]
		y /= self.scroll_factor
		y -= -self.scroll_center[1]
		y /= scheight/float(height+20)
		#y -= self.pan_dx[1]+self.scroll_center[1]+self.pan_offset[1]
		# y is wrong!!
		#self.redo_view()
		point = plot_to_graph([x, y], self.view)
		return point

	def measure(self) :
		active = self.entities_get_active()
		if len(active) != 2 : return 0.0
		return dist(active[0]['loc'], active[1]['loc'])

	def time_series_request(self, other, event) :
		sim = self.get_main_sim()
		if not sim : return

		mode = 1 if event.state & gtk.gdk.CONTROL_MASK else 0
		aname = sim.get_aname()
		#self.simB.get_aname() if event.state & gtk.gdk.SHIFT_MASK else self.simA.get_aname()
		self.point_select_on = True

		#x, y = self.points[0]
		#point = self.point_find(x, y)
		if len(self.points) != 1 : return
		point = self.points[0]
		self.emit("time-series-request", point['loc'][0], mode, aname)# 0.0, 5, 500.0)

	def do_clear_points(self, other = None, event = None) :
		self.points = []
		self.queue_draw()

	def entities_set_active(self, en, active) :
		for eno in self.entities :
			if en == None or en == eno : eno['active'] = active
		self.context_menu_measure.set_sensitive(len(self.entities_get_active())==2)

	def entities_get_active(self) :
		active = []
		for en in self.entities :
			if en['active'] : active.append(en)
		return active

	def point_select(self, event):
		sim = self.get_main_sim()
		if not sim : return
		point = self.point_find(event.x, event.y)
		pointb, sim_loc = sim.get_point(point)
		if not pointb : return

		if not (event.state & gtk.gdk.SHIFT_MASK) : self.points = []
		self.points.append( { 'loc' : pointb, 'sim' : sim, 'col' : \
		  [random.random(),random.random(),random.random()] } )

		self.context_menu_root_find.set_sensitive(len(self.points)==2)
		self.context_menu_time_series.set_sensitive(len(self.points)==1)
		self.queue_draw()

	def format_point(self, x, y):
	        return "(%.3f, %.3f)" % (x, y)

	def do_button_press_event(self, event):
		self.grab_focus()
		if (event.button == 1) :
			
			if self.entity_move_on :
				self.entity_move_on = False
				loc = self.point_find(event.x, event.y)
				self.emit("info", "Entity dropped at "+self.format_point(loc[0], loc[1]))
				return

			for en in self.entities :
			  if dist([event.x,event.y],self.point_lose(en['loc'][0],en['loc'][1])) < 10.0 :
			  	self.entities_set_active(en, not en['active']); self.queue_draw(); return
			self.point_select(event)
		if (event.button == 2) :
			self.pan_on = True
			self.pan_center = [event.x, event.y]
			self.queue_draw()
		if (event.button == 3) :
			for en in self.entities :
			  if dist([event.x,event.y],self.point_lose(en['loc'][0],en['loc'][1])) < 10.0 :
				for eno in self.entities : self.entities_set_active(None, False)
			  	self.entities_set_active(en, True); self.queue_draw()
				self.entity_context_menu.popup(None, None, None, event.button, 0)
				return
			self.target = self.point_find(event.x, event.y)
			self.context_menu.popup(None, None, None, event.button, 0)

	def do_button_release_event(self, event):
		if (event.button == 2) :
			self.pan_on = False
			self.pan_offset[0] += self.pan_dx[0]
			self.pan_offset[1] += self.pan_dx[1]
			self.pan_dx = [0.0, 0.0]
			self.redo_view()
		if (event.button == 3) : self.point_select_on = False

	def render_frame(self, other = None, event = None) :
		im = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
		cr = cairo.Context(im)
		self.draw(cr, self.time, self.simlist, self.main_sim, width, height)
		im.write_to_png("test.png")

	def do_sim_property_change(self, sim, prop, val, aname) :
		#sims.set_siml(self.siml, self.simA, self.comp, self.simB)
		if sim == self.get_main_sim() and prop == 'dt' :
			self.timestep = float(val)
		self.queue_draw()

	def render_anim(self) :
		#siml = list(self.siml)
		t = self.begin
		sequence = []
		while ( t <= self.end ):
			#self.emit("process-time", t)
			im = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
			cr = cairo.Context(im)
			tmp_simA = sims.Sim(self.get_main_sim().get_run(), t, ['left', 'right', 'plate1'])
			tmp_simA.change_rgb_colour([0.1,0.1,0.1])
			tmp_simA.set_aname_nice("4m init. elev.")
			#tmp_simB = sims.Sim(self.simB.get_run(), t+self.simB.get_time()-self.simA.get_time(), ['left', 'right', 'plate1'])\
			#	if self.simB else None
			#sims.set_siml(siml, tmp_simA, comp, tmp_simB)
			self.draw(cr, t, [tmp_simA], tmp_simA.get_run(), width, height)
			pil_im = Image.frombuffer("RGBA", (im.get_width(), im.get_height()), im.get_data(), "raw", "RGBA",0,1)
			pil_im = pil_im.convert("P")
			sequence.append(pil_im)
			t += self.timestep
			print t
		self.emit("process-time-done")
		fp = open("out.gif", "wb")
		gifmaker.makedelta(fp, sequence)
		fp.close()

	def do_move_home(self, other=None, event=None) :
		self.adjust_time(self, 0)

	def do_move_end(self, other=None, event=None) :
		sim = self.get_main_sim()
		if sim : self.end = sim.get_end()
		self.adjust_time(self, self.end)

	def do_move_speed_up(self, other=None, event=None) :
		self.timestep *= 2
		#self.adjust_time(self.ts * int(self.simA.get_time()/self.ts+1e-10))

	def do_move_speed_down(self, other=None, event=None) :
		self.timestep = self.timestep/2.0

	def do_anim(self, other=None, event=None) :
		self.auto = not self.auto
		if self.auto :
			self.auto_sid = gobject.timeout_add(self.auto_delay, self.update_anim)
		else :
			gobject.source_remove(self.auto_sid)

	def do_render_anim(self, other=None, event=None) :
		render_anim_thread = threading.Thread(None, self.render_anim)
		#render_anim_thread.start()
		self.render_anim()

	def do_make_entity(self, other=None, event=None) :
		self.entities_add(self.target)

	def do_points_to_entities(self, other=None, event=None) :
		for pt in self.points :
			self.entities_add(pt['loc'], pt['sim'])
		self.points = []
		self.queue_draw()

	def do_measure(self, other=None, event=None) :
		self.emit("info", "Distance between active entities: " + str(self.measure()))

	def entities_add(self, loc, sim=None, active = False) :
		en = self.entities.append({'loc' : loc, 'sim' : sim, 'active' : active})
		self.entities_set_active(en, active)
		self.queue_draw()

	def do_root_find(self, other=None, event=None) :
		if len(self.points) < 2 : return

		#simh = open(self.simA.get_files()[self.points[0]['sim']], 'r')
		#xvals, yvals = load_sim(simh)
		point_set = self.points[0]['sim'].get_point_set(self.points[0]['loc'])
		xvals, yvals = zip(*point_set['point_set'])
		simf = scipy.interpolate.interp1d(xvals, yvals, 'quadratic')
		root = scipy.optimize.brentq(simf, self.points[0]['loc'][0], self.points[1]['loc'][0])
		self.emit("info", "Root found: " + str(root))

		self.entities_add([root, 0.0], self.points[0]['sim'])
		self.queue_draw()

	def do_key_press_event(self, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
		m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
		mod = 10.0 if m_control else 1.0
		if keyname == "Right" :
			if self.time+self.timestep*mod > self.end and self.get_main_sim() :
				self.end = self.get_main_sim().get_end()
			if self.time+self.timestep*mod > self.end : return True
			self.adjust_time(self, self.time+ self.timestep*mod)
		if keyname == "Left" :
			if self.time-self.timestep*mod < self.begin : return True
			self.adjust_time(self, self.time - self.timestep*mod)
		if keyname == "Home" : self.do_move_home()
		if keyname == "End" : self.do_move_end()
		if keyname == "Escape" : self.do_clear_points()
		if keyname == "Page_Up" : self.do_move_speed_up()
		if keyname == "Page_Down" : self.do_move_speed_down()
		if keyname == "w" : self.render_frame()
		if keyname == "W" :
			self.wave = not self.wave; self.queue_draw()
		if keyname == "a" : self.do_render_anim()
		if keyname == "M" : self.do_measure()
		if keyname == "R" : self.do_root_find()
		if keyname == "p":
			self.broad_plate = not self.broad_plate
			self.queue_draw()
		if keyname == "i":
			self.invert = not self.invert
			self.queue_draw()
		if keyname == "v":
			self.vertices = not self.vertices
			self.queue_draw()
		if keyname == "r":
			self.timestep = -self.timestep
		if keyname == "space" : self.do_anim()
		#sims.set_siml(self.siml, self.runA, self.timeA, self.comp, self.runB, self.timeB)
		#self.queue_draw()
		return True
	
	def redo_view(self) :
		ofx = self.pan_dx[0] + self.pan_offset[0]; ofy = self.pan_dx[1] + self.pan_offset[1]
		self.view = [ self.zoom_factor_x*self.gview[0]-ofx, self.zoom_factor_x*self.gview[1]-ofx, \
			self.zoom_factor_y*self.gview[2]-ofy, self.zoom_factor_y*self.gview[3]-ofy ]

	def draw(self, cr, time, simlist, main_sim, swidth, sheight):
		geom = self.window.get_geometry(); scwidth = geom[2]; scheight = geom[3]
		cr.translate(self.scroll_center[0], self.scroll_center[1])
		cr.scale(self.scroll_factor, self.scroll_factor)
		cr.translate(-self.scroll_center[0], -self.scroll_center[1])
		cr.scale(scwidth/float(width+60), scheight/float(height+20))
		cr.translate(60, 0)
		#cr.translate(self.pan_dx[0]+self.pan_offset[0], self.pan_dx[1]+self.pan_offset[1])
		self.redo_view()
		dorender_cr(cr, self.view, time, simlist, main_sim, self.comp, self.plotref, self.left1, self.left2, self.vertices, self.plateside, self.wave, \
		  self.fabien_file, self.broad_plate, self.points, self.entities)
		cr.translate(self.scroll_center[0], self.scroll_center[1])
		

def plot_to_graph(point, window):
	ppt = []
	ppt.append((window[1] - window[0])*float(point[0])/width + window[0])
	ppt.append((window[2] - window[3])*float(point[1])/height + window[3])
	return ppt

def graph_to_plot(point, window):
	ppt = []
	ppt.append((window[0] - float(point[0]))*width/(window[0] - window[1]))
	ppt.append((window[3] - float(point[1]))*height/(window[3] - window[2]))
	return ppt

def plotplate_cr(cr, window, handle, colour, draft, thickness):
	leftlines = handle.readlines()
	lastpoint = len(leftlines)-1

	#pointb = leftlines[1].strip().split(',') #; pointb = graph_to_plot(pointb, window)
	#pointb[1] = float(pointb[1])+0.2
	#pointb = graph_to_plot(pointb, window)
	#pointb = [ float(pointb[0]),float(pointb[1]) ]

	leftlines[1] = leftlines[1].strip()
	pointb = leftlines[1].split(',')
	left = pointb[0]
	if left.find('.')>=-1 : left = left.strip('0')
	if (left[len(left)-1] == '.') : left = left + '0'
	pointb[1] = float(pointb[1])+(thickness-draft)
	pointb = graph_to_plot(pointb, window)
	cr.move_to(pointb[0], pointb[1])
	#string3 = '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1])+'" x2="'+ \
	#	str(pointb[0])+'" y2="'+str(pendsy)+'" style="stroke:#888888;stroke-width:1.0;stroke-dasharray:9,5"/>\n'
	#string3 = string3 + '<text stroke="none" fill="#888888" x="'+str(pointb[0])+'" y="'+str(pendsy-10)+'" text-anchor="middle">'+left+'</text>\n'

	for i in range(1,lastpoint+1):
		#pointa = pointb
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		pointb[1] = float(pointb[1])+(thickness-draft)
		pointb = graph_to_plot(pointb, window)#; pointb[1] += 0.2
		cr.line_to(pointb[0], pointb[1])
		#string += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		#string2 += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		#string = string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1]+0.2)+\
		#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]+0.2)+'"/>\n'
	#string = string + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1]+0.2)+\
	#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]-2)+'"/>\n'

	right = leftlines[lastpoint].split(',')[0]
	if right.find('.')>=-1 : right = right.strip('0')
	if (right[len(right)-1] == '.') : right = right + '0'
	#string3 = string3 + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1])+'" x2="'+ \
	#	str(pointb[0])+'" y2="'+str(pendsy)+'" style="stroke:#888888;stroke-width:1.0;stroke-dasharray:9,5"/>\n'
	#string3 = string3 + '<text stroke="none" fill="#888888" x="'+str(pointb[0])+'" y="'+str(pendsy-10)+'" text-anchor="middle">'+right+'</text>\n'

	for i in range(1,lastpoint+1):
		#pointa = pointb
		pointb = leftlines[lastpoint+1-i].split(',')
		pointb[1] = float(pointb[1])-draft
		pointb = graph_to_plot(pointb, window)
		#string += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		cr.line_to(pointb[0], pointb[1])
		#string = string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1]-2)+\
		#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]-2)+'"/>\n'
	#string = string + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1]-2)+\
	#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]+0.2)+'"/>\n'
	cr.close_path()
	cr.set_source_rgba(colour[0], colour[1], colour[2], 0.5); cr.fill_preserve()
	cr.set_source_rgba(colour[0], colour[1], colour[2], 1.0); cr.stroke()
	#string += '" opacity=".5" fill="#AAAAFF"/>\n'
	#string2 += '" style="fill:none;stroke:'+colour+';stroke-width:2.0"/>\n'
	#return string+string2+string3

def plotplate(handle, colour, draft, thickness):
	leftlines = handle.readlines()
	lastpoint = len(leftlines)-1

	#pointb = leftlines[1].strip().split(',') #; pointb = graph_to_plot(pointb, window)
	#pointb[1] = float(pointb[1])+0.2
	#pointb = graph_to_plot(pointb, window)
	#pointb = [ float(pointb[0]),float(pointb[1]) ]
	string = '<polygon points="'
	string2 = '<polyline points="'

	leftlines[1] = leftlines[1].strip()
	pointb = leftlines[1].split(',')
	left = pointb[0];
	if left.find('.')>=-1 : left = left.strip('0')
	if (left[len(left)-1] == '.') : left = left + '0'
	pointb[1] = float(pointb[1])+(thickness-draft)
	pointb = graph_to_plot(pointb, window)
	string3 = '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1])+'" x2="'+ \
		str(pointb[0])+'" y2="'+str(pendsy)+'" style="stroke:#888888;stroke-width:1.0;stroke-dasharray:9,5"/>\n'
	string3 = string3 + '<text stroke="none" fill="#888888" x="'+str(pointb[0])+'" y="'+str(pendsy-10)+'" text-anchor="middle">'+left+'</text>\n'

	for i in range(1,lastpoint+1):
		#pointa = pointb
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		pointb[1] = float(pointb[1])+(thickness-draft)
		pointb = graph_to_plot(pointb, window)#; pointb[1] += 0.2
		string += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		string2 += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		#string = string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1]+0.2)+\
		#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]+0.2)+'"/>\n'
	#string = string + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1]+0.2)+\
	#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]-2)+'"/>\n'


	right = leftlines[lastpoint].split(',')[0]
	if right.find('.')>=-1 : right = right.strip('0')
	if (right[len(right)-1] == '.') : right = right + '0'
	string3 = string3 + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1])+'" x2="'+ \
		str(pointb[0])+'" y2="'+str(pendsy)+'" style="stroke:#888888;stroke-width:1.0;stroke-dasharray:9,5"/>\n'
	string3 = string3 + '<text stroke="none" fill="#888888" x="'+str(pointb[0])+'" y="'+str(pendsy-10)+'" text-anchor="middle">'+right+'</text>\n'

	for i in range(1,lastpoint+1):
		#pointa = pointb
		pointb = leftlines[lastpoint+1-i].split(',')
		pointb[1] = float(pointb[1])-draft
		pointb = graph_to_plot(pointb, window)
		string += str(pointb[0]) + ',' + str(pointb[1]) + ' '
		#string = string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1]-2)+\
		#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]-2)+'"/>\n'
	#string = string + '<line x1="'+str(pointb[0])+'" y1="'+str(pointb[1]-2)+\
	#	'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1]+0.2)+'"/>\n'
	string += '" opacity=".5" fill="#AAAAFF"/>\n'
	string2 += '" style="fill:none;stroke:'+colour+';stroke-width:2.0"/>\n'
	return string+string2+string3

def plotdiff_cr(cr, window, handle, ref, scale = 1.0):
	global invert
	leftlines = handle.readlines()
	reflines = ref.readlines()
	lastpoint = len(leftlines)-1
	rlastpoint = len(reflines)-1

	#pointb = leftlines[1].strip().split(',') #; pointb = graph_to_plot(pointb, window)
	#pointb = graph_to_plot(pointb, window)
	j = 2
	i = 1
	leftlines[i] = leftlines[i].strip()
	pointb = leftlines[i].split(',')
	pointr = reflines[j].split(',')
	while float(pointr[0]) < float(pointb[0]) and j < rlastpoint-1 :
		j += 1
		pointr = reflines[j].split(',')
	q = float(pointb[0])
	pointr = reflines[j].split(','); r = float(pointr[0])
	points = reflines[j+1].split(','); s = float(points[0])
	t = ((q-r)/(s-r))*(float(points[1]) - float(pointr[1])) + float(pointr[1]) - float(pointb[1])
	point = [ pointb[0], t*scale ]
	point = graph_to_plot(point, window)
	cr.move_to(point[0], point[1])

	for i in range(2,lastpoint+1):
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		pointr = reflines[j].split(',')
		while float(pointr[0]) < float(pointb[0]) and j < rlastpoint :
			j += 1
			pointr = reflines[j].split(',')
		q = float(pointb[0])
		pointr = reflines[j].split(','); r = float(pointr[0])
		points = reflines[j+1].split(','); s = float(points[0])
		if invert : points[1] = -float(points[1]); pointr[1] = -float(pointr[1])
		t = ((q-r)/(s-r))*(float(points[1]) - float(pointr[1])) + float(pointr[1]) - float(pointb[1])
		point = [ pointb[0], t*scale ]
		point = graph_to_plot(point, window)
		cr.line_to(point[0], point[1])
		#string += str(point[0])+','+str(point[1])+' ' # string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1])+\
			#'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1])+'"/>\n'
	#string += '" style="fill:none"/>\n'
	cr.stroke()
	return string

def load_sim(handle):
	leftlines = handle.readlines()
	lastpoint = len(leftlines)-1

	sim_vals_x = []; sim_vals_y = []
	for i in range(1,lastpoint+1):
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		if len(pointb) == 1 : pointb = leftlines[i].split(' ')
		sim_vals_x.append(float(pointb[0])); sim_vals_y.append(float(pointb[1]))
	return (sim_vals_x, sim_vals_y)

def plotdiff(handle, ref, scale = 1.0):
	leftlines = handle.readlines()
	reflines = ref.readlines()
	lastpoint = len(leftlines)-1
	rlastpoint = len(reflines)-1

	#pointb = leftlines[1].strip().split(',') #; pointb = graph_to_plot(pointb, window)
	#pointb = graph_to_plot(pointb, window)
	string = '<polyline points="'
	j = 2
	for i in range(2,lastpoint+1):
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		pointr = reflines[j].split(',')
		while float(pointr[0]) < float(pointb[0]) and j < rlastpoint-1 :
			j += 1
			pointr = reflines[j].split(',')
		q = float(pointb[0])
		pointr = reflines[j].split(','); r = float(pointr[0])
		points = reflines[j+1].split(','); s = float(points[0])
		t = ((q-r)/(s-r))*(float(points[1]) - float(pointr[1])) + float(pointr[1]) - float(pointb[1])
		point = [ pointb[0], t*scale ]
		point = graph_to_plot(point, window)
		string += str(point[0])+','+str(point[1])+' ' # string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1])+\
			#'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1])+'"/>\n'
	string += '" style="fill:none"/>\n'
	return string

def plotsim_cr(cr, sim, window, scale = 1.0, voff = 0.0, hscale = 1.0, hoff = 0.0, rectify = False, vertices = False):
	for point_set in sim.get_point_sets() :
		if not point_set['extent'] : continue
		points = point_set['point_set']
		pointb = list(points[0])
		pointb[1] = pointb[1]*scale
		pointb = graph_to_plot(pointb, window)
		cr.move_to(hscale*(pointb[0])+hoff, pointb[1]+voff)
	
		for i in range(1,len(points)):
			pointb = list(points[i])
			pointb[1] = float(pointb[1])*scale
			pointb[0] = float(pointb[0])*hscale
			#pointb[1] = (-1 if invert == True else 1) * float(pointb[1])*scale
			pointb = graph_to_plot(pointb, window)
			if (rectify and i == 1): refpt = pointb[0]
			if vertices:
				cr.move_to((pointb[0])+hoff,pointb[1]+voff)
				cr.rel_line_to(0,4)
				cr.rel_line_to(1,0)
				cr.rel_line_to(0,-8)
				cr.rel_line_to(-1,0)
				cr.close_path()
				cr.fill()
			else:
				cr.line_to(hscale*(pointb[0])+hoff,pointb[1]+voff)
	
	#if vertices:
	#	stringend = ';stroke:none" marker-mid="url(#Triangle)"/>\n'
	#else:
	#	stringend = '"/>\n'
	cr.stroke()
def plotfile_cr(cr, window, handle, scale = 1.0, voff = 0.0, hscale = 1.0, hoff = 0.0, rectify = False, vertices = False):
	leftlines = handle.readlines()
	lastpoint = len(leftlines)-1

	refpt = 0.0

	leftlines[1] = leftlines[1].strip()
	pointb = leftlines[1].split(',')
	if len(pointb) == 1 : pointb = leftlines[i].split(' ')
	pointb[1] = float(pointb[1])*scale
	pointb = graph_to_plot(pointb, window)
	cr.move_to(hscale*(pointb[0]-refpt)+hoff, pointb[1]+voff)
	if vertices : cr.set_source_rgb(0.0, 0.0, 0.0)

	for i in range(2,lastpoint+1):
		#pointa = pointb
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		if len(pointb) == 1 : pointb = leftlines[i].split(' ')
		pointb[1] = float(pointb[1])*scale
		pointb[0] = float(pointb[0])*hscale
		#pointb[1] = (-1 if invert == True else 1) * float(pointb[1])*scale
		pointb = graph_to_plot(pointb, window)
		if (rectify and i == 1): refpt = pointb[0]
		if vertices:
			cr.move_to((pointb[0]-refpt)+hoff,pointb[1]+voff)
			cr.rel_line_to(0,4)
			cr.rel_line_to(1,0)
			cr.rel_line_to(0,-8)
			cr.rel_line_to(-1,0)
			cr.close_path()
			cr.fill()
		else:
			cr.line_to(hscale*(pointb[0]-refpt)+hoff,pointb[1]+voff)

	#if vertices:
	#	stringend = ';stroke:none" marker-mid="url(#Triangle)"/>\n'
	#else:
	#	stringend = '"/>\n'
	cr.stroke()

def plotfile(handle, scale = 1.0, voff = 0.0, hscale = 1.0, hoff = 0.0, rectify = False, vertices = False):
	leftlines = handle.readlines()
	lastpoint = len(leftlines)-1

	#pointb = leftlines[1].strip().split(',') #; pointb = graph_to_plot(pointb, window)
	#pointb = graph_to_plot(pointb, window)
	string = '<polyline points="'

	refpt = 0.0
	for i in range(1,lastpoint+1):
		#pointa = pointb
		leftlines[i] = leftlines[i].strip()
		pointb = leftlines[i].split(',')
		if len(pointb) == 1 : pointb = leftlines[i].split(' ')
		pointb[1] = float(pointb[1])*scale
		pointb = graph_to_plot(pointb, window)
		if (rectify and i == 1): refpt = pointb[0]
		string += str(hscale*(pointb[0]-refpt)+hoff)+','+str(pointb[1]+voff)+' ' # string + '<line x1="'+str(pointa[0])+'" y1="'+str(pointa[1])+\
			#'" x2="'+str(pointb[0])+'" y2="'+str(pointb[1])+'"/>\n'
	if vertices:
		stringend = ';stroke:none" marker-mid="url(#Triangle)"/>\n'
	else:
		stringend = '"/>\n'

	string += '" style="fill:none' + stringend
	return string

def plateparams(loc):
	print loc

def doaxes_cr(cr, window, comp, plotref, let1, left2, vertices, plateside):
	cr.set_source_rgb(0.0, 1.0, 0.0); cr.set_line_width(1.0)
	
	# Axes
	origin = graph_to_plot([0.0,0.0], window)
	xstart = graph_to_plot([window[0],0.0], window)
	ystart = graph_to_plot([0.0,window[2]], window)
	xend = graph_to_plot([window[1],0.0], window)
	yend = graph_to_plot([0.0,window[3]], window)
	cr.set_source_rgb(0.5, 0.5, 0.5); cr.set_line_width(0.4)
	cr.set_font_size(24);
	leftend = origin[0] if origin[0]>xstart[0] else xstart[0]
	cr.move_to(leftend-40, (ystart[1]+yend[1])*0.5+70)
	cr.rotate(-90*math.pi/4)
	cr.show_text(u'Displacement, \u03B6 (m)')
	cr.rotate(90*math.pi/4)
	
	gtic = int((window[3]-window[2])/10**(math.floor(math.log10(window[3]-window[2]))))*10.0**(math.floor(math.log10(window[3]-window[2])))/10.0
	i = int(window[2]/gtic)
	cr.set_font_size(18)
	while i*gtic < window[3]:
		point = graph_to_plot([0,gtic*i], window)
		point[0] = leftend
		cr.move_to(point[0]-5, point[1]); cr.line_to(point[0], point[1])
		if i%2 == 0:
			cr.move_to(point[0]-8, point[1]+4)
			cr.show_text(str(gtic*i))
		i+=1
	gtic = int((window[1]-window[0])/10**(int(math.log10(window[1]-window[0]))-1))*10.0**(int(math.log10(window[1]-window[0]))-1)/20.0
	#gtic = 30/12.0
	i = int(window[0]/gtic)
	#for i in range(1,20):
	while i*gtic < window[1]:
		point = graph_to_plot([gtic*i,0], window)
		cr.move_to(point[0], point[1]); cr.line_to(point[0], point[1]+5)
		if i%2 == 0:
			cr.move_to(point[0]-15, point[1]+20)
			cr.show_text(str(gtic*i))
		i+=1

	cr.move_to(xend[0]-80, xend[1]+80)
	cr.set_font_size(24)
	cr.show_text("x (m)")

	cr.move_to(xstart[0], xstart[1]); cr.line_to(xend[0], xend[1])
	cr.move_to(leftend, ystart[1]); cr.line_to(leftend, yend[1])
	cr.stroke()

def dorender_cr(cr, window, primary_time, simlist, main_sim_ind, comp, plotref, left1, left2, vertices, plateside, wave, fabien_file, broad_plate = True, highlighted = [], entities = []):
	fabien = fabien_file != None

	cr.set_source_rgb(1.0, 1.0, 1.0)

	cr.rectangle(-60, 0, width+60, height+20); cr.fill()

	doaxes_cr(cr, window, comp, plotref, left1, left2, vertices, plateside)
	
	if plotref :
		i = len(simlist)
		if simlist[i].get_aname() == main_sim_ind : i -= 1
		refsim = simlist[i]
	
	time = str(primary_time) + 's'
	if comp :
		for sim in simlist :
			t2 = sim.get_time()
			if abs(primary_time - t2) > 1e-10 :
				time +=  ', ' + str(t2) + 's (' + name[1] + ')'
	
	cr.move_to(10, height+10); cr.set_font_size(20); cr.set_source_rgb(0.0, 0.5, 0.0)
	cr.show_text('Time '+time)
	
	# We take the first given parameter set for the global variables (e.g. Dt)
	out = ''
	legrows = []
	i = 0
	cr.set_line_width(2.0)
	if fabien and os.path.exists(fabien_file) :
		cr.set_source_rgb(0.0, 0.0, 0.0)
		fabien = open(fabien_file, 'r')
		main_sim = True
		plotfile_cr(cr, window, fabien)
		main_sim = False
	for sim in simlist:
		if not sim.is_valid() : continue
		#plates = sim.params['platect']
		main_sim = True if i==0 else False
		#if int(plates)>0 :
		#	pparams = sims.parse_params(sim.params['plate'], False)
		#	draft = float(pparams['draft']); thickness = float(pparams['h'])
		legrow = []
		files = sim.get_files()
		rgb_colour = sim.get_rgb_colour()
		cr.set_source_rgb(*rgb_colour)
		if (sim.is_valid()) :
			plotsim_cr(cr, sim, window)
			legrow.append(sim.get_rgb_colour())
		if left1 and os.path.exists(files['left1']) :
			cr.set_source_rgb(0.0, 0.0, 0.0)
			left1h = open(files['left1'], 'r')
			plotfile_cr(cr, window, left1h)
		if wave and os.path.exists(files['wave']) :
			cr.set_source_rgb(0.5, 1.0, 1.0)
			waveh = open(files['wave'], 'r')
			plotfile_cr(cr, window, waveh, 1.0, 0.0)
		if plateside and os.path.exists(files['plate1side']) :
			cr.set_source_rgb(1.0, 0.5, 1.0)
			platesideh = open(files['plate1side'], 'r')
			plotfile_cr(cr, window, platesideh, 1.0, 0.0, 300.0, 100, True)
		if left2 and os.path.exists(files['left2']) and os.path.exists(files['left4']) :
			scale = 1.0
			left2h = open(files['left2'], 'r')
			left4h = open(files['left4'], 'r')
			plotfile_cr(cr, window, left4h, scale)
			plotfile_cr(cr, window, left2h, scale)
			scale = 5.0
			left2h = open(files['left2'], 'r')
			left4h = open(files['left4'], 'r')
			plotdiff_cr(cr, window, left2h, left4h, scale)
		#if int(plates)>0 and os.path.exists(files['plate1']) :
		if os.path.exists(files['plate1']) :
			plate1 = open(files['plate1'], 'r')
			plate_colour = list(rgb_colour)
			for n in [0,1,2] : plate_colour[n] *= 1.3
			if broad_plate :
				plotplate_cr(cr, window, plate1, plate_colour, draft, thickness)
			plate1 = open(files['plate1'], 'r')
			cr.set_source_rgb(*plate_colour)#[0], plate_colour[1], plate_colour[2])
			cr.set_line_width(4*cr.get_line_width())
			plotfile_cr(cr, window, plate1)
			for n in [0,1,2] : plate_colour[n] /= 1.3
			cr.set_source_rgb(*plate_colour)#[0], plate_colour[1], plate_colour[2])
			cr.set_line_width(0.25*cr.get_line_width())
		if vertices and os.path.exists(files['leftp']) :
			verticesh = open(files['leftp'], 'r')
			plotfile_cr(cr, window, verticesh, 1.0, 0.0, 1.0, 0, False, True)
		legrows.append(legrow)
		cr.move_to(width - 200, 95+20*i)
		cr.set_source_rgb(*rgb_colour)#[0],rgb_colour[1],rgb_colour[2])
		cr.rel_line_to(20, 0)
		cr.stroke()
		cr.move_to(width - 175, 100+20*i)
		cr.set_source_rgb(0,0,0)
		cr.show_text(sim.get_aname_nice())
		cr.stroke()
	
		i = i + 1
	i = 0
	for hl in highlighted :
		hlp = graph_to_plot(hl['loc'], window)
		cr.arc(hlp[0], hlp[1], 5.0, 0, 2*math.pi)
		cr.set_source_rgb(0.0, 0.0, 0.0)
		cr.stroke_preserve()
		cr.set_source_rgb(*hl['col'])#[0], hl['col'][1], hl['col'][2])
		cr.fill()
		i += 1
	cr.set_line_width(4*cr.get_line_width())
	for en in entities :
		if en['active'] : cr.set_source_rgb(1.0, 0.0, 0.0)
		else : cr.set_source_rgb(0.5, 0.5, 0.5)
		enp = graph_to_plot(en['loc'], window)
		cr.move_to(enp[0]-2.5, enp[1]-2.5); cr.line_to(enp[0]+2.5, enp[1]+2.5)
		cr.move_to(enp[0]-2.5, enp[1]+2.5); cr.line_to(enp[0]+2.5, enp[1]-2.5)
		cr.stroke()
		i += 1
	cr.set_line_width(0.25*cr.get_line_width())
	
	if plotref :
		files = simlist[0].get_files()
		left = open(files['left'], 'r')
		right = open(files['right'], 'r')
		ref = open(refsim.get_files()['left'], 'r')
		rrgb_colour = refsim.get_rgb_colour()
		cr.set_source_rgb(*rrgb_colour)#[0],rrgb_colour[1],rrgb_colour[2])
		plotdiff_cr(cr, window, left, ref)

class SimScape(gtk.Frame, aobject.AObject):
	plot_widget = None

	def __init__(self, env = None, aes = None):
		gtk.Frame.__init__(self)
		aobject.AObject.__init__(self, "SimScape", env, view_object = True)
	
	def __del__(self) :
		aobject.AObject.__del__(self)

	def get_new_plot_window(self, comp, plotref, runA, runB, timeA, timeB, left1, fabien_file, plateside, vertices, left2):

		global gleft, gright, gbottom, gtop
		gview = [gleft, gright, gbottom, gtop]

		simlist = []
		if runA != None :
			simA = sims.Sim( runA, timeA, ['left','right','plate1'] )
			timestep = simA.get_timestep()
			simlist.append(simA)
		if timeB : simlist.append(sims.Sim( runB, timeB, ['left','right','plate1'] ))
	
		if comp==True:
		 siml = [ \
		 {'left' : 'left-1.csv', 'left1' : 'left1-1.csv', 'left2' : 'left2-1.csv', 'leftp' : 'leftp-1.csv', 'left4' : 'left4-1.csv', 'wave' : 'wave-1.csv', 'plate1side' : 'plate1side-1.csv', 'right' : 'right-1.csv', 'plate1' : 'plate1-1.csv', 'rgb_colour' : [0,1.0,0], 'colour' : 'green', 'hl' : 'red', 'params' : 'parameters-1.tmp'}, \
		 {'left' : 'left-2.csv', 'left1' : 'left1-2.csv', 'left2' : 'left2-2.csv', 'leftp' : 'leftp-2.csv', 'left4' : 'left4-2.csv', 'wave' : 'wave-2.csv', 'plate1side' : 'plate1side-2.csv', 'right' : 'right-2.csv', 'plate1' : 'plate1-2.csv', 'rgb_colour' : [0,0.0,1.0], 'colour' : 'blue', 'hl' : 'orange', 'params' : 'parameters-2.tmp' } \
		 ]
		else:
		 siml = [ {'rgb_colour' : [0,1.0,0], 'colour' : 'green', 'hl' : 'red', 'left' : 'left.csv', 'left1' : 'left1.csv', 'left2' : 'left2.csv', 'leftp' : 'leftp.csv', 'left4' : 'left4.csv', \
		   'wave' : 'wave.csv', 'plate1side' : 'plate1side.csv', 'right' : 'right.csv', 'plate1' : 'plate1.csv', 'params' : 'parameters.tmp'} ]
			
		frames = []
		output_file = ''
	
		#T = simA.get_end()
		#firstleft = open('output.'+runA+'/left-000000.csv', 'r'); firstleftlines = firstleft.readlines()
		#gleftarr = firstleftlines[1].split(','); gleft = float(gleftarr[0])
		#grightarr = firstleftlines[len(firstleftlines)-1].split(','); gright = float(grightarr[0])
		#if os.path.exists('output.'+runA+'/right-%06d.csv' % T) :
		#	firstright = open('output.'+runA+'/right-000000.csv', 'r'); firstrightlines = firstright.readlines()
		#	grightarr = firstrightlines[len(firstrightlines)-1].split(','); gright = float(grightarr[0])
	
		vbox = gtk.VBox()
		hbox = gtk.HBox()
	
		da = PlotWidget(self.get_aenv())
		self.plot_widget = da

		da.show(); vbox.pack_start(da)
	
		tl = TimeLineWidget(0, 100, 0.5)
		if runA != None : tl.set_time(None, timeA)
		tl.show_all()
		tl_conn = da.connect("change-time", tl.set_time)
		tl_conn = da.connect("process-time", tl.set_process_time)
		tl_conn = da.connect("process-time-done", tl.hide_process_time)
		tlst_conn = tl.connect("selected-time", da.adjust_time)

		da.setup(simlist, comp, gview, vertices, False, fabien_file, plateside, plotref, left1, left2)
		#dalog_conn = da.connect("logger", lambda o, n, s : self.emit('logger', n, s))
		self.absorb_properties(da)
		vbox.pack_start(tl, False)
	
		tab = gtk.Toolbar()
		ta = OverTimeWidget(0, 100);
		tab_hide = gtk.ToolButton(gtk.STOCK_QUIT); tab_hide.set_label("Hide"); \
			tab.insert(tab_hide, 0); tab_hide.connect("clicked", (lambda other: hbox.hide()))
		tab_fft = gtk.ToggleToolButton(gtk.STOCK_REFRESH); tab_fft.set_label("FFT"); \
			tab.insert(tab_fft, 1); tab_fft.connect("toggled", ta.do_fft_toggle)
		tab_fft = gtk.ToggleToolButton(gtk.STOCK_PRINT); tab_fft.set_label("Output"); \
			tab.insert(tab_fft, 1); tab_fft.connect("toggled", ta.do_write)
		tab.set_orientation(gtk.ORIENTATION_VERTICAL)
		hbox.pack_start(tab)
		hbox.pack_start(ta)
		tab.show_all(); ta.show(); hb_conn = ta.connect("loaded-time-series", (lambda other, run, point: hbox.show()))
		vbox.pack_start(hbox)
	
		ts_conn = da.connect("time-series-request", ta.load_time_series)
		#ps_conn = da.connect("point-select", status.display_point_select)
		ps_conn = ta.connect("loaded-time-series", self.aes_append_status)
		ds_conn = da.connect("info", self.aes_append_status)
	
		vbox.show()
		self.add(vbox)
		self.show()

	def print_out(self, op, pc, pn) :
	        w = pc.get_width(); h = pc.get_height()
		c = pc.get_cairo_context()
		p = self.plot_widget
		p.draw(c, p.time, p.simlist, p.main_sim, w, h)
