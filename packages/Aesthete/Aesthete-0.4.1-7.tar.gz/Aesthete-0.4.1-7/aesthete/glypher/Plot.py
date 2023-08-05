from sympy import *
import lxml.etree as etree

import gtk
import threading
import gobject
import glypher as g

import warnings

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
         g.have_pyglet = False
         #sys.exit("Aesthete currently requires pyglet")

from ..sources.Function import SympySource
from aobject.utils import *

def make_source(ent, caret, limits=None) :
    try :
        sy_func = ent.get_sympy()
    except :
        return None

    fs = SympySource(sy_func, limits) #, env = caret.glypher.get_aenv())
    #args = f.args
    #fs = FunctionSource(lambda *args : f(*args).evalf(),
    #                    len(args),
    #                    env = caret.glypher.get_aenv())
    xml = ent.get_xml()

    font_size = float(ent.get_scaled_font_size())

    xml.set('width', str(ent.get_width()/font_size))
    xml.set('height', str(ent.get_height()/font_size))

    fs.set_aesthete_xml(etree.ElementTree(xml))
    fs.set_aname_nice("$%s$" % ent.to_latex())

    return fs.get_aname()

def make_plot(ent, caret, limits=None) :
    aname = make_source(ent, caret, limits)
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
