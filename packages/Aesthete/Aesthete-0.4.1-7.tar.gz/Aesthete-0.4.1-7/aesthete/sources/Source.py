import re
import sympy
import pickle
from aobject.utils import debug_print
import numpy
import gobject
import gtk
import os
import random
from ..glypher import Dynamic
from aobject.aobject import AObject, aname_root_catalog, AOBJECT_CAN_NONE, string_to_int_tup
from ..tablemaker import *

class Source (AObject) :
    reloadable = False
    needs_x_range = False
    needs_resolution = False

    def get_auto_aesthete_properties(self) :
        return {
            'domain_cols' : (string_to_int_tup, (AOBJECT_CAN_NONE,)),
            'range_cols' : (string_to_int_tup, (AOBJECT_CAN_NONE,)),
            'time_cols' : (string_to_int_tup, (AOBJECT_CAN_NONE,)),
        }

    def __init__(self, stem, env = None, show = False, reloadable = False, needs_x_range = False) :
        self.add_me("Source")
        self.reloadable = reloadable
        self.needs_x_range = needs_x_range
        AObject.__init__(self, stem, env, show)
    def source_set_x_range(self, x_range) :
        self.x_range = x_range
    def source_get_values(self, time=None, multi_array=False, x_range=None,
                          resolution=None) :
        pass # MUST OVERRIDE!!
    def source_get_max_dim(self) :
        pass # MUST OVERRIDE!!
    def source_type(self) :
        pass # MUST OVERRIDE!!
    def source_reload(self) :
        self.emit("aes_needs_reloaded_status_change", False)
    def is_needs_reloaded(self) : return False
    def source_get_resolution(self) :
        return self.resolution

    def source_set_resolution(self, resolution=None) :
        if resolution is None :
            self.resolution = 10
        else :
            self.resolution = resolution
    def get_action_panel(self) :
        win = gtk.Label('This source is not configurable')
        win.aes_title = "Configure source"
        return win

gobject.signal_new("aes_needs_reloaded_status_change", Source, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))

