import sympy
import xml.etree.ElementTree as ET

import gtk
import threading
import gobject
import glypher as g

g.have_pyglet = True
try :
     from sympy.thirdparty import import_thirdparty
     pyglet = import_thirdparty("pyglet")
except :
     try :
         import pyglet
         import pyglet.app as pyga
         from sympy.plotting import plot, managed_window
     except :
         warning.warn("pyglet not found")
         g.have_pyglet = False
         #sys.exit("Aesthete currently requires pyglet")

from ..sims import FunctionSource
from ..utils import *

def make_source(ent, caret) :
    sy_func = ent.get_sympy()

    if hasattr(sy_func, "free_symbols") :
        syms = sy_func.free_symbols
    else :
        syms = sy_func.atoms(sympy.core.symbol.Symbol)

    args = list(syms) + [sy_func]
    f = sympy.core.function.Lambda(*args)
    args = f.args
    debug_print(ent.to_string())
    fs = FunctionSource('glypher_function',
                        lambda *args : f(*args).evalf(),
                        len(args),
                        env = caret.glypher.get_aenv())
    fs.set_aesthete_xml(ET.ElementTree(ent.get_xml()))
    fs.set_aname_nice(ent.to_latex())

    return fs.get_aname()

def make_plot(ent, caret) :
    aname = make_source(ent, caret)
    if aname is None :
        return False
    caret.glypher.emit('request-plot', aname)
    return True

def make_sympy_plot(ent) :
    f = ent.get_sympy()
    if g.have_pyglet :
        p = plot.Plot(f)
    else :
         warning.warn("pyglet not found")


gtk.gdk.threads_init()
