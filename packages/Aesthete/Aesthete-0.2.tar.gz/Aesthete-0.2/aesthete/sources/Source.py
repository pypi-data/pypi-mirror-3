import re
from ..utils import debug_print
import numpy
import gobject
import gtk
import os
import random
from ..aobject import AObject

class Source (AObject) :
    reloadable = False
    needs_x_range = False
    def __init__(self, stem, env = None, show = False, reloadable = False, needs_x_range = False) :
        self.add_me("Source")
        self.reloadable = reloadable
        self.needs_x_range = needs_x_range
        AObject.__init__(self, stem, env, show)
    def source_set_x_range(self, x_range) :
        self.x_range = x_range
    def source_get_values(self, time = None, multi_array = False, x_range = None) :
        pass # MUST OVERRIDE!!
    def source_get_max_dim(self) :
        pass # MUST OVERRIDE!!
    def source_type(self) :
        pass # MUST OVERRIDE!!

    def source_reload(self) :
        self.emit("aes_needs_reloaded_status_change", False)
    def is_needs_reloaded(self) : return False
gobject.signal_new("aes_needs_reloaded_status_change", Source, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))

class FunctionSource(Source) :
    resolution = None
    function = None

    def source_type(self) :
        return 'line'

    def __init__(self, stem, function, arg_count, env = None, show = False,
                 reloadable = False, resolution = 10) :
        self.resolution = resolution
        self.function = function
        self.max_dim = arg_count
        Source.__init__(self, stem, env, show, reloadable, needs_x_range=True)

    def source_get_values(self, time = None, multi_array = False,
                          x_range = (0.,1.), y_range = (0.,1.)) :
        f = self.function
        xa = numpy.arange(x_range[0], x_range[1], (x_range[1]-x_range[0])/self.resolution)

        debug_print(self.source_get_max_dim())
        if self.source_get_max_dim() == 3 :
            debug_print(self.resolution)
            ya = numpy.arange(y_range[0], y_range[1],
                              (y_range[1]-y_range[0])/self.resolution)
            xc = len(xa)
            yc = len(ya)
            xa, ya = numpy.meshgrid(xa, ya)
            p = xa.copy()
            for ind, val in numpy.ndenumerate(p) :
                try :
                    p[ind] = f(xa[ind], ya[ind])
                except :
                    p[ind] = numpy.nan
            if multi_array :
                return [{'values':p,'x':xa,'y':ya,'name':self.get_aname_nice()}]
        else :
            p = numpy.array([ f(x) for x in xa ])
            if multi_array :
                return [{'values':p,'x':xa,'name':self.get_aname_nice()}]

        return p
    def source_get_max_dim(self) :
        return self.max_dim

class CSV (Source) :
    vals = None
    dim = 2
    filename = ""
    sort = True
    last_write = None
    needs_reloaded = False

    def __init__(self, filename, env = None) :
        Source.__init__(self, "CSV", env, show = False, reloadable = True)
        self.filename = filename
        self.set_aname_nice(os.path.basename(filename) + ' [' + filename + ']')
        self.source_reload()
        gobject.timeout_add(5000, self.source_check)
    
    def source_type(self) :
        return 'line'

    def source_check(self) :
        try : mtime = os.stat(self.filename).st_mtime
        except (OSError) : return True
        if not self.needs_reloaded and self.last_write < mtime :
            self.needs_reloaded = True
            self.emit("aes_needs_reloaded_status_change", True)
        return True
    def is_needs_reloaded(self) : return self.needs_reloaded

    def source_reload(self) :
        vals = []
        self.needs_reloaded = False
        self.last_write = os.stat(self.filename).st_mtime
        with open (self.filename) as f:
            #columns = f.readline().split(',')
            vals = numpy.loadtxt(f, delimiter=',', unpack = True, skiprows = 1)

        multicol = True
        try :
            test = vals[0][0]
        except : multicol = False

        #for i in range(0, len(vals[1])) : vals[1][i] *= 0.001

        if multicol :
            self.dim = len(vals)
            debug_print(self.dim)
            vals = zip(*vals)
            vals.sort(lambda x, y : cmp(x[0], y[0]))
        else :
            vals.sort()
            vals = [vals]
            self.dim = 1

        # Remove!
        self.vals = vals
        Source.source_reload(self)
    
    def source_get_max_dim(self) : return self.dim
    def source_get_values(self, time = None, multi_array = False, x_range = None) :
        if multi_array :
            vals = zip(*self.vals)
            return [{'values':vals[1],'x':vals[0],'name':self.get_aname_nice()}]
        else : return self.vals

    def get_useful_vars(self) :
        return {
                 'vals' : 'Values',
               }
