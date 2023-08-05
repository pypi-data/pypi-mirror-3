import re
from aobject.utils import debug_print, AesFile
import gio
import numpy
import gobject
import gtk
import os
import random
from Source import Source

from aobject.aobject import AObject, aname_root_catalog, AOBJECT_CAN_NONE,\
    get_status_bar, string_to_int_tup
from .. import tablemaker

def abs_sum(v, c, t) :
    return sum(map(lambda j : abs(v[c[j]]-t[j]),
               range(0, len(t))))

class CSV (Source) :
    vals = None
    dim = 2
    skip_rows = 1
    sort = True
    last_write = None
    needs_reloaded = False

    def get_auto_aesthete_properties(self) :
        d = Source.get_auto_aesthete_properties(self)
        d.update({
            'uri' : (str, (AOBJECT_CAN_NONE,)),
            'skip_rows' : (int,),
            'presort' : (bool,),
        })
        return d

    def change_uri(self, val) :
        if self.uri is None :
            self.set_aname_nice(val.rsplit('/',1)[1])# + ' [' + val + ']')
        self.uri = val
        self.source_reload()

    def __init__(self, uri=None, env = None, presort=False, skip_rows=1,
                 range_cols=None, domain_cols=None, time_cols=None) :
        Source.__init__(self, "CSV", env, show = False, reloadable = True)

        self.set_skip_rows(skip_rows)
        self.set_presort(presort)

        self.dim = 0
        if domain_cols is not None and len(domain_cols) > 0 :
            self.set_domain_cols(domain_cols)
            self.dim += len(domain_cols)
        if range_cols is not None and len(range_cols) > 0 :
            self.set_range_cols(range_cols)
            self.dim += len(range_cols)
        if time_cols is not None and len(time_cols) > 0 :
            self.set_time_cols(time_cols)
        if self.dim == 0:
            self.dim = None

        if uri is not None :
            self.set_uri(uri)
        gobject.timeout_add(5000, self.source_check)
    
    def source_type(self) :
        return 'line'

    def source_check(self) :
        if self.uri[:7] != 'file://' :
            return

        #FIXME: swap to GIO monitor file (for modifications)
        try :
            mtime = os.stat(self.uri[7:]).st_mtime
        except (OSError) :
            return True

        #FIXME: swap to GIO monitor file (for modifications)
        if not self.needs_reloaded and self.last_write < mtime :
            self.needs_reloaded = True
            self.emit("aes_needs_reloaded_status_change", True)
        return True
    def is_needs_reloaded(self) : return self.needs_reloaded

    def source_reload(self) :
        if self.uri is None :
            return

        vals = []
        self.needs_reloaded = False

        #FIXME: swap to GIO monitor file (for modifications)
        if self.uri[:7] == 'file://' :
            self.last_write = os.stat(self.uri[7:]).st_mtime

        gf = gio.File(uri=self.uri)
        f = AesFile(gf)
        #columns = f.readline().split(',')
        vals = numpy.loadtxt(f, delimiter=',', unpack = True,
                             skiprows=self.get_skip_rows())

        multicol = True
        try :
            test = vals[0][0]
        except : multicol = False

        #for i in range(0, len(vals[1])) : vals[1][i] *= 0.001

        if multicol :
            if self.dim is None :
                self.dim = len(vals)
            else :
                self.dim = min(self.dim, len(vals))

            debug_print(self.dim)
            vals = zip(*vals)
            vals.sort(lambda x, y : cmp(x[0], y[0]))
        else :
            vals.sort()
            vals = [vals]
            self.dim = 1

        # Remove!
        self.vals = vals
        Source.source_reload(self)
    
    def source_get_max_dim(self) :
        return self.dim
    def source_get_values(self, multi_array = False, x_range=None,
                          y_range=None,
                          time=None,
                          resolution=None) :

        c = None
        time_cols = self.get_time_cols()
        if time_cols is not None :
            if time is None :
                time = [0]*len(time_cols)

            if len(time)==len(time_cols):
                c = [0]
                prox = abs_sum(self.vals[0], time_cols, time)
                for i in range(1, len(self.vals)) :
                    new_prox = abs_sum(self.vals[i], time_cols, time)
                    if abs(new_prox-prox) <= 1e-10 :
                        c.append(i)
                    elif new_prox < prox :
                        prox = new_prox
                        c = [i]

        if multi_array :
            vals = list(self.vals)
            if c is not None :
                vals = [vals[i] for i in c]

            if self.get_presort() :
                sort_col = self.get_domain_cols()[0]
                vals = sorted(vals, lambda a, b : cmp(a[sort_col], b[sort_col]))

            vals = zip(*vals)

            ret = {'name':self.get_aname_nice()}

            domain_cols = self.get_domain_cols()
            if domain_cols is not None :
                names = ('x','y')
                for r in range(0, len(domain_cols)) :
                    ret[names[r]] = vals[domain_cols[r]]
            else :
                names['x'] = vals[0]

            range_cols = self.get_range_cols()
            if range_cols is not None :
                if len(range_cols) == 1 :
                    ret['values'] = vals[range_cols[0]]
                else :
                    ret['values'] = [vals[i] for i in range_cols]

            return [ret]

        else : return self.vals

    def get_useful_vars(self) :
        return {
                 'vals' : 'Values',
               }

IGNORE = 0
DOMAIN = 1
RANGE = 2
TIME = 3
col_types = (IGNORE,DOMAIN,RANGE,TIME)

aname_root_catalog['CSV'] = CSV
default_csv_signatures = {
    1 : (RANGE,),
    2 : (DOMAIN,RANGE),
    3 : (DOMAIN,DOMAIN,RANGE),
    4 : (TIME,DOMAIN,DOMAIN,RANGE),
}

csv_sig_props = {
  IGNORE : { 'max' : 0, 'name' : '',       'colour' : 'white'  },
  DOMAIN : { 'max' : 2, 'name' : 'Domain', 'colour' : 'yellow' },
  RANGE  : { 'max' : 2, 'name' : 'Range',  'colour' : 'red'    },
  TIME   : { 'max' : 0, 'name' : 'Time',   'colour' : 'green'  },
}

def _cycle_header(trvc, user_data) :
    i, csv_sig, csv_cols = user_data
    
    col_type = csv_sig[i]

    csv_cols[col_type].remove(i)

    col_type = col_types[(col_type+1)%len(col_types)]

    csv_sig[i] = col_type

    csv_cols[col_type].append(i)

    if csv_sig_props[col_type]['max'] > 0 and \
            len(csv_cols[col_type]) > csv_sig_props[col_type]['max'] :
        j = csv_cols[col_type][0]
        _cycle_header(None, (j, csv_sig, csv_cols))

def _redo_trvc(trvc, user_data) :
    tree_view, csv_sig, csv_cols, col_lsst, skip_rows_entr = user_data

    try :
        skip_rows = int(skip_rows_entr.get_text())
    except :
        skip_rows = 0

    dim = len(csv_sig)
    for i in range(0, dim) :
        col_trvc = tree_view.get_column(i)
        col_type = csv_sig[i]

        n = csv_cols[col_type].index(i)

        if col_type is IGNORE :
            col_title = ''
        else :
            col_title = csv_sig_props[col_type]['name'] + (' %d'%(n+1))

        col_trvc.set_title(col_title)

        k = 0
        for row in col_lsst :
            if k < skip_rows :
                colour = 'gray'
            else :
                colour = csv_sig_props[col_type]['colour'] 
            col_lsst.set_value(row.iter, i+dim, colour)
            k += 1

        col_trvc.set_fixed_width(300)

def _clear_sig(csv_sig, csv_cols) :
    for i in range(0, len(csv_sig)) :
        csv_sig[i] = IGNORE
    for ty in col_types :
        csv_cols[ty] = []
    csv_cols[IGNORE] = range(0, len(csv_sig))

def CSV_factory(uri, env = None) :
    gf = gio.File(uri=uri)
    f = AesFile(gf)
    vals = numpy.genfromtxt(f, delimiter=',', unpack=True, skiprows=0)

    vals_by_row = zip(*vals)
    for i in range(0, 5) :
        try :
            map(float, vals_by_row[i])
        except:
            debug_print(vals_by_row[i])
            break

    skip_rows = 0
    if i < 4 :
        skip_rows = i

    chooser = gtk.Dialog(\
                  title="Import CSV", parent=env.toplevel, 
                  flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    chooser.set_default_response(gtk.RESPONSE_OK)

    vbox = gtk.VBox()

    pref_tab = tablemaker.PreferencesTableMaker()

    name_as_entr = gtk.Entry()
    pref_tab.append_row('Name as', name_as_entr)

    skip_rows_entr = gtk.Entry()
    skip_rows_entr.set_text(str(skip_rows))
    pref_tab.append_row('Skip rows', skip_rows_entr)

    presort_chkb = gtk.CheckButton()
    pref_tab.append_row('Presort', presort_chkb)

    vbox.pack_start(pref_tab.make_table())

    vbox.pack_start(gtk.VSeparator())

    col_select_labl = gtk.Label()
    col_select_labl.set_markup('<b>Set column types</b>')
    vbox.pack_start(col_select_labl)

    dim = len(vals)
    cols = [str]*(2*dim)
    col_lsst = gtk.ListStore(*cols)
    col_trvw = gtk.TreeView(col_lsst)

    if dim in default_csv_signatures : 
        csv_sig = list(default_csv_signatures[dim])
    else :
        csv_sig = [IGNORE]*dim

    csv_cols = {}
    for col_type in col_types :
        csv_cols[col_type] = []

    for i in range(0, dim) :
        col_type = csv_sig[i]
        csv_cols[col_type].append(i)
        col_trvc = gtk.TreeViewColumn('')
        col_trvw.append_column(col_trvc)
        col_trvc.set_clickable(True)
        col_crtx = gtk.CellRendererText()
        col_trvc.pack_start(col_crtx, True)
        col_trvc.add_attribute(col_crtx, 'text', i)
        col_trvc.add_attribute(col_crtx, 'background', i+dim)

        col_trvc.connect("clicked", _cycle_header, (i, csv_sig, csv_cols))
        col_trvc.connect_after("clicked", _redo_trvc, (col_trvw, csv_sig,
                                                       csv_cols, col_lsst,
                                                       skip_rows_entr))

    for i in range(0, 4) :
        if i < len(vals[0]) :
            col_lsst.append(\
                [str(vals[j][i]) for j in range(0, dim)]+\
                [csv_sig_props[csv_sig[j]]['colour'] for j in range(0, dim)]\
            )
        else :
            col_lsst.append(['']*dim)

    _redo_trvc(None, (col_trvw, csv_sig, csv_cols, col_lsst, skip_rows_entr))

    vbox.pack_start(col_trvw)

    clear_butt = gtk.Button("Clear")
    clear_butt.connect("clicked", lambda w : (\
        _clear_sig(csv_sig, csv_cols),
        _redo_trvc(None, (col_trvw, csv_sig, csv_cols, col_lsst, skip_rows_entr))))

    skip_rows_entr.connect('changed', lambda e :
        _redo_trvc(None, (col_trvw, csv_sig, csv_cols, col_lsst, e)))

    vbox.pack_start(clear_butt)

    chooser.get_content_area().add(vbox)
    chooser.get_content_area().show_all()
    resp = chooser.run()
    chooser.grab_focus()

    if resp == gtk.RESPONSE_OK :
        try :
            skip_rows = int(skip_rows_entr.get_text())
        except :
            skip_rows = 0
            #status_bar = get_status_bar()
            #status_bar.push(0, "[CSV Import] Could not parse preferences")
            #chooser.destroy()
            #return

        presort = presort_chkb.get_active()

        name_as = name_as_entr.get_text()
        if name_as == '' :
            name_as = uri.rsplit('/',1)[1]
            if len(csv_cols[IGNORE])>0 :
                name_as += ' [%s]' % ','.join(map(str,csv_cols[RANGE]))

        chooser.destroy()
    else :
        chooser.destroy()
        return

    csv = CSV(uri, env, skip_rows=skip_rows,
              presort=presort,
              domain_cols=tuple(csv_cols[DOMAIN]),
              range_cols=tuple(csv_cols[RANGE]),
              time_cols=tuple(csv_cols[TIME]),
             )
    csv.set_aname_nice(name_as)

    return csv
