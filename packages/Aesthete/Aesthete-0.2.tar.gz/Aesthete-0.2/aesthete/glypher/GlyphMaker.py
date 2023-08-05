import uuid
import glypher as g
import Mirror
import math
from types import *
from Toolbox import *
import ConfigWidgets
from ..utils import debug_print
import gtk
import re
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
from Widget import *

debugging = False
phrasegroups_dir = get_user_location() + 'glypher/phrasegroups/'

class GlyphMaker (gtk.Frame, aobject.AObject) :
    properties = None
    gmg = None
    xmlview = None
    vbox = None
    filename = None
    selected_entity = None
    getting_shortcut_mode = False

    def do_set_padding(self, entry, side) :
        if self.property_store.entity is None :
            return
        new_padding = entry.get_text()
        if len(new_padding) == 0 :
            new_padding = 0.0
        else :
            new_padding = float(new_padding)

        self.property_store.entity.set_padding(side, new_padding)
        self.gmg.queue_draw()

    def do_key_press_event(self, button, event) :
        if self.getting_shortcut_mode :
            if gtk.gdk.keyval_name(event.keyval) == 'Escape' :
                self.phrasegroup_keyboard_shortcut.get_child().set_text('[None]')
                self.do_keyboard_shortcut(self.phrasegroup_keyboard_shortcut)
            if gtk.gdk.keyval_name(event.keyval) == 'Return' :
                self.do_keyboard_shortcut(self.phrasegroup_keyboard_shortcut)
            else :
                self.phrasegroup_keyboard_shortcut.get_child().set_text(
                        gtk.accelerator_name(event.keyval, event.state))
                self.phrasegroup_keyboard_shortcut.get_child().set_ellipsize(pango.ELLIPSIZE_START)
            return True
        return False
        
    def do_keyboard_shortcut(self, button) :
        if self.getting_shortcut_mode :
            self.getting_shortcut_mode = False
            button.set_relief(gtk.RELIEF_NORMAL)
            self.phrasegroup_name.show()
            self.phrasegroup_latex_name.show()
            self.phrasegroup_title.show()
        else :
            self.getting_shortcut_mode = True
            button.set_relief(gtk.RELIEF_NONE)
            self.phrasegroup_name.hide()
            self.phrasegroup_latex_name.hide()
            self.phrasegroup_title.hide()

    def do_select(self, button) :
        self.gmg.caret.set_selected(self.property_store.entity)

    def do_inherited_property_view_edited(self, cell, path, new_text) :
        r = self.inherited_property_store[path]
        r[1] = new_text
        debug_print(r[2])
        self.property_store.entity.set_ip(r[0], make_val(new_text, r[2]) if new_text is not '' else None)
        self.property_store.entity.recalc_bbox()

    def do_property_view_edited(self, cell, path, new_text) :
        r = self.property_store[path]
        r[1] = new_text
        self.property_store.entity.set_p(r[0], make_val(new_text, r[2]))
        self.property_store.entity.recalc_bbox()

    def do_ae_toggled(self, toggle, att) :
        ent = self.property_store.entity
        if ent is None : return
        if att : ent.set_attachable(toggle.get_active())
        else :   ent.set_enterable(toggle.get_active())

    def do_rc_spin(self, spin, row) :
        ent = self.property_store.entity
        v = int(round(spin.get_value()))
        if ent is None or not ent.included() : return
        if row : ent.parent.add_row(v); ent.config[0].row = v
        else :     ent.parent.add_col(v); ent.config[0].col = v
        ent.parent.recalc_bbox()

    def highlight_codebuffer(self, codebuffer) :
        start = codebuffer.get_start_iter()
        codebuffer.remove_all_tags(start, codebuffer.get_end_iter())

        mat = start.forward_search('`', gtk.TEXT_SEARCH_VISIBLE_ONLY)

        while mat is not None :
            opening = mat[1]

            mat = mat[1].forward_search('`', gtk.TEXT_SEARCH_VISIBLE_ONLY)

            if mat is None :
                break

            closing = mat[0]

            text = opening.get_text(closing)

            tag = "name_highlight_unmatched"
            for row in self.targets_liss :
                if row[0] == text :
                    tag = "name_highlight_matched"

            codebuffer.apply_tag_by_name(tag, opening, closing)

            mat = mat[1].forward_search('`', gtk.TEXT_SEARCH_VISIBLE_ONLY)

    def new_default_phrasegroup_name(self) :
        self.default_phrasegroup_name = 'untitled-' + str(uuid.uuid4())
        self.phrasegroup_name.set_text(self.default_phrasegroup_name)
        
    def __init__(self, env = None):
        gtk.Frame.__init__(self)
        aobject.AObject.__init__(self, "GlyphMaker", env, view_object=True)
        self.connect("aesthete-property-change", lambda o, p, v, a : self.queue_draw())

        self.vbox = gtk.VBox()

        hbox = gtk.HBox(False, 4)
        self.vbox.pack_start(hbox, False)
        hbox.pack_start(gtk.Label("Name"), False)
        self.phrasegroup_name = gtk.Entry()
        hbox.pack_start(self.phrasegroup_name)
        hbox.pack_start(gtk.Label("Title"), False)
        self.phrasegroup_title = gtk.Entry()
        hbox.pack_start(self.phrasegroup_title)
        hbox.pack_start(gtk.Label("LaTeX Name"), False)
        self.phrasegroup_latex_name = gtk.Entry()
        self.default_phrasegroup_name = ""
        hbox.pack_start(self.phrasegroup_latex_name)
        hbox.pack_start(gtk.Label("Keyboard Shortcut"), False)
        self.phrasegroup_keyboard_shortcut = gtk.Button('[None]')
        self.phrasegroup_keyboard_shortcut.get_child().set_ellipsize(pango.ELLIPSIZE_START)
        self.phrasegroup_keyboard_shortcut.connect("clicked",
                                                   self.do_keyboard_shortcut)
        self.phrasegroup_keyboard_shortcut.connect("key-press-event",
                                                   self.do_key_press_event)
        hbox.pack_start(self.phrasegroup_keyboard_shortcut)

        self.gmg = GlyphBasicGlypher(env=env, evaluable=False)
        self.gmg.caret.editor_mode = True
        self.gmg.main_phrase.by_first_row = False
        self.gmg.main_phrase.move()
        self.gmg.main_phrase.set_enterable(True)
        self.gmg.main_phrase.set_attachable(True)
        self.absorb_properties(self.gmg)
        self.vbox.pack_start(self.gmg)
        self.log(1, "New GlyphMaker initalized")
        self.gmg.connect("content-changed", lambda o : self.update_xmlview())

        ex = gtk.expander_new_with_mnemonic("_Show Source")
        sc = gtk.ScrolledWindow()
        self.xmlview = gtk.TextView()
        self.xmlview.set_size_request(-1, 300)
        self.xmlview.get_buffer().set_text("")
        sc.add(self.xmlview)
        ex.add(sc)
        ex.set_expanded(False)
        self.vbox.pack_start(ex, False, False)

        toolbox = gtk.HBox()
        add_vbox = gtk.VBox()
        ex.connect("activate", lambda o : toolbox.hide() if not ex.get_expanded() else toolbox.show())
        add_vbox.pack_start(GlyphToolbox(self.gmg.caret, grab_entities=False, expanded=True, cols=10))

        code_ntbk = gtk.Notebook()
        code_ntbk.set_tab_pos(gtk.POS_LEFT)
        code_ntbk.set_property("scrollable", True)
        code_ntbk.set_property("enable-popup", True)

        cat_hbox = gtk.HBox()
        cat_hbox.pack_start(gtk.Label('Symbol'), False)

        self.symbol_entr = gtk.Entry()
        self.symbol_entr.set_size_request(20, -1)
        cat_hbox.pack_start(self.symbol_entr)

        self.category_entr = gtk.Entry()
        cat_hbox.pack_start(gtk.Label('Category'), False)
        cat_hbox.pack_start(self.category_entr)

        self.alt_entr = gtk.Entry()
        cat_hbox.pack_start(gtk.Label('Alternatives Cat'), False)
        cat_hbox.pack_start(self.alt_entr)

        add_vbox.pack_start(cat_hbox, False)

        self.sympy_view = gtk.TextView()
        self.sympy_view.set_wrap_mode(gtk.WRAP_CHAR)
        self.sympy_view.get_buffer().create_tag("name_highlight_matched",
                                                foreground="green")
        self.sympy_view.get_buffer().create_tag("name_highlight_unmatched",
                                                foreground="red")
        self.sympy_view.get_buffer().connect("changed", self.highlight_codebuffer)
        code_ntbk.append_page(self.sympy_view, gtk.Label('Sympy'))
        self.string_view = gtk.TextView()
        self.string_view.set_wrap_mode(gtk.WRAP_CHAR)
        self.string_view.get_buffer().connect("changed", self.highlight_codebuffer)
        self.string_view.get_buffer().create_tag("name_highlight_matched",
                                                foreground="green")
        self.string_view.get_buffer().create_tag("name_highlight_unmatched",
                                                foreground="red")
        code_ntbk.append_page(self.string_view, gtk.Label('Text'))
        self.latex_view = gtk.TextView()
        self.latex_view.set_wrap_mode(gtk.WRAP_CHAR)
        code_ntbk.append_page(self.latex_view, gtk.Label('LaTeX'))
        self.latex_view.get_buffer().connect("changed", self.highlight_codebuffer)
        self.latex_view.get_buffer().create_tag("name_highlight_matched",
                                                foreground="green")
        self.latex_view.get_buffer().create_tag("name_highlight_unmatched",
                                                foreground="red")

        other = gtk.Table(1, 2)
        other.attach(gtk.Label("Wiki"), 0, 1, 0, 1, False, False)
        self.wiki_entr = gtk.Entry()
        other.attach(self.wiki_entr, 0, 1, 1, 2)
        code_ntbk.append_page(other, gtk.Label("Other"))

        self.info_view = gtk.TextView()
        self.info_view.set_wrap_mode(gtk.WRAP_CHAR)
        code_ntbk.append_page(self.info_view, gtk.Label('Info'))

        code_ntbk.set_size_request(300, -1)

        add_vbox.pack_start(code_ntbk)

        mathml_hbox = gtk.HBox()
        mathml_hbox.pack_start(gtk.Label("Content MathML operation"), False)
        self.phrasegroup_mathml_op = gtk.Entry()
        mathml_hbox.pack_start(self.phrasegroup_mathml_op)
        add_vbox.pack_start(mathml_hbox, False)

        add_hbox = gtk.HBox()
        self.add_target_butt = gtk.Button('Make Phrase into Target')
        self.add_target_butt.connect("clicked", self.do_add_target)
        add_hbox.pack_start(self.add_target_butt)
        self.break_word_butt = gtk.Button('Break Word')
        self.break_word_butt.connect("clicked", self.do_break_word)
        add_hbox.pack_start(self.break_word_butt)
        self.selection_mirror_butt = gtk.Button('Insert Selection Mirror')
        self.selection_mirror_butt.connect("clicked", self.do_selection_mirror)
        add_hbox.pack_start(self.selection_mirror_butt)
        add_vbox.pack_start(add_hbox, False)
        toolbox.pack_start(add_vbox)

        self.targets_liss = gtk.ListStore(gobject.TYPE_STRING)
        self.targets_liss.append(('[None]',))
        self.targets_liss.connect("row-changed", lambda tl, p, i : \
            (self.highlight_codebuffer(self.latex_view.get_buffer()),
             self.highlight_codebuffer(self.sympy_view.get_buffer()),
             self.highlight_codebuffer(self.string_view.get_buffer())))

        sides_hbox = gtk.HBox()
        sides_hbox.pack_start(gtk.Label("LHS"), False)
        lhs_cell = gtk.CellRendererText()
        self.lhs_cmbo = gtk.ComboBox(self.targets_liss)
        self.lhs_cmbo.set_active(0)
        self.lhs_cmbo.pack_start(lhs_cell)
        self.lhs_cmbo.add_attribute(lhs_cell, 'text', 0)
        self.lhs_cmbo.connect("changed", self.do_set_side, True)
        sides_hbox.pack_start(self.lhs_cmbo)
        sides_hbox.pack_start(gtk.Label("RHS"), False)
        rhs_cell = gtk.CellRendererText()
        self.rhs_cmbo = gtk.ComboBox(self.targets_liss)
        self.rhs_cmbo.set_active(0)
        self.rhs_cmbo.pack_start(rhs_cell)
        self.rhs_cmbo.add_attribute(rhs_cell, 'text', 0)
        self.rhs_cmbo.connect("changed", self.do_set_side, False)
        sides_hbox.pack_start(self.rhs_cmbo)
        add_vbox.pack_start(sides_hbox, False)

        self.vbox.pack_start(toolbox, False)

        self.property_store = gtk.ListStore(str, str, str)
        property_view = gtk.TreeView(self.property_store)
        property_view_cren0 = gtk.CellRendererText()
        property_view_cren1 = gtk.CellRendererText()
        property_view_cren1.set_property('editable', True)
        property_view_cren1.connect('edited', self.do_property_view_edited)
        property_view_col0 = gtk.TreeViewColumn('Property', property_view_cren0, text=0)
        property_view_col1 = gtk.TreeViewColumn('Value', property_view_cren1, text=1)
        property_view.append_column(property_view_col0)
        property_view.append_column(property_view_col1)
        self.gmg.caret.connect("changed-attached-to", lambda o, s, l : self.set_property_store())
        sc1 = gtk.ScrolledWindow()
        sc1.add(property_view)
        ex1 = gtk.expander_new_with_mnemonic("_Properties")
        ex1.add(sc1)

        self.inherited_property_store = gtk.ListStore(str, str, str)
        inherited_property_view = gtk.TreeView(self.inherited_property_store)
        inherited_property_view_cren0 = gtk.CellRendererText()
        inherited_property_view_cren1 = gtk.CellRendererText()
        inherited_property_view_cren1.set_property('editable', True)
        inherited_property_view_cren1.connect('edited', self.do_inherited_property_view_edited)
        inherited_property_view_col0 = gtk.TreeViewColumn('Property', inherited_property_view_cren0, text=0)
        inherited_property_view_col1 = gtk.TreeViewColumn('Value', inherited_property_view_cren1, text=1)
        inherited_property_view.append_column(inherited_property_view_col0)
        inherited_property_view.append_column(inherited_property_view_col1)
        sc2 = gtk.ScrolledWindow()
        sc2.add(inherited_property_view)
        ex2 = gtk.expander_new_with_mnemonic("_Inherited Properties")
        ex2.add(sc2)

        ent_vbox = gtk.VBox()
        ent_vbox.set_size_request(150, 350)
        self.ent_label = gtk.Label()
        ent_vbox.pack_start(self.ent_label, False)
        fm_hbox = gtk.HBox()
        self.fm_mes = gtk.combo_box_new_text()
        self.fm_mes.set_title('Mes')
        self.fm_mes.set_tooltip_text('Who am I?')
        fm_hbox.pack_start(self.fm_mes)
        self.fm_mes.connect("changed", self.do_fm_mes_changed)
        self.fm_ancs = gtk.combo_box_new_text()
        self.fm_ancs.set_title('Ancestors')
        self.fm_ancs.set_tooltip_text('Who are my ancestors?')
        self.fm_ancs.connect("changed", self.do_fm_ancs_changed)
        fm_hbox.pack_start(self.fm_ancs)
        ent_vbox.pack_start(fm_hbox, False)

        select_entity_butt = gtk.Button("Select")
        select_entity_butt.connect("clicked", self.do_select)
        ent_vbox.pack_start(select_entity_butt, False)

        scaling_hbox = gtk.HBox()
        self.scaling_entr = gtk.Entry()
        scaling_hbox.pack_start(self.scaling_entr)
        scaling_butt = gtk.Button("Set scaling")
        scaling_hbox.pack_start(scaling_butt)
        scaling_butt.connect("clicked", self.do_scaling_butt_clicked)
        ent_vbox.pack_start(scaling_hbox, False)

        row_col_hbox = gtk.HBox()
        row_col_hbox.pack_start(gtk.Label("Row"), False)
        row_adj = gtk.Adjustment(step_incr=1)
        self.row_spin = gtk.SpinButton(row_adj)
        self.row_spin.connect("value-changed", self.do_rc_spin, True)
        row_col_hbox.pack_start(self.row_spin)
        row_col_hbox.pack_start(gtk.Label("Col"), False)
        col_adj = gtk.Adjustment(step_incr=1)
        self.col_spin = gtk.SpinButton(col_adj)
        self.col_spin.connect("value-changed", self.do_rc_spin, False)
        row_col_hbox.pack_start(self.col_spin)
        ent_vbox.pack_start(row_col_hbox, False)

        padding_hbox = gtk.HBox()
        padding_hbox.pack_start(gtk.Label("Padd."), False)
        self.padding_entrs = []
        for i in range(0, 4) :
            e = gtk.Entry()
            self.padding_entrs.append(e)
            padding_hbox.pack_start(e)
            e.connect("changed", self.do_set_padding, i)
        ent_vbox.pack_start(padding_hbox, False)

        att_ent_hbox = gtk.HBox()
        self.att_chkb = gtk.CheckButton("Attach")
        self.att_chkb.connect("toggled", self.do_ae_toggled, True)
        att_ent_hbox.pack_start(self.att_chkb, False)
        self.ent_chkb = gtk.CheckButton("Enter")
        self.ent_chkb.connect("toggled", self.do_ae_toggled, False)
        att_ent_hbox.pack_start(self.ent_chkb, False)
        ent_vbox.pack_start(att_ent_hbox, False)

        self.config_widget_fram = gtk.Frame()
        ent_vbox.pack_start(self.config_widget_fram, False)
        
        ent_vbox.pack_start(ex1, False)
        ent_vbox.pack_start(ex2, False)
        toolbox.pack_start(ent_vbox)

        self.add(self.vbox)
        self.show_all()
        self.gmg.grab_focus()

        self.new()
    
    def do_scaling_butt_clicked(self, butt) :
        sc = float(self.scaling_entr.get_text())
        ent = self.property_store.entity
        if ent is None : return
        ent.set_size_scaling(sc)

    def do_set_side(self, cmbo, lhs=True) :
        if not cmbo.get_active_iter() :
            return
        target = cmbo.get_model().get_value(cmbo.get_active_iter(), 0)
        pg = self.add_target_butt.phrasegroup
        if target is None or pg is None :
            return

        if target == '[None]' :
            target = None

        if lhs :
            pg.set_lhs_target(target)
        else :
            pg.set_rhs_target(target)

    def do_add_target(self, butt) :
        if self.add_target_butt.phrasegroup is None : return
        dialog = gtk.Dialog(title="Target name", parent=self.add_target_butt.get_toplevel(),\
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        e = gtk.Entry()
        dialog.vbox.pack_start(e)
        dialog.show_all()
        resp = dialog.run()
        text = e.get_text()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK :
            debug_print(text)
            self.gmg.caret.phrased_to.target_name = text
            self.add_target_butt.phrasegroup.add_target(self.gmg.caret.phrased_to, text, stay_enterable=True)
            self.targets_liss.append((text,))
            self.gmg.caret.try_suggestion()
        self.gmg.grab_focus()
    
    def do_break_word(self, butt) :
        if self.gmg.caret.phrased_to.am('word') :
            self.gmg.caret.exit_phrase()
            self.gmg.caret.reset()
        self.gmg.grab_focus()

    def do_selection_mirror(self, butt) :
        selection = self.gmg.caret.get_selected()
        mirror = Mirror.make_mirror(self.gmg.caret.phrased_to,
                                    selection[0])
        self.gmg.caret.insert_entity(mirror)

    def set_property_store(self, anc = 0) :
        self._is_fm_ancs_changeable = False

        self.property_store.clear()
        self.scaling_entr.set_text('')
        self.inherited_property_store.clear()
        self.fm_mes.get_model().clear()
        self.fm_ancs.get_model().clear()
        self.ent_label.set_text('[None]')
        self.ent_label.set_tooltip_text('[None]')
        self.property_store.entity = None

        ent = self.gmg.caret.attached_to

        self.add_target_butt.set_sensitive(False)

        tl = self.targets_liss
        tl.clear()
        self.lhs_cmbo.set_sensitive(False)
        self.rhs_cmbo.set_sensitive(False)

        self.break_word_butt.set_sensitive(self.gmg.caret.phrased_to.am('word'))

        for e in self.padding_entrs :
            e.set_text("")
            e.set_sensitive(False)

        for s in (self.row_spin, self.col_spin) :
            a = s.get_adjustment()
            s.set_value(0)
            a.lower = 0; a.upper = 0

        for s in (self.att_chkb, self.ent_chkb) :
            s.set_active(False)
        
        if ent is None :
            return

        pgs = filter(lambda a : a.mes[-1] == 'phrasegroup' or \
                     a.mes[-1] == self.phrasegroup_name.get_text(),
                     ent.get_ancestors())
        self.add_target_butt.phrasegroup = pgs[0] if len(pgs) > 0 else None
        self.add_target_butt.set_sensitive(len(pgs)>0)

        pg = self.add_target_butt.phrasegroup
        if pg :
            tl.append(("[None]",))
            for target in pg.target_phrases :
                it = tl.append((target,))
                if target == pg.lhs_target :
                    self.lhs_cmbo.set_active_iter(it)
                if target == pg.rhs_target :
                    self.rhs_cmbo.set_active_iter(it)
            if pg.lhs_target is None :
                self.lhs_cmbo.set_active(0)
            if pg.rhs_target is None :
                self.rhs_cmbo.set_active(0)

            self.lhs_cmbo.set_sensitive(True)
            self.rhs_cmbo.set_sensitive(True)
        self.property_store.entity = ent.get_ancestors()[anc]

        for i in range(0, 4) :
            paddstr = str(ent.padding[i])
            if paddstr != "0.0" :
                self.padding_entrs[i].set_text(paddstr)
            self.padding_entrs[i].set_sensitive(True)

        fm = ent.format_me()
        lab = ent.to_string()
        self.ent_label.set_text(lab)
        self.ent_label.set_tooltip_text(fm[0])

        self.scaling_entr.set_text(str(ent.get_size_scaling()))

        self.row_spin.set_value(ent.config[0].row)
        self.col_spin.set_value(ent.config[0].col)
        self.att_chkb.set_active(ent.get_attachable())
        if ent.am('phrase') :
            self.ent_chkb.set_active(ent.get_enterable())
        a = self.row_spin.get_adjustment()
        b = self.col_spin.get_adjustment()
        if ent.included() :
            a.upper, a.lower = ent.parent.row_range()
            b.upper, b.lower = ent.parent.col_range()
            a.upper += 1; b.upper += 1
            a.lower -= 1; b.lower -= 1

        for a in ent.mes : self.fm_mes.append_text(a)
        self.fm_mes.set_active(len(ent.mes)-1)
        for a in ent.get_ancestors() : self.fm_ancs.append_text(a.mes[-1])

        if self.gmg.caret.phrased_to in ent.get_ancestors() :
            n = ent.get_ancestors().index(self.gmg.caret.phrased_to)
            self.fm_ancs.set_active(n)
        else :
            self.fm_ancs.set_active(-1)

        props = set(ent.default_properties.keys() + ent.properties.keys())
        for p in props :
            val = ent.get_p(p)
            it = self.property_store.append([p, val, type(val).__name__])
        for p in ent.inherited_properties :
            val = ent.get_ip(p) if p in ent.inherited_properties_overrides else None
            it = self.inherited_property_store.append([p, val if val is not None else '', type(val).__name__])
        
        self._is_fm_ancs_changeable = True

    _is_fm_ancs_changeable = True
    def do_fm_ancs_changed(self, cmbo) :
        if self._is_fm_ancs_changeable and cmbo.get_active() >= 0 :
            debug_print(cmbo.get_active_text())
            self.gmg.caret.change_attached(self.property_store.entity.get_ancestors()[cmbo.get_active()])

    def do_fm_mes_changed(self, cmbo) :
        ent = self.property_store.entity
        if ent is None : return
        w = self.config_widget_fram.get_child()
        if w is not None : self.config_widget_fram.remove(w)
        cw = ConfigWidgets.get_config_widget(cmbo.get_active_text(),
                                             self.property_store.entity,
                                             self.gmg.caret)
        if cw is not None : self.config_widget_fram.add(cw)

    def new(self) :
        self.filename = None
        self.gmg.clear()
        pg = GlypherPhraseGroup(self.gmg.main_phrase)
        pg.edit_mode = True
        self.new_default_phrasegroup_name()
        self.set_property_store()
        self.gmg.caret.insert_entity(pg)
        pg.set_recommending(pg)
        self.queue_draw()
        self.phrasegroup_name.grab_focus()

    def get_method_window(self) :
        vbox = gtk.VBox()
        new_butt = gtk.Button(stock=gtk.STOCK_NEW)
        new_butt.connect("clicked", lambda o : self.new())
        vbox.pack_start(new_butt)
        open_butt = gtk.Button(stock=gtk.STOCK_OPEN)
        open_butt.connect("clicked", lambda o : self.open())
        vbox.pack_start(open_butt)
        save_butt = gtk.Button(stock=gtk.STOCK_SAVE)
        save_butt.connect("clicked", lambda o : self.save())
        vbox.pack_start(save_butt)
        save_as_butt = gtk.Button(stock=gtk.STOCK_SAVE_AS)
        save_as_butt.connect("clicked", lambda o : self.save(save_as=True))
        vbox.pack_start(save_as_butt)
        vbox.show_all()
        #config_butt = gtk.Button(self.get_aname_nice()+'...')
        #config_butt.set_relief(gtk.RELIEF_HALF)
        #self.connect("aesthete-aname-nice-change", lambda o, a, v : self.set_label_for_button(config_butt,v))
        #hbox.pack_start(config_butt)
        #remove_butt = gtk.Button(); remove_butt.add(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_SMALL_TOOLBAR))
        #remove_butt.connect("clicked", lambda o : self.self_remove())
        #hbox.pack_start(remove_butt, False)
        return vbox
    
    def _do_open_selection_changed(self, fc, pw) :
        fn = fc.get_preview_filename()
        pw.clear()
        if fn is not None and fn != '' :
            try :
                debug_print(fn)
                tree = ET.parse(fn)
                pw.set_xml(tree, top=True)
            except IOError :
                return

    def open(self) :
        chooser = gtk.FileChooserDialog(\
                      title="Open GlyphMaker XML File", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder(phrasegroups_dir)
        chooser.set_default_response(gtk.RESPONSE_OK)

        ge = GlyphEntry(interactive=False)
        ge.show_all()
        chooser.set_preview_widget(ge)
        chooser.connect("selection-changed", self._do_open_selection_changed, ge)

        resp = chooser.run()
        if resp == gtk.RESPONSE_CANCEL : chooser.destroy(); return
        elif resp == gtk.RESPONSE_OK : self.filename = chooser.get_filename()
        chooser.destroy()

        self.gmg.reset_main_phrase()
        pg = make_phrasegroup_by_filename(self.gmg.main_phrase, self.filename, operands = None)

        pg.edit_mode = True

        root = ET.parse(self.filename).getroot()
        sympy_el = root.find("sympy")
        if sympy_el is not None :
            sympy_text = re.sub('self\[["\']([^"\']*)["\']\]\.get_sympy\(\)',
                                "`\\1`",
                                sympy_el.text)
            self.sympy_view.get_buffer().set_text(sympy_text)

        string_el = root.find("string")
        if string_el is not None :
            string_text = re.sub(unicode('self\[["\']([^"\']*)["\']\]\.to_string\(\)'),
                                unicode("`\\1`"),
                                string_el.text)
            self.string_view.get_buffer().set_text(string_text)

        latex_el = root.find("latex")
        if latex_el is not None :
            latex_text = re.sub('self\[["\']([^"\']*)["\']\]\.to_latex\(\)',
                                "`\\1`",
                                latex_el.text)
            self.latex_view.get_buffer().set_text(latex_text)

        info_el = root.find("info")
        if info_el is not None :
            self.info_view.get_buffer().set_text(info_el.text)

        wiki_el = root.find("wiki")
        if wiki_el is not None :
            self.wiki_entr.set_text(wiki_el.text)

        symbol_el = root.find("symbol")
        if symbol_el is not None : self.symbol_entr.set_text(symbol_el.text)
        category_el = root.find("category")
        if category_el is not None : self.category_entr.set_text(category_el.text)
        alt_el = root.find("alternatives")
        if alt_el is not None : self.alt_entr.set_text(alt_el.text)

        self.phrasegroup_name.set_text(root.tag)
        ln = root.get('latex_name')
        self.phrasegroup_latex_name.set_text(ln if ln is not None else '')
        ln = root.get('title')
        self.phrasegroup_title.set_text(ln if ln is not None else '')

        ln = root.get('mathml')
        self.phrasegroup_mathml_op.set_text(ln if ln is not None else '')

        ln = root.find('shortcut')
        self.phrasegroup_keyboard_shortcut.get_child().set_text(ln.text \
                                                     if ln is not None else \
                                                     '[None]')
        self.phrasegroup_keyboard_shortcut.get_child().set_ellipsize(pango.ELLIPSIZE_START)

        if isinstance(pg, str) :
            raise(RuntimeError(pg))
        self.gmg.caret.change_attached(self.gmg.main_phrase)
        self.gmg.caret.insert_entity(pg)

        self.gmg.grab_focus()

    target_re = None
    def get_xml(self) :
        if len(self.gmg.main_phrase.get_entities()) == 0 : return None
        root = self.gmg.main_phrase.get_entities()[0].get_xml(full=True,
                                                              top=True)
        debug_print(self.gmg.main_phrase.get_entities()[0].format_me())
        debug_print(ET.tostring(root))

        b = self.latex_view.get_buffer()
        latex_text = b.get_text(b.get_start_iter(), b.get_end_iter())

        debug_print(latex_text)
        if len(latex_text) > 0 :
            latex_text = re.sub("`([^`]*)`", 'self["\\1"].to_latex()',
                                latex_text)
            latex_element = ET.SubElement(root, 'latex')
            latex_element.text = latex_text

        b = self.sympy_view.get_buffer()
        sympy_text = b.get_text(b.get_start_iter(), b.get_end_iter())
        if len(sympy_text) > 0 :
            sympy_text = re.sub("`([^`]*)`",
                                'self["\\1"].get_sympy()',
                                sympy_text)
            sympy_element = ET.SubElement(root, 'sympy')
            sympy_element.text = sympy_text

        b = self.string_view.get_buffer()
        string_text = b.get_text(b.get_start_iter(), b.get_end_iter())
        if len(string_text) > 0 :
            string_text = re.sub(unicode("`([^`]*)`"),
                                 unicode('self["\\1"].to_string()'),
                                string_text)
            string_element = ET.SubElement(root, 'string')
            string_element.text = string_text

        b = self.info_view.get_buffer()
        info_text = b.get_text(b.get_start_iter(), b.get_end_iter())
        if len(info_text) > 0 :
            info_element = ET.SubElement(root, 'info')
            info_element.text = info_text

        t = self.wiki_entr.get_text()
        if len(t) > 0 :
            ET.SubElement(root, 'wiki').text = t

        t = self.symbol_entr.get_text()
        if len(t) > 0 :
            ET.SubElement(root, 'symbol').text = t

        t = self.category_entr.get_text()
        if len(t) > 0 :
            ET.SubElement(root, 'category').text = t

        t = self.alt_entr.get_text()
        if len(t) > 0 :
            ET.SubElement(root, 'alternatives').text = t

        t = self.phrasegroup_name.get_text()
        if len(t) > 0 :
            root.tag = t
        else :
            root.tag = self.default_phrasegroup_name

        t = self.phrasegroup_latex_name.get_text()
        if len(t) > 0 :
            root.set('latex_name', t)

        t = self.phrasegroup_title.get_text()
        if len(t) > 0 :
            root.set('title', t)

        t = self.phrasegroup_mathml_op.get_text()
        if len(t) > 0 :
            root.set('mathml', t)

        t = self.phrasegroup_keyboard_shortcut.get_child().get_text()
        if t != '[None]' :
            shortcut = ET.SubElement(root, 'shortcut')
            shortcut.text = t

        return root
        #space_array = self.gmg.main_phrase.entities[0]
        #if space_array.get_op_count() > 1 :
        #    root = space_array.get_xml()
        #else :
        #    if len(space_array.get_target('pos0').get_entities()) == 0 : return None
        #    root = space_array.get_target('pos0').get_entities()[0].get_xml()
        #return root

    def save(self, save_as = False) :
        root = self.get_xml()

        if root is None :
            self.gmg.grab_focus()

        if self.filename is None or save_as :
            chooser = gtk.FileChooserDialog(\
                          title="Save GlyphMaker XML File", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                          buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
            chooser.set_current_folder(phrasegroups_dir)
            chooser.set_default_response(gtk.RESPONSE_OK)
            chooser.set_current_name(root.tag + '.xml')
            resp = chooser.run()
            if resp == gtk.RESPONSE_OK :
                filename = chooser.get_filename()
                debug_print(filename)
                chooser.destroy()
                if filename is None or filename == '' : return
                self.filename = filename
            else :
                chooser.destroy()
                return
        gutils.xml_indent(root)
        tree = ET.ElementTree(root)
        tree.write(self.filename, encoding="utf-8")

        self.gmg.grab_focus()

    def update_xmlview(self) :
        root = self.get_xml()
        if root is not None :
            gutils.xml_indent(root)
            self.xmlview.get_buffer().set_text(ET.tostring(root))

    #PROPERTIES
    def get_aesthete_properties(self):
        return { }
    #BEGIN PROPERTIES FUNCTIONS
    #END PROPERTIES FUNCTIONS

    def __del__(self) :
        aobject.AObject.__del__(self)
