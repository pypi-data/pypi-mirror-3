import re
from ..utils import debug_print
import numpy
import gobject
import gtk
import os
import random
from Source import Source

try :
    import vtk as pyvtk
except :
    have_vtk = False
else :
    have_vtk = True

class SourceVTK (Source) :
    vals = None
    dim = 2
    filename = ""
    sort = True
    last_write = None
    needs_reloaded = False

    def __init__(self, filename, env = None) :
        Source.__init__(self, "VTK", env, show = False, reloadable = True)
        self.filename = filename

        self.reader = pyvtk.vtkXMLUnstructuredGridReader()
        self.reader.SetFileName(self.filename)

        self.set_aname_nice(os.path.basename(filename) + ' [' + filename + ']')
        self.source_reload()
        gobject.timeout_add(5000, self.source_check)
        if not have_vtk :
            raise RuntimeError("Don't have VTK Python package")
    
    def source_type(self) :
        return 'scatter'

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

        self.reader.Update()
        grid = self.reader.GetOutput()
        points = grid.GetPoints()
        num_points = int(points.GetNumberOfPoints())
        
        for i in range(0, num_points) :
            point_array = points.GetPoint(i)
            vals.append(point_array)

        multicol = True
        self.vals = vals
        Source.source_reload(self)
    
    def source_get_max_dim(self) : return self.dim
    def source_get_values(self, time = None, multi_array = False, x_range = None) :
        if multi_array :
            return [{'values':self.vals,'name':self.get_aname_nice()}]
        else : return self.vals
