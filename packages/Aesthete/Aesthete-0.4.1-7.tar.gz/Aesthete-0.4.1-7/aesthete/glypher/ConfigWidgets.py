import gtk
from Spacer import *

def symbol(sp, c) :
    togg = gtk.ToggleButton("BBox to Ink")
    togg.set_active(sp.get_ink())
    togg.connect("toggled", lambda tb : (\
                 sp.set_ink(tb.get_active()), \
                 sp.recalc_bbox(), \
                 tb.set_active(sp.get_ink())))
    togg.show_all()
    return togg

def space(sp, c) :
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label("H"), False)
	h_entr = gtk.Entry()
	h_entr.set_text(str(sp.get_dims()[0]))
	h_entr.connect("activate", lambda e : sp.set_dims((float(e.get_text()), sp.get_dims()[1])))
	hbox.pack_start(h_entr)
	v_entr = gtk.Entry()
	v_entr.set_text(str(sp.get_dims()[1]))
	v_entr.connect("activate", lambda e : sp.set_dims((sp.get_dims()[0], float(e.get_text()))))
	hbox.pack_start(gtk.Label("V"), False)
	hbox.pack_start(v_entr)
	hbox.show_all()
	return hbox

def phrase(sp, c) :
	vbox = gtk.VBox()
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label("Row"), False)
	row_entr = gtk.Entry()
	row_entr.set_text('0')
	hbox.pack_start(row_entr)
	hbox.pack_start(gtk.Label("Align"), False)
	al_entr = gtk.Entry()
	al_entr.set_text(sp.row_aligns[0])
	hbox.pack_start(al_entr)
	vbox.pack_start(hbox, False)
	set_row_al_butt = gtk.Button("Set row align")
	set_row_al_butt.connect("clicked", lambda o : sp.set_row_align(int(row_entr.get_text()), al_entr.get_text()))
	vbox.pack_start(set_row_al_butt, False)
	vbox.show_all()
	return vbox

def vertical_line(sp, c) :
    tie_to_butt = gtk.Button("Tie to sel")
    tie_to_butt.connect("clicked",
            lambda butt : sp.set_tied_to(
                c.get_selected()[0] \
                if len(c.get_selected())>0 else \
                None))
    tie_to_butt.show_all()
    return tie_to_butt

def horizontal_line(sp, c) :
    tie_to_butt = gtk.Button("Tie to sel")
    tie_to_butt.connect("clicked",
            lambda butt : sp.set_tied_to(
                c.get_selected()[0] \
                if len(c.get_selected())>0 else \
                None))
    tie_to_butt.show_all()
    return tie_to_butt

config_widgets = {\
	"space" : space,
	"symbol" : symbol,
	"phrase" : phrase,
    "horizontal_line" : horizontal_line,
    "vertical_line" : vertical_line
	}

def get_config_widget(ty, ent, caret) :
	return config_widgets[ty](ent, caret) if ty in config_widgets else None
