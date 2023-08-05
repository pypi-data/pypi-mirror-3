from sympy import *
import sympy
from sympy.series import limits
import glypher as g
from ..utils import *

current_globals = {}

def rebuild_globals() :
    global current_globals
    current_globals = {}
    dicts = [l.__dict__ for l in loaded_libraries.values()]
    dicts += [globals()]
    for d in dicts :
        current_globals.update(d)

def eval_for_sympy_args(code, *args) :
    '''This gives the evaluated code access to the sympy globals by a 'from
    sympy import *' in this closed-off module.'''

    try:
        return eval(code, current_globals, {'args':args})
    except TypeError as e : # hack to get mpmath functions working
        debug_print(e)
        new_args = []
        for arg in args:
            new_args.append(N(arg))
        return eval(code, current_globals, {'args':new_args})

def eval_for_sympy(ent, code) :
    '''This gives the evaluated code access to the sympy globals by a 'from
    sympy import *' in this closed-off module.'''
    return eval(code, current_globals, {'self':ent})

def get_sympy_function(func_name) :
    '''Finds a sympy function in the globals from a 'from sympy import *'.'''
    if func_name in globals() :
        return globals()[func_name]
    else :
        return None

loaded_libraries = {}
def load_library(name, unload = False) :
    '''Load (or unload) a library from the dynamic list.'''

    if name not in g.libraries :
        return False

    if unload :
        if name in loaded_libraries :
            del loaded_libraries[name]
        rebuild_globals()
        return True

    if name not in loaded_libraries :
        new_lib = __import__(name, globals(), locals(), ['*'])
        loaded_libraries[name] = new_lib
        rebuild_globals()

    return True

def get_library_function(func_name) :
    '''Try the loaded libraries (other than sympy) for the given function.'''

    for lib_name in loaded_libraries :
        lib = loaded_libraries[lib_name]
        if func_name in lib.__dict__ :
            return lib.__dict__[func_name]

    return None

def text_to_func(text) :
    sympy_code = compile(text, '<string>', 'eval')
    return lambda *args : eval_for_sympy_args(sympy_code, *args)

rebuild_globals()
