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
from ..aobject import *

class GlancerLegend(AObject) :
    legend = None
    font = None

    def get_useful_vars(self) :
        return {
                 'legend' : 'mpl Legend',
               }

    def __init__ (self, legend, queue_draw, env=None):
        self.legend = legend
        self.queue_draw = queue_draw
        AObject.__init__(self, "GlancerLegend", env, elevate = False)

    #PROPERTIES
    def get_aesthete_properties(self):
        return { 'loc' : [None, self.get_loc, False],
                 'font' : [self.change_font, self.get_font, True] }
    #BEGIN PROPERTIES FUNCTIONS
    def get_loc(self, val=None) : return self.legend._loc if val==None else val
    def change_font(self, val) : 
        texts = self.legend.get_texts()
        for text in texts :
            label_props = text.get_fontproperties()
            font_to_mpl(label_props, val)
        self.queue_draw()
    def get_font(self, val=None) :
        if val is not None : return val

        texts = self.legend.get_texts()
        if len(texts) < 1 :
            return ''
        label_props = texts[0].get_fontproperties()
        return mpl_to_font(label_props)
    #END PROPERTIES FUNCTIONS
