from ..glypher.Widget import GlyphBasicGlypher
from ..utils import debug_print
from ..glypher.PhraseGroup import GlypherBracketedPhrase
import gtk
from ..aobject import *
from ..glypher.Word import make_word
from sympy.core.symbol import Symbol
from ..sims import Source

class GlypherSourceReference(GlypherBracketedPhrase) :
    source = None

    def __init__(self, parent, source, name) :
        GlypherBracketedPhrase.__init__(self, parent, bracket_shapes=('[',']'), auto=False)
        self.mes.append('reference')
        self.mes.append('source_reference')
        self.source = source
        obj = get_object_from_dictionary(source)
        source_name = make_word(name, self)
        source_name.set_bold(True)
        source_name.set_auto_italicize(False)
        source_name.set_italic(False)
        self.get_target('expression').adopt(source_name)
        self.set_recommending(self["expression"])
        self['expression'].set_font_size_scaling(0.6)
        source_name.set_enterable(False)
        self.get_target('expression').IN().set_enterable(False)
        self.set_rgb_colour([0.5, 0.4, 0])
    
    def get_sympy(self) :
        return Symbol('aesthete_source_'+self.source)

class Gluer(gtk.Frame, AObject) :
    line_height = 35.
    default_height = 560
    default_width = 360

    def __init__(self, env = None):
        gtk.Frame.__init__(self)
        AObject.__init__(self, "Gluer", env, view_object=True)
        self.connect("aesthete-property-change", lambda o, p, v, a : self.queue_draw())

        self.vbox = gtk.VBox()

        self.sources = []

        self.gmg = GlyphBasicGlypher(env=env, evaluable=False)
        self.gmg.main_phrase.move()
        self.gmg.main_phrase.set_enterable(True)
        self.gmg.main_phrase.set_attachable(True)
        self.gmg.main_phrase.line_length = self.default_width
        self.absorb_properties(self.gmg)
        self.vbox.pack_start(self.gmg)

        self.source_action = self.insert_source_ref

        self.add(self.vbox)
        self.show_all()

        self.log(1, "New Gluer initalized")

    sources = None
    def insert_source_ref(self, source) :
        self.sources.append(source)
        obj = get_object_from_dictionary(source)
        ref = GlypherSourceReference(None, str(len(self.sources)-1),
                                     obj.get_aname_nice())
        self.gmg.caret.insert_entity(ref)
        self.gmg.grab_focus()

        if self.base_cmbo.get_active_iter() is None :
            mdl = self.base_cmbo.get_model()
            it = mdl.get_iter_first()
            while it is not None and \
                    mdl.get_value(it,0) != source :
                it = mdl.iter_next(it)

            if it is not None :
                self.base_cmbo.set_active_iter(it)

    def get_method_window(self) :
        win = gtk.VBox()

        make_hbox = gtk.HBox()
        make_hbox.set_spacing(5)
        make_entr = gtk.Entry()
        make_entr.set_tooltip_text("Name for new Source")
        make_entr.set_width_chars(10)
        make_hbox.pack_start(make_entr)
        make_butt = gtk.Button()
        make_butt.set_tooltip_text("Generate Source")
        make_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_GOTO_LAST,
                                                     gtk.ICON_SIZE_BUTTON))
        make_butt.connect("clicked", lambda b : self.make_new_source(make_entr.get_text()))
        make_hbox.pack_start(make_butt, False)
        make_hbox.pack_start(gtk.Label('Base'), False)
        base_cmbo = gtk.ComboBox( get_object_dictionary().get_liststore_by_am('Source') )
        base_cmbo.set_size_request(100, -1)
        make_hbox.pack_start(base_cmbo)
        base_cllr = gtk.CellRendererText(); base_cmbo.pack_start(base_cllr); base_cllr.props.ellipsize = pango.ELLIPSIZE_END;
        base_cmbo.add_attribute(base_cllr, 'text', 1)
        self.base_cmbo = base_cmbo

        win.pack_start(make_hbox, False)

        icon_table = gtk.Table(1, 1)

        sim_butt = gtk.Button()
        sim_butt.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX,
                                                    gtk.ICON_SIZE_BUTTON))
        sim_butt.set_tooltip_text("Reference currently selected Source")
        sim_butt.set_sensitive(False)
        icon_table.attach(sim_butt, 0, 1, 0, 1)
        sim_butt.connect("clicked", lambda o : self.insert_source_ref(\
                            get_object_dictionary().selected_source))
        get_object_dictionary().connect(\
            'aesthete-selected-source-change',
            lambda tr : sim_butt.set_sensitive(True))


        win.pack_start(icon_table, False)

        win.show_all()

        return win

    def make_new_source(self, aname_nice) :
        sy = self.gmg.get_sympy()

        base_source = self.base_cmbo.get_active_iter()
        if base_source is None :
            return
        base_source = \
            self.base_cmbo.get_model().get_value(base_source, 0)

        cs = ComposedSource('composed', sy, sources=self.sources,
                            base_source=base_source)
        cs.set_aname_nice(aname_nice)
        self.gmg.grab_focus()

tol = 1e-7
class ComposedSource(Source) :
    resolution = None
    sympy_object = None
    def __init__(self, stem, sympy_object, sources, base_source, env = None, show = False, reloadable = False, resolution = 300) :
        self.resolution = resolution
        self.sympy_object = sympy_object
        self.sources = sources
        self.base_source = base_source
        Source.__init__(self, stem, env, show, reloadable)

    def source_type(self) :
        return get_object_from_dictionary(self.base_source).source_type()

    def source_get_values(self, time = None, multi_array = False, x_range = (0,1)) :
        debug_print(self.sympy_object.args)
        debug_print(self.sympy_object)
        sub_dict = {}
        for arg in list(self.sympy_object.atoms(Symbol)) :
            if str(arg).startswith('aesthete_source_') :
                name = str(arg)[len('aesthete_source_'):]
                sub_dict[name] =\
                get_object_from_dictionary(self.sources[int(name)])

        if len(sub_dict) == 0:
            raise RuntimeError('Need some other Source!')

        basis_source = get_object_from_dictionary(self.base_source)
        xa = basis_source.source_get_values(time=time, multi_array=False)

        value_dict = {}
        for source in sub_dict :
            value_dict[source] = sub_dict[source].source_get_values(time=time,
                multi_array=False)

        p = []

        for source in value_dict :
            if len(value_dict[source]) < len(xa) :
                raise RuntimeError( \
                    """Components don\'t match!
                    (length %d for %s < %d for %s)""" % \
                    (len(value_dict[source]), sub_dict[source].get_aname_nice(),
                    len(xa), basis_source.get_aname_nice()))

        for i in range(0, len(xa)) :
            x = xa[i][0]
            sub_val_dict = {'x':x}
            for source in value_dict :
                pair = value_dict[source][i]
                if abs(pair[0]-x) > tol :
                    raise RuntimeError(
                        """Components don\'t match!
                        (%lf for %s vs %lf for %s at point %d)""" %\
                        (pair[0], sub_dict[source].get_aname_nice(),
                         x, basis_source.get_aname_nice()))
                sub_val_dict['aesthete_source_'+source] = pair[1]
                y = self.sympy_object.subs(sub_val_dict)
            p.append( (x, float(y)) )

        if multi_array :
            return [{'values':p,'name':self.get_aname_nice()}]
        return p

    def source_get_max_dim(self) :
        return 2
