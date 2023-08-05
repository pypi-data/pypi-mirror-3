import glypher as g
import gtk
from PhraseGroup import *
import Parser
from sympy.matrices import matrices

def matrix_hadamard_multiply(a, b) :
    alst = a.tolist()
    blst = b.tolist()
    return matrices.Matrix(a.shape[0], a.shape[1],
                           lambda i, j : alst[i][j]*blst[i][j])

class GlypherTableCell(GlypherPhrase) :
    def set_auto_copy_paste_contents(self, auto_copy_paste_contents) : self.set_p('auto_copy_paste_contents', auto_copy_paste_contents)
    def get_auto_copy_paste_contents(self) : return self.get_p('auto_copy_paste_contents')

    def __init__(self, parent, area = (0,0,0,0), auto_copy_paste_contents = False) :
        GlypherPhrase.__init__(self, parent)
        self.mes.append('table_cell')
        self.set_p('align_as_entity', True)
        self.set_auto_copy_paste_contents(auto_copy_paste_contents)

    def process_button_release(self, event) :
        if event.button==1 and self.get_auto_copy_paste_contents() :
            self.to_clipboard(auto_paste=True)
            return True
        return GlypherPhrase.process_button_release(self, event)

class GlypherTable(GlypherPhraseGroup) :
    row_colours = None
    col_colours = None
    cells = None

    def get_dims(self) :
        return (len(self.rows), len(self.cols))

    def set_max_dimensions(self, max_dimensions) : self.set_p('max_dimensions', max_dimensions); self.recalc_bbox()
    def get_max_dimensions(self) : return self.get_p('max_dimensions'); self.recalc_bbox()
    def set_min_dimensions(self, min_dimensions) : self.set_p('min_dimensions', min_dimensions)
    def get_min_dimensions(self) : return self.get_p('min_dimensions')
    def set_proportional_width(self, proportional_width) : self.set_p('proportional_width', proportional_width)
    def get_proportional_width(self) : return self.get_p('proportional_width')
    def set_proportional_height(self, proportional_height) : self.set_p('proportional_height', proportional_height)
    def get_proportional_height(self) : return self.get_p('proportional_height')
    def set_cell_padding(self, cell_padding) : self.set_p('cell_padding', cell_padding)
    def get_cell_padding(self) : return self.get_p('cell_padding')
    def set_outside_border(self, outside_border) : self.set_p('outside_border', outside_border)
    def get_outside_border(self) : return self.get_p('outside_border')

    def get_xml(self, name=None, top=True, targets=None, full=False) :
        root = GlypherPhraseGroup.get_xml(self, name, top, targets, full)
        self._xml_table(root)

        return root

    def _xml_table(self, root) :
        dims = self.get_dims()
        root.set('rows', str(dims[0]))
        root.set('cols', str(dims[1]))

        cells = ET.Element('cells')
        for i in range(0, dims[0]) :
            for j in range(0, dims[1]) :
                r = self.ij(i,j).get_xml(name='cell', top=False, full=False)
                r.set('table_row', str(i))
                r.set('table_col', str(j))
                cells.append(r)

        if len(cells) > 0 :
            root.append(cells)

        debug_print(ET.tostring(root))

    def ij(self, i, j) :
        """Return the (i,j)th cell."""

        i = int(i)
        j = int(j)
        if i not in self.rows :
           raise IndexError("Table has no row " + str(i))
        if j not in self.cols :
           raise IndexError("Table has no col " + str(j))
        return self.cells[i][j]

    def get_cell(self, i, j) :
        return self.ij(i, j)

    def set_col_width(self, i, w) :
        self.col_offsets[i+1] = w
        for c in self.get_col(i) :
            c.get_entity().line_length = w
            c.get_entity().word_wrap()

    def set_defaults(self) :
        self.set_proportional_height(1.)
        self.set_proportional_width(1.)
        self.set_p('row_colours', self.row_colours)
        self.set_p('col_colours', self.col_colours)
        self.set_p('scroll_offset', self.scroll_offset)
        self.set_max_dimensions((10*self.get_scaled_font_size(), 6*self.get_scaled_font_size()))
        self.set_min_dimensions(None)

    def __init__(self, parent, first_col = None, border = 2.0, cell_padding = 2,
                 add_first_cell = True, cell_class=GlypherTableCell) :
        self.scroll_offset = [0,0]
        GlypherPhraseGroup.__init__(self, parent, [])
        self.mes.append('table')
        self.add_properties({'default_cell_border' : None})

        self.cell_class = cell_class

        self.set_cell_padding(cell_padding)
        self.col_border = {}
        self.row_border = {}
        self.row_colours = {}
        self.col_colours = {}
        self.set_outside_border(None)
        self.set_p('align_as_entity', True)
        self.set_enterable(False)
        self.set_defaults()
        self.cells = {}

        if first_col is not None or add_first_cell :
            a = self.add_cell(0,0)
            self.set_recommending(a)
        if first_col is not None :
            a.append(first_col)
    
    def slide(self, h, v) :
        if (h!=0 and (self.scroll_offset[0]+h > 0 or \
                     self.scroll_offset[0]+h+(self.get_proportional_width()-1)*self.get_width() < 0)) or \
           (v!=0 and (self.scroll_offset[1]+v > 0 or \
                     self.scroll_offset[1]+v+(self.get_proportional_height()-1)*self.get_height() < 0)) :
               return
        self.scroll_offset[0] += h
        self.scroll_offset[1] += v

        if len(self.entities) > 0 :
            ents = self.sort_entities(rev=(h>0))
            for ent in ents :
                ent.translate(h, v, quiet=True)
        self.recalc_bbox()
        
    def process_scroll(self, event) :
        m_control = bool(event.state & gtk.gdk.CONTROL_MASK)

        if m_control :
            self.slide(0.3*self.get_scaled_font_size()*(\
                        -1 if event.direction == gtk.gdk.SCROLL_UP else 1),
                       0)
        else :
            self.slide(0, 0.3*self.get_scaled_font_size()*(-1 if event.direction == gtk.gdk.SCROLL_UP else 1))
        return True

    def set_row_colour(self, c, rgb) :
        for a in self.get_row(c) :
            a.get_entity().set_rgb_colour(rgb)
        self.row_colours[c] = rgb
    
    def set_col_colour(self, c, rgb) :
        for a in self.get_col(c) :
            a.get_entity().set_rgb_colour(rgb)
        self.col_colours[c] = rgb
    
    default_cell_border = None
    def set_default_cell_border(self, attr = None) :
        self.set_p('default_cell_border', attr)
        self.default_cell_border = attr

    def add_cell(self, r, c) :
        a = self.cell_class(self)
        self.append(a, row=r, col=c)

        if c in self.col_colours : a.set_rgb_colour(self.col_colours[c])
        if r in self.row_colours : a.set_rgb_colour(self.row_colours[r])

        if c not in self.col_border : self.col_border[c] = [None, None]
        if r not in self.row_border : self.row_border[r] = [None, None]

        a.set_padding_all(self.get_cell_padding())
        if c+1 in self.col_offsets and self.col_offsets[c+1] is not None : a.line_length = self.col_offsets[c+1]
        #debug_print((c, self.col_bboxes[c]))
        a.set_deletable(2)

        if r not in self.cells :
            self.cells[r] = {}
        self.cells[r][c] = a

        return a
    
    def set_outside_border(self, width = 1.0, colour = (0.0, 0.0, 0.0)) :
        self.set_outside_border({'width':width, 'colour':colour}) if width is not None else None
    def set_col_border_left(self, col, width = 1.0, colour = (0.0, 0.0, 0.0)) :
        self.col_border[col][0] = {'width':width, 'colour':colour}
    def set_col_border_right(self, col, width = 1.0, colour = (0.0, 0.0, 0.0)) :
        self.col_border[col][1] = {'width':width, 'colour':colour}
    def set_row_border_top(self, row, width = 1.0, colour = (0.0, 0.0, 0.0)) :
        self.row_border[row][0] = {'width':width, 'colour':colour}
    def set_row_border_bottom(self, row, width = 1.0, colour = (0.0, 0.0, 0.0)) :
        self.row_border[row][1] = {'width':width, 'colour':colour}
    
    def recalc_bbox(self, quiet = False, enact = True, realign = True,
                    sub_pos_search_dir = None, compare_rows = False,
                    in_feed_chain = False, do_reset = True) :
        chg = GlypherPhraseGroup.recalc_bbox(self, quiet, enact, realign,
                                             sub_pos_search_dir, compare_rows,
                                             in_feed_chain,
                                             do_reset=do_reset)
        if enact :
            self.config[0].bbox[0] -= self.scroll_offset[0]
            self.config[0].bbox[1] -= self.scroll_offset[1]
            self.config[0].bbox[2] -= self.scroll_offset[0]
            self.config[0].bbox[3] -= self.scroll_offset[1]

            self.set_proportional_height(self.get_height())
            self.set_proportional_width(self.get_width())
            md = self.get_max_dimensions()
            if md :
                self.config[0].bbox[2] = min(self.config[0].bbox[0]+md[0], self.config[0].bbox[2])
                self.config[0].bbox[3] = min(self.config[0].bbox[1]+md[1], self.config[0].bbox[3])
            md = self.get_min_dimensions()
            if md :
                self.config[0].bbox[2] = max(self.config[0].bbox[0]+md[0], self.config[0].bbox[2])
                self.config[0].bbox[3] = max(self.config[0].bbox[1]+md[1], self.config[0].bbox[3])
            self.set_proportional_height(self.get_proportional_height()/self.get_height() if self.get_height() != 0 else 0)
            self.set_proportional_width(self.get_proportional_width()/self.get_width() if self.get_width() != 0 else 0)
            self.recalc_basebox()
            self.feed_up(quiet=quiet, in_feed_chain=in_feed_chain)
        return chg

    def process_key(self, name, event, caret) :
        mask = event.state
        m_control = bool(mask & gtk.gdk.CONTROL_MASK)
        if name == 'Right' :
            self.suspend_recommending()
            self.add_table_column()
            self.resume_recommending()
        elif name == 'Down' :
            self.suspend_recommending()
            self.add_table_row()
            self.resume_recommending()
        else :
            return GlypherPhraseGroup.process_key(self, name, event, caret)
        return True

    def add_table_row(self) :
        u,w = self.row_range()
        for c in self.cols :
            self.add_cell(w+1, c)

    def add_table_column(self) :
        u,w = self.col_range()
        for r in self.rows :
            self.add_cell(r, w+1)

    def draw(self, cr) :
        if not self.get_visible() or self.get_blank() : return
        cr.save()
        cr.new_path()
        cr.set_source_rgba(0.0,0.0,0.0,0.2)
        cr.rectangle(self.config[0].bbox[0], self.config[0].bbox[1], \
            min(self.config[0].bbox[2]-self.config[0].bbox[0], self.get_max_dimensions()[0]),\
            min(self.config[0].bbox[3]-self.config[0].bbox[1], self.get_max_dimensions()[1]))
        cr.clip()
        GlypherPhraseGroup.draw(self, cr)

        if self.get_outside_border() is not None :
            cr.save()
            cr.set_line_width(self.get_outside_border()['width'])
            cr.set_source_rgba(*self.get_outside_border()['colour'])
            cr.rectangle(self.config[0].bbox[0], self.config[0].bbox[1], \
                min(self.config[0].bbox[2]-self.config[0].bbox[0], self.get_max_dimensions()[0]),\
                min(self.config[0].bbox[3]-self.config[0].bbox[1], self.get_max_dimensions()[1]))
            cr.stroke()
            cr.restore()

        cr.save()
        for r in self.rows :
            if len(self.get_row(r)) == 0 :
                continue
            b = self.row_border[r][0]
            if b is None :
                b = self.default_cell_border
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.config[0].bbox[0], self.row_bboxes[r][1])
                cr.line_to(self.config[0].bbox[2], self.row_bboxes[r][1])
                cr.stroke()
            b = self.row_border[r][1]
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.config[0].bbox[0], self.row_bboxes[r][3])
                cr.line_to(self.config[0].bbox[2], self.row_bboxes[r][3])
                cr.stroke()
        for c in self.cols :
            if len(self.get_row(c)) == 0 :
                continue
            b = self.col_border[c][0]
            if b is None :
                b = self.default_cell_border
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.config[0].bbox[0], self.row_bboxes[r][1])
                cr.line_to(self.config[0].bbox[2], self.row_bboxes[r][1])
                cr.stroke()
            b = self.row_border[r][1]
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.config[0].bbox[0], self.row_bboxes[r][3])
                cr.line_to(self.config[0].bbox[2], self.row_bboxes[r][3])
                cr.stroke()
        for c in self.cols :
            if len(self.get_row(c)) == 0 :
                continue
            b = self.col_border[c][0]
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.col_bboxes[c][0], self.config[0].bbox[1])
                cr.line_to(self.col_bboxes[c][0], self.config[0].bbox[3])
                cr.stroke()
            b = self.col_border[c][1]
            if b is not None :
                cr.set_line_width(b['width'])
                cr.set_source_rgba(*b['colour'])
                cr.move_to(self.col_bboxes[c][2], self.config[0].bbox[1])
                cr.line_to(self.col_bboxes[c][2], self.config[0].bbox[3])
                cr.stroke()
        cr.restore()
        cr.restore()

class GlypherMatrixCell(GlypherTableCell) :
    _am_zero = False
    def __init__(self, parent, area = (0,0,0,0), auto_copy_paste_contents = False) :
        GlypherTableCell.__init__(self, parent, area, auto_copy_paste_contents)
        self.mes.append('matrix_cell')
    def decorate(self, cr) :
        self.draw_topbaseline(cr)
        if not self.get_visible() : return
        if self.child_active :
            cr.save()
            cr.set_line_width(2.0)
            bbox = self.config[0].get_bbox()
            cr.rectangle(bbox[0]-2, bbox[1]-2, bbox[2]-bbox[0]+4, bbox[3]-bbox[1]+4)
            cr.set_source_rgba(0.0, 0.5, 0.0, 0.2)
            if g.stroke_mode :
                cr.fill_preserve()
                cr.set_source_rgba(0.0, 0.5, 0.0, 1.0)
                cr.stroke()
            else : cr.fill()
            cr.restore()
    def draw(self, cr) :
        if self.child_active or not (self._am_zero and g.zeros_mode) :
            return GlypherPhrase.draw(self, cr)
    def child_change(self) :
        self._am_zero = (self.to_string() == u'0')
        return GlypherPhrase.child_change(self)
    def get_sympy(self) :
        if len(self.get_entities()) == 0 :
            return 0
        return GlypherPhrase.get_sympy(self)

class GlypherDictionary(GlypherTable) :
    def __init__(self, d, parent, border = 0, cell_padding = 10) :
        GlypherTable.__init__(self, parent, first_col=None, border=border, cell_padding=cell_padding, add_first_cell=False)
        n = 0
        for key in d :
            a = self.add_cell(n,0)
            a.append(key)
            a = self.add_cell(n,1)
            a.append(d[key])
            n += 1
        self.set_col_colour(0, (0.4, 0.4, 0.8))

class GlypherList(GlypherTable) :
    def __init__(self, li, parent, border = 0, cell_padding = 10) :
        GlypherTable.__init__(self, parent, first_col=None, border=border, cell_padding=cell_padding, add_first_cell=False)
        n = 0
        for entry in li :
            a = self.add_cell(n,0)
            a.append(entry)
            n += 1

    def get_sympy() :
        return [cell.get_sympy() for cell in self.get_col(0)]

class GlypherMatrix(GlypherPhraseGroup) :
    table = None

    def get_pow_options(self) :
        return ('python', 'elementwise')

    def get_dims(self) :
        return self.table.get_dims()

    def ij(self, i, j) :
        return self.table.ij(i,j)

    def get_xml(self, name=None, top=True, targets=None, full=False) :
        root = GlypherPhraseGroup.get_xml(self, name, top, targets, full)
        self.table._xml_table(root)

        return root

    @classmethod
    def parse_element(cls, parent, root, names, targets, operands, recommending, lead,
                  add_entities, am = None, top = True) :
        rows = int(root.get('rows'))
        cols = int(root.get('cols'))
        matrix = GlypherMatrix(parent, rows, cols)

        for cell in root.find('cells'):
            c = Parser.parse_element(matrix, cell, names, targets, operands,
                              recommending, lead, add_entities, top=False)
            matrix.ij(int(cell.get('table_row')),
                      int(cell.get('table_col'))).adopt(c)

        matrix.recalc_bbox()

        return matrix

    @classmethod
    def from_python_lists(cls, parent, py_lists) :
        matrix = cls(parent, rows=len(py_lists), cols=len(py_lists[0]))

        for i in range(0, len(py_lists)) :
            for j in range(0, len(py_lists[i])) :
                matrix.ij(i,j).adopt(py_lists[i][j])

        return matrix

    def __init__(self, parent, rows = 1, cols = 1) :
        GlypherPhraseGroup.__init__(self, parent)
        self.mes.append('matrix')

        # Set up an outer BracketedPhrase
        bracketed_phrase = GlypherBracketedPhrase(parent, auto=False)
        bracketed_phrase.set_attachable(False)
        bracketed_phrase.set_enterable(False)
        bracketed_phrase.set_deletable(3)
        self.adopt(bracketed_phrase)

        # Make a Table
        table = GlypherTable(parent, add_first_cell=False,
                             cell_class=GlypherMatrixCell)
        table.set_cell_padding(3)

        #table.set_default_cell_border({'width':1.0,'colour':(0.6,0.8,0.6)})

        for i in range(0, rows) :
            for j in range(0, cols) :
                table.add_cell(i, j)

        table.set_p('align_as_entity', True)
        table.set_attachable(False)
        table.set_deletable(3)
        bracketed_phrase.adopt(table)
        self.table = table

    def get_sympy(self) :
        '''Return a sympy matrix.'''

        table = self.table
        py_mat = [ [cell_cfg.get_entity().get_sympy() for cell_cfg in table.get_row(r)] \
                  for r in table.rows ]

        return matrices.Matrix(py_mat)

g.phrasegroups['matrix'] = GlypherMatrix
g.phrasegroups['table'] = GlypherTable
g.phrasegroups['table_cell'] = GlypherTableCell
g.phrasegroups['matrix_cell'] = GlypherMatrixCell
Parser.parse_element_fns['matrix'] = GlypherMatrix.parse_element
