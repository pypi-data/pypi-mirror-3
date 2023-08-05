import glypher as g
import StringIO
from types import *
from Toolbox import *
from ..utils import debug_print
import gtk
from ..paths import *
from .. import aobject

try :
    import sympy
    import sympy.parsing.maxima
    have_sympy = True
except ImportError :
    have_sympy = False

from Interpret import *
from Caret import *
from Phrase import *
from Parser import *

debugging = False
phrasegroups_dir = get_user_location() + 'phrasegroups/'

display_cache = {}
class GlyphDisplay() :
    main_phrase = None
    line_height = 45
    def __init__(self) :
        self.main_phrase = GlypherMainPhrase(None,
                                             self.line_height, self.line_height,
                                             (0.0,0.0,0.0), is_decorated=False,
                                             by_bbox=True)
        self.main_phrase.set_is_caching(True)

    def render(self, xml) :
        str_xml = ET.tostring(xml.getroot())
        if len(str_xml) in display_cache and \
           str_xml in display_cache[len(str_xml)] :
            return display_cache[len(str_xml)][str_xml]

        # Do stuff
        pg = parse_phrasegroup(self.main_phrase, xml, top=True)
        self.main_phrase.empty()
        self.main_phrase.adopt(pg)
        self.main_phrase.draw()
        ims = self.main_phrase.cairo_cache_image_surface
        pixbuf = gtk.gdk.pixbuf_new_from_data(
            ims.get_data(),
            gtk.gdk.COLORSPACE_RGB,
            False,
            8,
            ims.get_width(),
            ims.get_height(),
            ims.get_stride()
        )

        if len(str_xml) not in display_cache :
            display_cache[len(str_xml)] = {}
        display_cache[len(str_xml)][str_xml] = pixbuf

        return pixbuf

class GlyphCellRenderer(gtk.GenericCellRenderer) :
    __gproperties__ = {
        "text": (gobject.TYPE_STRING, "text", "Text", "", gobject.PARAM_READWRITE),
        "xml": (gobject.TYPE_PYOBJECT, "xml", "Glypher XML", gobject.PARAM_READWRITE),
        "width": (gobject.TYPE_INT, "width", "Width", 0, 1000, 0, gobject.PARAM_READWRITE),
        "height": (gobject.TYPE_INT, "height", "Height", 0, 1000, 0, gobject.PARAM_READWRITE),
    }
    line_height = 25

    def __init__(self) :
        self.__gobject_init__()
        self.xml = None
        self.main_phrase = GlypherMainPhrase(None,
                                             self.line_height, self.line_height,
                                             (0.0,0.0,0.0), is_decorated=False,
                                             by_bbox=True)

    def do_set_property(self, pspec, value) :
        if pspec.name == 'xml'  and value is not None :
            pg = parse_phrasegroup(self.main_phrase, value, top=False)
            self.main_phrase.empty()
            self.main_phrase.adopt(pg)
            self.width = self.main_phrase.get_width()
            self.height = self.main_phrase.get_height()

        setattr(self, pspec.name, value)

    def do_get_property(self, pspec) :
        return getattr(self, pspec.name)

    def on_render(self, window, widget, background_area, cell_area, expose_area,
                  flags) :
        cr = window.cairo_create()
        
        cr.save()
        cr.translate(cell_area.x, cell_area.y)

        #if expose_area is not None :
        #    cr.rectangle(*expose_area)
        #    cr.clip()

        if self.xml is not None :
            self.main_phrase.draw(cr)
        else :
            debug_print(self.text)

        cr.restore()

    def on_get_size(self, widget, cell_area=None):
        x = 0
        y = 0

        if self.xml is not None :
            return (x, y, self.main_phrase.get_width(),
                                    self.main_phrase.get_height())
        else :
            return (x, y, self.line_height, self.line_height)

        #ims = self.main_phrase.cairo_cache_image_surface
gobject.type_register(GlyphCellRenderer)

class GlyphEntry(gtk.Layout) :
    caret = None
    main_phrase = None
    margins = [5, 5, 5, 5]

    default_width = 200
    default_height = 100
    line_height = 45
    who_is_phrased_to = "None yet"
    who_is_attached_to = "None"

    __gsignals__ =     { \
                "expose-event" : "override", \
                 "key-press-event" : "override",\
                 "key-release-event" : "override",\
                 "button-press-event" : "override",\
                 "button-release-event" : "override",\
                "scroll-event" : "override",\
                "content-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                     ()),
                "size-allocate" : "override",\
                "processed-line" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                    ()),
                "request-plot" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                  (gobject.TYPE_STRING,))
            }
    
    def do_size_allocate(self, allocation) :
        gtk.Layout.do_size_allocate(self, allocation)
        if not self.fixed_main_phrase :
            self.main_phrase.set_area((0, allocation.height-self.position[1]))
        self._resize_to_allocation(allocation)

    def do_content_changed(self, o = None) :
        self.queue_draw()

    def set_font_size(self, font_size) :
        self.line_height = font_size
        self.main_phrase.set_font_size_scaling(0.5)
        self.main_phrase.child_change()

    def __init__(self, position = (5, 5), interactive = True,
                 resize_to_main_phrase = False, evaluable = False,
                 fixed_main_phrase = False):
        gtk.Layout.__init__(self)

        self.container = self
        container = self
        self.interactive = interactive
        self.fixed_main_phrase = fixed_main_phrase
        self.resize_to_main_phrase = resize_to_main_phrase
        self.evaluable = evaluable

        self.clipboard = gtk.Clipboard()
        self.set_size_request(self.default_width, self.default_height)

        self.set_property("can-focus", interactive)
        self.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.add_events(gtk.gdk.SCROLL_MASK)

        ps = self.process_main_phrase_signal

        self.position = position
        self.main_phrase = GlypherMainPhrase(ps,
                                             self.line_height, self.line_height,
                                             (0.0,0.0,0.0), is_decorated=True,
                                             by_bbox=True)
        self.caret = GlypherCaret(self.main_phrase, interactive=interactive,
                            container=container, glypher=self)
        global caret
        caret = self.caret
        caret.connect('content-changed', lambda o : self.emit('content-changed'))
        self.connect('content-changed', self.do_content_changed)
        #self.caret.font_size = 40

        self.main_phrase.line_length = self.get_allocation().width
        self.grab_focus()

        self.caret.new_phrase(self.main_phrase)
        #self.caret.enter_phrase(self.main_phrase, at_start = True)
        #self.caret.new_word()
        #self.main_phrase.set_shows_active(False)
        #self.response_phrase.set_shows_active(False)
        self.caret.connect("changed-phrased-to", lambda o, s, l : self.set_who_is_phrased_to(l))
        self.caret.connect("changed-attached-to", lambda o, s, l : self.set_who_is_attached_to(l))
        self.reset_main_phrase()

        self.main_phrases = [self.main_phrase]
        self.main_phrases_offsets = {self.main_phrase : self.position}

        parse_phrasegroups()
    
    def process_line(self) :
        self.caret.remove_boxes()

        try :
            input_line, response = self.response_processor()
        except GlypherTargetPhraseError as e :
            debug_print("Error : " + str(e))
            l = GlypherLabelBox(str(e),\
                widget_parent=self.container, attached_to=e.tp,
                caret=self.caret,
                box_colour=(0.9, 0.3, 0.3))
            self.caret.boxes.append(l)
            debug_print("Error : " + str(e))
            return None, None

        self.emit("processed-line")
        return input_line, response

    def set_status(self, text) :
        pass

    def do_info(self, entity) :
        title = entity.get_title()
        if title is None :
            title = "<i>%s</i>" % entity.mes[-1]

        info_text = entity.get_info_text()
        if info_text is None :
            info_text = "<i>No info text</i>"

        wiki_link = entity.get_wiki_link()

        dialog = gtk.Dialog('Entity info', None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        vbox = dialog.get_content_area()
        info_head_labl = gtk.Label()
        info_head_labl.set_markup('<b>%s</b>' % title)
        vbox.pack_start(info_head_labl, False)
        info_labl = gtk.Label()
        info_labl.set_line_wrap(True)
        info_labl.set_size_request(400, 60)
        info_text = re.sub("\\n", " ", info_text)
        info_labl.set_markup(info_text.strip())
        vbox.pack_start(info_labl)

        if wiki_link is not None :
            vbox.pack_start(gtk.HSeparator())

            wiki_gtk_link = \
                "http://en.wikipedia.org/wiki/Special:Search?search=%s" % \
                wiki_link
            wiki_gtk_link = gtk.LinkButton(wiki_gtk_link, wiki_link)
            wiki_hbox = gtk.HBox()
            wiki_hbox.pack_start(gtk.Label("Wiki:"), False)
            wiki_hbox.pack_start(wiki_gtk_link)
            vbox.pack_start(wiki_hbox, False)

        vbox.show_all()

        dialog.get_action_area().get_children()[-1].grab_focus()
        dialog.run()
        dialog.destroy()

    def do_bracket_warning(self) :
        dialog = gtk.Dialog('Open parentheses..?', None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        vbox = dialog.get_content_area()
        info_head_labl = gtk.Label()
        info_head_labl.set_markup('<b>Glypher Tip</b>')
        vbox.pack_start(info_head_labl, False)
        info_labl = gtk.Label()
        info_labl.set_line_wrap(True)
        info_labl.set_size_request(600, -1)
        info_labl.set_markup(\
"""
Don't forget that, as a Glypher expression is actually a tree of subexpressions
in disguise, for the moment, ordinary parentheses aren't used. To do something
to an expression, hit <i>Left</i> or <i>Right</i> until the expression on which
you wish to operate is enclosed in blue Caret brackets. Then go for it - hit ^,
+, *, or whatever takes your fancy! If <i>Aesthete</i> reckons they're needed
for clarity, it'll show brackets, but they're always there implicitly.

If you are looking for a matrix, try <i>Alt+(</i> . Using <i>Super+Left/Down</i>
gives you extra rows and cols. You may also be looking for <i>Ctrl+(</i> which
turns a Word into a function.
""")
        vbox.pack_start(info_labl)
        vbox.show_all()
        dialog.run()
        dialog.destroy()

    def clear(self) :
        self.reset_main_phrase()

    def reset_main_phrase(self, space_array=None) :
        self.main_phrase.empty()
        self.caret.attached_to = None
        self.caret.enter_phrase(self.main_phrase)
    
    def set_who_is_phrased_to(self, string) :
        self.who_is_phrased_to = string
    def set_who_is_attached_to(self, string) :
        self.who_is_attached_to = string

    show_phrase_order = False
    #def do_expose_event(self, event):
    #    cr = self.window.cairo_create()
    #    cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
    #    cr.clip()
    #    self.draw(cr, *self.window.get_size())
    #    self.show_all()

    def do_expose_event(self, event):
        cr = self.get_bin_window().cairo_create()
        cr.rectangle ( event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.get_bin_window().get_size())

    def draw(self, cr, swidth, sheight):
        cr.save()
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, swidth, sheight); cr.fill()
        
        #cr.move_to(0, 20)
        #cr.set_font_size(14); cr.set_source_rgb(0.0, 0.0, 0.0)
        #cr.show_text('GlyphMaker')
        if debugging :
            cr.move_to(140, 20)
            cr.show_text("Phrased to "+self.who_is_phrased_to)
            cr.move_to(140, 40)
            cr.show_text("Attached to "+self.who_is_attached_to)
            cr.move_to(10, 28); cr.rel_line_to(100, 0)
            cr.stroke()

        cr.save()
        cr.translate(*self.position)
        self.main_phrase.draw(cr)
        self.caret.draw(cr)
        if self.caret.symbol_active : self.caret.attached_to.draw_alternatives(cr)
        cr.restore()

        if self.show_phrase_order : self.draw_phrase_order(cr)
        cr.restore()

    def do_button_press_event(self, event) :
        if not self.interactive :
            return False
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            if fc(m.find_distance((x, y)), 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
                if not target[1] or not target[1].process_button_press(event) :
                    debug_print((event.x,event.y,event.button))
                    if (event.button == 1) :
                        debug_print(m.config[0].bbox)
                        debug_print(m.config[0].basebox)
                        target = m.find_nearest\
                            (point=(x,y), fall_through=True, enterable_parent=True)
                        debug_print(target)
                        if target[1] : debug_print(target[1].format_me())
                        self.caret.change_attached(target[1])
                        self.queue_draw()

    def do_button_release_event(self, event) :
        self.grab_focus()
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            if fc(m.find_distance((x, y)), 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
        self.queue_draw()

    def do_scroll_event(self, event) :
        debug_print('h')
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            if fc(m.find_distance((x, y)), 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
                if not target[1] or not target[1].process_scroll(event) :
                    _scaling = 1.2 if event.direction == gtk.gdk.SCROLL_UP else 1/1.2
                    m.set_size_scaling(_scaling*m.get_ip('font_size_coeff'))
        self.queue_draw()

    def do_key_release_event(self, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        self.caret.process_key_release(keyname, event)
        self.queue_draw()

    def do_key_press_event(self, event):
        if not self.interactive :
            return

        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        debug_print(keyname)
        g.dit = False
        
        if m_super and m_control :
            self.caret.process_key_press(keyname, event)
            self.queue_draw()
        elif (keyname == 'k' and m_control and not m_shift and not m_alt) or (keyname == 'K' and m_control and not m_shift and not m_alt) :
            self.caret.delete_from_shape()
        elif (keyname == 'u' and m_control and not m_shift and not m_alt) or (keyname == 'U' and m_control and not m_shift and not m_alt) :
            self.caret.delete_to_shape()
        elif (keyname == 'percent' and m_control) :
            ref = self.caret.insert_named('response_reference')
            ref.IN().adopt(make_word('r'+str(len(self.responses)), ref))
            self.caret.change_attached(ref, outside=True)
        elif keyname == 'BackSpace' and m_control and not m_alt :
            self.reset_main_phrase()
        elif m_control and not m_alt and not m_super and keyname == 'x' :
            self.copy(cut=True)
        elif m_control and not m_alt and not m_super and keyname == 'c' :
            self.copy(cut=False)
        elif m_control and not m_alt and not m_super and keyname == 'v' :
            self.paste_text(xml=True)
        elif m_control and not m_alt and not m_super and keyname == 'V' :
            self.paste_text()
        elif m_control and not m_alt and not m_super and keyname == 'Y' :
            self.paste_text(alternative=True)
        elif m_control and not m_alt and m_super and keyname == 'y' :
            self.paste_text(verbatim=True)
        elif self.evaluable and not m_control and not m_alt and not m_super and keyname == 'Return' :
            debug_print(self.process_line())
        elif m_control and not m_alt and keyname=='l' :
            g.show_rectangles = not g.show_rectangles
            self.queue_draw()
        else :
            ret = self.caret.process_key_press(keyname, event)
            self.queue_draw()
            return ret
        self.queue_draw()
        self.emit("content-changed") #FIXME: THIS SHOULD CHECK THAT A CHANGE IN FACT OCCURS
        return False
    
    def response_processor(self) :
        return (self.main_phrase, interpret_sympy(None, self.main_phrase.get_sympy()))

    def draw_phrase_order(self, cr) :
        if not self.caret.attached_to or not self.caret.attached_to.am("phrase"): return
        ents = self.caret.attached_to.sort_entities()
        cr.save()
        cr.translate(40, 200)
        across_dist = 0
        down_dist = 0
        bbox_0 = None
        cr.set_source_rgb(0.5,0.5,0.5)
        for ent in ents :
            cr.save()
            cr.translate(-ent.config[0].bbox[0] + across_dist, -ent.config[0].bbox[1] + down_dist)
            ent.draw(cr)
            cr.rectangle(ent.config[0].bbox[0], ent.config[0].bbox[1], ent.config[0].bbox[2]-ent.config[0].bbox[0], ent.config[0].bbox[3]-ent.config[0].bbox[1])
            cr.stroke()
            cr.restore()
            if bbox_0 is None or ent.config[0].bbox[0] != bbox_0 :
                down_dist = 0
                across_dist += ent.config[0].bbox[2]-ent.config[0].bbox[0]+5
            else :
                down_dist += ent.config[0].bbox[3]-ent.config[0].bbox[1]+5
            bbox_0 = ent.config[0].bbox[0]
        cr.restore()

    def process_main_phrase_signal(self, main_phrase, signal, data = None) :
        if signal == 'copy' :
            self.copy(data[1], contents=data[2])
            if data[0] : self.paste_text(alternative=False)
            return True
        if signal == 'recalc' :
            self._auto_resize()
            self.queue_draw()
        return False

    def _resize_to_allocation(self) :
        pass

    def _auto_resize(self) :
        if self.resize_to_main_phrase :
            m = self.margins
            self.set_size_request(int(round(self.main_phrase.get_width()))+m[0]+m[2],
                                  int(round(self.main_phrase.get_height()))+m[1]+m[3])

    def copy(self, contents = False, cut = False, fmt='xml') :
        #e = entity.copy()
        #self.clipboard.set_text(e.get_repr() if not contents else " ".join([f.get_repr() for f in e.get_entities()]))
        try :
            copied = self.caret.copy(cut=cut, fmt=fmt)
        except RuntimeError as reason :
            self.set_status('Could not copy %s: %s' % (fmt, reason))
            return

        if fmt == 'xml' :
            string = StringIO.StringIO()
            copied.write(string, encoding="utf-8")
            string = string.getvalue()
        else :
            string = copied

        if len(string) < 100 :
            self.set_status('Copied %s : %s' % (fmt, string.replace('\n', '; ')))
        else :
            self.set_status('Copied %s' % fmt)

        self.clipboard.set_text(string)

    def paste_text(self, verbatim = False, alternative = False, xml = False) :
        debug_print(xml)
        text = self.clipboard.request_text(self.do_request_clipboard,
                        (verbatim, alternative, xml))
    
    def do_request_clipboard(self, clipboard, text, paste_text_args) :
        self.caret.paste_text(text, *paste_text_args)
    
    def set_xml(self, xml, insert=False, top=False) :
        pg = parse_phrasegroup(self.main_phrase, xml, top=top)
        if not insert :
            if pg.am('space_array') :
                self.reset_main_phrase(space_array=pg)
            else :
                self.reset_main_phrase()
                self.main_phrase.adopt(pg)
        #self.caret.insert_entity(pg)

    def get_sympy(self) :
        return self.main_phrase.get_sympy()

    def get_text(self) :
        return self.main_phrase.to_string()

    def get_xml(self, full = False) :
        root = self.main_phrase.get_xml(targets={}, top=False,
                                                      full=full)
        debug_print(ET.tostring(root))
        xml = ET.ElementTree(root)
        return xml
    
    def clear(self) :
        self.reset_main_phrase()

class GlyphBasicGlypher(GlyphEntry, aobject.AObject) :
    container = None
    caret = None
    main_phrase = None
    margins = [10, 40, 0, 10]

    default_width = -1
    default_height = 160

    def do_content_changed(self, o = None) :
        self.queue_draw()

    def __init__(self, name_root="GlypherBasicGlypher", position = (10, 40),
                 env = None, evaluable = True):
        GlyphEntry.__init__(self, position=position, interactive=True,
                            evaluable=evaluable, fixed_main_phrase=True)
        aobject.AObject.__init__(self, name_root, env, view_object=True)

        self.main_phrase.set_by_bbox(False)
        self.main_phrase.set_enterable(False)
        self.main_phrase.set_attachable(False)
        self.reset_main_phrase()
        self.caret.enter_phrase(self.main_phrase)

        self.main_phrases = [self.main_phrase]
        self.main_phrases_offsets = {self.main_phrase : self.position}
    
    def __del__(self) :
        aobject.AObject.__del__(self)

    #PROPERTIES
    def get_aesthete_properties(self):
        return { }
    #BEGIN PROPERTIES FUNCTIONS
    #END PROPERTIES FUNCTIONS

    def _local_coords_for_main_phrase(self, m, point) :
        x = point[0] - self.main_phrases_offsets[m][0]
        y = point[1] - self.main_phrases_offsets[m][1]
        return x, y

    _move_from = None
    _mp_from = None
    def do_button_press_event(self, event) :
        nearest = (None, 0)
        self.grab_focus()
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            d = m.find_distance((x, y))
            if fc(d, 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
                bp = target[1].process_button_press(event)
                if bp is None : return False
                debug_print(bp)
                if not target[1] or not bp :
                    debug_print((x,y,event.button))
                    if (event.button == 1) :
                        self.caret.go_near((x, y), change=True)
                        self.queue_draw()
                    if (event.button == 2) :
                        self._move_from = (event.x,event.y,m)
                        self._mp_from = m.get_anchor_point()
                return True
            elif nearest[0] is None or d < nearest[1] :
                nearest = (m, d)
        if nearest[0] is not None and event.button == 1 :
            self.caret.go_near((x, y), change=True)
            self.queue_draw()
        return True
    
    def do_motion_notify_event(self, event) :
        if self._move_from is not None :
            m = self._move_from[2]
            delta = (event.x-self._move_from[0], event.y-self._move_from[1])
            m.move(delta[0] + self._mp_from[0], delta[1] + self._mp_from[1])
            self.queue_draw()

    def do_button_release_event(self, event) :
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            if fc(m.find_distance((x, y)), 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
                bp = target[1].process_button_release(event)
                debug_print(bp)
                if bp is None : return False
                if not target[1] or not bp :
                    if (event.button == 2) :
                        self._move_from = None
                        self._mp_from = None
        self.queue_draw()
        return True

    def do_scroll_event(self, event) :
        for m in self.main_phrases :
            x, y = self._local_coords_for_main_phrase(m,(event.x, event.y))
            if fc(m.find_distance((x, y)), 0) :
                target = m.find_nearest(point=(x,y), fall_through=True, enterable_parent=False)
                if not target[1] or not target[1].process_scroll(event) :
                    _scaling = 1.2 if event.direction == gtk.gdk.SCROLL_UP else 1/1.2
                    m.set_size_scaling(_scaling*m.get_ip('font_size_coeff'))
        self.queue_draw()
        return True

class GlyphResponder(GlyphEntry) :
    input_phrase = None
    response_phrase = None
    input_interactive = True
    evalf = False

    def __init__(self, position = (5, 5), interactive = True,
                 resize_to_main_phrase = False, evaluable = False, evalf = False):
        ps = self.process_main_phrase_signal
        self.evalf = evalf
        self.response_phrase = GlypherMainPhrase(ps,
                                                 self.line_height,
                                                 self.line_height,
                                                 (0.0,0.0,0.0),
                                                 is_decorated=False,
                                                 by_bbox=True)
        self.response_phrase.is_caching = True
        GlyphEntry.__init__(self, position=position, interactive=False,
                            resize_to_main_phrase=resize_to_main_phrase,
                            evaluable=evaluable)
        self.input_phrase = self.main_phrase
        self.input_interactive = interactive
        self.reset_main_phrase()
    
    def reset_main_phrase(self) :
        self.caret.attached_to = None
        if self.input_phrase :
            self.input_phrase.empty()
            self.caret.enter_phrase(self.input_phrase)

        self.response_phrase.empty()
    
    def process_main_phrase_signal(self, main_phrase, signal, data = None) :
        ret = GlyphEntry.process_main_phrase_signal(self, main_phrase, signal, data)
        self.response_phrase.background_colour = (1.0, 1.0, 1.0, 0.0)
        if main_phrase == self.input_phrase and signal == 'recalc' :
            if len(main_phrase) > 0 :
                debug_print(main_phrase.format_entities())
                self.process_line()
                if not main_phrase.entities[0].am('word') :
                    self.response_phrase.background_colour = (1.0, 1.0, 0.0, 0.4)
            else :
                self.response_phrase.empty()
            debug_print(self.get_text())
            return True
        return ret

    def response_processor(self) :
        sym = self.input_phrase.get_sympy()

        if self.evalf and isinstance(sym, sympy.core.basic.Basic) :
            sym = sym.evalf()
        return (self.input_phrase, interpret_sympy(self.response_phrase, sym))

    def process_line(self) :
        input_line, response = GlyphEntry.process_line(self)

        self.response_phrase.empty()
        caret = GlypherCaret(self.response_phrase, interactive=True,
                            container=self, glypher=self)
        caret.enter_phrase(self.response_phrase)
        if isinstance(response, str) :
            caret.insert_entity(make_word(response, self.response_phrase))
        else :
            caret.insert_entity(response)

        return input_line, response

    def get_xml(self, input_phrase = False, full = False) :
        mp = self.input_phrase if input_phrase else self.response_phrase
        debug_print(ET.tostring(mp.get_xml(targets={},
                                                             top=False,
                                           full=full)))
        xml = ET.ElementTree(mp.get_xml(targets={}, top=False, full=full))
        debug_print(ET.tostring(xml.getroot()))
        return xml

    def set_xml(self, xml) :
        pg = parse_phrasegroup(self.input_phrase, xml, top=False)
        if pg.am('space_array') :
            self.reset_main_phrase(space_array=pg)
        else :
            self.reset_main_phrase()
        #debug_print(pg.to_string())
        #self.caret.insert_entity(pg)
        #self.input_phrase.adopt(pg, go_inside=False)
        #self.queue_draw()

    def swap(self) :
        if self.main_phrase == self.input_phrase :
            self.main_phrase = self.response_phrase
            self.interactive = False
        else :
            self.main_phrase = self.input_phrase
            self.interactive = self.input_interactive

        self._auto_resize()
        self.queue_draw()
