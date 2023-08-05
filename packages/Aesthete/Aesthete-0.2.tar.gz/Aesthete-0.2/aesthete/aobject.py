import re
import shutil
from utils import debug_print, debug_print_stack
import traceback
import os
import xml.etree.ElementTree as ET
import details
import paths
import pango
import matplotlib
import alogger
import gobject
import gtk

ICON_SIZE_PREFERENCE =\
        gtk.icon_size_register('aes-icon-size-preference', 8, 8)

def check_float(var) :
    if var == '' or var is None :
        return False
    try : float(var)
    except ValueError :
        return False
    if var[0] == '.' or var[-1] == '.' :
        return False
    return True

class Env :
    logger = None
    action_panel = None
    toplevel = None

    def __init__ (self, logger = None, action_panel = None, toplevel = None) :
        self.logger = logger
        self.action_panel = action_panel
        self.toplevel = toplevel
        
def butt_adj(obj, butt, propname) :
    get = obj.aesthete_properties[(propname, obj.get_aname())][1]
    if (obj.get_preference(propname) == str(get())) :
        if not butt.get_active() : obj.set_preference(propname, None)
    else :
        if butt.get_active() : obj.set_preference(propname, str(get()))

def col_to_tup_str (c) : string = '('+str(c.red/65535.0)+','+str(c.green/65535.0)+','+str(c.blue/65535.0)+')'; return string

def mpl_to_tuple (c) : return tuple(map(float,matplotlib.colors.colorConverter.to_rgb(c)))

font_weight_hash = {
    pango.WEIGHT_ULTRALIGHT : "ultralight",\
    pango.WEIGHT_LIGHT : "light",\
    pango.WEIGHT_NORMAL : "normal",\
    pango.WEIGHT_BOLD : "bold",\
    pango.WEIGHT_ULTRABOLD : "ultrabold",\
    pango.WEIGHT_HEAVY : "heavy"
}
font_style_hash = {
    pango.STYLE_NORMAL : "normal",
    pango.STYLE_ITALIC : "italic",
    pango.STYLE_OBLIQUE : "oblique"
}
font_variant_hash = {
    pango.VARIANT_NORMAL : "normal",
    pango.VARIANT_SMALL_CAPS : "small-caps"
}
font_variant_bhash = {}
for k in font_variant_hash : font_variant_bhash[font_variant_hash[k]] = k
font_style_bhash = {}
for k in font_style_hash : font_style_bhash[font_style_hash[k]] = k
font_weight_bhash = {}
for k in font_weight_hash : font_weight_bhash[font_weight_hash[k]] = k

def update_combo (cmbo, lv) :
    mdl = cmbo.get_model()
    for row in mdl : mdl.remove(row.iter)
    for v in lv : cmbo.append_text(v)

def update_combo_select(cmbo, v) :
    mdl = cmbo.get_model()
    for row in mdl :
        if row[0] == v : cmbo.set_active_iter(row.iter)

def update_object_combo (cmbo, lv) :
    mdl = cmbo.get_model()
    for row in mdl : mdl.remove(row.iter)
    for v in lv : mdl.append((v, get_object_from_dictionary(v).get_aname_nice()))

def font_to_mpl (label_props, val) :
    fdes = pango.FontDescription(val)
    label_props.set_name(fdes.get_family()); label_props.set_size(fdes.get_size()/pango.SCALE)
    label_props.set_style(font_style_hash[fdes.get_style()])
    label_props.set_weight(font_weight_hash[fdes.get_weight()])
    label_props.set_variant(font_variant_hash[fdes.get_variant()])

def mpl_to_font (label_props) :
    fdes = pango.FontDescription()
    fdes.set_family(label_props.get_name()); fdes.set_size(int(label_props.get_size_in_points()*pango.SCALE))
    fdes.set_style(font_style_bhash[label_props.get_style()])
    fdes.set_weight(font_weight_bhash[label_props.get_weight()])
    fdes.set_variant(font_variant_bhash[label_props.get_variant()])
    return fdes.to_string()

def string_to_float_tup (string) :
  string_tuple = string.split(',')
  float_list = []
  for string_entry in string_tuple :
    entry_match = re.match('[^\d]*([\d\.]+)[^\d]*', string_entry)
    float_list.append(float(entry_match.group(1)))
  return tuple(float_list)

#PROPERTIES FUNCTIONS
#Remember that the get_ should never return None
#Properties are phrased as 'name' : [change_cb, get_cb, log changes]

class AObject(gobject.GObject) :
    aname = None
    aname_root = None
    aname_num = 0
    aname_xml = None

    # While we can add as many loggers as we desire,
    # this approach allows us to expect every object
    # to be logging somewhere
    logger = None
    logger_con = None

    aesthete_properties = None
    property_manager = False
    property_manager_conn = None
    property_store = None

    method_children = None
    method_window = None

    view_object = False

    status_id = None
    row_changed_conn = -1

    editable_aname_nice = True

    absorber_win = None
    absorber_conn = None
    absorber_ann_conn = None
    absorber_as = None
    absorber = None

    aesthete_method_widgets = None

    mes = None
    property_connections = None

    aesthete_xml = None

    def get_arepr(self) :
        if self.get_aesthete_xml() is not None :
            return self.get_aesthete_xml()
        return self.get_aname_nice()

    def set_aesthete_xml(self, xml) :
        self.aesthete_xml = xml
        # Trigger redisplay
        self.change_property('name_nice', self.get_aname_nice())

    def get_aesthete_xml(self) :
        return self.aesthete_xml

    def print_out(self, op, pc, pn) :
        op.cancel()

    def __init__(self, name_root, env = None, show = True, property_manager = True, view_object = False, editable_aname_nice = True, elevate = True) :
        self.add_me('aobject') # make sure name_root always in there!
        self.add_me(name_root) # make sure name_root always in there!
        self.aesthete_properties = {}
        self.property_connections = {}
        self.method_children = []
        self.absorbed = []

        object_dictionary = get_object_dictionary()
        # PROPERTIES
        gobject.GObject.__init__(self)
        self.aname_root = name_root
        self.view_object = view_object
        self.editable_aname_nice = editable_aname_nice

        # aname only valid after this statement
        object_dictionary.assign(self)

        #self.aesthete_properties = self.get_aesthete_properties()
        #self.aesthete_properties['name_nice'] = [self.change_aname_nice, self.set_aname_nice, True]
        self.env = env
        if self.env is not None : self.logger = env.logger
        self.env = env
        if self.logger is not None : self.add_logger(self.logger)
        self.init_properties(property_manager)

        self.aesthete_method_widgets = []
        self.method_window = gtk.VBox()
        self.add_method_window(self.get_method_window())
        #self.method_window.show_all()
        self.method_window.show()

        self.set_ui()

        object_dictionary.add(self, show)
        self.status_id = get_status_bar().get_context_id(self.get_aname())

        self.connect('aesthete-property-change', self.aes_method_update)

        if show and elevate : self.elevate()

    source_action = None

    def add_me(self, what) :
        if self.mes == None : self.mes = [what]
        else : self.mes.append(what)
    
    def am(self, what) : return what in self.mes

    def aes_remove(self):
        if self.absorber != None : self.absorber.rinse_properties(self)
        global object_dictionary
        object_dictionary.remove(self)

    def __del__(self):
        self.aes_remove()

    def init_properties(self, property_manager = True) :
        self.property_store = gtk.TreeStore(str, str, str, bool, bool, str, bool)
        self.set_property_manager(property_manager)
        self.append_properties()
        self.row_changed_conn = self.property_store.connect("row-changed",\
            (lambda model, path, it : \
             self.change_property(\
                self.property_store.get_value(it,0),\
                self.property_store.get_value(it,2),\
                self.property_store.get_value(it,1))))
    
    def add_logger(self, logger) : self.connect("aesthete-logger", logger.append_line)

    def add_property_connection(self, prop, handler) :
        if (prop, self.get_aname()) not in self.aesthete_properties :
            print "UNKNOWN PROPERTY : " + prop + " FOR " + self.get_aname_nice()
        if prop not in self.property_connections :
            self.property_connections[prop] = []
        self.property_connections[prop].append(handler)

    def change_property(self, prop, val, aname = None):
        if self.absorber != None :
            self.absorber.emit_property_change(prop,
                    self.absorber_as if aname is None else aname)
        if aname == None : aname = self.get_aname()
        fns = self.aesthete_properties[(prop,aname)]
        if (fns[1](val) == fns[1]()): return
        if fns[0] : fns[0](fns[1](val))
        self.emit("aesthete-property-change", prop, str(fns[1]()), aname)
        # SHOULD THIS NOW GO THROUGH ABSORBEES p_c's?
        if prop in self.property_connections :
            for handler in self.property_connections[prop] :
                handler(val)
    
    def emit_property_change(self, prop, aname = None):
        if self.absorber != None :
            self.absorber.emit_property_change(prop, 
                    self.absorber_as if aname is None else aname)
        if aname == None : aname = self.get_aname()
        fns = self.aesthete_properties[(prop,aname)]
        self.emit("aesthete-property-change", prop, str(fns[1]()), aname)

    ui_merge_id = None
    ui_ui_string = None
    ui_action_group = None
    def set_ui(self) :
        pass

    def get_useful_vars(self) :
        return None

    def get_aesthete_properties(self) : return {}

    def get_property_store(self) : return self.property_store
    def get_property_manager(self) : return self.property_manager
    def get_aname(self) : return self.aname_root + '-' + str(self.aname_num)
    def get_aname_nice(self, val=None) : return self.aname_nice if val==None else val #compat w properties
    def get_aname_root(self) : return self.aname_root
    def get_aname_num(self) : return self.aname_num
    def get_alogger(self) : return self.logger
    def get_aenv(self) : return self.env

    def set_aname_num(self, name_num) : self.aname_num = name_num
    # Distinguish between these two! set_aname_nice is a convenience end-user fn, change_aname_nice is the background work-a-day.
    def set_aname_nice(self, name_nice) : self.change_property('name_nice', name_nice)
    def change_aname_nice(self, name_nice) : self.aname_nice = name_nice; self.emit("aesthete-aname-nice-change", self.get_aname(), name_nice)
    def set_property_manager(self, property_manager) :
        # Should set properties page_matrix to absorber, somehow reversably
        if property_manager == self.property_manager : return
        if property_manager :
            self.property_manager_conn = self.connect("aesthete-property-change", self.do_property_change)
        else :
            self.disconnect(self.property_manager_conn)
            self.property_manager_conn = None
        self.property_manager = property_manager
        global object_dictionary; object_dictionary.set_show(self, property_manager)

    def log(self, nature, string) :
        self.emit("aesthete-logger", self.get_aname_nice(), nature, string)

    def elevate(self, properties=True) :
        get_object_dictionary().set_active(self, properties)

    def update_absorbee_aname_nice(self, obj, aname, new) :
        if self.row_changed_conn > 0 : self.property_store.handler_block(self.row_changed_conn)
        for row in self.property_store :
            if row[1] == aname and self.property_store.iter_n_children(row.iter) > 0 :
                row[0] = new
            #if self.property_store.iter_n_children(row.iter) > 0 : row[0] = get_object_from_dictionary(row[1]).get_aname_nice()
        if self.row_changed_conn > 0 : self.property_store.handler_unblock(self.row_changed_conn)

    def aes_method_update(self, other, prop, val, aname) :
        if aname != self.get_aname() : return
        for tup in self.aesthete_method_widgets :
            if tup[0] == prop :
                get = self.aesthete_properties[(prop,aname)][1]
                if val is not None : tup[2](get(val))
                pref = self.get_preference(prop)
                if tup[3] != None : tup[3](pref is not None and pref==str(get()))

    def aes_method_preference_toggle(self, propname, get) :
        butt = gtk.ToggleButton();
        butt.set_relief(gtk.RELIEF_NONE)
        butt_im = gtk.Image(); butt_im.set_from_stock(gtk.STOCK_JUMP_TO,
                                                      ICON_SIZE_PREFERENCE)
        butt.add(butt_im); butt.set_size_request(30, 0)
        butt.set_active(self.get_preference(propname) == str(get()))
        butt.connect("toggled", lambda o : butt_adj(self, butt, propname))
        return butt

    def aes_method_colour_button(self, propname, button_text = None, preferencable = True) :
        if button_text == None : button_text = "Set " + propname
        prop = self.aesthete_properties[(propname, self.get_aname())]
        co_butt = gtk.ColorButton(); co_butt.set_title(button_text)
        co_butt.set_color(gtk.gdk.Color(*prop[1]()))

        ret = co_butt; pref_func = None
        if preferencable :
            co_hbox = gtk.HBox()
            cop_butt = self.aes_method_preference_toggle(propname, prop[1])
            co_hbox.pack_start(co_butt)
            co_hbox.pack_start(cop_butt, False, False)
            pref_func = cop_butt.set_active
            ret = co_hbox

        self.aesthete_method_widgets.append((propname, co_butt, lambda v : co_butt.set_color(gtk.gdk.Color(*v)), pref_func))

        co_butt.connect("color-set", \
            lambda o : self.change_property(propname, col_to_tup_str(o.get_color())))

        return ret
        
    def aes_method_font_button(self, propname, button_text = None, preferencable = True) :
        if button_text == None : button_text = "Set " + propname
        prop = self.aesthete_properties[(propname, self.get_aname())]
        ft_butt = gtk.FontButton(); ft_butt.set_title(button_text)
        ft_butt.set_font_name(prop[1]())

        ret = ft_butt; pref_func = None
        if preferencable :
            ft_hbox = gtk.HBox()
            ftp_butt = self.aes_method_preference_toggle(propname, prop[1])
            ft_hbox.pack_start(ft_butt)
            ft_hbox.pack_start(ftp_butt, False, False)
            pref_func = ftp_butt.set_active
            ret = ft_hbox

        self.aesthete_method_widgets.append((propname, ft_butt, lambda v : ft_butt.set_font_name(v), pref_func))

        ft_butt.connect("font-set", \
            lambda o : self.change_property(propname, o.get_font_name()))

        ft_butt_font_labl = ft_butt.get_child().get_children()[0]
        ft_butt_size_labl = ft_butt.get_child().get_children()[2]
        attrs = pango.AttrList()
        attrs.insert(pango.AttrScale(pango.SCALE_SMALL, 0, -1))
        for labl in (ft_butt_font_labl, ft_butt_size_labl) :
            labl.set_attributes(attrs)
        ft_butt_font_labl.set_ellipsize(pango.ELLIPSIZE_END)

        return ret

    # Does nothing on selection!
    def aes_method_object_combo(self, propname) :
        prop = self.aesthete_properties[(propname, self.get_aname())]
        en_lsto = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        en_cmbo = gtk.ComboBox(en_lsto)
        en_cllr = gtk.CellRendererText(); en_cmbo.pack_start(en_cllr)
        en_cllr.props.ellipsize = pango.ELLIPSIZE_END
        en_cmbo.add_attribute(en_cllr, 'text', 1)
        update_object_combo(en_cmbo, prop[1]())
        self.aesthete_method_widgets.append((propname, en_cmbo, lambda v : update_object_combo(en_cmbo, v), None))
        return en_cmbo

    def aes_method_automate_combo_text(self, combo, propname) :
        self.aesthete_method_widgets.append((propname, combo, lambda v : update_combo_select(combo, v), None))
        combo.connect("changed", \
            lambda o : self.change_property(propname, o.get_active_text()))

    def aes_method_combo(self, propname, preferencable = True) :
        prop = self.aesthete_properties[(propname, self.get_aname())]
        en_cmbo = gtk.combo_box_new_text()
        #en_cmbo.set_size_request(30,-1)
        en_cmbo[0].props.ellipsize = pango.ELLIPSIZE_END
        update_combo(en_cmbo, prop[1]())

        ret = en_cmbo; pref_func = None
        if preferencable :
            en_hbox = gtk.HBox()
            enp_butt = self.aes_method_preference_toggle(propname, prop[1])
            en_hbox.pack_start(en_cmbo)
            en_hbox.pack_start(enp_butt, False, False)
            pref_func = enp_butt.set_active
            ret = en_hbox

        self.aesthete_method_widgets.append((propname, en_cmbo, lambda v : update_combo(en_cmbo, v), pref_func))

        return ret

    # Automatic update
    def aes_method_entry(self, propname, has_frame = False, preferencable = True, wait_until_parsable_float = False) :
        prop = self.aesthete_properties[(propname, self.get_aname())]
        en_entr = gtk.Entry(); en_entr.set_has_frame(has_frame)
        en_entr.set_text(str(prop[1]()))

        ret = en_entr; pref_func = None
        if preferencable :
            en_hbox = gtk.HBox()
            enp_butt = self.aes_method_preference_toggle(propname, prop[1])
            en_hbox.pack_start(en_entr)
            en_hbox.pack_start(enp_butt, False, False)
            pref_func = enp_butt.set_active
            ret = en_hbox

        self.aesthete_method_widgets.append((propname, en_entr, lambda v : en_entr.set_text(str(v)), pref_func))
        if wait_until_parsable_float :
            en_entr.connect("changed", \
                lambda o : self.change_property(propname, str(en_entr.get_text())) if check_float(en_entr.get_text()) else 0)
        else :
            en_entr.connect("changed", \
                lambda o : self.change_property(propname, str(en_entr.get_text())))

        return ret
        
    # Manual (button) update
    def aes_method_entry_update(self, propname, button_text = None, preferencable = True) :
        if button_text == None : button_text = "Set " + propname
        prop = self.aesthete_properties[(propname, self.get_aname())]
        eu_hbox = gtk.HBox()
        eu_entr = gtk.Entry()
        eu_entr.set_size_request(30,-1)
        eu_butt = gtk.Button(button_text)
        eu_entr.set_text(str(prop[1]()))

        ret = eu_entr; pref_func = None
        if preferencable :
            eup_butt = self.aes_method_preference_toggle(propname, prop[1])
            eu_hbox.pack_end(eup_butt, False, False)
            pref_func = eup_butt.set_active
            ret = eu_hbox

        self.aesthete_method_widgets.append((propname, eu_entr, lambda v : eu_entr.set_text(str(v)), pref_func))

        eu_butt.connect("clicked", \
            lambda o : self.change_property(propname, str(eu_entr.get_text())))
        # Pack end to allow easy label addition
        eu_hbox.pack_end(eu_butt); eu_hbox.pack_end(eu_entr)
        return ret
        
    def aes_method_toggle_button(self, propname, label = None,
                                 preferencable = True, onoff = None) :
        check = gtk.ToggleButton(label=label)
        prop = self.aesthete_properties[(propname, self.get_aname())]

        ret = check; pref_func = None
        if preferencable :
            ck_hbox = gtk.HBox()
            ckp_butt = self.aes_method_preference_toggle(propname, prop[1])
            ck_hbox.pack_start(check)
            ck_hbox.pack_start(ckp_butt, False, False)
            pref_func = ckp_butt.set_active
            ret = ck_hbox

        self.aesthete_method_widgets.append((propname, check, lambda v : check.set_active(v), pref_func))
        check.set_active(prop[1]())
        check.connect("toggled", \
            lambda o : self.change_property(propname, str(check.get_active())))

        if onoff is not None :
            text = label + " : " if label is not None else ""
            update_label = \
                lambda o : check.set_label(text + onoff[\
                            0 if check.get_active() else 1])
            check.connect("toggled", update_label)
            update_label(check)
        return ret
        
    def aes_method_check_button(self, propname, label = None, preferencable = True) :
        check = gtk.CheckButton(label)
        prop = self.aesthete_properties[(propname, self.get_aname())]

        ret = check; pref_func = None
        if preferencable :
            ck_hbox = gtk.HBox()
            ckp_butt = self.aes_method_preference_toggle(propname, prop[1])
            ck_hbox.pack_start(check)
            ck_hbox.pack_start(ckp_butt, False, False)
            pref_func = ckp_butt.set_active
            ret = ck_hbox

        self.aesthete_method_widgets.append((propname, check, lambda v : check.set_active(v), pref_func))
        check.set_active(prop[1]())
        check.connect("toggled", \
            lambda o : self.change_property(propname, str(check.get_active())))
        return ret
        
    # Doesn't get ancestors!!
    def get_all_aesthete_properties(self) :
        props = self.get_aesthete_properties()
        props['name_nice'] = [self.change_aname_nice if self.editable_aname_nice else None, self.get_aname_nice, True]
        return props

    def get_preference(self, prop) :
        return get_preferencer().get_preference(self.get_aname_root(), prop)
    def set_preference(self, prop, val = None) :
        get_preferencer().set_preference(self.get_aname_root(), prop, val)
        self.do_property_change(None, prop, None, self.get_aname())
        self.aes_method_update(None, prop, None, self.get_aname())

    def append_properties(self, props = None, aname = None) :
        parent = None
        if props == None :
            props = self.get_all_aesthete_properties()
        if aname == None :
            aname = self.get_aname()
        elif aname != self.get_aname() :
            obj = get_object_from_dictionary(aname)
            if self.row_changed_conn > 0 : self.property_store.handler_block(self.row_changed_conn)
            parent = self.property_store.append(None, [obj.get_aname_nice(), aname, '', False, True, aname, False])
            if self.row_changed_conn > 0 : self.property_store.handler_unblock(self.row_changed_conn)
        for name in props :
            get = props[name][1]
            change = props[name][0]
            self.aesthete_properties[(name,aname)] = props[name]
            pref = None
            if (change!=None) :
                pref = self.get_preference(name)
                if pref != None : change(get(pref)); pref = get(pref)
            val = get()
            if self.row_changed_conn > 0 : self.property_store.handler_block(self.row_changed_conn)
            self.property_store.append(parent, [name, aname, val, (change!=None), (change==None), name + ' [' + aname + ']',\
                pref==val])
            if self.row_changed_conn > 0 : self.property_store.handler_unblock(self.row_changed_conn)
    
        if self.absorber is not None :
            self.absorber.append_properties(props,
                None if self.absorber_as_self else aname)

    def aes_append_status(self, other, string) :
        status_bar = get_status_bar()
        status_bar.push(self.status_id, "[" + self.get_aname_nice() + "] " + string)

    def display_plotwidget(self, other, string):
        self.push(self.plotwidget_cid, "[Plotter] " + string)

    def do_property_change_under_(self, iter, prop, val, aname) :
        for row in iter :
            if row[0] == prop and row[1] == aname :
                is_pref = self.get_preference(prop) == row[2]
                if row[6] != is_pref : row[6] = is_pref
                #if prop == 'yhide_oom' : print str(row[6]) + str(is_pref)
                if val != None :
                    row[2] = val
                    if self.aesthete_properties[(prop,aname)][2] :
                        self.log(2, '[' + prop + '] set to [' + val + ']')
                    return True
        return False

    def do_property_change(self, other, prop, val, aname = None):
        if aname == None : aname = self.get_aname()
        done = self.do_property_change_under_(self.property_store, prop, val, aname)
        if not done :
            for row in self.property_store :
                if self.property_store.iter_n_children(row.iter) > 0 and row[1] == aname :
                    self.do_property_change_under_(row.iterchildren(), prop, val, aname)

    absorbed = None
    def absorb_properties(self, absorbee, as_self = True) :
        absorbee.set_property_manager(False)
        absorbee.absorber_conn = absorbee.connect("aesthete-property-change", self.do_property_change)
        absorbee.absorber_ann_conn = absorbee.connect("aesthete-aname-nice-change", self.update_absorbee_aname_nice)
        absorbee.absorber_as = self.get_aname() if as_self else absorbee.get_aname()
        absorbee.absorber_as_self = as_self
        absorbee.absorber = self
        self.append_properties(absorbee.get_all_aesthete_properties(), absorbee.absorber_as)
        new_win = absorbee.get_method_windows()
        absorbee.absorber_win = new_win
        if new_win.get_parent() : new_win.get_parent().remove(new_win)
        self.add_method_window(new_win)
        #self.method_window.show_all()
        self.method_window.show()
        for absabs in absorbee.absorbed :
            absorbee.rinse_properties(absabs)
            self.absorb_properties(absabs, as_self=absabs.absorber_as_self)
            debug_print(self.aesthete_properties)
        self.absorbed.append(absorbee)
    
    def rinse_properties(self, absorbee) :
        absorbee.disconnect(absorbee.absorber_conn)
        absorbee.disconnect(absorbee.absorber_ann_conn)
        for prop in absorbee.get_all_aesthete_properties() :
            self.aesthete_properties[(prop,absorbee.absorber_as)]
            for row in self.property_store :
                if row[0] == prop and row[1] == absorbee.absorber_as :
                    self.property_store.remove(row.iter)
        for row in self.property_store :
            if row[1] == absorbee.get_aname() and row.iterchildren() != None :
                self.property_store.remove(row.iter)
        self.remove_method_window(absorbee.absorber_win)
        absorbee.absorber = None
        absorbee.absorber_win = None
        absorbee.absorber_as = None
        absorbee.absorber_as_self = None
        absorbee.absorber_conn = -1
        absorbee.set_property_manager(True)
        self.log(2, absorbee.get_aname_nice() + ' rinsed')
        self.absorbed.remove(absorbee)
    
    def get_new_property_view(self):
        if not self.property_manager : return None
        property_prop_rend = gtk.CellRendererText(); property_prop_col = gtk.TreeViewColumn('Property', property_prop_rend)
        property_prop_col.add_attribute(property_prop_rend, 'text', 0); property_prop_col.set_expand(True)
        property_val_rend = gtk.CellRendererText()
        property_val_col = gtk.TreeViewColumn('Value', property_val_rend)
        property_pref_rend = gtk.CellRendererToggle()
        property_pref_col = gtk.TreeViewColumn('Preference', property_pref_rend)

        property_val_rend.set_property('foreground', '#AAAAAA')
        property_val_col.add_attribute(property_val_rend, 'text', 2);
        property_val_col.add_attribute(property_val_rend, "editable", 3)
        property_val_col.add_attribute(property_val_rend, "foreground-set", 4)
        property_val_rend.connect('edited', \
            (lambda cell, path, new : (self.property_store.set_value(self.property_store.get_iter(path),2,new))))
        property_val_col.set_expand(True)
        property_pref_col.add_attribute(property_pref_rend, 'active', 6)
        property_pref_rend.connect('toggled', \
            (lambda cell, path : self.set_preference(self.property_store.get_value(self.property_store.get_iter(path),0), \
                self.property_store.get_value(self.property_store.get_iter(path),2) if (not cell.get_active()) else None)))
        
        property_view = gtk.TreeView(self.property_store)
        property_view.append_column(property_prop_col); property_view.append_column(property_val_col)
        property_view.append_column(property_pref_col)
        property_view.set_tooltip_column(5)
        property_view.show_all()
        swin = gtk.ScrolledWindow()
        swin.add(property_view)
        swin.show()
        return swin

    # Whatever this returns should have a save_preferences method
    # such as a PreferencesTableMaker table
    def get_preferences_window(self) :
        return None
    
    def get_method_window(self) :
        return None
    
    def remove_method_window(self, win) :
        if win : self.method_window.remove(win); self.method_window.show()
    def add_method_window(self, win) :
        if win : self.method_window.pack_start(win, False, False); self.method_window.show()#; self.method_window.show()

    def get_method_windows(self) : 
        return self.method_window

class ObjectDictionary(gobject.GObject) :
    __gsignals__ = { "add" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ( gobject.TYPE_STRING, gobject.TYPE_STRING )),
             "remove" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ( gobject.TYPE_STRING, gobject.TYPE_STRING )) }

    dictionary = {}
    to_remove = {}
    page_matrix = {}
    liststores = {}
    view_page_matrix = {}
    notebook = gtk.Notebook()
    view_notebook = gtk.Notebook()
    root_counts = {}
    props_butts = {}
    icon_size = None
    concise = False

    def __init__ (self) :
        gobject.GObject.__init__(self)

        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.notebook.set_property("scrollable", True)
        self.notebook.set_property("enable-popup", True)
        self.view_notebook.set_property("scrollable", True)
        self.view_notebook.set_property("enable-popup", True)
        self.view_notebook.connect("switch-page", self.do_view_change_current_page)
        self.icon_size = gtk.icon_size_register("mini", 2, 2)

        self.useful_vars = gtk.ListStore(gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,
                                         gobject.TYPE_STRING)

    selected_source = None
    def selected_source_change(self, aname) :
        if aname is None :
            return
        self.selected_source = aname
        self.emit('aesthete-selected-source-change')

    def try_active_source_action(self) :
        active_view = self.active_view
        if not self.selected_source or not active_view or \
            not active_view.source_action :
                return

        active_view.source_action(self.selected_source)
        #active_view.grab_focus()

    active_view = None
    def do_view_change_current_page(self, nb, page, pn) :
        obj = nb.get_nth_page(pn)
        po = self.page_matrix[obj.get_aname()]
        ppn = self.notebook.page_num(po)
        if ppn != -1 : self.notebook.set_current_page(ppn)
    
        old_view = self.active_view
        if old_view is not None and old_view.ui_merge_id is not None :
            ui_manager.remove_ui(old_view.ui_merge_id)
            if old_view.ui_action_group is not None :
                ui_manager.remove_action_group(old_view.ui_action_group)
    
        if obj.ui_action_group is not None :
            debug_print(obj.get_aname())
            debug_print_stack()
            ui_manager.insert_action_group(obj.ui_action_group)
            obj.ui_merge_id = \
                ui_manager.add_ui_from_string(obj.ui_ui_string)

        #Not necessary while tabs do not accept focus
        #obj.grab_focus()
        self.active_view = obj

    def get_notebook(self) : return self.notebook
    def get_viewnotebook(self) : return self.view_notebook

    def assign(self, obj):
        name_root = obj.get_aname_root()
        if name_root in self.root_counts : self.root_counts[name_root] += 1
        else : self.root_counts[name_root] = 1
        name_num = self.root_counts[name_root]
        #for oobj_name in self.dictionary :
        #    oobj = self.dictionary[oobj_name]
        #    if oobj.get_aname_root() == name_root and oobj.get_aname_num() >= name_num :
        #        name_num = oobj.get_aname_num() + 1
        obj.set_aname_num(name_num)
        aname = obj.get_aname()

        aname_nice = obj.aname_root
        if name_num > 1 : aname_nice += ' (' + str(name_num) + ')'
        obj.aname_nice = aname_nice

        self.dictionary[aname] = obj

    def add(self, obj, show):
        aname = obj.get_aname()
        if aname == None : self.assign(obj)
        view = obj.get_new_property_view()
        self.page_matrix[aname] = None
        self.set_show(obj, show)
        
        obj.connect("aesthete-aname-nice-change", self.update_label)
        obj.connect("aesthete-aname-nice-change", self.update_liststores)

        lss = set(self.liststores.keys()) & set(obj.mes)
        for ls in lss :
            ls = self.liststores[ls]
            ls.append((obj.get_aname(), obj.get_aname_nice(),
                       obj.get_aesthete_xml()))

        useful_vars = obj.get_useful_vars()
        if useful_vars is not None :
            for var in useful_vars :
                debug_print(var)
                self.useful_vars.append((obj.get_aname(), var, useful_vars[var]))

        self.emit("add", aname, obj.get_aname_root())

    def update_liststores(self, obj, aname, aname_nice) :
        lss = set(self.liststores.keys()) & set(obj.mes)
        for ls in lss :
            ls = self.liststores[ls]
            for row in ls :
                if row[0] == aname :
                    row[1] = aname_nice
                    row[2] = obj.get_aesthete_xml()
    
    def update_label(self, obj, aname, aname_nice) :
        page = self.page_matrix[aname]
        if page != None :
            self.props_butts[aname].get_children()[0].set_text(obj.get_aname_nice())
            self.notebook.set_menu_label_text(page, obj.get_aname_nice())
            page.get_children()[1].set_label(obj.get_aname_nice()+' Toolbox')
            # self.notebook.set_tab_label(page, self.make_label(obj))
        if obj.view_object and self.view_notebook.page_num(obj) >= 0 :
            self.view_notebook.set_tab_label(obj, self.make_label(obj))

    def remove_widgets(self, obj) :
        aname = obj.get_aname()
        page = self.page_matrix[aname]
        if page != None :
            method_frame = page.get_children()[1]
            method_frame.remove(method_frame.get_children()[0])
            self.notebook.remove(page); self.page_matrix[aname] = None
        if obj.view_object and self.view_notebook.page_num(obj) >= 0 :
            self.view_notebook.remove(obj)

    def make_label(self, obj) :
        label = gtk.Label(obj.get_aname_nice()); label.set_tooltip_text(obj.get_aname())
        return label

    def show_props(self, props, show) :
        if show : props.show()
        else : props.hide()

    def _make_full_label(self, obj) :
        label = self.make_label(obj)
        full_label = gtk.HBox()
        full_label.pack_start(label, True, True)
        self.props_butts[obj.get_aname()] = full_label
        killv = gtk.VBox()
        kill = gtk.Button()
        kill.set_relief(gtk.RELIEF_NONE)
        kill_im = gtk.Image(); kill_im.set_from_stock(gtk.STOCK_CLOSE, self.icon_size)
        kill.add(kill_im); kill.set_size_request(15, 15)
        kill.connect("clicked", lambda o : obj.aes_remove())
        killv.pack_start(kill, False)
        full_label.pack_start(killv, False)
        full_label.show_all()
        return full_label

    def set_show(self, obj, show):
        aname = obj.get_aname()
        if aname not in self.page_matrix : return
        page = self.page_matrix[aname]

        if not show : self.remove_widgets(obj)
        if show and page == None :
            prop_view = obj.get_new_property_view()
            prop_view.hide()
            meth_view = gtk.Frame(obj.get_aname_nice()+" Toolbox")
            meth_view.add(obj.get_method_windows())
            button_row = gtk.HButtonBox()
            button_row.set_layout(gtk.BUTTONBOX_START)
            show_props = gtk.ToggleButton()
            show_props_im = gtk.Image(); show_props_im.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_SMALL_TOOLBAR)
            show_props.add(show_props_im)
            show_props.connect("toggled", lambda o : self.show_props(prop_view, o.get_active()))
            show_props.show_all()
            button_row.pack_start(show_props, False)
            if not self.concise : button_row.show()

            view = gtk.VBox(); view.pack_start(prop_view); view.pack_start(meth_view); view.pack_start(button_row, False)
            if view :
                full_label = self._make_full_label(obj)

                self.page_matrix[aname] = view
                notebook_child = self.notebook.append_page(view, full_label)
                self.notebook.set_menu_label_text(view, obj.get_aname_nice())

                #meth_view.show_all()
                meth_view.show()
                view.show()

        if show and obj.view_object and self.view_notebook.page_num(obj) == -1 :
            full_label = self._make_full_label(obj)
            pn = self.view_notebook.append_page(obj, full_label)
            full_label.get_parent().set_property('can-focus', False)
            debug_print(obj.get_aname())
            self.view_notebook.set_tab_detachable(obj, True)
            obj.show()
            self.view_notebook.set_current_page(pn)
    
    def set_active(self, obj, properties = True) :
        if obj.view_object :
            pn = self.view_notebook.page_num(obj)
            self.view_notebook.set_current_page(pn)

        if properties :
            po = self.page_matrix[obj.get_aname()]
            ppn = self.notebook.page_num(po)
            if ppn != -1 : self.notebook.set_current_page(ppn)

    def remove(self, obj):
        aname = obj.get_aname()
        self.remove_widgets(obj)

        if self.selected_source == aname :
            self.selected_source = None

        lss = set(self.liststores.keys()) & set(obj.mes)
        for ls in lss :
            ls = self.liststores[ls]
            for row in ls :
                if row[0] == aname :
                    ls.remove(row.iter)
        for row in self.useful_vars :
            if row[0] == aname :
                self.useful_vars.remove(row.iter)

        self.to_remove[aname] = obj
        del self.dictionary[aname]
        self.emit("remove", aname, obj.get_aname_root())
        del self.to_remove[aname]
    
    def get_objects_by_am(self, what) :
        if what == '' or what == None : return []
        objs = []
        for key in self.dictionary :
            obj = self.dictionary[key]
            if obj.am(what) : objs.append(obj)
        return objs

    def get_liststore_by_am(self, what):
        if what in self.liststores : return self.liststores[what]
        ls = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                           gobject.TYPE_PYOBJECT)
        self.liststores[what] = ls
        for key in self.dictionary :
            obj = self.dictionary[key]
            if obj.am(what) : ls.append((obj.get_aname(),
                                         obj.get_aname_nice(),
                                         obj.get_aesthete_xml()))
        return ls
    
    def set_concise_notebook (self, concise) :
        self.concise = concise
        self.notebook.set_show_tabs(not concise)
        for p in self.notebook.get_children() :
            c = p.get_children()
            #c[1].get_label_widget().hide() if concise else c[1].get_label_widget().show()
            c[2].hide() if concise else c[2].show()

status_bar = gtk.Statusbar()
def get_status_bar() : return status_bar

object_dictionary = ObjectDictionary()
ui_manager = gtk.UIManager()

def get_object_dictionary():
    return object_dictionary
def get_object_from_dictionary(name):
    if name == '' or name == None : return None
    if not name in object_dictionary.dictionary : return None
    return object_dictionary.dictionary[name]
def get_removing_from_dictionary(name) :
    if name == '' or name == None : return None
    if not name in object_dictionary.to_remove : return None
    return object_dictionary.to_remove[name]
def get_active_object() :
    nb = object_dictionary.get_viewnotebook()
    return nb.get_children()[nb.get_current_page()]

class Preferencer :
    tree = None
    preferences_file = paths.get_user_location() + "preferences.xml"
    default_file = paths.get_share_location()+"preferences.default.xml"
    pref_change = False

    def __init__ (self) :
        if not os.path.exists(self.preferences_file) :
            try :
                shutil.copyfile(self.default_file,
                                self.preferences_file)
            except :
                root = ET.Element("preferences")
                head = ET.SubElement(root, "head")
                program = ET.SubElement(head, "program")
                program.set("name", details.get_name())
                program.set("version", details.get_version())
                program.set("description", details.get_description())
                body = ET.SubElement(root, "body")
                tree = ET.ElementTree(root)
                tree.write(self.preferences_file)
                self.tree = tree
        if self.tree is None :
            self.tree = ET.parse(self.preferences_file)
        self.body = self.tree.find("body")
    
    def __del__ (self) :
        if (self.pref_change) :
            self.tree.write(self.preferences_file)
            print "Preferences saved"

    def get_preference (self, aroot, prop) :
        pref = self.body.find(aroot + '/' + prop)
        if pref is None : return None
        return pref.get("value")

    def set_preference (self, aroot, prop, val = None) :
        prop = str(prop)
        if val != None :
            pe = self.body.find(aroot + '/' + prop)
            if pe is None :
                ao = None
                for el in list(self.body) :
                    if el.tag == aroot : ao = el
                if ao == None : ao = ET.SubElement(self.body, aroot)
                pe = ET.SubElement(ao, prop)
            pe.set("value", str(val))
        else :
            ao = self.body.find(aroot)
            pe = self.body.find(aroot + '/' + prop)
            if pe is not None :
                ao.remove(pe)
                if len(list(ao)) == 0 : self.body.remove(ao)
        self.pref_change = True
    
preferencer = Preferencer()

def get_preferencer() : return preferencer

def new_tab_win(source, page, x, y) :
    win = gtk.Window()
    nb = gtk.Notebook()
    win.add(nb)
    win.show_all()
    return nb

gtk.notebook_set_window_creation_hook(new_tab_win)

gobject.signal_new("aesthete-logger", AObject, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,gobject.TYPE_INT,gobject.TYPE_STRING,))
gobject.signal_new("aesthete-aname-nice-change", AObject, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,))
gobject.signal_new("aesthete-property-change", AObject, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))
gobject.signal_new("aesthete-selected-source-change", ObjectDictionary, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
