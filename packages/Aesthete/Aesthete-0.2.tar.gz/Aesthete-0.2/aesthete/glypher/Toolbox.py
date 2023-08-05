import gtk
import math
import xml.etree.ElementTree as ET
from ..paths import *
from ..utils import *
from Parser import *

# Tool tuple description using "field [to_ignore1 or to_ignore2]"
# (unicode symbol, name, shortcut (or None), properties [omittable or None], entity [omittable or False])
toolbar_dictionary = {\
    'Functions' : ( \
        (u'f', 'function', 'Alt+f'), \
        (u'\u2111', 'im', None), \
        (u'\u211C', 're', None), \
        (u'Ylm', 'Ylm', None), \
        (u'\u0393', 'gamma', None), \
        (u'logn', 'logn', None), \
        ),
    'Sets' : (
        (u'(,)', 'interval', None),
        (u'\u2205', 'empty_set', None),
        (u'\u2102', 'complexC', None), \
        (u'\u211A', 'rationalQ', None), \
        (u'\u211D', 'realR', None), \
        ),
    'Calculus' : ( \
        (u'\u222B', 'integral', 'Alt+i'), \
        (u'd/d', 'derivative', 'Alt+d') \
        ),
    'Utilities' : ( \
        (u'\u2637', 'table', 'Alt+T'),
        )
}
# Needs later version of sympy (and Interpret impl)
#        (u'{,}', 'finite_set', None),
#    'Bessel' : ( \
#        (u'J\u03BD', 'bessel_j', None) \
#        ),

expanded_toolbar_dictionary = {\
    'Utilities' : ( \
        (u'\u2318', 'phrasegroup', None, {'enterable':True}), \
        (u'\u2311', 'phrase', None), \
        (u'()', 'bracketed_phrase', None), \
        ),
    'Spacers' : ( \
        (u'\u2423', 'space', None, {'attachable':True,'blank':False,'show_decorated':True}, True), \
        (u'\u2015', 'horizontal_line', None),
        (u'|', 'vertical_line', None),
        )
}

def add_toolbar_dictionary(d, tdict = toolbar_dictionary) :
    for k in d :
        tdict[k] = tdict[k] + d[k] \
                if k in tdict else \
               d[k]

def initialize(tdict, expanded = False) :
    for trees in (phrasegroup_trees, user_phrasegroup_trees) :
        for name in trees :
            tree = trees[name]
            sy = tree.find('symbol')
            ca = tree.find('category')
            sh = tree.find('shortcut')
            if sy is not None and ca is not None :
                add_toolbar_dictionary( { ca.text : ( \
                        (sy.text, name, sh.text if sh is not None else None), ) }, tdict )
    if expanded :
        add_toolbar_dictionary(expanded_toolbar_dictionary, tdict)

class GlyphToolbox(gtk.Table, gtk.ToolShell) :
    caret = None
    grab_entities = True
    c = 3
    def __init__(self, caret, grab_entities = True, expanded = False, cols = 3) :
        self.caret = caret
        self.c = cols
        self.grab_entities = grab_entities

        tdict = toolbar_dictionary.copy()
        initialize(tdict, expanded=expanded)

        rs = len(tdict)/self.c + 1
        gtk.Table.__init__(self, rs, self.c)

        k = 0
        for key in sorted(tdict.keys()) :
            items = tdict[key]
            menu_toob = gtk.MenuToolButton(gtk.Label(items[0][0] + ' ...'), key)
            menu_toob.set_size_request(80, -1)
            menu_toob.connect('clicked', self.do_m_clicked)
            menu_menu = gtk.Menu()
            menu_toob.set_menu(menu_menu)
            menu_toob.set_arrow_tooltip_text(key)
            n = 0
            for it in items :
                it_meni = gtk.MenuItem(it[0])
                if n == 0 : menu_toob.active_item = it_meni
                it_meni.item_index = n
                it_meni.set_tooltip_text(it[1] + ' ' + '[No shortcut]' if it[2] is None else it[2])
                menu_menu.attach(it_meni, n, n+1, 0, 1)
                it_meni.glypher_name = (it[1], it[3] if len(it) > 3 else None, len(it) > 4 and it[4])
                it_meni.connect('activate', self.do_mi_clicked, menu_toob)
                n += 1
            menu_menu.show_all()
            r = k / self.c
            c = k % self.c
            self.attach(menu_toob, c, c+1, r, r+1, False, False)
            k += 1
    
    def do_mi_clicked(self, it_meni, menu_toob) :
        if menu_toob.active_item != it_meni :
            menu_toob.active_item = it_meni
            lb = gtk.Label(it_meni.get_label() + ' ...')
            lb.show_all()
            menu_toob.set_icon_widget(lb)
        gn = it_meni.glypher_name
        if gn[2] :
            debug_print(gn)
            self.caret.insert_named_entity(gn[0], properties=gn[1])
        else :
            self.caret.insert_phrasegroup(gn[0], properties=gn[1], grab_entities=self.grab_entities)
    
    def do_m_clicked(self, menu_toob) :
        it_meni = menu_toob.active_item
        self.do_mi_clicked(it_meni, menu_toob)
