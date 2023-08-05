import gtk
import math
import xml.etree.ElementTree as ET
from ..paths import *
from ..utils import *
from Parser import *

# Based on the Comprehensive LaTeX Symbol List
# Scott Pakin
#mirror.ctan.org/info/symbols/comprehensive/symbols-a4.pdf
charmap_dictionary = {\
    # Table 130
    'CHiNa2e Number Sets' : ( \
        (u'\u2102', '\\Complex'), \
        (u'\u2124', '\\Integer'), \
        (u'\u2115', '\\Natural'), \
        (u'\u211A', '\\Rational'), \
        (u'\u211D', '\\Real'), \
        ),
    # Table 137
    'Hebrew' : ( \
        (u'\u2135', '\\aleph'), \
        (u'\u2136', '\\beth'), \
        (u'\u2137', '\\gimel'), \
        (u'\u2138', '\\daleth'), \
        ),
    # Table 139
    'Letter-like symbols' : ( \
        (u'\u2762', '\\bot'), \
        (u'\u2200', '\\forall'), \
        (u'\u2118', '\\wp'), \
        ),
    # Table 201
    'Miscellaneous LaTeX2e Math Symbols' : ( \
        (u'\u2220', '\\angle'), \
        (u'\u25A1', '\\Box'), \
        (u'\u2663', '\\clubsuit'), \
        (u'\u25C7', '\\Diamond'), \
        (u'\u2662', '\\diamondsuit'), \
        (u'\u2205', '\\emptyset'), \
        (u'\u266D', '\\flat'), \
        (u'\u2661', '\\heartsuit'), \
        (u'\u221E', '\\infty'), \
        (u'\u2127', '\\mho'), \
        (u'\u2207', '\\nabla'), \
        (u'\u266E', '\\natural'), \
        (u'\u00AC', '\\neg'), \
        (u'\u266F', '\\sharp'), \
        (u'\u2660', '\\spadesuit'), \
        (u'\u221A', '\\surd'), \
        (u'\u25B3', '\\triangle'), \
        ),
}

for table in charmap_dictionary :
    table = charmap_dictionary[table]
    for sym in table :
        latex_to_shape[sym[1]] = sym[0]

def add_charmap_dictionary(d, tdict = charmap_dictionary) :
    for k in d :
        tdict[k] = tdict[k] + d[k] \
                if k in tdict else \
               d[k]

class GlyphCharMap(gtk.Table, gtk.ToolShell) :
    caret = None
    grab_entities = True
    c = 4
    def __init__(self, caret, cols=4) :
        self.caret = caret
        self.c = cols

        tdict = charmap_dictionary.copy()

        rs = len(tdict)/self.c + 1
        gtk.Table.__init__(self, rs, self.c)

        k = 0
        for key in sorted(tdict.keys()) :
            items = tdict[key]
            menu_toob = gtk.MenuToolButton(gtk.Label(items[0][0] + ' ...'), key)
            menu_toob.connect('clicked', self.do_m_clicked)
            menu_menu = gtk.Menu()
            menu_toob.set_menu(menu_menu)
            menu_toob.set_arrow_tooltip_text(key)
            n = 0
            for it in items :
                it_meni = gtk.MenuItem(it[0])
                if n == 0 : menu_toob.active_item = it_meni
                it_meni.item_index = n
                it_meni.set_tooltip_text(it[1])
                menu_menu.attach(it_meni, n, n+1, 0, 1)
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
        self.caret.insert_shape(it_meni.get_label())
    
    def do_m_clicked(self, menu_toob) :
        it_meni = menu_toob.active_item
        self.do_mi_clicked(it_meni, menu_toob)
