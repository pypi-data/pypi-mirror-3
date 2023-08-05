import glypher as g
import threading
from Widget import *
from aobject.utils import debug_print
import gtk
from aobject import aobject

try :
    import sympy
    import sympy.parsing.maxima
    have_sympy = True
except ImportError :
    have_sympy = False

from ..tablemaker import PreferencesTableMaker
from Toolbox import *
from Interpret import *
from Caret import *
from Phrase import *
from Parser import *
from Alternatives import *
from aobject import aobject

debugging = False

class Glypher (gtk.VPaned, aobject.AObject) :
    def get_auto_aesthete_properties(self) :
        return {'expand_toolbox' : (bool,)}

    def set_status(self, string) :
        self.aes_append_status(None, string)

    def set_ui(self) :
        self.ui_action_group = gtk.ActionGroup('GlypherActions')
        self.ui_action_group.add_actions([\
        ('GlypherMenu', None, 'Glypher'),
            ('GlypherOpen', None, 'Open', None, None,
                lambda w : self.inside_.open_xml()),
            ('GlypherInsert', None, 'Insert', None, None,
                lambda w : self.inside_.open_xml(insert=True)),
            ('GlypherSave', None, 'Save', None, None,
                lambda w : self.inside_.save_xml()),
            ('GlypherSaveAsFormula', None, 'Save as Formula', None, None,
                lambda w : self.inside_.save_formula()),
            ('GlypherGlyphMaker', None, 'Insert GlyphMaker', None, None,
                lambda w : self.inside_.open_phrasegroup()),
            ('GlypherExport', None, 'Export', None, None,
                lambda w : self.inside_.export()),
            ('GlypherShowLaTeX', None, 'Show LaTeX', None, None,
                lambda w : self.inside_.show_latex()),
            ('GlypherCopy', None, 'Copy'),
                ('GlypherCopyXML', None, 'Glypher XML', None, None,
                    lambda w : self.inside_.copy(fmt='xml')),
                ('GlypherCopySympy', None, 'Sympy', None, None,
                    lambda w : self.inside_.copy(fmt='sympy')),
                ('GlypherCopyMathML', None, 'MathML', None, None,
                    lambda w : self.inside_.copy(fmt='mathml')),
                ('GlypherCopyPython', None, 'Python', None, None,
                    lambda w : self.inside_.copy(fmt='python')),
                ('GlypherCopyLaTeX', None, 'LaTeX', None, None,
                    lambda w : self.inside_.copy(fmt='latex')),
                ('GlypherCopyUnicode', None, 'Unicode', None, None,
                    lambda w : self.inside_.copy(fmt='unicode')),
                ('GlypherCopyText', None, 'Text', None, None,
                    lambda w : self.inside_.copy(fmt='text')),
                                         ])
        self.ui_ui_string = '''
            <ui>
                <menubar name="MenuBar">
                    <menu action="GlypherMenu">
                        <menuitem action="GlypherOpen"/>
                        <menuitem action="GlypherInsert"/>
                        <menuitem action="GlypherSave"/>
                        <menuitem action="GlypherSaveAsFormula"/>
                        <menuitem action="GlypherGlyphMaker"/>
                        <separator/>
                        <menuitem action="GlypherExport"/>
                        <menuitem action="GlypherShowLaTeX"/>
                        <separator/>
                        <menu action="GlypherCopy">
                            <menuitem action="GlypherCopyXML"/>
                            <menuitem action="GlypherCopySympy"/>
                            <menuitem action="GlypherCopyMathML"/>
                            <menuitem action="GlypherCopyPython"/>
                            <menuitem action="GlypherCopyLaTeX"/>
                            <menuitem action="GlypherCopyUnicode"/>
                            <menuitem action="GlypherCopyText"/>
                        </menu>
                    </menu>
                </menubar>
            </ui>
        '''

    def __del__(self) :
        aobject.AObject.__del__(self)

    def _do_treeview_changed(self, treeview, ev) :
        '''
        STICKY BOTTOM
        If we are within 1/5 of a page (scrolled window height) of bottom,
        scroll down with new entry
        '''

        sw = treeview.get_parent()
        adj = sw.get_vadjustment()
        if adj.get_value() > adj.upper - 1.2*adj.page_size :
            adj.set_value(adj.upper - adj.page_size)

    def _do_caret_moved(self, glyph_entry) :
        att = glyph_entry.caret.attached_to

        if att is not None :
            anc = att.get_ancestors()
            anc_strings = []
            quote_mark1 = u'<span foreground="#CCCCCC">[</span>'
            quote_mark2 = u'<span foreground="#CCCCCC">]</span>'

            for a in anc :
                if a.am('phrasegroup') :
                    anc_strings.append(unicode(g.describe_phrasegroup(a.mes[-1])))
                if a.am('word') :
                    anc_strings.append(quote_mark1+a.to_string()+quote_mark2)
            
            anc_strings.reverse()

            if att.am('target_phrase') :
                anc_strings.append(u'<span foreground="#FF8888">%s</span>' %\
                               att.get_name())
            elif att.am('symbol') :
                anc_strings.append(u'<span foreground="#FF8888">%s</span>' %\
                               att.get_shape())

            anc_string = u'\u21f0'.join(anc_strings)
        else :
            anc_string = '<i>Unattached</i>'

        self.where_label.set_markup(u'<b>Caret location</b> : %s' % anc_string)
        self.where_label.set_ellipsize(pango.ELLIPSIZE_START)

    def __init__(self, env=None) :
        gtk.VPaned.__init__(self)
        vbox = gtk.VBox()
        self.set_property('can-focus', True)
        self.connect_after('focus-in-event', lambda w, e : self.inside_.grab_focus())

        self.inside_ = GlyphInside_()
        aobject.AObject.__init__(self, name_root="Glypher", env=env, view_object=True)
        self.pack1(self.inside_, True, True)

        scrolled_window = gtk.ScrolledWindow()

        self.where_label = gtk.Label()
        self.where_label.show()
        self.where_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#888888'))
        self.where_label.set_alignment(0,0.5)
        vbox.pack_start(self.where_label, False)
        self.inside_.connect('caret-moved', self._do_caret_moved)
        self._do_caret_moved(self.inside_)

        self.treeview = gtk.TreeView(g.responses_lsst)
        self.treeview.set_rules_hint(True)
        code_trvc = gtk.TreeViewColumn('Code')
        self.treeview.append_column(code_trvc)
        code_trvc.set_expand(False)
        statement_trvc = gtk.TreeViewColumn('Statement')
        self.treeview.append_column(statement_trvc)
        response_trvc = gtk.TreeViewColumn('Response')
        self.treeview.append_column(response_trvc)

        code_crtx = gtk.CellRendererText()
        code_trvc.pack_start(code_crtx, True)
        statement_cllr = GlyphCellRenderer()
        statement_trvc.pack_start(statement_cllr, True)
        response_cllr = GlyphCellRenderer()
        response_trvc.pack_start(response_cllr, True)

        code_trvc.add_attribute(code_crtx, 'text', 0)
        statement_trvc.add_attribute(statement_cllr, 'obj', 1)
        response_trvc.add_attribute(response_cllr, 'obj', 2)

        scrolled_window.add(self.treeview)
        self.treeview.connect('size-allocate', self._do_treeview_changed)
        scrolled_window.set_size_request(-1, 200)
        vbox.pack_start(scrolled_window)

        self.pack2(vbox, True, True)
        self.show_all()

        self.action_panel = self.make_action_panel()

        self.inside_.connect('status-update', lambda w, s : self.set_status(s))

        if env is not None :
            self.inside_.connect('request-plot', env.toplevel.plot_source)

    def make_action_panel(self) :

        settings_ntbk = gtk.Notebook()
        settings_ntbk.set_tab_pos(gtk.POS_LEFT)
        settings_ntbk.aes_title = "Glypher Prefs"

        # Expand
        expand_vbox = gtk.VBox()
        expand_vbox.pack_start(gtk.Label('Expand flags'), False)
        complex_togb = gtk.ToggleButton("Complex")
        complex_togb.set_active(g.expand['complex'])
        complex_togb.connect("toggled", lambda b : g.set_expand_flag('complex', b.get_active()))
        expand_vbox.pack_start(complex_togb, False)
        trig_togb = gtk.ToggleButton("Trig")
        trig_togb.set_active(g.expand['trig'])
        trig_togb.connect("toggled", lambda b : g.set_expand_flag('trig', b.get_active()))
        expand_vbox.pack_start(trig_togb, False)
        settings_ntbk.append_page(expand_vbox, gtk.Label("Ex"))

        # Complex
        complex_vbox = gtk.VBox()
        complex_vbox.pack_start(gtk.Label('Complex settings'), False)
        plane_togb = gtk.ToggleButton("Complex Plane")
        plane_togb.set_active(g.plane_mode)
        plane_togb.connect("toggled", lambda b : g.set_plane_mode(b.get_active()))
        complex_vbox.pack_start(plane_togb, False)
        settings_ntbk.append_page(complex_vbox, gtk.Label("Cx"))

        # LA
        la_vbox = gtk.VBox()
        la_vbox.pack_start(gtk.Label('Linear algebra'), False)
        zeros_togb = gtk.ToggleButton("Blank zeros")
        zeros_togb.set_active(g.zeros_mode)
        zeros_togb.connect("toggled", lambda b : g.set_zeros_mode(b.get_active()))
        la_vbox.pack_start(zeros_togb, False)
        settings_ntbk.append_page(la_vbox, gtk.Label("Mx"))

        # Libraries
        libraries_vbox = gtk.VBox()
        libraries_vbox.pack_start(gtk.Label('Active libraries'), False)
        for lib in g.libraries :
            cpts = lib.split('.')
            lib_togb = gtk.ToggleButton(cpts[len(cpts)-1])
            lib_togb.set_active(g.libraries[lib])
            lib_togb.connect("toggled", lambda b : g.set_library(lib, b.get_active()))
            libraries_vbox.pack_start(lib_togb, False)
        settings_ntbk.append_page(libraries_vbox, gtk.Label("Li"))

        # General
        general_vbox = gtk.VBox()
        general_vbox.pack_start(gtk.Label('General'), False)
        show_all_pow_diff_togb = gtk.ToggleButton("Show Pow/Diff")
        show_all_pow_diff_togb.set_active(g.show_all_pow_diff)
        show_all_pow_diff_togb.connect("toggled", lambda b :
                                 (g.set_show_all_pow_diff(b.get_active()),
                                       self.inside_.queue_draw()))
        general_vbox.pack_start(show_all_pow_diff_togb, False)
        general_vbox.pack_start(gtk.Label("Pow Mode"), False)

        pow_adjt = gtk.Adjustment(0, -1, 1, 1)
        pow_hscl = gtk.HScale(pow_adjt)
        pow_hscl.set_draw_value(False)
        pow_hscl.connect('value-changed', lambda r :
                         g.set_pow_mode_force(int(round(r.get_value()))))
        pow_hbox = gtk.HBox()
        pow_hbox.pack_start(gtk.Label('Off'))
        pow_hbox.pack_start(pow_hscl)
        pow_hbox.pack_start(gtk.Label('On'))
        general_vbox.pack_start(pow_hbox)
        general_vbox.pack_start(gtk.Label("Diff Mode"), False)

        diff_adjt = gtk.Adjustment(0, -1, 1, 1)
        diff_hscl = gtk.HScale(diff_adjt)
        diff_hscl.set_draw_value(False)
        diff_hscl.connect('value-changed', lambda r :
                          g.set_diff_mode_force(int(round(r.get_value()))))
        diff_hbox = gtk.HBox()
        diff_hbox.pack_start(gtk.Label('Off'))
        diff_hbox.pack_start(diff_hscl)
        diff_hbox.pack_start(gtk.Label('On'))
        general_vbox.pack_start(diff_hbox)

        #general_vbox.pack_start(self.aes_method_toggle_button(\
        #                        'formulae_set_or_insert',
        #                        label="Formulae",
        #                        preferencable=True,
        #                        onoff=('Set','Insert')))

        settings_ntbk.append_page(general_vbox, gtk.Label("Gn"))

        settings_ntbk.show_all()

        return settings_ntbk

    def get_method_window(self) :
        vbox = GlyphToolbox(self.inside_.caret, grab_entities=True,
                            hidden=not self.get_expand_toolbox())
        self.toolbox = vbox.entbox

        preferences_butt = gtk.Button("Preferences")
        preferences_butt.connect("clicked", lambda o :
                            self.env.action_panel.to_action_panel(self.action_panel))
        preferences_butt.show_all()

        vbox.pack_start(preferences_butt, False)

        vbox.show()

        return vbox

class GlyphInside_ (GlyphEntry) :
    container = None
    caret = None
    main_phrase = None
    margins = [10, 40, 0, 10]

    response_phrase = None
    responses = None
    line_height = 35.
    default_height = 240
    default_width = 460
    expand_toolbox = True

    def do_content_changed(self, o = None) :
        self.queue_draw()

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

    def _resize_to_allocation(self, allocation=None) :
        if allocation is not None :
            self.default_height = allocation.height
            self.default_width = allocation.width

        self.response_loc = (40, self.default_height-80, self.default_width-40,
                             self.default_height-40)
        self.main_phrase.line_length = self.response_loc[2]-self.response_loc[0]
        self.response_phrase.line_length = self.response_loc[2]-self.response_loc[0]
        #self.responses_phrase.set_max_dimensions((self.response_loc[2]-self.response_loc[0], self.response_loc[3]-self.response_loc[1]))
        #self.responses_phrase.set_min_dimensions(self.responses_phrase.get_max_dimensions())
        #self.responses_phrase.set_col_width(1, 0.5*(self.responses_phrase.get_max_dimensions()[0]-50))
        #self.responses_phrase.set_col_width(2, 0.5*(self.responses_phrase.get_max_dimensions()[0]))
        #self.responses_phrase.recalc_bbox()

        #self.main_phrases_offsets[self.responses_main_phrase] = self.response_loc[0:2]
        self.main_phrases_offsets[self.response_phrase] = (self.position[0],
                                                          .5*(self.position[0]+40+\
                                                               self.response_loc[3]))

    def __init__(self, position = (40, 40)):
        GlyphEntry.__init__(self, position=position, interactive=True,
                            evaluable=True, fixed_main_phrase=True,
                            dec_with_focus=False, corner_art=True)

        self.main_phrase.set_by_bbox(False)
        self.main_phrase.set_enterable(False)
        self.main_phrase.set_attachable(False)
        self.reset_main_phrase()
        self.caret.enter_phrase(self.main_phrase)

        self.main_phrases = [self.main_phrase]
        self.main_phrases_offsets = {self.main_phrase : self.position}

        self.responses = {}

        ps = self.process_main_phrase_signal

        self.response_phrase = GlypherMainPhrase(ps, self.line_height, self.line_height, (0.0,0.0,0.0))
        #self.responses_main_phrase = GlypherMainPhrase(ps, self.line_height, self.line_height, (0.0,0.0,0.0), anchor=('l','t'))
        #self.responses_phrase = GlypherTable(self.responses_main_phrase, first_col=GlypherSymbol(None, " "), cell_padding=5, border=None)
        #self.responses_phrase.set_max_dimensions((10*self.responses_phrase.get_scaled_font_size(),
        #                                          6*self.responses_phrase.get_scaled_font_size()))
        #self.responses_main_phrase.append(self.responses_phrase)
        #self.responses_main_phrase.set_font_size(20)
        #self.responses_phrase.set_col_width(0, 50)
        #self.responses_phrase.recalc_bbox()

        #inpu_word = make_word('Statement', None); inpu_word.set_font_name('sans')
        #self.responses_phrase.add_cell(0,1).append(inpu_word); inpu_word.set_bold(True)
        #resp_word = make_word('Response', None); resp_word.set_font_name('sans')
        #c = self.responses_phrase.add_cell(0,2)
        #c.is_caching = True
        #c.append(resp_word); resp_word.set_bold(True)

        #self.responses_phrase.set_row_border_bottom(0)

        #self.responses_phrase.set_col_colour(0, (0.8,0.0,0.0))
        #self.responses_phrase.set_col_colour(1, (0.5,0.5,0.5))
        #self.responses_phrase.set_col_colour(2, (0.8,0.5,0.5))
        #self.responses_phrase.set_row_colour(0, (0.3,0.3,0.3))

        self.caret.enter_phrase(self.space_array)

        self.main_phrases = [self.main_phrase, self.response_phrase]
        #self.main_phrases = [self.main_phrase, self.responses_main_phrase, self.response_phrase]
        self.main_phrases_offsets = {self.main_phrase : self.position,
                                     self.response_phrase : None }

        self._resize_to_allocation()

    def reset_main_phrase(self, space_array=None) :
        GlyphEntry.reset_main_phrase(self)

        self.caret.remove_boxes()

        if space_array is None :
            self.space_array = GlypherSpaceArray(self.main_phrase, spacing=0.2,
                                       num_ops=1)
        else :
            self.space_array = space_array

        self.space_array.set_deletable(False)
        self.space_array.set_highlight_group(False)

        self.main_phrase.append(self.space_array)
        self.space_array.set_recommending(self.space_array.get_target('pos0'))
        self.caret.try_suggestion()

    def show_latex(self) :
        d = gtk.Dialog("LaTeX", self.get_toplevel(), gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,\
            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        d.set_size_request(300, -1)
        e = gtk.TextView()
        f = gtk.TextView()
        e.get_buffer().set_text(self.main_phrase.to_latex())
        f.get_buffer().set_text(self.response_phrase.to_latex())
        d.vbox.pack_start(gtk.Label("Statement"))
        d.vbox.pack_start(e)
        d.vbox.pack_start(gtk.Label("Response"))
        d.vbox.pack_start(f)
        d.show_all()
        resp = d.run()
        d.destroy()
        #if resp == gtk.RESPONSE_OK :
        #    debug_print(text)
        #    self.add_target_butt.phrasegroup.add_target(self.gmg.caret.phrased_to, text, stay_enterable=True)
        #    self.gmg.caret.try_suggestion()
        self.grab_focus()

    def open_xml(self, insert = False) :
        '''Open (or insert) Glypher XML from file.'''

        chooser = gtk.FileChooserDialog(\
                      title=\
                         (("Insert" if insert else "Open")+" XML File"),
                      action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder(get_user_location()+'glypher/snippets/')
        chooser.set_default_response(gtk.RESPONSE_OK)
        resp = chooser.run()
        self.grab_focus()

        if resp == gtk.RESPONSE_CANCEL : chooser.destroy(); return
        elif resp == gtk.RESPONSE_OK : self.filename = chooser.get_filename()
        chooser.destroy()

        with open(self.filename) as f :
            xml_content = f.read()
            tree = ET.ElementTree(ET.XML(xml_content))
            self.set_xml(tree, insert=insert)

    def export(self) :
        '''Export Glypher as an image.'''

        if self.caret.attached_to is None :
            return

        root = self.get_xml()

        chooser = gtk.FileChooserDialog(\
                      title="Export File", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        
        extra_hbox = gtk.HBox()
        extra_hbox.pack_start(gtk.Label("Decoration"), False)
        decoration_chkb = gtk.CheckButton()
        extra_hbox.pack_start(decoration_chkb, False)
        extra_hbox.pack_start(gtk.Label("Padding"), False)
        padding_chkb = gtk.CheckButton()
        padding_chkb.set_active(True)
        extra_hbox.pack_start(padding_chkb, False)
        extra_hbox.pack_start(gtk.Label("Transparent"), False)
        transparent_chkb = gtk.CheckButton()
        extra_hbox.pack_start(transparent_chkb, False)
        extra_hbox.pack_start(gtk.Label("Scale"), False)
        scale_entr = gtk.Entry()
        scale_entr.set_text("3.")
        extra_hbox.pack_start(scale_entr, False)
        extra_hbox.show_all()

        chooser.set_extra_widget(extra_hbox)
        chooser.set_current_folder(get_user_home())
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_current_name('.svg')
        resp = chooser.run()
        self.grab_focus()

        if resp == gtk.RESPONSE_OK :
            filename = chooser.get_filename()
        else :
            chooser.destroy()
            return

        #f = open(filename, 'w')

        ent = self.main_phrase

        if padding_chkb.get_active() :
            padding = 10
        else :
            padding = 0

        debug_print(scale_entr.get_text())
        sc = float(scale_entr.get_text())

        if filename.endswith('.png') :
            cairo_svg_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                   int(sc*(int(ent.get_width())+2*padding)),
                                   int(sc*(int(ent.get_height())+2*padding)))
        else :
            cairo_svg_surface = cairo.SVGSurface(filename,
                                   int(sc*(int(ent.get_width())+2*padding)),
                                   int(sc*(int(ent.get_height())+2*padding)))
        cc = cairo.Context(cairo_svg_surface)

        cc.scale(sc, sc)

        if not transparent_chkb.get_active() :
            cc.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            cc.rectangle(0, 0, 
                (int(ent.get_width())+2*padding),
                (int(ent.get_height())+2*padding))
            cc.fill()

        dec = ent.show_decoration()
        ent.set_p('is_decorated', decoration_chkb.get_active())

        # Move to middle of padded surface
        cc.translate(padding-ent.config[0].bbox[0],
                     padding-ent.config[0].bbox[1])

        ent.set_p('is_decorated', dec)

        ent.draw(cc)

        if filename.endswith('.png') :
            cairo_svg_surface.write_to_png(filename)

        chooser.destroy()

    def _do_validate_formula(self, entr, params) :
        ok_butt, id_entr, cat_entr, sym_entr = params

        match = re.match('[a-zA-Z0-9_-]+$', id_entr.get_text())
        if match is None :
            ok_butt.set_sensitive(False)
            id_entr.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color('pink'))
        elif len(cat_entr.get_text()) == 0 or len(sym_entr.get_text()) == 0 :
            ok_butt.set_sensitive(False)
        else:
            ok_butt.set_sensitive(True)
            id_entr.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color('white'))

    def save_formula(self) :
        '''Save selected Glypher text as a formula.'''

        if self.caret.attached_to is None :
            return

        attached_root = self.caret.attached_to.get_xml()

        chooser = gtk.Dialog(\
                      title="Save as Formula", parent=self.get_toplevel(), 
                      flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)

        try :
            ok_butt = chooser.get_widget_for_response(gtk.RESPONSE_OK)
        except :
            ok_butt = chooser.get_action_area().get_children()[0]
        ok_butt.set_sensitive(False)

        vbox = gtk.VBox()

        preview_glyi = GlyphImage()
        preview_glyi.set_xml(ET.ElementTree(attached_root))
        preview_glyi.set_font_size(40)

        vbox.pack_start(preview_glyi)

        content_table_maker = PreferencesTableMaker()
        content_table_maker.append_heading("New formula")
        id_entr = gtk.Entry()
        content_table_maker.append_row("ID", id_entr,
                                       tip="Unique ASCII name (w/o whitespace)")
        title_entr = gtk.Entry()
        content_table_maker.append_row("Title", title_entr,
                                       tip="Informative title for user")

        sym_entr = gtk.Entry()
        content_table_maker.append_row("Symbol", sym_entr,
              tip="A one/two character symbol to include in the Toolbox")

        info_txvw = gtk.TextView()
        info_txvw.set_size_request(400, 100)
        content_table_maker.append_row("Description", info_txvw,
              tip="A short help text for the user")

        cat_entr = gtk.Entry()
        content_table_maker.append_row("Category", cat_entr,
              tip="A Toolbox formula category to add this to")

        wiki_entr = gtk.Entry()
        content_table_maker.append_row("Wikipedia", wiki_entr,
              tip="Title of Wikipedia page to link to")

        params = (ok_butt, id_entr, cat_entr, sym_entr)
        id_entr.connect("changed", self._do_validate_formula, params)
        cat_entr.connect("changed", self._do_validate_formula, params)
        sym_entr.connect("changed", self._do_validate_formula, params)

        vbox.pack_start(content_table_maker.make_table())
        chooser.get_content_area().add(vbox)
        chooser.get_content_area().show_all()
        resp = chooser.run()
        self.grab_focus()

        if resp == gtk.RESPONSE_OK :
            name = id_entr.get_text()
            title = title_entr.get_text()
            cat = cat_entr.get_text()
            sym = sym_entr.get_text()
            ib = info_txvw.get_buffer()
            info = ib.get_text(ib.get_start_iter(), ib.get_end_iter())
            wiki = wiki_entr.get_text()

            filename = get_user_location()+'glypher/formulae/'+name+'.xml'
            chooser.destroy()
        else :
            chooser.destroy()
            return
        
        f = open(filename, 'w')

        root = ET.Element("glypher")
        root.set("name", name)
        content_node = ET.SubElement(root, "content")
        content_node.append(attached_root)

        root.set("title", title)
        cat_node = ET.SubElement(root, "category")
        cat_node.text = cat
        sym_node = ET.SubElement(root, "symbol")
        sym_node.text = sym
        wiki_node = ET.SubElement(root, "wiki")
        wiki_node.text = wiki
        info_node = ET.SubElement(root, "info")
        info_node.text = info

        gutils.xml_indent(root)
        tree = ET.ElementTree(root)
        tree.write(f, encoding="utf-8")
        f.close()

    def save_xml(self) :
        '''Save selected Glypher XML to file.'''

        if self.caret.attached_to is None :
            return

        tree = self.get_xml()

        chooser = gtk.FileChooserDialog(\
                      title="Save XML File", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_current_folder(get_user_location()+'glypher/snippets/')
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_current_name('.xml')
        resp = chooser.run()
        self.grab_focus()

        if resp == gtk.RESPONSE_OK :
            filename = chooser.get_filename()
            chooser.destroy()
        else :
            chooser.destroy()
            return
        
        f = open(filename, 'w')
        gutils.xml_indent(tree.getroot())
        tree.write(f, encoding="utf-8")
        f.close()

    def open_phrasegroup(self) :
        chooser = gtk.FileChooserDialog(\
                      title="Open GlyphMaker XML File", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder(get_user_location())
        chooser.set_default_response(gtk.RESPONSE_OK)
        resp = chooser.run()
        if resp == gtk.RESPONSE_CANCEL : chooser.destroy(); return
        elif resp == gtk.RESPONSE_OK : self.filename = chooser.get_filename()
        chooser.destroy()

        pg = make_phrasegroup_by_filename(self.main_phrase, self.filename, operands = None)
        if isinstance(pg, str) :
            raise(RuntimeError(pg))
        self.caret.insert_entity(pg)
        self.grab_focus()

    def draw(self, cr, swidth, sheight):
        GlyphEntry.draw(self, cr, swidth, sheight)
        cr.save()
        cr.translate(*self.main_phrases_offsets[self.response_phrase])

        if self.draw_corner_art and not self.suspend_corner_art :
            bb = list(self.response_phrase.config[0].bbox)
            bb[0] -= 10
            bb[1] -= 10
            bb[2] = self.allocation.width - 30 - bb[0] - self.position[0]
            bb[3] = bb[3]-bb[1]
            box_colour = (1.0, 1.0, 0.7)
            draw.draw_box(cr, box_colour, bb)

        self.response_phrase.draw(cr)
        cr.restore()

    def set_status(self, string) :
        self.emit('status-update', string)

    def process_line(self) :
        self.response_phrase.empty()
        self.response_processor = lambda : parse_space_array(self.space_array, self.caret)
        input_line, response = GlyphEntry.process_line(self)

        if response is None :
            self.set_status("[No output]")
        elif isinstance(response, str) :
            self.response_phrase.append(make_word('Unsuccessful', None))
            self.set_status(str(response))
        elif response.am('entity') :
            self.response_phrase.append(response)
            response = self.response_phrase.get_entities()[0]
            self.set_status(input_line.to_string() + ' |==| ' + response.to_string())

            #input_line = input_line.OUT().copy()
            #response = response.get_entities()[0].copy() \
            #    if response.am('phrase') and len(response.get_entities()) == 1\
            #    else response.copy()
            self.i += 1
            i = self.i

            resp_thread = threading.Thread(None, self._make_response, None,
                                           args=(i, input_line, response))
            resp_thread.start()

        return response

    i = 0
    def _make_response(self, i, input_line, response) :
            #xml = input_line.OUT().get_xml(targets={}, top=False, full=False)
            #xml = ET.ElementTree(xml)
            #input_line = Parser.parse_phrasegroup(self.responses_phrase, xml, top=False)
            input_line = GlypherEntity.xml_copy(None, input_line)
            response = GlypherEntity.xml_copy(None, response)
            self._append_response(i, input_line, response)

    def _append_response(self, i, input_line, response) :
            #self.responses[i] = (input_line, response)
            #c = self.responses_phrase.get_cell(i, 1)
            #c.append(input_line)
            #c = self.responses_phrase.get_cell(i, 2)
            #c.append(response)
            g.add_response(i, input_line, response)

    def do_key_press_event(self, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        if (keyname == 'equal' and m_control) or (keyname == 'plus' and m_control) :
            phrase = self.main_phrase
            sympy_output = ""
            if m_control :
                output = ""
                string = phrase.to_string("maxima")
                if have_sympy :
                    try :
                        result = sympy.parsing.maxima.parse_maxima(string)
                        try : num = result.evalf()
                        except ValueError, AttributeError : num = "[Cannot evaluate]"
                        result = str(result) + " = " + str(num)
                    except ValueError :
                        result = "[Cannot parse]"
                    output += "parse_maxima: {" + string + ":: " + str(result) + "}"

                string = phrase.to_string("sympy")
                output += " || "
                if have_sympy :
                    try :
                        sympy_output = sympy.core.sympify(string)
                        try : num = sympy_output.evalf()
                        except ValueError, AttributeError : num = "[Cannot evaluate]"
                        result = str(sympy_output) + " = " + str(num)
                    except ValueError :
                        result = "[Cannot parse]"
                    output += "sympify: {" + string + ":: " + str(result) + "}"
                else :
                    output += " [NO SYMPY]"
            else :
                output = str(phrase) + phrase.to_string("string")
            self.set_status(output)
            self.response_phrase.empty()
            sympy_output = phrase.get_sympy().doit() if keyname == 'equal' else phrase.get_sympy().evalf()
            try :
                sy = interpret_sympy(self.response_phrase, sympy_output)
                self.response_phrase.append(sy)
            except GlypherTargetPhraseError as e :
                debug_print("Error : " + str(e))
        else :
            return GlyphEntry.do_key_press_event(self, event)
        self.queue_draw()
        return True
