import re
import glypher
import glypher.Widget
import glypher.Word
from details import get_command, get_name
import tablemaker
from utils import debug_print
import paths
import numpy
import gobject
import gtk
import os
import random
import aobject
from sources.Source import Source, CSV, FunctionSource
from sources.VTK import SourceVTK
import xml.etree.ElementTree as ET

def load_from_file(filename, new_name, env) :
    suff = filename.split('.')
    suff = suff[-1].lower() if len(suff) > 1 else None

    if suff == 'csv' :
        source = CSV_factory(filename, env)
        mime_type = 'text/csv'
    elif suff == 'vtu' :
        source = VTK_factory(filename, env)
        mime_type = 'text/csv'
    else :
        raise RuntimeError('Unrecognized file type : ' + filename)

    if new_name is not None :
        source.set_aname_nice(new_name)
        debug_print(new_name)

    recman = gtk.recent_manager_get_default()
    recman.add_full(filename, {'mime_type' : mime_type,
                               'app_name' : get_name(),
                               'app_exec' : get_command(),
                               'display_name' : source.get_aname_nice(),
                               'description' : 'Aesthete-imported source',
                               'is_private' : True,
                               'groups' : ['aesthete-sources']})

class SourceImporter(gtk.FileChooserDialog) :
    last_dir = os.path.expanduser('~')

    def __init__(self) :
        gtk.FileChooserDialog.__init__(self,
                      title="Import Source", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

    @classmethod
    def run_chooser(cls, env = None) :
        chooser = cls()
        chooser.set_current_folder(cls.last_dir)
        chooser.set_default_response(gtk.RESPONSE_OK)

        extra_hbox = gtk.HBox()
        extra_hbox.pack_start(gtk.Label("Name as"), False)
        extra_entr = gtk.Entry()
        extra_entr.set_activates_default(True)
        extra_hbox.pack_start(extra_entr)
        extra_hbox.show_all()
        chooser.set_extra_widget(extra_hbox)

        resp = chooser.run()

        new_name = extra_entr.get_text()
        if len(new_name) == 0:
            new_name = None

        if resp == gtk.RESPONSE_OK :
            filename = chooser.get_filename()
            chooser.destroy()
        else :
            chooser.destroy()
            return

        cls.last_dir = os.path.dirname(filename)

        load_from_file(filename, new_name, env)

def parse_params(pfn, header = True):
    pfile = open(pfn, 'r')
    params = {}
    for line in pfile:
        if cmp(line[0],'=') == 0:
         if header :
          header = False
          continue
         else :
          break
        if header: continue
        commpos = line.find('#')
        if commpos > 0 : line = line[0:commpos-1]
        line = line.strip()
        if commpos == 0 or len(line) == 0: continue
        var,val = line.split('=')
        var = var.strip(); val = val.strip()
        params[var] = val
    return params

def CSV_factory(filename, env = None) :
    csv = CSV(filename, env)
    return csv
        
def VTK_factory(filename, env = None) :
    vtk = SourceVTK(filename, env)
    return vtk

class SourceDictionary(gobject.GObject) :
    def __init__(self) :
        gobject.GObject.__init__(self)
        dic = aobject.get_object_dictionary()
        dic.connect("add", self.check_source)
        dic.connect("remove", self.check_source)
    def check_source(self, ob, n, r) :
        ob = aobject.get_object_from_dictionary(n)
        if ob == None : ob = aobject.get_removing_from_dictionary(n)
        if ob == None or ob.am("Source") :
            self.emit("aesthete-source-change", n, r)

source_dictionary = SourceDictionary()
def get_source_dictionary() : return source_dictionary

def do_source_rename(dlog, resp) :
    if resp == gtk.RESPONSE_ACCEPT :
        dlog.object.set_aname_nice(dlog.get_text())

def make_source_rename_dialog(parent, object) :
    rename_dlog = gtk.Dialog("Rename source", parent, 0,\
        (gtk.STOCK_CANCEL    , gtk.RESPONSE_REJECT,\
         gtk.STOCK_OK        , gtk.RESPONSE_ACCEPT))
    rename_hbox = gtk.HBox()
    rename_dlog.vbox.pack_start(rename_hbox)
    rename_hbox.pack_start(gtk.Label("Name"), False, False, 15)
    rename_entr = gtk.Entry()
    rename_entr.set_text(object.get_aname_nice())
    rename_hbox.pack_start(rename_entr)
    rename_dlog.get_text = rename_entr.get_text
    rename_dlog.object = object
    rename_dlog.connect("response", do_source_rename)
    rename_dlog.show_all()
    rename_dlog.run()
    rename_dlog.destroy()

def do_source_treeview_popup(trvw, event) :
    if event.button != 3 : return
    item = trvw.get_path_at_pos(int(event.x), int(event.y))
    if item == None : return
    time = event.time

    context_menu = gtk.Menu()
    obj = aobject.get_object_from_dictionary(trvw.get_model()[item[0]][0])

    context_menu_aname_nice = gtk.MenuItem(obj.get_aname_nice())
    context_menu_aname_nice.set_sensitive(False)
    context_menu.add(context_menu_aname_nice)
    
    context_menu_rename = gtk.MenuItem("Rename")
    context_menu_rename.connect("button-press-event", lambda o, e : make_source_rename_dialog(trvw.get_toplevel(), obj))
    context_menu.add(context_menu_rename)

    context_menu_rename = gtk.MenuItem("Remove")
    context_menu_rename.connect("button-press-event",
                                lambda o, e : obj.aes_remove())
    context_menu.add(context_menu_rename)

    if (obj.reloadable) :
        context_menu_reload = gtk.MenuItem("Reload")
        context_menu_reload.connect("button-press-event", lambda o, e : obj.source_reload())
        context_menu.add(context_menu_reload)

    context_menu.popup( None, None, None, event.button, time )
    context_menu.show_all()

connected = []
_entry_server = None

def init_entry_server() :
    global _entry_server
    if _entry_server is None :
        _entry_server = glypher.Widget.GlyphEntry(position=(0,0))
        root = glypher.Word.make_word('hi',
                                                     _entry_server.main_phrase).get_xml()
        xml = ET.ElementTree(root)
        _entry_server.set_xml(xml)
        _entry_server.main_phrase.set_is_caching(True)
        _entry_server.main_phrase.set_font_size(5)
        _entry_server.main_phrase.background_colour = (0.3,0.5,0.4)

def cdf(c, cr, tm, it) :
    obj = aobject.get_object_from_dictionary(tm.get_value(it,0))
    if obj is None : return
    cr.set_property('text', tm.get_value(it, 1))
    cr.set_property('xml', tm.get_value(it, 2))
    #cr.set_property('foreground', 'red' if obj.is_needs_reloaded() else 'black')

    #if obj.get_aname_xml() is None :
    #    root = glypher.Word.make_word(obj.get_aname_nice(),
    #                                                 _entry_server.main_phrase).get_xml()
    #else :
    #    root = obj.get_aname_xml()
    #xml = ET.ElementTree(root)
    ##_entry_server.set_xml(xml)

    #_entry_server.main_phrase.draw()
    #cis = _entry_server.main_phrase.cairo_cache_image_surface
    #pixbuf = \
    #    gtk.gdk.pixbuf_new_from_data(cis.get_data(),
    #                                 gtk.gdk.COLORSPACE_RGB,
    #                                 True,
    #                                 8,
    #                                 cis.get_width(),
    #                                 cis.get_height(),
    #                                 cis.get_stride())

    #cr.set_property('pixbuf', pixbuf)
def on_needs_reloaded_status_change(ob, val, tm, i, tv, cr) :
    tv.get_column(0).set_cell_data_func(cr, cdf)
    tv.queue_draw()
def connect_sources_reload_signal(tm, p, i, tv, cr) :
    obj = aobject.get_object_from_dictionary(tm.get_value(i,0))
    if obj.get_aname() in connected : return
    obj.connect("aes_needs_reloaded_status_change", on_needs_reloaded_status_change, tm, i, tv, cr)
    connected.append(obj.get_aname())
def make_source_treeview() :
    init_entry_server()
    sources_lsst = aobject.get_object_dictionary().get_liststore_by_am('Source')
    sources_trvw = gtk.TreeView(sources_lsst)
    sources_trvw.unset_flags(gtk.CAN_FOCUS)
    sources_trvc = gtk.TreeViewColumn('Sources'); sources_trvw.append_column(sources_trvc)
    #sources_cllr = gtk.CellRendererPixbuf(); sources_trvc.pack_start(sources_cllr, True)
    sources_cllr = glypher.Widget.GlyphCellRenderer(); sources_trvc.pack_start(sources_cllr, True)
    #sources_trvc.set_attributes(sources_cllr, text=1)
    sources_trvc.set_cell_data_func(sources_cllr, cdf)
    sources_trvw.connect("button-press-event", do_source_treeview_popup)
    sources_trvw.connect("row-activated", lambda t, p, c : \
                         aobject.get_object_dictionary().try_active_source_action())
    sources_trvw.connect("cursor-changed", lambda trvw :
                         aobject.get_object_dictionary().selected_source_change(\
                                sources_lsst.get_value(\
                                    sources_lsst.get_iter(trvw.get_cursor()[0]), 0)))
    sources_lsst.connect("row-changed", connect_sources_reload_signal, sources_trvw, sources_cllr)
    sources_lsst.connect("row-changed", \
            lambda tm, p, i : sources_trvw.set_cursor(p, sources_trvc))
    return sources_trvw
def reload_sources(ness = True) :
    d = aobject.get_object_dictionary().dictionary
    for key in d :
        obj = d[key]
        if obj.am('Source') and obj.reloadable and ( not ness or obj.is_needs_reloaded() ) :
            print "Reloading", obj.get_aname_nice()
            obj.source_reload()

gobject.signal_new("aesthete-source-change", SourceDictionary, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING))
