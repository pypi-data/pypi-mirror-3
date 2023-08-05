import glypher as g
import threading
from Widget import *
from ..utils import debug_print
import gtk
from .. import aobject

try :
    import sympy
    import sympy.parsing.maxima
    have_sympy = True
except ImportError :
    have_sympy = False

from Toolbox import *
from CharMap import *
from Interpret import *
from Caret import *
from Phrase import *
from Parser import *
from Alternatives import *

debugging = False

class Glypher (GlyphBasicGlypher) :
    response_phrase = None
    responses = None
    line_height = 35.
    default_height = 360
    default_width = 460

    def set_ui(self) :
        self.ui_action_group = gtk.ActionGroup('GlypherActions')
        self.ui_action_group.add_actions([\
        ('GlypherMenu', None, 'Glypher'),
            ('GlypherOpen', None, 'Open', None, None,
                lambda w : self.open_xml()),
            ('GlypherInsert', None, 'Insert', None, None,
                lambda w : self.open_xml(insert=True)),
            ('GlypherSave', None, 'Save', None, None,
                lambda w : self.save_xml()),
            ('GlypherGlyphMaker', None, 'Insert GlyphMaker', None, None,
                lambda w : self.open_phrasegroup()),
            ('GlypherExport', None, 'Export', None, None,
                lambda w : self.export()),
            ('GlypherShowLaTeX', None, 'Show LaTeX', None, None,
                lambda w : self.show_latex()),
            ('GlypherCopy', None, 'Copy'),
                ('GlypherCopyXML', None, 'Glypher XML', None, None,
                    lambda w : self.copy(fmt='xml')),
                ('GlypherCopySympy', None, 'Sympy', None, None,
                    lambda w : self.copy(fmt='sympy')),
                ('GlypherCopyMathML', None, 'MathML', None, None,
                    lambda w : self.copy(fmt='mathml')),
                ('GlypherCopyPython', None, 'Python', None, None,
                    lambda w : self.copy(fmt='python')),
                ('GlypherCopyLaTeX', None, 'LaTeX', None, None,
                    lambda w : self.copy(fmt='latex')),
                ('GlypherCopyUnicode', None, 'Unicode', None, None,
                    lambda w : self.copy(fmt='unicode')),
                ('GlypherCopyText', None, 'Text', None, None,
                    lambda w : self.copy(fmt='text')),
                                         ])
        self.ui_ui_string = '''
            <ui>
                <menubar name="MenuBar">
                    <menu action="GlypherMenu">
                        <menuitem action="GlypherOpen"/>
                        <menuitem action="GlypherInsert"/>
                        <menuitem action="GlypherSave"/>
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

    def _resize_to_allocation(self, allocation=None) :
        if allocation is not None :
            self.default_height = allocation.height
            self.default_width = allocation.width

        self.response_loc = (40, self.default_height-220, self.default_width-40, self.default_height-40)
        self.main_phrase.line_length = self.response_loc[2]-self.response_loc[0]
        self.response_phrase.line_length = self.response_loc[2]-self.response_loc[0]
        self.responses_phrase.set_max_dimensions((self.response_loc[2]-self.response_loc[0], self.response_loc[3]-self.response_loc[1]))
        self.responses_phrase.set_min_dimensions(self.responses_phrase.get_max_dimensions())
        self.responses_phrase.set_col_width(1, 0.5*(self.responses_phrase.get_max_dimensions()[0]-50))
        self.responses_phrase.set_col_width(2, 0.5*(self.responses_phrase.get_max_dimensions()[0]))
        self.responses_phrase.recalc_bbox()

        self.main_phrases_offsets[self.responses_main_phrase] = self.response_loc[0:2]
        self.main_phrases_offsets[self.response_phrase] = (self.position[0],
                                                           0.5*(self.position[1]+self.response_loc[1]))

    def __init__(self, position = (40, 80), env = None):
        GlyphBasicGlypher.__init__(self, name_root="Glypher", position=position, env=env)

        self.toolbox.caret = self.caret

        self.responses = {}

        if env is not None :
            self.connect('request-plot', env.toplevel.plot_source)

        ps = self.process_main_phrase_signal

        self.response_phrase = GlypherMainPhrase(ps, self.line_height, self.line_height, (0.0,0.0,0.0))
        self.responses_main_phrase = GlypherMainPhrase(ps, self.line_height, self.line_height, (0.0,0.0,0.0), anchor=('l','t'))
        self.responses_phrase = GlypherTable(self.responses_main_phrase, first_col=GlypherSymbol(None, " "), cell_padding=5, border=None)
        self.responses_main_phrase.append(self.responses_phrase)
        self.responses_main_phrase.set_font_size(20)
        self.responses_phrase.set_col_width(0, 50)
        self.responses_phrase.recalc_bbox()

        inpu_word = make_word('Statement', None); inpu_word.set_font_name('sans')
        self.responses_phrase.add_cell(0,1).append(inpu_word); inpu_word.set_bold(True)
        resp_word = make_word('Response', None); resp_word.set_font_name('sans')
        c = self.responses_phrase.add_cell(0,2)
        c.is_caching = True
        c.append(resp_word); resp_word.set_bold(True)

        self.responses_phrase.set_row_border_bottom(0)

        self.responses_phrase.set_col_colour(0, (0.8,0.0,0.0))
        self.responses_phrase.set_col_colour(1, (0.5,0.5,0.5))
        self.responses_phrase.set_col_colour(2, (0.8,0.5,0.5))
        self.responses_phrase.set_row_colour(0, (0.3,0.3,0.3))

        self.caret.enter_phrase(self.space_array)

        self.main_phrases = [self.main_phrase, self.responses_main_phrase, self.response_phrase]
        self.main_phrases_offsets = {self.main_phrase : self.position,
                                     self.response_phrase : None,
                                     self.responses_main_phrase : None}

        self._resize_to_allocation()

    def draw_responses(self, cr) :
        cr.save()
        bb = (self.responses_main_phrase.config[0].bbox[0],\
            self.responses_main_phrase.config[0].bbox[1],\
            self.responses_main_phrase.config[0].bbox[2],\
            self.responses_main_phrase.config[0].bbox[3]+10)
        cr.set_source_rgba(0.3, 0.2, 0, 0.2)
        area=(bb[0]-2, bb[2]+10, bb[1]-10, bb[3]+10)
        draw.trace_rounded(cr, area, 2)
        cr.fill()
        cr.set_source_rgba(0.975, 0.9625, 0.95, 0.5)
        #cr.rectangle(bb[0]-2, bb[1]-2, bb[2]-bb[0]+4, bb[3]-bb[1]+4)
        area=(bb[0]-6, bb[2]+6, bb[1]-16, bb[3]+6)
        draw.trace_rounded(cr, area, 2)
        cr.fill_preserve()

        cr.set_line_width(4)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.stroke()
        cr.restore()

        cr.save()
        #cr.translate(self.response_loc[0], self.response_loc[1])
        self.responses_main_phrase.draw(cr)
        #cr.translate(-self.response_loc[0], -self.response_loc[1])
        cr.restore()

    def reset_main_phrase(self, space_array=None) :
        GlyphBasicGlypher.reset_main_phrase(self)

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
        d.set_size_request(300, 200)
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

    def get_method_window(self) :
        vbox = gtk.VBox()
        self.toolbox = GlyphToolbox(self.caret, grab_entities=True)
        vbox.pack_start(gtk.Label("Useful Entities"))
        vbox.pack_start(self.toolbox)
        vbox.pack_start(gtk.HSeparator())
        vbox.pack_start(gtk.Label("Unicode Characters"))
        self.charmap = GlyphCharMap(self.caret)
        vbox.pack_start(self.charmap)

        settings_ntbk = gtk.Notebook()
        settings_ntbk.set_tab_pos(gtk.POS_LEFT)

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
                                       self.queue_draw()))
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

        settings_ntbk.append_page(general_vbox, gtk.Label("Gn"))

        vbox.pack_start(settings_ntbk)

        vbox.show_all()
        return vbox
    
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
        self.response_phrase.draw(cr)
        cr.restore()
        cr.save()
        cr.translate(*self.main_phrases_offsets[self.responses_main_phrase])
        self.draw_responses(cr)
        cr.restore()

    def set_status(self, string) :
        self.aes_append_status(None, string)

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
            self.set_status(input_line.to_string() + ' |==| ' + response.to_string())

            #input_line = input_line.OUT().copy()
            #response = response.get_entities()[0].copy() \
            #    if response.am('phrase') and len(response.get_entities()) == 1\
            #    else response.copy()
            self.i += 1
            i = self.i

            c = self.responses_phrase.add_cell(i, 0)
            c.append(make_word('[%d]' % i, c))
            c = self.responses_phrase.add_cell(i, 1)
            c.is_caching = True
            c = self.responses_phrase.add_cell(i, 2)
            c.is_caching = True

            resp_thread = threading.Thread(None, self._make_response, None,
                                           args=(i, input_line, response))
            resp_thread.start()

        return response

    i = 0
    def _make_response(self, i, input_line, response) :
            xml = input_line.OUT().get_xml(targets={}, top=False, full=False)
            xml = ET.ElementTree(xml)
            input_line = Parser.parse_phrasegroup(self.responses_phrase, xml, top=False)
            response = GlypherEntity.xml_copy(response)
            self._append_response(i, input_line, response)

    def _append_response(self, i, input_line, response) :
            self.responses[i] = (input_line, response)
            c = self.responses_phrase.get_cell(i, 1)
            c.append(input_line)
            c = self.responses_phrase.get_cell(i, 2)
            c.append(response)
            g.add_response(i, input_line, response)

    def do_key_press_event(self, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)
        m_shift = bool(event.state & gtk.gdk.SHIFT_MASK)
        m_alt = bool(event.state & gtk.gdk.MOD1_MASK)
        m_super = bool(event.state & gtk.gdk.SUPER_MASK)
        debug_print(keyname)
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
            debug_print(sympy_output)
            try :
                sy = interpret_sympy(self.response_phrase, sympy_output)
                self.response_phrase.append(sy)
            except GlypherTargetPhraseError as e :
                debug_print("Error : " + str(e))
        else :
            return GlyphBasicGlypher.do_key_press_event(self, event)
        self.queue_draw()
        return True
