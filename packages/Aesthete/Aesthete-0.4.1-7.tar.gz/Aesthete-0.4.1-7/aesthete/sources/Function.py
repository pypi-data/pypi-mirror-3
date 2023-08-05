from sympy.core.function import Lambda as aes_Lambda
import pickle
import numpy
import lxml.etree as ET
from aobject.aobject import AObject, aname_root_catalog, AOBJECT_CAN_NONE, string_to_float_tup
from aobject.utils import debug_print
from Source import Source

class FunctionSource(Source) :
    function = None
    needs_resolution = True
    xlim = None

    def aes_get_parameters(self) :
        return {
            'resolution' : self.resolution
        }

    def get_auto_aesthete_properties(self) :
        d = Source.get_auto_aesthete_properties(self)
        d.update({
            "xlim" : (string_to_float_tup, (AOBJECT_CAN_NONE,))
        })
        return d

    i = 0
    def change_xlim(self, new_xlim) :
        self.xlim = new_xlim
        self.i += 1
        if self.i > 4 :
            quit()
        self.source_reload()

    def source_type(self) :
        return 'line'

    def __init__(self, function, max_dim, limits=None, env = None, stem='FunctionSource', show = False,
                 reloadable=True, resolution = 10) :
        self.resolution = resolution 
        self.function = function
        self.max_dim = max_dim

        #FIXME : moving ranges for 3D and buffering for both
        needs_x_range = max_dim==2

        Source.__init__(self, stem, env, show, reloadable,
                        needs_x_range=needs_x_range)
        if limits is not None :
            self.set_xlim((str(limits[1]), str(limits[2])))

    def source_get_values(self, time = None, multi_array = False,
                          x_range=None, y_range=(0, 1.), resolution=10.) :
        f = self.function

        if self.xlim is not None and x_range is None:
            x_range = map(float, self.xlim)

        if x_range is None :
            x_range = (0., 1.)

        self.current_x_range = x_range

        if resolution < 1 :
            resolution = 10.

        xa = numpy.arange(x_range[0], x_range[1], (x_range[1]-x_range[0])/resolution)

        if self.source_get_max_dim() == 3 :
            ya = numpy.arange(y_range[0], y_range[1],
                              (y_range[1]-y_range[0])/resolution)
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

class SympySource(FunctionSource) :

    def aes_get_parameters(self) :
        d = FunctionSource.aes_get_parameters(self)
        d.update({'sympy_function_pickled' : self.get_sympy_function_pickled()})
        return d

    def get_auto_aesthete_properties(self) :
        d = FunctionSource.get_auto_aesthete_properties(self)
        d.update({ 'sympy_function_pickled' : (str,) })
        return d

    def get_sympy_function_pickled(self) :
        return pickle.dumps(self.sympy_function)

    def change_sympy_function_pickled(self, var) :
        f = pickle.loads(var)
        self.set_function_from_sympy(f)

    def set_function_from_sympy(self, f, source_reload=True) :
        self.sympy_function = f

        if hasattr(f, "free_symbols") :
            syms = f.free_symbols
        else :
            syms = f.atoms(Dynamic.Symbol)

        #args = list(syms)+[f]
        symbols = len(f.free_symbols)+1
        f = aes_Lambda(syms, f)

        self.function = lambda *args : f(*args).evalf()
        self.max_dim = symbols
        if source_reload :
            self.source_reload()

    def __init__(self, f, limits=None, env = None, show = False,
                 reloadable = False, resolution = 10) :
        self.resolution = resolution 
        self.set_function_from_sympy(f, source_reload=False)
        if limits is not None :
            limits = (limits[0], limits[1].evalf(), limits[2].evalf())
        FunctionSource.__init__(self, self.function, self.max_dim,
                                stem='SympySource',
                                limits=limits,
                                env=env,
                                show=show,
                                reloadable=reloadable,
                                resolution=resolution)

    @classmethod
    def aes_load_a(cls, env, **parameters) :
        f = pickle.loads(parameters['sympy_function_pickled'])
        return cls(f, env=env,
                   resolution=int(parameters['resolution']))

aname_root_catalog['SympySource'] = SympySource.aes_load_a
