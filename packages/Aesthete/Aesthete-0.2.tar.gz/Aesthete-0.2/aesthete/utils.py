import sys, traceback, os

debug_print_on = False
def get_debug_print() :
    return debug_print_on

def set_debug_print(on) :
    global debug_print_on
    debug_print_on = on

def debug_print(var) :
    if not get_debug_print() :
        return

    tbt = traceback.extract_stack()
    num = len(tbt)-2
    print unicode(os.path.basename(tbt[num][0])+':'+str(tbt[num][1])+' ('+tbt[num][2]+') >> ') + unicode(var)

def debug_print_stack() :
    if not get_debug_print() :
        return

    tbt = traceback.extract_stack()
    num = len(tbt)-1
    out = [t[2]+':'+str(t[1]) for t in tbt[:num]]
    print os.path.basename(tbt[num][0]+': '+' -> '.join(out))
