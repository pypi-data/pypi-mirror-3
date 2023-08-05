import gtk
import pango
from aobject.paths import get_share_location
import math
import lxml.etree as ET
from aobject.paths import *
from aobject.utils import *
from Parser import *
from operator import itemgetter

class GradientLabel(gtk.DrawingArea) :
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, text, down_arrow=False) :
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.text = text
        self.set_size_request(-1, 30)
        self.down_arrow = down_arrow
    def set_text(self, text) :
        self.text = text
        self.queue_draw()
    def do_expose_event(self, event) :
        a = self.get_allocation()
        x = a.x
        y = a.y
        w = a.width
        h = a.height
        x = 0
        y = 0

        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
                 event.area.width, event.area.height)
        cr.clip()

        colour = (0.7, 0.7, 0.7)
        cr.save()
        cr.set_source_rgb(*colour)
        cr.move_to(x, y)
        cr.rel_line_to(0, h)
        cr.rel_line_to(w, 0)
        cr.rel_line_to(0, -h)
        cr.rel_line_to(-w, 0)
        cr.close_path()
        blush_grad = cairo.LinearGradient(x+w/2,y,x+w/2,y+h)
        colour = list(colour)+[1]
        blush_grad.add_color_stop_rgba(0, *colour)
        colour[3] = 0
        blush_grad.add_color_stop_rgba(1, *colour)
        cr.set_source(blush_grad)

        cr.fill()
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(13)
        cr.set_source_rgba(0.5,0.5,0.5,1.0)
        txb, tyb, tw, th, txa, tya = cr.text_extents(self.text)
        if self.down_arrow :
            cr.move_to(x,y+h/2)
            cr.show_text(u'\u21D5')
        cr.move_to(x+w/2-tw/2,y+h/2)
        cr.show_text(self.text)
        cr.restore()

# Tool tuple description using "field [to_ignore1 or to_ignore2]"
# (unicode symbol, name, shortcut (or None), properties [omittable or None], entity [omittable or False], priority [omittable or 0])
toolbar_dictionary = {\
    'Functions' : ( \
        (u'f', 'function', 'Alt+f', None, False, 0), \
        (u'\u2111', 'im', None, None, False, 0), \
        (u'\u211C', 're', None, None, False, 0), \
        (u'Ylm', 'Ylm', None, None, False, 0), \
        (u'\u0393', 'gamma', None, None, False, 0), \
        (u'logn', 'logn', None, None, False, 0), \
        ),
    'Sets' : (
        (u'(,)', 'interval', None, None, False, 0),
        (u'\u2205', 'empty_set', None, None, False, 0),
        (u'\u2102', 'complexC', None, None, False, 0), \
        (u'\u211A', 'rationalQ', None, None, False, 0), \
        (u'\u211D', 'realR', None, None, False, 0), \
        ),
    'Calculus' : ( \
        (u'\u222B', 'integral', 'Alt+i', None, False, 0), \
        (u'd/d', 'derivative', 'Alt+d', None, False, 0) \
        ),
    'Utilities' : ( \
        (u'\u2637', 'table', 'Alt+T', None, False, 0),
        )
}
# Needs later version of sympy (and Interpret impl)
#        (u'{,}', 'finite_set', None),
#    'Bessel' : ( \
#        (u'J\u03BD', 'bessel_j', None) \
#        ),

expanded_toolbar_dictionary = {\
    'Utilities' : ( \
        (u'\u2318', 'phrasegroup', None, {'enterable':True}, False, 0), \
        (u'\u2311', 'phrase', None, None, False, 0), \
        (u'()', 'bracketed_phrase', None, None, False, 0), \
        ),
    'Spacers' : ( \
        (u'\u2423', 'space', None, {'attachable':True,'blank':False,'show_decorated':True}, True, 0), \
        (u'\u2015', 'horizontal_line', None, None, False, 0),
        (u'|', 'vertical_line', None, None, False, 0),
        )
}

def add_toolbar_dictionary(d, tdict = toolbar_dictionary) :
    for k in d :
        tdict[k] = tdict[k] + d[k] \
                if k in tdict else \
               d[k]

def initialize(tdict, expanded = False) :
    for name in g.phrasegroups :
        pg = g.phrasegroups[name]
        if hasattr(pg, 'toolbox') and pg.toolbox is not None :
                sy = pg.toolbox['symbol']
                ca = pg.toolbox['category']
                sh = pg.toolbox['shortcut']
                pr = pg.toolbox['priority']
                add_toolbar_dictionary( { ca : ( \
                        (sy, name, sh.text if sh is not None else None, None, False, int(pr) if pr is not None else 0), ) }, tdict )
    for trees in (phrasegroup_trees, user_phrasegroup_trees) :
        for name in trees :
            tree = trees[name]
            sy = tree.find('symbol')
            ca = tree.find('category')
            sh = tree.find('shortcut')
            pr = tree.find('priority')
            if sy is not None and ca is not None :
                add_toolbar_dictionary( { ca.text : ( \
                        (sy.text, name, sh.text if sh is not None else None, None, False, int(pr.text) if pr is not None else 0), ) }, tdict )
            
    if expanded :
        add_toolbar_dictionary(expanded_toolbar_dictionary, tdict)

def find_category_image(catname) :
    catfilename = catname.replace(' ', '_').lower()

    catpath = get_share_location() + 'images/icons/glypher/categories/' + catfilename + '.svg'
    if os.path.exists(catpath) :
        return catpath
    
    return None

class GlyphEntBox(gtk.Table) :
    caret = None
    grab_entities = True
    will_set_glypher_expanded_property = False
    c = 3
    def __init__(self, caret, tool_table, tdict, grab_entities=True, expanded=False, cols=3) :
        self.caret = caret
        self.tool_table = tool_table
        self.c = cols
        self.grab_entities = grab_entities

        rs = len(tdict)/self.c + 1
        gtk.Table.__init__(self, rs, self.c)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))

        k = 0
        for key in sorted(tdict.keys()) :
            items = sorted(tdict[key], key=itemgetter(self.order_index), reverse=True)
            catfile = find_category_image(key)
            if catfile is None :
                menu_toob = gtk.Button(items[0][0] + ' ...')
            else :
                menu_toob = gtk.Button()
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(catfile, 24, 24)
                menu_imag = gtk.Image()
                menu_imag.set_from_pixbuf(pixbuf)
                menu_toob.set_image(menu_imag)
            menu_toob.set_tooltip_text(key)

            menu_toob.set_relief(gtk.RELIEF_NONE)
            menu_toob.set_size_request(50, -1)
            n = 0
            menu_items = []
            for it in items :
                it_meni = gtk.Button(it[0])
                it_meni.set_relief(gtk.RELIEF_NONE)
                it_meni.get_child().modify_font(pango.FontDescription("9"))
                #if n == 0 : menu_toob.active_item = it_meni
                #menu_menu.attach(it_meni, n, n+1, 0, 1)
                self._make_it(it_meni, it)
                it_meni.connect('clicked', self.do_mi_clicked)
                menu_items.append(it_meni)
                n += 1

            r = k / self.c
            c = k % self.c
            self.attach(menu_toob, c, c+1, r, r+1)
        
            menu_toob.connect('clicked', self.do_m_clicked, key, menu_items)
            k += 1
    
    def _make_it(self, it_meni, it) :
        pass

    def do_mi_clicked(self, it_meni) :
        pass

    def do_m_clicked(self, menu_toob, cat, menu_items) :
        self.tool_table.show_items(cat, menu_items)
        #it_meni = menu_toob.active_item
        #self.do_mi_clicked(it_meni, menu_toob)

class GlyphPGBox(GlyphEntBox) :
    order_index = 5
    will_set_glypher_expanded_property = True
    def __init__(self, caret, tool_table, grab_entities=True, expanded=False, cols=4) :
        tdict = toolbar_dictionary.copy()
        initialize(tdict, expanded=expanded)
        GlyphEntBox.__init__(self, caret, tool_table, tdict, grab_entities, expanded, cols)

    def do_mi_clicked(self, it_meni) :
        gn = it_meni.glypher_name
        if gn[2] :
            debug_print(gn)
            self.caret.insert_named_entity(gn[0], properties=gn[1])
        else :
            self.caret.insert_phrasegroup(gn[0], properties=gn[1], grab_entities=self.grab_entities)
        self.caret.glypher.grab_focus()

    def _make_it(self, it_meni, it) :
        it_meni.set_tooltip_text(it[1] + ' ' + '[No shortcut]' if it[2] is None else it[2] + ' ' + str(it[5]))
        it_meni.glypher_name = (it[1], it[3] if len(it) > 3 else None, len(it) > 4 and it[4])
    
# Based on the Comprehensive LaTeX Symbol List
# Scott Pakin
#mirror.ctan.org/info/symbols/comprehensive/symbols-a4.pdf
charmap_dictionary = {\
    # Table 130
    'CHiNa2e Number Sets' : ( \
        (u'\u2102', '\\Complex',0), \
        (u'\u2124', '\\Integer',0), \
        (u'\u2115', '\\Natural',0), \
        (u'\u211A', '\\Rational',0), \
        (u'\u211D', '\\Real',0), \
        ),
    # Table 137
    'Hebrew' : ( \
        (u'\u2135', '\\aleph',0), \
        (u'\u2136', '\\beth',0), \
        (u'\u2137', '\\gimel',0), \
        (u'\u2138', '\\daleth',0), \
        ),
    # Table 139
    'Letter-like symbols' : ( \
        (u'\u2762', '\\bot',0), \
        (u'\u2200', '\\forall',0), \
        (u'\u2118', '\\wp',0), \
        ),
    # Table 201
    'Miscellaneous LaTeX2e Math Symbols (a)' : ( \
        (u'\u2220', '\\angle',0), \
        (u'\u25A1', '\\Box',0), \
        (u'\u2205', '\\emptyset',0), \
        (u'\u221E', '\\infty',0), \
        (u'\u2127', '\\mho',0), \
        (u'\u2207', '\\nabla',0), \
        (u'\u00AC', '\\neg',0), \
        (u'\u221A', '\\surd',0), \
        (u'\u25B3', '\\triangle',0), \
        ),
    # Table 201
    'Miscellaneous LaTeX2e Math Symbols (b)' : ( \
        (u'\u2663', '\\clubsuit',0), \
        (u'\u25C7', '\\Diamond',0), \
        (u'\u2662', '\\diamondsuit',0), \
        (u'\u266D', '\\flat',0), \
        (u'\u2661', '\\heartsuit',0), \
        (u'\u266E', '\\natural',0), \
        (u'\u266F', '\\sharp',0), \
        (u'\u2660', '\\spadesuit',0), \
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

class GlyphFormulaMap(GlyphEntBox) :
    order_index = 3
    def __init__(self, caret, tool_table, grab_entities=True, expanded=False, cols=4) :
        fdict = {}
        for name in formula_trees :
            tree = formula_trees[name]
            title = tree.getroot().get('title')
            if title is None :
                title = name
            sy = tree.find('symbol')
            ca = tree.find('category')
            pr = tree.find('priority')
            if sy is not None and ca is not None :
                add_toolbar_dictionary( { ca.text : ( \
                        (sy.text, name, title,
                         int(pr.text) if pr is not None else 0), ) }, fdict )

        GlyphEntBox.__init__(self, caret, tool_table, fdict, grab_entities, expanded, cols)

    def do_mi_clicked(self, it_meni) :
        gn = it_meni.glypher_name
        self.caret.insert_formula(gn[0])
        self.caret.glypher.grab_focus()

    def _make_it(self, it_meni, it) :
        it_meni.set_tooltip_text(it[2])
        it_meni.glypher_name = (it[1],)
    
class GlyphCharMap(GlyphEntBox) :
    order_index = 2
    def __init__(self, caret, tool_table, grab_entities=True, expanded=False, cols=4) :
        tdict = charmap_dictionary.copy()
        GlyphEntBox.__init__(self, caret, tool_table, tdict, grab_entities, expanded, cols)

    def _make_it(self, it_meni, it) :
        it_meni.set_tooltip_text(it[1])
    
    def do_mi_clicked(self, it_meni) :
        self.caret.insert_shape(it_meni.get_label())

class GlyphToolTable(gtk.VBox) :
    rows = 4
    cols = 4
    def __init__(self) :
        gtk.VBox.__init__(self)
        self.table = gtk.Table(rows=self.rows, columns=self.cols, homogeneous=True)
        self.gradient_label = GradientLabel('')
        self.table.set_size_request(self.rows*50, self.cols*24)
        self.pack_start(self.gradient_label, False)
        self.pack_start(self.table)
        self.show_all()

    def show_items(self, cat, items) :
        self.gradient_label.set_text(cat)
        for child in self.table.get_children() :
            self.table.remove(child)
        cols = self.cols
        for i in range(0, len(items)) :
            self.table.attach(items[i], i%cols, i%cols+1, i/cols, i/cols+1)
        self.show_all()
        debug_print(items)

class GlyphToolbox(gtk.VBox) :
    def __init__(self, caret, grab_entities=False, expanded=False, cols=None,
                 hidden=False) :
        self.tool_table = GlyphToolTable()
        gtk.VBox.__init__(self)

        if cols is not None :
            params = { 'cols' : cols }
        else :
            params = {}
        self.entbox = GlyphPGBox(caret, self.tool_table, grab_entities,
                                 expanded=expanded, **params)
        ue_gradient_label = GradientLabel('Useful Entities', down_arrow=True)
        ue_gradient_label.connect("button-release-event",
                                  self.toggle_show,
                                  self.entbox)
        ue_gradient_label.show_all()
        self.pack_start(ue_gradient_label, False)
        self.pack_start(self.entbox)
        self.pack_start(gtk.HSeparator())

        uf_gradient_label = GradientLabel('Formulae', down_arrow=True)
        self.formulamap = GlyphFormulaMap(caret, self.tool_table, grab_entities,
                                    expanded=expanded, **params)
        uf_gradient_label.connect("button-release-event", self.toggle_show,
                                  self.formulamap)
        self.pack_start(uf_gradient_label, False)
        self.pack_start(self.formulamap)
        self.pack_start(gtk.HSeparator())

        uc_gradient_label = GradientLabel('Unicode Characters', down_arrow=True)
        self.charmap = GlyphCharMap(caret, self.tool_table, grab_entities,
                                    expanded=expanded, **params)
        uc_gradient_label.connect("button-release-event", self.toggle_show, self.charmap)
        self.pack_start(uc_gradient_label, False)
        self.pack_start(self.charmap)
        self.pack_start(self.tool_table)
        self.show_all()
        self.formulamap.hide()
        self.charmap.hide()
        if hidden :
            self.entbox.hide()

    def toggle_show(self, label, event, box) :
        box.set_visible(not box.get_visible())
