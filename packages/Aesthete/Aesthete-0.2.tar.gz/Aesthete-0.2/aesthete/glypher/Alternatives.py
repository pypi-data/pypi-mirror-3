from Symbol import *
import traceback
import gtk
from Phrase import *
from Word import make_word
import Parser

class GlypherBox(GlypherPhrase) :
    colour = None
    anchor = None
    attached_to = None
    caret = None

    def __init__(self, phrase, colour = (0.9, 0.8, 0.6), anchor = None, attached_to = None, caret = None) :
        GlypherPhrase.__init__(self, parent=None)
        self.mes.append('box')
        self.adopt(phrase)
        self.colour = colour
        if anchor is not None :
            self.move_to(*anchor)
            self.anchor = anchor
        elif attached_to is not None :
            self.attached_to = attached_to
        elif caret is not None :
            self.caret = caret
        #else :
        #    raise(RuntimeError("Tried to create Box without specifying location or attached_to"))
        self.cast()
        debug_print(self.anchor)

    def cast(self) :
        a = None
        if self.attached_to is not None :
            x, y = self.attached_to.get_local_offset()
            x += self.attached_to.get_width()
            y += self.attached_to.get_height()
            a = (x+10, y)
        elif self.caret is not None :
            a = self.caret.position
        if a is not None and a != self.anchor:
            self.move_to(*a)
            self.anchor = a
        return
        
    def draw(self, cr) :
        self.cast()
        cr.save()
        bb = self.config[0].get_bbox()
        cr.set_source_rgba(0.3, 0.2, 0, 0.5)
        area=(bb[0]-2, bb[2]+10, bb[1]-2, bb[3]+10)
        draw.trace_rounded(cr, area, 5)
        cr.fill()
        c = self.colour
        cr.set_source_rgba(0.75+0.25*c[0], 0.75+0.25*c[1], 0.75+0.25*c[2], 0.8)
        #cr.rectangle(bb[0]-2, bb[1]-2, bb[2]-bb[0]+4, bb[3]-bb[1]+4)
        area=(bb[0]-6, bb[2]+6, bb[1]-6, bb[3]+6)
        draw.trace_rounded(cr, area, 5)
        cr.fill_preserve()

        cr.set_line_width(4)
        cr.set_source_rgb(*self.colour)
        cr.stroke()
        cr.restore()
        debug_print(self.config[0].bbox)
    
        GlypherPhrase.draw(self, cr)

class GlypherWidgetBox(GlypherBox) :
    gw = None
    widget = None

    def destroy(self) :
        self.caret.boxes.remove(self)
        self.caret.return_focus()
        self.widget.get_parent().remove(self.widget)
        del self

    def __init__(self, widget, widget_parent, caret = None, attached_to = None, box_colour = (0.9, 0.8, 0.6)) :
        self.widget = widget
        self.caret = caret
        self.gw = GlypherWidget(None, widget, widget_parent, self,
                                caret.glypher.position)
                                

        faded = map(lambda c: 1-(1-c)*0.2, box_colour)
        self.gw.ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(*faded))
        GlypherBox.__init__(self, self.gw, caret=caret, attached_to=attached_to, colour=box_colour)
        self.mes.append('widget_box')
        self.widget.grab_focus()

class GlypherLabelBox(GlypherWidgetBox) :
    labl = None
    def __init__(self, text, widget_parent, caret = None, attached_to = None, box_colour = (0.9, 0.8, 0.6)) :
        self.labl = gtk.Label(text)
        self.labl.set_line_wrap(True)
        self.labl.set_size_request(200, -1)
        self.labl.set_alignment(1.0, 1.0)
        GlypherWidgetBox.__init__(self, self.labl, widget_parent, caret=caret, attached_to=attached_to, box_colour=box_colour)
        widget_parent.move(self.labl, 0,0)

class GlypherSymbolShortener(GlypherWidgetBox) :
    sym_entry = None
    def __init__(self, widget_parent, caret, box_colour = (0.9, 0.8, 0.6)) :
        hbox = gtk.HBox(False, 4)
        hbox.pack_start(gtk.Label("Symbol"), False)
        sym_entry = gtk.Entry(); sym_entry.set_size_request(30, -1)
        self.sym_entry = sym_entry
        hbox.pack_start(sym_entry)
        hbox.pack_start(gtk.Label("Trigger text"), False)
        trigger_entry = gtk.Entry()
        hbox.pack_start(trigger_entry)
        GlypherWidgetBox.__init__(self, hbox, widget_parent, caret=caret, box_colour=box_colour)

        sym_entry.grab_focus()
        trigger_entry.connect('activate', self.do_trigger_entry_activate)
        trigger_entry.connect('key-press-event', \
            lambda w, e : self.destroy() if gtk.gdk.keyval_name(e.keyval) == 'Escape' else 0)
        sym_entry.connect('key-press-event', \
            lambda w, e : self.destroy() if gtk.gdk.keyval_name(e.keyval) == 'Escape' else 0)

    def do_trigger_entry_activate(self, entry) :
        ue = unicode(entry.get_text())
        if ue == '' and ue in g.combinations :
            del g.combinations[ue]
        else :
            g.combinations[ue] = unicode(self.sym_entry.get_text())
            l = make_word(ue, self.caret.phrased_to)
            self.caret.insert_entity(l)
        self.destroy()

class GlypherEntry(GlypherWidgetBox) :
    entry = None
    gw = None
    caret = None
    def __init__(self, widget_parent, caret, box_colour = (0.9, 0.8, 0.6)) :
        self.entry = gtk.Entry()
        GlypherWidgetBox.__init__(self, self.entry, widget_parent, caret=caret, box_colour=box_colour)
        self.mes.append('TeX_entry')

        self.caret = caret
        self.wrong_colour = (1.0, 0.5, 0.5)

        self.entry.connect('activate', self.do_entry_activate)
        self.entry.connect('key-press-event', \
            lambda w, e : self.destroy() if gtk.gdk.keyval_name(e.keyval) == 'Escape' else 0)
        
    
    def submit(self) :
        t = self.entry.get_text()
        debug_print(t)
        l = make_word(t, self.caret.phrased_to)
        self.caret.insert_entity(l)
        return True

    def do_entry_activate(self, entry) :
        if self.submit() : self.destroy()
        else :
            self.entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(*self.wrong_colour))

class GlypherTeXEntry(GlypherEntry) :
    def __init__(self, widget_parent, caret) :
        GlypherEntry.__init__(self, widget_parent, caret, box_colour = (0.9, 0.5, 0.3))

    def submit(self) :
        t = Parser.get_name_from_latex(self.entry.get_text())
        if t is not None :
            try :
                debug_print(t)
                self.caret.insert_named(t)
                return True
            except RuntimeError :
                debug_print(Parser.latex_to_name)
                return False
        t = Parser.get_shape_from_latex(self.entry.get_text())
        if t is not None :
            self.caret.insert_shape(t)
            return True
        return False

class GlypherWidget(GlypherEntity) :
    widget = None
    ebox = None
    def __init__(self, parent, widget, widget_parent, box, global_offset) :
        GlypherEntity.__init__(self, parent)

        self.add_properties({'local_space' : True})
        self.widget = widget
        self.box = box
        self.offset = global_offset

        #widget.grab_focus()

        self.ebox = gtk.EventBox()
        #widget.modify_bg(0, gtk.gdk.Color(1,1,1))
        e = self.ebox
        #e.set_size_request(100, 50)
        e.set_events(gtk.gdk.ALL_EVENTS_MASK)
        e.connect("button-press-event", lambda w, e : debug_print(e))
        #sc = e.get_screen()
        #e.set_colormap(sc.get_rgba_colormap())
        #e.set_app_paintable(True)
        e.add(widget)
        widget_parent.put(e, 0, 0)
        #e.window.set_composited(True)
        al = e.get_size_request()
        debug_print(al)
        m = e.size_request()
        self.ref_width = m[0]#al.height
        self.ref_height = m[1]#al.width
        self.recalc_bbox()
        r = self._get_rect(None)
        #e.window.move(self.config[0].bbox[0], self.config[0].bbox[1])
        e.size_allocate(r)
        self.first_move = False
        widget_parent.move(e, 0, 0)
        debug_print(widget.get_allocation())
        #debug_print(widget.window.get_geometry())
        #debug_print(widget.window.get_frame_extents())
        debug_print(self.config[0].bbox)
        e.set_visible(False)
        #widget.grab_focus()
    
    def _get_rect(self, cr) :
        #x, y = self.get_local_offset()
        x, y = (0,0)
        #x = self.offset[0]
        #y = self.offset[1]
        #y += self.ref_height
        if cr is not None :
            self.box.cast()
            x, y = self.box.get_local_offset()
            x += self.box.config[0].bbox[0]
            y += self.box.config[0].bbox[1]
            x, y = cr.user_to_device(x, y)
        w, h = (self.ref_width, self.ref_height)
        if cr is not None :
            w, h = cr.user_to_device_distance(w, h)
        #y -= self.ref_height
        #return gtk.gdk.Rectangle(int(x), int(y-w), int(h), int(w))
        return gtk.gdk.Rectangle(int(x), int(y), int(w), int(h))

    def _move_ebox(self, cr=None) :
        e = self.ebox
        a = e.get_allocation()
        e.show_all()
        m = e.size_request()

        if cr is not None :
            m = cr.device_to_user_distance(*m)

        self.ref_width = m[0]#al.height
        self.ref_height = m[1]#al.width
        r = self._rect
        debug_print(r)
        r1 = self._get_rect(cr)

        if cr is not None :
            debug_print(r1)
            debug_print(self.box.anchor)
            e.get_parent().move(e, r1.x, r1.y)
            debug_print(e.get_allocation())

        e.show_all()
        self.recalc_bbox()

    x = None
    y = None
    _rect = None
    def draw(self, cr) :
        #if self._rect != self._get_rect(cr) :
        self._rect = self._get_rect(cr)
        self._move_ebox(cr)
        self.ebox.set_visible(True)
        #cr.save()
        #e = self.ebox
        #a = e.get_allocation()
        #if a.x != int(self.config[0].bbox[0]) or \
        #        a.y != int(self.config[0].bbox[1]) :
        
    #def process_key(self, name, event, caret) :
    #    if not self.widget.has_focus() : return
    #    return self.ebox.event(event)
    def process_button_release(self, event) :
        #self.widget.grab_focus()
        #return self.widget.has_focus()
        #self.widget.do_button_release_event(self.widget, event)
        #return True if self.widget.event(event) else None
        return None
    def process_button_press(self, event) :
        #self.widget.grab_focus()
        #return self.widget.has_focus()
        #self.widget.do_button_press_event(self.widget, event)
        #return True if self.widget.event(event) else None
        return None
    def process_scroll(self, event) :
        self.widget.grab_focus()
        return None
        #return True if self.widget.event(event) else None

class GlypherAltBox(GlypherBox) :
    alts = None
    alts_syms = None
    alts_phrase = None
    anchor = (0,0)

    def __init__(self, alts) :
        self.alts = alts
        self.alts_phrase = GlypherPhrase(None)
        GlypherBox.__init__(self, self.alts_phrase)
        self.alts_phrase.mes.append('altbox_phrase')
        self.cast()
    
    def cast(self) :
        n = 0
        self.alts_syms = {}
        self.alts_phrase.empty()
        for alt in self.alts :
            if isinstance(alt, GlypherEntity) and alt.included() : raise(RuntimeError, alt.format_me())
        for alt in self.alts :
            if isinstance(alt, GlypherEntity) :
                ns = alt
            else :
                ns = GlypherSymbol(None, str(alt), ink=True)
            self.alts_syms[alt] = ns
            self.alts_phrase.append(ns, row=n)
            self.alts_phrase.set_row_align(n, 'c')
            ns.set_padding_all(4)
            n -= 1
        self.anchor = (0,0) # (self.alts_phrase.config[0].bbox[0]-20, self.alts_phrase.config[0].bbox[1])
    
        self.translate(-self.config[0].bbox[0], -self.config[0].bbox[1])

    def draw(self, cr, anchor, size, rgb_colour, active=None) :
        if anchor != self.anchor :
            self.anchor = (0,0)
        if size != self.alts_phrase.get_font_size() :
            self.set_font_size(size)
        if rgb_colour != self.alts_phrase.get_rgb_colour() :
            self.set_rgb_colour(rgb_colour)

        GlypherBox.draw(self, cr)

        if active and active in self.alts_syms :
            cr.save()
            bbp = self.alts_syms[active].config[0].get_bbox()
            bbs = self.alts_syms[active].config[0].get_bbox()
            cr.set_source_rgba(0.9, 0.8, 0.6)
            mp = 0.5*(bbs[1]+bbs[3])
            cr.move_to(bbp[0] - 16, mp-4)
            cr.line_to(bbp[0] - 10, mp)
            cr.line_to(bbp[0] - 16, mp+4)
            cr.close_path()
            cr.fill_preserve()
            cr.set_line_width(2)
            cr.set_source_rgb(0.8,0.6,0.2)
            cr.stroke()
            cr.restore()

class GlypherAlternativesPhrase(GlypherPhrase) :
    active_child = None

    def __init__(self, parent, area = (0,0,0,0), line_size_coeff = 1.0, font_size_coeff = 1.0, align = ('l','m'), auto_fices = False) :
        GlypherPhrase.__init__(self, parent, area, line_size_coeff, font_size_coeff, align, auto_fices)
        self.mes.append('alts_phrase')
        self.set_enterable(False)
        self.set_attachable(True)
        self.set_have_alternatives(True)
        self.altbox = GlypherAltBox([])
        #self.characteristics.append('_in_phrase')
    
    def decorate(self, cr) :
        hl_anc = None
        # If this is in an unhighlighted highlight group, don't show it, otherwise if the first highlighted group is
        # above it, show it
        for anc in self.get_ancestors() :
            if anc.am('phrasegroup') :
                if anc.first_highlighted_pg_over_active : hl_anc = anc; break
                #else : hl_anc = None; break
                elif anc.highlight_group : hl_anc = None; break
        if not hl_anc : return

        cr.save()
        bb = self.config[0].get_bbox()
        cr.move_to(bb[2]-2, bb[1]-3)
        cr.line_to(bb[2]+3, bb[1]-3)
        cr.line_to(bb[2]+3, bb[1]+2)
        cr.close_path()
        cr.set_source_rgba(0.0, 1.0, 0.0, 0.5)
        cr.fill_preserve()
        cr.set_source_rgba(0.0, 0.5, 0.0, 1.0)
        cr.stroke()
        cr.restore()
    
    def child_change(self) :
        GlypherPhrase.child_change(self)
        self.cast()
        for child in self.entities :
            if child != self.active_child and child.get_visible() :
                child.hide()
        if len(self.entities)>0 :
            if not self.active_child :
                self.active_child = self.entities[0]
                self.active_child.show()
            elif not self.active_child.get_visible() :
                self.active_child.show()

    def cast(self) :
        self.altbox.alts = copy.deepcopy(self.entities)
        alist = list(self.altbox.alts)
        for alt in alist :
            alt.set_parent(None)
            if alt.included() : raise(RuntimeError, str(alt.format_me()))
        self.altbox.cast()

    def next_alternative(self) :
        alts = self.entities
        if self.active_child == None : return
        ind = alts.index(self.active_child)
        self.active_child = alts[(len(alts) + ind - 1)%len(alts)]
        self.child_change()

    def prev_alternative(self) :
        alts = self.entities
        if self.active_child == None : return
        ind = alts.index(self.active_child)
        self.active_child = alts[(len(alts) + ind - 1)%len(alts)]
        self.child_change()

    def draw_alternatives(self, cr) :
        if not self.get_visible() : return

        altbox = self.altbox
        altbox.draw(cr, anchor=(self.config[0].bbox[2], self.config[0].bbox[1]),\
            size=self.get_scaled_font_size(), rgb_colour=self.get_rgb_colour(), active=self.active_child)
        self.draw(cr)
    
    def set_alternative(self, child) :
        if child not in self.entities : return
        self.active_child = child
        self.child_change()

    def set_alternative_by_name(self, name) :
        named = filter(lambda e : e.get_name() == name, self.entities)
        if len(named) == 0 : return
        self.set_alternative(named[0])

ref_alts_phrase = None
def make_alts_phrase () :
    global ref_alts_phrase
    if ref_alts_phrase is None :
        ref_alts_phrase = GlypherAlternativesPhrase(None)
    return copy.deepcopy(ref_alts_phrase)
