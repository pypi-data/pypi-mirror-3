import sys, traceback, os
import StringIO
import gio

debug_print_on = False
non_interactive_override = False
def get_debug_print() :
    return debug_print_on

def set_debug_print(on) :
    global debug_print_on
    debug_print_on = on

def debug_print(*args) :
    if not get_debug_print() or non_interactive_override :
        return

    strargs = map(unicode, args)

    tbt = traceback.extract_stack()
    num = len(tbt)-2
    print unicode(os.path.basename(tbt[num][0])+':'+str(tbt[num][1])+\
                  '('+tbt[num][2]+') >> ') + u' '.join(strargs)

def debug_print_stack(force=False) :
    if (not force and not get_debug_print()) or non_interactive_override :
        return

    tbt = traceback.extract_stack()
    num = len(tbt)-1
    out = [t[2]+':'+str(t[1]) for t in tbt[:num]]
    print os.path.basename(tbt[num][0]+': '+' -> '.join(out))

class AesFile(StringIO.StringIO) :
    '''
    Intended to augment a gio File object so it can be used in place of a
    standard Python input stream. Ultimately, this should be able to stream
    line by line rather than reading in one go.
    '''

    def __init__(self, gf) :
        StringIO.StringIO.__init__(self, gf.read().read())
        self.gf = gf
