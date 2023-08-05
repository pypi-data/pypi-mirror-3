import glypher as g
from ..utils import debug_print
import StringIO
import cairo
import time
import copy
import traceback
import sympy
import draw
import Entity
import Parser
import gutils
import xml.etree.ElementTree as ET

# Comparison functions
ac = gutils.array_close
fc = gutils.float_close
fgte = gutils.float_greater_than_or_equal
fgt = gutils.float_greater_than
flt = gutils.float_less_than

# Motion tolerance; when we give up aligning
sm_tol = g.sm_tol
bg_tol = g.bg_tol
_testing_phr = None

GLYPHERDIRECTION_UP   =  1
GLYPHERDIRECTION_DOWN = -1

default_keep_min_row_height = True

class GlypherPhrase(Entity.GlypherEntity) :
    '''
    Main container class
    '''

    rows = None
    cols = None
    row_offsets = None
    col_offsets = None
    row_aligns = None
    col_aligns = None
    row_bboxes = None
    col_bboxes = None
    row_redirects = None
    col_redirects = None
    name = None

    is_caching = False
    cached_xml = None

    width = 0

    # Default binary expression containment rule
    stop_for_binary_expression_default = False
    # Exceptions to the rule
    stop_for_binary_expression_exceptions = ()

    def stop_for_binary_expression(self, name) :
        """
        If a BinaryExpression is suggested inside this PhraseGroup, do we force
        it to render below here, or check whether we should continue checking
        upwards for an extant BinaryExpression to tag it on to.
        """
        return self.stop_for_binary_expression_default ^ \
               (name in self.stop_for_binary_expression_exceptions)

    def __len__(self) :
        """Return the number of entities in this entity (not .IN()!)."""
        return len(self.entities)

    def __getitem__(self, key) :
        """Return the key-th item in the sorted entities (not .IN()!)."""
        if not isinstance(key, int) :
            raise KeyError("""
                           Looking for non-int index in a Phrase; did you want
                           a PhraseGroup?
                           """)
        return self.sort_entities()[key]

    def is_leading_with_num(self) :
        '''
        Tells us whether this function starts with a digit, for visual
        formatting purposes
        '''
        return len(self.rows) == 1 and len(self.get_row(0)) > 0 and  \
            self.get_row(0)[0].get_entity().am('phrase') and \
            self.get_row(0)[0].get_entity().is_leading_with_num()

    def set_row_col_defaults(self) :
        '''
        Note the default row/col_aligns for XML omission, if unchanged.
        '''
        self.default_row_aligns = self.row_aligns.copy()
        self.default_col_aligns = self.col_aligns.copy()

    def get_bold(self) : 
        return self.get_ip('bold')
    def set_bold(self, bold) :
        self.set_ip('bold', bold)

    def get_entities(self) :
        '''
        Return (a tuple copy of) the list of entities
        '''
        if self != self.IN() : return self.IN().get_entities()
        return tuple(self.entities)
    
    def get_row(self, r, only_visible = False) :
        '''
        Return configs in a given row, potentially restricting to visible.
        '''
        cfgs = self.sort_configs()
        if only_visible :
            return filter(\
                lambda c : c.row==r and c.get_entity().get_visible(), cfgs)
        else :
            return filter(lambda c : c.row==r, cfgs)
    
    def get_col(self, r, only_visible = False) :
        '''
        Return configs in a given col, potentially restricting to visible.
        '''
        cfgs = self.sort_configs()
        if only_visible :
            return filter(\
                lambda c : c.col==r and c.get_entity().get_visible(), cfgs)
        else :
            return filter(lambda c : c.col==r, cfgs)
    
    def set_col_align(self, r, align) :
        '''
        Set the alignment of a given column.
        '''
        self.col_aligns[r] = align
        self.recalc_bbox()

    def set_row_align(self, r, align) :
        '''
        Set the alignment of a given row.
        '''
        self.row_aligns[r] = align
        self.recalc_bbox()

    def set_default_entity_xml(self) :
        '''
        Log the XML at creation to work out whether its changed come compilation
        (and so needs stored)
        '''
        for e in self.entities :
            self.default_entity_xml[e] = \
            ET.tostring(e.get_xml(name=e.get_name(), top=False))

    def get_xml(self, name=None, top=True, targets=None, full=False) :
        '''
        Retrieve an XML expression for this Phrase and its contents.
        '''
        root = Entity.GlypherEntity.get_xml(self, name, top, full=full)

        ents = ET.Element('entities')
        ent_list = self.sort_entities()

        # Add in all of the contained entities
        for e in ent_list :
            r = e.get_xml(name=e.get_name(), top=False, targets=targets,
                          full=full)
            if e.am('target_phrase') :
                # If this is a target, note it
                if targets is not None and e in targets.values() :
                    r.set('target', e.get_name())
                continue
            # Include placement information
            if e.config[0].row != 0 :
                r.set('row', str(e.config[0].row))
            if e.config[0].col != 0 :
                r.set('col', str(e.config[0].col))
            m = ' '.join(map(str, e.padding))
            if m != "0.0 0.0 0.0 0.0" :
                r.set('padding', m)

            # Mention what this is
            r.set('type', e.mes[len(e.mes)-1])

            # If this wasn't the same when we set the default XML, include it
            if e not in self.default_entity_xml or \
                    ET.tostring(r) != self.default_entity_xml[e] :
                ents.append(r)
        if len(ents) > 0 :
            root.append(ents)

        # Things to get rid of
        #FIXME: does this do anything?
        rms = ET.Element('removes')
        for e in self.default_entity_xml :
            if e not in self.entities :
                ET.SubElement(rms, e.get_name())
        if len(rms) > 0 : root.append(rms)

        # Store details of the rows themselves
        rows = ET.Element('rows')
        for r in self.rows :
            row = ET.Element('row')
            row.set('id', str(r))
            if self.row_offsets[r] is not None :
                row.set('offset', str(self.row_offsets[r]))
            if r not in self.default_row_aligns or \
              self.row_aligns[r] is not self.default_row_aligns[r] :
                row.set('align', self.row_aligns[r])
            if len(row.keys()) > 1 : rows.append(row)
        if len(rows) > 0 : root.append(rows)

        # Store details of the cols themselves
        cols = ET.Element('cols')
        for r in self.cols :
            col = ET.Element('col')
            col.set('id', str(r))
            if self.col_offsets[r] is not None :
                col.set('offset', str(self.col_offsets[r]))
            if r not in self.default_col_aligns or \
              self.col_aligns[r] is not self.default_col_aligns[r] :
                col.set('align', self.col_aligns[r])
            if len(col.keys()) > 1 : cols.append(col)
        if len(cols) > 0 : root.append(cols)

        debug_print(ET.tostring(root))
        return root
    
    # FIXME: why aren't we passing the quiet through !?
    def children_check(self, parent_change=False, quiet=False, force=False) :
        '''
        See if some change to the inherited properties needs filtered down
        '''
        resp = self.check_inherited_properties()
        if not force and resp == 0 : return

        # This assumes that if a recalc is necessary, it will happen when one of
        # the children changes
        if self.entities and len(self.entities) > 0 :
            for ent in self.entities :
                ent.children_check(parent_change=parent_change, quiet=quiet)
        elif not quiet and resp == 2 :
            self.recalc_bbox(quiet=quiet)
            self.child_altered()

        if g.anal_retentive_mode :
            self.consistency_check_sub_poses()

        self.set_redraw_required()

    def is_enterable(self) :
        '''
        Can the caret rest directly inside this?
        '''
        if self != self.IN() :
            return self.IN().is_enterable()
        return (self.get_enterable() or self.is_edit_mode()) and \
               self.get_visible() and not self.get_blank()

    def child_change(self) :
        '''
        Feed up a change for the parent
        '''
        if self.included() :
            self.get_parent().child_change()

    def delete(self, sender=None, if_empty=False, quiet=False) :
        '''
        Get rid of this entity.
        if_empty - only delete if no children
        '''

        if not if_empty or len(self.get_entities()) == 0 :
            return Entity.GlypherEntity.delete(self)

        # Tell parent
        if not quiet :
            self.child_change()
    
    def empty(self, override_in = False) :
        '''
        Dump all of the children
        '''
        if not override_in and self != self.IN() :
            self.IN().empty()
            return
        l = list(self.entities)
        for ent in l :
            self.remove(ent)

    def __init__(self, parent, area=(0,0,0,0), line_size_coeff=1.0,
                 font_size_coeff=1.0, align=('l','m'), auto_fices=False,
                 align_as_entity = False) :

        # Generate dictionaries and lists belonging to this object
        self.entities = []
        self.rows = []
        self.cols = []
        self.col_bboxes = {}
        self.col_offsets = {}
        self.col_aligns = {}
        self.col_redirects = {}
        self.row_bboxes = {}
        self.row_offsets = {}
        self.row_aligns = {}
        self.row_redirects = {}

        Entity.GlypherEntity.__init__(self, parent)

        # Add child_configs member to our first config - only useful
        # for phrases
        self.config[0].child_configs = []

        # Give self a provisional name
        self.set_name('phrase_'+str(id(self)))

        # Set default properties
        self.add_properties(\
            {'default_offset_per_row' : 30,
             'blank_ratio' : 0.0,
             'align_as_entity' : False, 
             'is_decorated': False,
             'enterable' : True})

        # Not currently displaying alternatives
        self.active = False

        # Generate an initial bbox
        self.config[0].set_bbox(area)
        self.config[0].baseboxes = {}

        # Add my type
        self.mes.append('phrase')

        # Minimal row/col
        self.add_row(0)
        self.add_col(0)
        self.set_row_col_defaults()

        # No children are currently active
        self.child_active = False

        # Reset & recalc
        self.recalc_baseboxes()
        self.config[0].reset()
        self.recalc_bbox(quiet = True)

        # If anyone's looking for a caret target, pick me
        self.set_recommending(self)

        # Save XML setup as default
        self.default_entity_xml = {}
        self.set_default_entity_xml()

        # Set the font size scaling from the init args
        self.set_font_size_scaling(font_size_coeff)

    def elevate_entities(self, new_parent, adopt=False, to_front=False) :
        '''
        Lift this phrase's children to a new_parent
        '''

        if self.IN() != self :
            self.IN().elevate_entities(new_parent, adopt, to_front)
            return

        l = list(self.entities)
        for ent in l :
            self.remove(ent)

            # Move to the front of this element before reattaching
            if to_front :
                ent.translate(\
                    self.OUT().config[0].bbox[0]-ent.config[0].bbox[0],0)

            if adopt :
                new_parent.adopt(ent)
            else :
                new_parent.append(ent)

    def exchange(self, former, latter) :
        '''
        Swap an entity for a child
        '''

        # Add after the current child
        self.append(latter, after=former, row=former.config[0].row,
                    col=former.config[0].col)

        # Orphan the current child
        former.orphan()

        self.set_recommending(latter)

    def set_child_active(self, child_active, desc) :
        '''
        Set the child_active flag
        '''

        self.child_active = child_active
        # This goes for parents too
        if self.included() :
            self.get_parent().set_child_active(child_active, desc)
    
    def set_col_redirect(self, col, to_phrase) :
        '''
        Rather than following standard search, Caret should go here when asked
        to enter column.
        '''

        self.col_redirects[col] = to_phrase

    def get_col_redirects(self) :
        '''
        Where are the column redirects going?
        '''

        if self != self.OUT() :
            return self.OUT().get_col_redirects()
        return self.col_redirects

    def set_row_redirect(self, row, to_phrase) :
        '''
        Rather than following standard approach, Caret should go here when asked
        to enter row.
        '''

        self.row_redirects[row] = to_phrase

    def get_row_redirects(self) :
        '''
        Where are the row redirects going?
        '''

        if self != self.OUT() :
            return self.OUT().get_row_redirects()
        return self.row_redirects

    def to_string(self, mode = "string") :
        '''
        Generate a unicode representation of this Phrase by concatenating string
        representations of its contents
        '''

        if not self.get_visible() :
            return unicode("")
        elif self.get_blank() :
            return unicode(" ")

        ents = self.sort_entities()
        body = unicode('').join([l.to_string(mode) for l in ents])
        return self.string_compile(body, mode)
    
    def to_latex(self) :
        '''
        Generate a LaTeX representation of this Phrase by concatenating LaTeX
        representations of its contents
        '''

        if not self.get_visible() :
            return ""
        elif self.get_blank() :
            return " "

        ents = self.sort_entities()
        body = ''.join([l.to_latex() for l in ents])
        return body
    
    def get_sympy(self) :
        '''
        Return a sympy version of this entity. If it isn't a 1-entity phrase,
        this must be overridden
        '''
        if len(self.IN().entities) == 0 :
            return None
        if len(self.IN().entities) == 1 :
            return self.IN().entities[0].get_sympy()
        raise RuntimeError(\
            "get_sympy: Multiple ents in phrase without get_sympy overridden")
    
    def _translate_enact(self, h, v, search_dir_fwd, config = None) :
        '''
        Do the hard labour of moving this object.
        '''

        Entity.GlypherEntity._translate_enact(self, h, v, search_dir_fwd,
                                              config=config)

        # If this object creates a local space, its internals should not move.
        if self.get_local_space() :
            return

        #FIXME: Tidy to avoid multiple recalcs
        #FIXME: Just eww.
        for r in self.row_bboxes :
            # If we have multiple configs and no rows (or child rows) ???
            #FIXME: what's going on here?
            if len(self.config) > 1 and config is not None and \
               len(set(self.rows) & \
                   set([c.row for c in self.config[config].child_configs]))==0:
                continue
            # if we have multiple configs and not all rows appear in this config
            elif len(self.config) > 1 and config is not None and \
               len(set(self.rows) - \
                   set([c.row for c in self.config[config].child_configs])) > 0:
                self.recalc_bbox(quiet=True, realign=False)
            # otherwise, we expect the row bboxes will just be the direct
            # translation of what they were
            else :
                self.row_bboxes[r][0] += h
                self.row_bboxes[r][2] += h
                self.row_bboxes[r][1] += v
                self.row_bboxes[r][3] += v

        # Same for columns
        for c in self.col_bboxes :
            if len(self.config) > 1 and config is not None and \
               len(set(self.cols) & \
                   set([d.col for d in self.config[config].child_configs]))==0:
                continue
            elif len(self.config) > 1 and config is not None and \
               len(set(self.cols) - \
                   set([d.col for d in self.config[config].child_configs])) > 0:
                self.recalc_bbox(quiet=True, realign=False)
            else :
                self.col_bboxes[c][0] += h
                self.col_bboxes[c][2] += h
                self.col_bboxes[c][1] += v
                self.col_bboxes[c][3] += v

    def translate(self, h, v, quiet=False, by_offset=True, after=None,
                  config=None, do_reset=True) :
        '''
        Move self and children, ideally without full recalc

        after - whether this should receive first or last subpos once moved
                (default : (h<0))
        '''

        if after is None :
            after = (h<0)

        # If we are in local space and are moving our first (reference) config,
        # we must instead move everything else the other way - potentially slow,
        # but usually outweighed by advantage of never having to translate the
        # first config (in local space mode). Its a bit like being the first
        # person in a bus queue and moving three side-steps towards the bus.
        # You've moved, but if the coordinate space is local to the queue 
        # (of which you are the head), actually everybody else just moved three
        # steps away.
        reverse_move = (config is 0 and self.get_local_space() and \
                        len(self.config) > 1)

        # If we have child entities and are not the only config in a local
        # space, move the children
        if len(self.entities) > 0 and (not self.get_local_space() or \
                                       (config not in (0,None)) or \
                                       reverse_move) :
            lh = h; lv = v

            # In local space, the anchor point is on config 0, so moving 0
            # is equivalent to moving all other configs the opposite direction
            #FIXME: isn't this just reverse_move ?
            if self.get_local_space() and config is 0 and len(self.config) > 1 :
                lh = -h; lv = -v
                cfgs = filter(lambda c : c.parent_config_index != 0,
                              self.sort_configs(rev=(lh>0)))
            else :
                cfgs = self.sort_configs(rev=(lh>0), config=config)

            # Actually move all (the entities providing) the component configs
            for cfg in cfgs :
                ent = cfg.get_entity()
                ent.translate(lh, lv, quiet=True, by_offset=by_offset,
                              config=cfg.index)

        # Actually move our own structure
        self._translate_enact(h, v, after, config=config)

        # If movements are being saved up before feeding up, let our caller deal
        # with it
        if do_reset :
            self.feed_up(quiet=quiet)

    def scale(self, s, quiet = False) :
        '''
        Try to scale this entity and children without a recalc
        '''

        # Don't scale if we're (close enough) scaling by 1.0
        if fc(s, 1.0) :
            return

        # Look at children if we have any
        if len(self.entities) > 0 :
            cfgs = self.sort_configs()

            # Define our new bottom-left offset
            if self.get_local_space() :
                l, b = (0,0)
            else :
                l = self.config[0].bbox[0]; b = self.config[0].bbox[3]

            # Translate all the configs to their new bottom left corners
            for cfg in cfgs :
                ent = cfg.get_entity()
                d1 = cfg.bbox[0]-l; d2 = cfg.bbox[3]-b
                ent.translate(d1*(s-1), d2*(s-1), quiet=True, config=cfg.index)

            # Scale them where they stand
            for ent in self.entities :
                ent.scale(s, quiet=True)

        # Scale our own structure
        self._scale_enact(s)

        if len(self.rows) > 0 or len(self.cols) > 0 :
            self.recalc_bbox(quiet=quiet)
        else :
            # Tell the world
            self.feed_up(quiet=quiet)
    
    def _scale_enact(self, s) :
        '''
        Mechanics of scaling our this entity's structure
        '''

        Entity.GlypherEntity._scale_enact(self, s)
        return
    
    def get_configs(self, config=None, only_visible=False) :
        '''
        Pick out all our child configs
        '''

        # Collect all child configs or just child configs of one child
        if config is None :
            cfgs = [cfg for cfgs in \
                    [self.config[c].child_configs for c in self.config] \
                    for cfg in cfgs]
        else :
            cfgs = self.config[config].child_configs

        # Return all configs or only the visible ones
        if only_visible :
            return filter(lambda c : c.get_entity().get_visible(), cfgs)
        else :
            return cfgs

    def get_free_sub_pos(self, child, search_dir_fwd=True) :
        '''
        Find a free sub position for a child config, that is an unoccupied index
        amongst the children sharing a point for their left bound
        '''

        cfgs = self.get_configs()
        new_sub_pos = 0
        for cfg in cfgs :
            # Ignore this cfg if it isn't matched on left
            if not fc(cfg.bbox[0], child.bbox[0]) or cfg.row != child.row or \
                    cfg.col != child.col :
                continue
            # Ignore this config if it's the child
            if cfg == child :
                continue
            # Increment or decrement new_sub_pos if this config has taken it
            if search_dir_fwd :
                if cfg.sub_pos >= new_sub_pos :
                    new_sub_pos = cfg.sub_pos+1
            elif cfg.sub_pos <= new_sub_pos :
                    new_sub_pos = cfg.sub_pos-1

        return new_sub_pos
    
    def format_entities(self) :
        '''
        List the format_me's for each child entity
        '''
        return "\n".join([str(e.format_me()) for e in self.entities])

    def consistency_check_sub_poses(self) :
        '''
        As one of the first indications of an alignment/movement screw-up is
        often the appearance of two entities at the same point and subpos, this
        convenience function can be called to make sure it hasn't happened.
        '''

        for ent in self.entities :
            for a in self.entities :
                if a != ent and \
                        fc(a.config[0].bbox[0], ent.config[0].bbox[0]) and\
                        a.config[0].sub_pos == ent.config[0].sub_pos and \
                        a.config[0].row == ent.config[0].row and \
                        a.config[0].col == ent.config[0].col :
                    debug_print(a.format_me())
                    debug_print(self.format_me())
                    debug_print(self.format_entities())
                    raise RuntimeError(\
                        'Two elements found sharing same position, '+\
                        'sub-position and row')

    def get_new_sub_pos_after(self, after) :
        '''
        Adds a subpos directly after the config 'after', moving subsequent
        configs along if necessary
        '''

        parent_config = self.config[after.parent_config_index]
        for cfg in parent_config.child_configs :
            if not fc(cfg.bbox[0], after.bbox[0]) \
                    or cfg.row != after.row or cfg.col != after.col :
                continue
            if cfg.sub_pos > after.sub_pos :
                cfg.sub_pos += 1

        if g.anal_retentive_mode :
            self.consistency_check_sub_poses()

        return after.sub_pos + 1

    def sort_entities(self, rev=False, old=False, only_visible=False) :
        '''
        Return a sorted copy of the entities. This is sorted in a unique ordered
        determined by a the entity's first child's col, row, pos and subpos
        '''

        if only_visible :
            ents = filter(lambda c : c.get_visible(), self.entities)
        else :
            ents = list(self.entities)

        # If we're empty, return trivial list
        if len(ents) == 0 :
            return []

        # Direction int
        d = -1 if rev else 1

        # Compare pos's
        b = lambda x : x.config[0].old_bbox[0] if old else x.config[0].bbox[0]
        # Compare subpos's
        c = lambda x : x.config[0].old_sub_pos if old else x.config[0].sub_pos

        ents.sort(lambda x,y :\
            -d if x.config[0].col < y.config[0].col else
             d if x.config[0].col > y.config[0].col else
            -d if x.config[0].row < y.config[0].row else
             d if x.config[0].row > y.config[0].row else
            -d if flt(b(x), b(y)) or (fc(b(x), b(y)) and flt(c(x), c(y))) else \
             d if flt(b(y), b(x)) or (fc(b(x), b(y)) and flt(c(y), c(x))) else \
             0 )

        return ents

    def sort_configs(self, rev=False, old=False, config=None) :
        '''
        Like the ent sorting, but we consider all individual configs
        '''

        cfgs = self.get_configs(config)
        d = -1 if rev else 1
        if len(cfgs) == 0 : return []
        b = lambda x : x.old_bbox[0] if old else x.bbox[0]
        c = lambda x : x.old_sub_pos if old else x.sub_pos
        cfgs.sort(lambda x,y :\
            -d if x.col < y.col else
             d if x.col > y.col else
            -d if x.row < y.row else
             d if x.row > y.row else
            -d if flt(b(x), b(y)) or (fc(b(x), b(y)) and flt(c(x), c(y))) else \
             d if flt(b(y), b(x)) or (fc(b(x), b(y)) and flt(c(y), c(x))) else \
             0 )
        return cfgs

    def child_altered(self, child = None) :
        '''
        Tell any parent that a child has been altered
        '''

        if self.included() :
            self.get_parent().child_altered(self)

    def child_bbox_change(self, child) :
        '''
        One of our child element bboxes has changed! Move any children that need
        to move to compensate.
        '''

        if g.anal_retentive_mode and self.get_parent() :
            self.get_parent().consistency_check_sub_poses()

        for c in child.config :
            child_cfg = child.config[c]

            # What is the bbox of this config?
            cb  = child_cfg.get_bbox()
            # What was the bbox of thie config?
            cob = list(child_cfg.old_bbox)

            cfgs = self.sort_configs(rev=False, old=True)

            # We're looking for knock-on effect on the rest of our configs;
            # where do we start?
            root = cfgs.index(child_cfg)

            # We'll need to calculate knock-on of left bdy movement, then right
            # bdy movement; should we go up the way or down?
            go_down = (cb[0]>cob[0], cb[2]>cob[2])
            # Where do we start from?
            i = root if go_down[0] else -1

            # Make sure something's actually changed
            if not ac(child_cfg.bbox, child_cfg.old_bbox) : 

              for n in (0, 1) :
                d = -1 if go_down[n] else 1
                i += d

                # If the left bdy has moved, make sure we have (the right) free
                # subpos.
                # Irrelevant the first time through, as overwritten on second
                if not fc(cb[0], cob[0]) :
                    child_cfg.sub_pos = \
                        self.get_free_sub_pos(child_cfg, search_dir_fwd=True)

                # Loop through the configs on whichever side
                while i >= 0 and i < len(cfgs) and i != root :
                    ecfg = cfgs[i]
                    ent = ecfg.get_entity()
                    if ecfg == child_cfg :
                        continue
                    eb  = list(ecfg.bbox)

                    # If child on the right of this cfg
                    if (flt(eb[2], cob[2])) and \
                            ecfg.row == child_cfg.row and \
                            ecfg.col == child_cfg.col :
                        ent.translate(cb[0] - cob[0], 0, quiet=True,
                                      config=child_cfg.index)
                    # If child on the left
                    if (fgte(eb[2], cob[2]) and \
                            (fgt(cob[2], cob[0]) or (fgt(eb[0], cob[0]) or \
                            (fc(eb[0], cob[0]) and \
                            ecfg.sub_pos > child_cfg.old_sub_pos)))) and \
                            ecfg.row == child_cfg.row and \
                            ecfg.col == child_cfg.col :
                        ent.translate(cb[2] - cob[2], 0, quiet=True,
                                      config=child_cfg.index)

                    i += d

                    # Very specific case (guess how many screeds of bbox output
                    # it took to find this bug) where we are in the second
                    # sorting loop, the child cfg is zero width, its right end
                    # hasn't moved and the current cfg under consideration has a
                    # left end on that boundary. Then we may need to give the
                    # current cfg a new subpos. Best way to think about this
                    # (and the whole routine) is as a deck of cards, spread out
                    # in a line with potential for overlap. When the left edges
                    # match, to provide a consistent order and to move them back
                    # and forward in order, we must assign vertical positions
                    # when the left edges match. Now imagine what happens if you
                    # take a card and change its width where it sits - what
                    # happens to the cards on either side and what order do you
                    # have to move them to preserve the distances and ordering?
                    if n==1 and fc(cb[0], cb[2]) and \
                            fc(cob[2], cb[2]) and fc(eb[0], cob[2]) :
                        ecfg.sub_pos = self.get_free_sub_pos(ecfg,
                                           search_dir_fwd=(not go_down[1]))
                        ecfg.old_sub_pos = ecfg.sub_pos
                #Where does the second loop start from?
                i = len(cfgs) if go_down[1] else root

            # This whole routine cries out "TROUBLE HERE!!!"; consistency check
            # is slow but not a bad idea for AR mode.
            if g.anal_retentive_mode and self.get_parent() :
                self.get_parent().consistency_check_sub_poses()

            child_cfg.old_sub_pos = child_cfg.sub_pos

        # Make sure any child movement we have initiated is incorporated (this
        # will also do the job of calling the same routine in any parent we
        # might have.
        self.recalc_bbox(in_feed_chain=True)
    
    def entities_by_name(self) :
        '''
        Return an (ordered) list of child entity names
        '''
        ents = self.sort_entities()
        return [p.get_name() for p in ents]

    def format_configs(self, collapsed=True) :
        '''
        Like format_entities but concatenating config details (or providing a
        list of them)
        '''
        cfgs = self.sort_configs()
        format_list = []
        for p in cfgs :
            name = '"'+str(p.to_string())+'"'
            if name is not None :
                name += ' ['+str(p.to_string())+']'
            format_list.append(name+'['+str(p.index)+']' + ' ' + str(p.bbox) +\
                               ":" + str(p.row) + '~' + str(p.col) + '\n')
        return "; ".join(format_list) if collapsed else format_list

    def col_range(self) :
        '''
        Return min and max col indices
        '''
        u,l = (0,0)
        for r in self.cols :
            if r > u : u = r
            if r < l : l = r
        return (u,l)

    def row_range(self) :
        '''
        Return min and max row indices
        '''
        u,l = (0,0)
        for r in self.rows :
            if r > u : u = r
            if r < l : l = r
        return (u,l)

    def add_col(self, r, col_align='m') :
        '''
        Add a rew column at index r (which will be changed to one beyond current
        limit if too big or small)
        '''

        # Don't try to add an existing col
        if r in self.cols :
            return

        u,l = self.col_range()
        if r < l :
            r = l - 1
        elif r > u :
            r = u + 1
            
        self.cols.append(r)

        self.col_aligns[r] = col_align

        # Starting, default offset
        offset = self.get_p('default_offset_per_row')*r

        # Initial bbox
        self.col_bboxes[r] = [self.config[0].bbox[0]+offset, self.get_topline(),
            self.config[0].bbox[2]+offset, self.get_baseline()]

        # It's possible an overriding offset has already been set (even if
        # column hasn't existed). If so, don't overwrite it
        if r not in self.col_offsets :
            self.col_offsets[r] = None

        return r
    
    def add_row(self, r, row_align='l') :
        '''
        Add a rew row at index r (which will be changed to one beyond current
        limit if too big or small)
        '''

        if r in self.rows : return

        u,l = self.row_range()
        if r < l :
            r = l - 1
        elif r > u :
            r = u + 1
            
        self.rows.append(r)

        self.row_aligns[r] = row_align

        offset = self.get_p('default_offset_per_row')*r

        self.row_bboxes[r] = [self.config[0].bbox[0], self.get_topline()+offset,
            self.config[0].bbox[0], self.get_baseline()+offset]

        #FIXME: why do these two statements not match col version?
        self.row_offsets[r] = None

        self.recalc_row_basebox(r)

        return r
    
    #FIXME: Check this, it probably doesn't work
    def remove_col(self, r) :
        '''
        Delete a column
        '''

        # Make sure we aren't deleting the 0th col
        if r not in self.cols or r == 0 :
            return

        self.cols.remove(r)
        del self.col_bboxes[r]
        del self.col_offsets[r]
        del self.col_aligns[r]

        # Move other cols in to avoid gaps
        u,l = self.col_range()
        if r > 0 :
            for i in range(r+1, u+1) :
                re = self.get_col(i)
                for e in re : e.col -= 1
        elif r < 0 :
            for i in range(l+1, r+1) :
                i = r+l-i
                re = self.get_col(i)
                for e in re : e.col += 1

        self.recalc_bbox()
    
    #FIXME: Check this, it probably doesn't work
    #FIXME: Why doesn't this match col?
    def remove_row(self, r) :
        '''
        Delete a row
        '''

        if r not in self.rows or r == 0 :
            return

        u,l = self.row_range()
        if r > 0 :
            for i in range(r+1, u+1) :
                re = self.get_row(i)
                for e in re : e.row -= 1
                self.row_bboxes[i-1] = self.row_bboxes[i]
                self.row_aligns[i-1] = self.row_aligns[i]
                self.row_offsets[i-1] = self.row_offsets[i]

            del self.row_aligns[u]
            del self.row_offsets[u]
            del self.row_bboxes[u]
            self.rows.remove(u)
        elif r < 0 :
            for i in range(l+1, r+1) :
                i = r+l-i
                re = self.get_row(i)
                for e in re : e.row += 1
                self.row_bboxes[i+1] = self.row_bboxes[i]
                self.row_aligns[i+1] = self.row_aligns[i]
                self.row_offsets[i+1] = self.row_offsets[i]

            del self.row_aligns[l]
            del self.row_offsets[l]
            del self.row_bboxes[l]
            self.rows.remove(l)

        self.recalc_bbox()

    def get_cell_bbox(self, r, c) :
        '''
        Get a bounding box for a specific row and column combo
        '''
        
        # All configs in this row and col
        cfgs = list(set(self.get_row(r)) & set(self.get_col(c)))

        # If we don't have any cfgs, return a zero-width bbox between row bbox
        # limits
        if len(cfgs) == 0 :
            if self.col_offsets[c] is None :
                l = self.col_bboxes[c][0]
            else :
                l = self.col_offsets[c]+self.col_bboxes[0][0]

            return [l, self.row_bboxes[r][1], l, self.row_bboxes[r][3]]

        # Start with first cfg and expand to include all others
        bbox = list(cfgs[0].bbox)
        for c in cfgs :
            ent = c.get_entity()
            if not ent.get_horizontal_ignore() and c.bbox[0] < bbox[0] :
                bbox[0] = c.bbox[0]
            if not ent.get_vertical_ignore()   and c.bbox[1] < bbox[1] :
                bbox[1] = c.bbox[1]
            if not ent.get_horizontal_ignore() and c.bbox[2] > bbox[2] :
                bbox[2] = c.bbox[2]
            if not ent.get_vertical_ignore()   and c.bbox[3] > bbox[3] :
                bbox[3] = c.bbox[3]

        return bbox
        
    def append(self, entity, quiet=False, recalc=True, row=0, col=0,
               override_in=False, move=(True,True), align=None, after=None) :
        '''
        Add an entity to the children. This, along with recalc_bbox and
        child_bbox_change are where it all happens in this object.
        '''

        if self.IN() != self and not override_in :
            self.IN().append(entity, quiet, recalc, row=row, col=col)
            return

        entity = entity.OUT()
        rel_scale = entity.get_scaled_font_size()

        # Make sure this entity is indeed parentless
        if entity.included() :
            raise RuntimeError('Trying to append an already included entity: '+\
                               str(entity.format_me())+\
                               ' into '+str(self.format_me()))

        # If anybody asks where to go, tell them whatever the entity
        # (at this moment) suggests
        self.set_recommending(entity.get_recommending())

        # Add rows and cols if necessary
        #FIXME: what happens if the row and col added aren't row & col?
        if row not in self.rows :
            row = self.add_row(row)
            self.config[0].reset()
        if col not in self.cols :
            col = self.add_col(col)
            self.config[0].reset()

        # Calculate the row and col offsets that adjust the entity's offset from
        # the Phrase's anchor
        row_offset = self.row_bboxes[row][3] - self.config[0].bbox[3]
        col_offset = self.col_bboxes[col][2] - self.config[0].bbox[2]
        if self.row_offsets[row] is not None :
            row_offset = self.row_offsets[row]
        if self.col_offsets[col] is not None :
            col_offset = self.col_offsets[col]

        # Get the limits of the current row-col cell
        cell_bbox = self.get_cell_bbox(row, col)

        # Pick out the final config of whatever we're locating the entity after
        if after is not None :
            ac = after.config[len(after.config)-1]

        # Pick the appropriate anchor to translate the entity
        if after == self :
            l = cell_bbox[0]
        elif after != None and after in self.entities :
            l = ac.bbox[2]
        else :
            l = cell_bbox[2]

        # Cancel any word wrapping and make sure we're only dealing with one
        # config in this entity
        entity.line_length = -1
        entity.config_collapse()

        # Set the child config's row and column
        entity.config[0].row = row
        entity.config[0].col = col

        # Move the entity to it's new location
        h, v = (0,0)
        if move[0] :
            h = l-entity.config[0].bbox[0]
        if move[1] :
            v = self.config[0].bbox[3]-entity.config[0].bbox[3]+row_offset
        entity.translate(h, v, quiet=True, after=False)

        # If we are inserting after a zero-length child, we'll need to make sure
        # that the new child config's subpos is after the 'after' child's
        if after is not self and after is not None and \
                fc(ac.bbox[0], ac.bbox[2]) :
           entity.config[0].sub_pos = self.get_new_sub_pos_after(ac)
           entity.config[0].old_sub_pos = entity.config[0].sub_pos
        else :
            entity.config[0].sub_pos = \
                self.get_free_sub_pos(entity.config[0],
                                      search_dir_fwd=(after is None))

        #FIXME: Umm... why is this here?
        if entity is None :
            return

        # If we're setting alignment, let the entity know
        if align != None :
            entity.align = align

        # Finally add it to our list of entities
        self.entities.append(entity)

        # Pick our config into which the child config should go
        #FIXME: shouldn't this depend on the spread of after's cfgs?
        if after is None or after in self.entities :
            config_ind = 0
        else :
            config_ind = ac.index

        # Tell all of the entity's child configs which this is
        #FIXME: shouldn't this always be zero? Or will the translate have
        #FIXME: potentially resplit it?
        for c in entity.config :
            entity.config[c].parent_config_index = config_ind

        # Finally add the config to the list of child configs
        self.config[config_ind].child_configs.append(entity.config[0])

        # Ensure the entity config old matches new
        entity.config[0].old_sub_pos = entity.config[0].sub_pos

        # No idea what this is. Probably completely redundant
        global _testing_phr
        _testing_phr = self

        # If we were a non-zero width blank and are no longer, a non-trivial
        # size change has occurred. Do a full recalc
        if len(self) == 1 and self.get_p('blank_ratio') > 0.0 :
            self.recalc_bbox()

        if g.anal_retentive_mode and entity.am('phrase') :
            entity.consistency_check_sub_poses()

        # Tell the entity who we are
        entity.set_parent(self)

        if g.anal_retentive_mode :
            if entity.am('phrase') :
                entity.consistency_check_sub_poses()
            self.consistency_check_sub_poses()

        # Make sure any inherited properties of ours get transmitted down to the
        # entity and to its children, ad nauseum
        entity.children_check()

        # The only way a size change should be initiated, other than to a
        # set_font* call, is here (and remove), where the parent changes. As
        # scale works once for all the children, we do not want to call it
        # multiple times and therefore call it now rather than inside
        # the cascading inherited properties chain
        rel_scale = entity.get_scaled_font_size()/rel_scale
        if not fc(rel_scale, 1.0) :
            entity.scale(rel_scale)

        # Get the entity to call our child_bbox_change by pretending to have
        # been zero-width and expanding to its full width : "Of course I was
        # here all along, I was just hiding!"
        entity.from_nought(quiet=quiet)

        if g.anal_retentive_mode :
            if entity.am('phrase') :
                entity.consistency_check_sub_poses()
            self.consistency_check_sub_poses()

        # Tell any phrases above us that a child has (materially) changed - this
        # is saved for heavy duty checks that would be inefficient to call for
        # simple resizings
        self.child_change()

        # If the child is the kind of phrase that wants to pretend it's our
        # inside let it (i.e. high-level interior stuff like general child
        # adding is directed to it, it directs its high-level exterior stuff to
        # us)
        if entity.am_c('_in_phrase') :
            self.set_in(entity)
            entity.set_deletable(2)
            self.recalc_bbox()
            self.child_change()

        # If the entity wants to do anything about the fact it's just been added
        # to us, this is the moment.
        entity.added()

        # Tell our caller which row the entity got added to
        return row

    def add_config(self, config) :
        '''
        Sticks another config on the end (and adds a child_configs member if it
        doesn't have one.
        '''

        self.config[len(self.config)] = config
        config.child_configs = []

    line_length = -1
    wrapped = 0
    def word_wrap(self, quiet=False, instigator=True) :
        '''
        Splits the phrase into multiple configs
        '''

        # If no parent is forcing us to split and we don't need to (i.e. we
        # haven't overrun the line length limit) then do nothing.
        #FIXME: wait what's the point of instigator?
        if instigator and self.line_length <= 0 :
            return

        # Break (the relevant) config distance self.line_length from LHS
        pr = self.config_break(self.config[0].bbox[0]+self.line_length)

        # If we have two halves, it worked, if not, nothing happened.
        if pr is not None :
            # pr should be two configs - the halves of whatever config we split
            # (iirc)
            m, n = pr

            # note that this implementation can't handle configs spanning
            # multiple rows
            #FIXME: is this still true?

            # As we're word wrapping, we still need to move the second half down
            # a row
            cfgs = n.child_configs

            # Find the last row in the second half
            r = max(cfgs, key=lambda a:a.row).row

            # Add a new row if necessary
            if r+1 not in self.rows :
                self.add_row(r+1)

            # Move all of the second half configs down a row. The recalc below
            # will pull them to the start of the row, so we don't need to worry
            # about that.
            #FIXME: what if something's on that row?
            for cfg in cfgs :
                cfg.row += 1

            #FIXME: what's this all about?
            cfgs = self.sort_configs(config=m.index)

            #FIXME: is this necessary?
            self.wrapped += 1

            # Adjust our own structure accordingly
            self.recalc_bbox(quiet=quiet)

            # We may need to wrap again, run this to do so if necessary
            self.word_wrap(quiet=True)

            # Now that we've done all that wrapping, check our bbox, etc.
            # structure
            self.recalc_bbox(quiet=quiet)

            # Tell any parent that we've materially changed
            if not quiet :
                self.child_altered()

    def remove(self, entity, override_in=False) :
        '''
        Take an entity out of the children
        '''

        entity = entity.OUT()
        if self.IN() != self :
            self.IN().remove(entity)
            return

        # Shrink to zero width (forces everything else to align)
        entity.squash()

        # This should be triggered by squash (if needed?)
        if g.anal_retentive_mode :
            self.recalc_bbox()

        # Take the config and entities out of our lists
        c = entity.config.values()
        rel_scale = entity.get_scaled_font_size()
        self.entities.remove(entity)
        for cfg in c :
            self.config[cfg.parent_config_index].child_configs.remove(cfg)
            cfg.parent_config_index = 0

        # Make sure the entity knows it no longer has a parent
        entity.set_parent(None)

        # Try and remove row & col - presumably (?) this will do nothing if the
        # row or col is non-empty
        for row in self.rows :
            self.remove_row(row)
        for col in self.cols :
            self.remove_col(col)

        # Make sure the entity is in sync with its defaults for any properties
        # it had been inheriting from us (esp. font_size)
        entity.children_check()

        # Return the entity's scale to 1.
        rel_scale = entity.get_scaled_font_size()/rel_scale
        if not fc(rel_scale, 1.0) :
            entity.scale(rel_scale)

        # Make sure our structure is adjusted accordingly
        self.recalc_bbox()

        # Inform any parent of material change
        self.child_change()

    # This allows us to add a first object and move it to our position
    def adopt(self, entity, quiet=False, row=0, go_inside=True) :
        """Clears children and adds entity. Uses IN()."""

        # Make sure we have an Entity and, moreover, we have the Outside of it
        if entity is None :
            return
        entity = entity.OUT()

        # Make sure we have the Inside of ourselves
        if go_inside and self.IN() != self :
            self.IN().adopt(entity, quiet)
            return
        
        # Empty if necessary
        self.empty()

        # Append
        self.append(entity, quiet=quiet, row=row)
    
    def find_nearest(self, point, fall_through=True, enterable_parent=False,
                     row=None, col=None, attachable=False, avoid=None) :
        '''
        Find the nearest child to a point.
        '''

        dist = self.find_distance(point)

        # If we require an enterable parent but are neither enterable nor
        # allowed to look inside our children, we might as well give up now.
        if not fall_through and enterable_parent and not self.is_enterable() :
            return (-1, self)

        # If the point is to our left, or the point is inside us and we can't
        # fall through, return ourselves if we may
        if (not enterable_parent or self.is_enterable()) and \
           (not attachable or self.is_attachable()) and\
            (point[0] <= self.config[0].bbox[0] or \
             (not fall_through and
             (point[0] >= self.config[0].bbox[0] and \
              point[0] < self.config[0].bbox[2]) and \
             (point[1] >= self.config[0].bbox[1] and \
              point[1] <= self.config[0].bbox[3]))) and \
           self != avoid :
                return (dist, self)

        nrtup = (-1, self)

        # What is the location of this point when considered inside us?
        if self.get_local_space() :
            lpoint = (point[0]-self.config[0].bbox[0],
                      point[1]-self.config[0].bbox[3])
        else :
            lpoint = point

        # Check through child entities
        for ent in self.entities :
            # If we can't see this entity or it's in the wrong r/c continue
            if not ent.get_visible() or \
                (row is not None and ent.config[0].row != row) or \
                (col is not None and ent.config[0].col != col):
                    continue

            if fall_through :
                # Try looking inside this entity
                newtup = ent.find_nearest(lpoint, fall_through=True,
                                      enterable_parent=enterable_parent,
                                      attachable=attachable, avoid=avoid)
            elif ent != avoid :
                # Work out the distance to this entity
                newtup = (ent.find_distance(point), ent)

            # If this entity is closer than any checked so far, update the
            # nearest tuple to be its tuple (if we are allowed this ent)
            if (not attachable or newtup[1].is_attachable()) and \
                newtup[0] >= 0 and (nrtup[0] < 0 or newtup[0] < nrtup[0]) :
                    nrtup = newtup

        # If we did not find one but can use ourselves, do so
        if nrtup[0] == -1 :
            if (self.is_enterable() or not enterable_parent) and \
               (not attachable or self.is_attachable()) and \
               self != avoid :
                nrtup = (dist, self)
            else :
                nrtup = (-1, self)

        return nrtup
    
    def show_decoration(self) :
        '''
        Do we show visual decoration for this Phrase?
        '''

        return Entity.GlypherEntity.show_decoration(self) or\
               self.get_p('show_decoration')

    def set_active(self, active) :
        '''
        Set this entity as active (and tell any parent)
        '''
        self.active = active
        self.set_child_active(active, self)

    def clear_all_errors(self) :
        '''
        Recursively hide error messages
        '''

        Entity.GlypherEntity.clear_all_errors(self)

        for ent in self.entities :
            ent.clear_all_errors()

    def _real_draw(self, cr) :
        '''
        Do the hard work of drawing
        '''

        # Handle any error indication
        if self.error :
            cr.save()
            cr.set_source_rgba(1.0, 0.8, 0.4, 1.0)
            area=(self.config[0].bbox[0]-2, self.config[0].bbox[2]+2,
                  self.config[0].bbox[1]-2, self.config[0].bbox[3]+2)
            draw.trace_rounded(cr, area, 5)
            cr.fill()
            cr.restore()

        # Don't draw what can't be seen
        if not self.get_visible() or self.get_blank() :
            return

        #FIXME: get rid of this hack - it's probably not even being used
        if self.draw_offset != (0,0) :
            cr.translate(*self.draw_offset)

        # If we're supposed to decorate, do
        if self.show_decoration() :
            self.decorate(cr)

        # Give us a restore point before drawing
        cr.save()

        # Translate to compensate for local coordinate system if necessary
        if self.get_local_space() :
            cr.translate(self.config[0].bbox[0], self.config[0].bbox[3])

        # Draw each of our children
        for ent in self.entities :
            ent.draw(cr)

        # Restore the context
        cr.restore()

        #FIXME: see above
        if self.draw_offset != (0,0) :
            cr.translate(-self.draw_offset[0], -self.draw_offset[1])

        # Down cache flag
        self.redraw_required = False
        
    def draw(self, cr=None, alpha=False) :
        '''
        Draw this entity to a context
        '''

        # If we're caching, load from ImageSurface, otherwise draw straight on
        if self.is_caching or cr is None :
            # Create image surface if necessary
            if self.redraw_required or self.cairo_cache_image_surface is None \
                    or cr is None:
                if alpha :
                    mode = cairo.FORMAT_ARGB32
                else :
                    mode = cairo.FORMAT_RGB24

                #FIXME: padding should be settable, rather than constant!!
                self.cairo_cache_image_surface =  \
                        cairo.ImageSurface(cairo.FORMAT_RGB24,
                                           int(self.get_width())+20,
                                           int(self.get_height())+20)
                cc = cairo.Context(self.cairo_cache_image_surface)

                if not alpha :
                    cc.set_antialias(cairo.ANTIALIAS_NONE)
                    cc.set_source_rgb(1.0, 1.0, 1.0)
                    cc.rectangle(0, 0, int(self.get_width())+20,
                                 int(self.get_height())+20)
                    cc.fill()

                # Move to middle of padded surface
                cc.translate(10-self.config[0].bbox[0],
                             10-self.config[0].bbox[1])

                # Do the work
                self._real_draw(cc)

                #FIXME: redundant?
                self.redraw_required = False

            # Load from image surface
            ci = self.cairo_cache_image_surface
            if cr is not None :
                cr.save()
                cr.translate(self.config[0].bbox[0]-10, self.config[0].bbox[1]-10)
                cr.set_source_surface(ci, 0, 0)
                cr.paint()
                cr.restore()
        else :
            # Draw straight on
            self._real_draw(cr)
    
    #FIXME: Do we really want to set r,c to 0,0
    def config_collapse(self, quiet = False) :
        '''
        If we are composed of multiple configs, collapse them into one config.
        '''

        # Pick the config into which everything else will get stuffed
        cfg = self.config[0]

        if self.get_local_space() :
            ol, ob = (self.config[0].bbox[0], self.config[0].bbox[3])
        else :
            ol, ob = (0,0)

        # Collapse all of our children in the primary config first
        cl = list(cfg.child_configs)
        for c in cl :
            c.get_entity().config_collapse(quiet=True)

        # Move through our own configs in order
        while cfg.next is not None :
            pcfg = cfg
            cfg = cfg.next
            horiz_off = pcfg.bbox[2]-cfg.bbox[0]

            # Collapse all of the children in this entity and make sure
            # their row and column are 0, 0
            cl = list(cfg.child_configs)
            for c in cl :
                c.get_entity().config_collapse(quiet=True)
                c.row = 0; c.col = 0

            # Move to end of previous config and vertical middle
            # align at end SHOULD tidy up
            self.translate(horiz_off, pcfg.basebox[4]-cfg.basebox[4],
                    quiet=True, after=(horiz_off>0), config=cfg.index)

        # Go through and add children of other configs to primary config
        cfg = self.config[0]
        while cfg.next is not None :
            pcfg = cfg; cfg = cfg.next
            self.config[0].child_configs += cfg.child_configs
            for c in cfg.child_configs :
                c.parent_config_index = 0

        # Make sure that any parent isn't hanging on to redundant config's of
        # ours
        if self.included() :
            for c in self.config :
                if c == 0 :
                    continue
                prt_cfg = self.parent.config[self.config[c].parent_config_index]
                prt_cfg.child_configs.remove(self.config[c])

        # Remove remaining references to old configs
        self.config[0].next = None
        self.config = {0:self.config[0]}

        # Do a recalc to tidy everything into position
        self.recalc_bbox(quiet=quiet)
    
    # do_break indicates whether we want to be the top-level config, which
    # I think we generally do not
    def config_break(self, x_pos, quiet=False, do_break=False) :
        '''
        Split ourselves around x_pos
        '''

        # Can we even do this?
        bkble = self.get_breakable()
        broken = False

        # Transform to local coords if ness
        lx_pos = x_pos
        if self.get_local_space() :
            lx_pos -= self.config[0].bbox[0]

        # Go through the configs and see if they need broken
        for c in self.config :
            c = self.config[c]
            # Does the break-point fall in this config?
            if c.get_bbox()[0] < x_pos and c.get_bbox()[2] > x_pos :
                # Add a new config (done in init)
                ind = len(self.config)
                new_cfg = Entity.GlypherConfiguration(self, ind)

                if not do_break :
                    # If we don't want this config inside us, remove from list
                    del self.config[ind]

                # Tell this new config where it is
                new_cfg.row = c.row
                new_cfg.col = c.col

                if do_break :
                    # Tie into our stream
                    new_cfg.next = c.next
                    c.next = new_cfg

                # Add the child_configs member as this is a config for a Phrase
                new_cfg.child_configs = []

                # Find child configs of current config
                ccs = list(c.child_configs)

                # How many of them do we want to stay in the current (leftward)
                # config?
                keepers = 0
                for cc in ccs :
                    if cc.get_bbox()[2] < x_pos :
                        keepers += 1

                keeper_shortage = False

                # Run through the child configs to see if they need broken
                for cc in ccs :
                    # This one does
                    if cc.get_bbox()[0] < x_pos and cc.get_bbox()[2] > x_pos :
                        child_config_halves = \
                                cc.get_entity().config_break(lx_pos, quiet=True,
                                                             do_break=True)

                        # If we can split this config, put the second half
                        # into the new config
                        if child_config_halves is not None :
                            broken = True

                            # If we break ourselves, tell the second half of the
                            # broken child config its in our new config,
                            # otherwise it thinks its in the current config
                            if do_break :
                                child_config_halves[1].parent_config_index = ind
                            else :
                                child_config_halves[1].parent_config_index = \
                                        c.index
                                c.child_configs.append(child_config_halves[1])
                            # In any case, new_cfg should have it
                            new_cfg.child_configs.append(child_config_halves[1])
                        # As long as there are some child configs in our current
                        # config then, if this didn't split, we can move the
                        # whole thing to the new config
                        elif keepers > 0 :
                            if do_break :
                                cc.parent_config_index = ind
                                c.child_configs.remove(cc)
                            new_cfg.child_configs.append(cc)
                        # If there aren't, then leave it where it is, otherwise
                        # we'll end up emptying the current config
                        else :
                            keeper_shortage = True
                    # This falls entirely on the RHS of x_pos - put it in the
                    # new config
                    elif cc.get_bbox()[0] >= x_pos :
                        if do_break :
                            cc.parent_config_index = ind
                            c.child_configs.remove(cc)
                        new_cfg.child_configs.append(cc)

                # If we made a successful split, tidy everything up and return
                # both halves
                if not keeper_shortage and len(new_cfg.child_configs) > 0 and \
                        (bkble or broken) :
                    new_cfg.reset()
                    self.recalc_basebox()
                    self.recalc_bbox(quiet=quiet, do_reset=quiet)
                    return (c, new_cfg)
                # Otherwise, if the new config has been added, remove it again,
                # as we didn't actually split anything
                elif do_break :
                    l = list(new_cfg.child_configs)
                    for cc in l :
                        cc.parent_config_index = c.index
                        new_cfg.child_configs.remove(cc)
                        c.child_configs.append(cc)
                    c.next = None
                    del self.config[ind]

        return None
    
    def decorate(self, cr) :
        '''
        Show frilly bits for interactive mode
        '''

        # Draw a line around our first config
        if len(self.entities) == 0 :
            cr.save()
            cr.move_to(self.config[0].bbox[0] - 4, self.config[0].bbox[1] - 10)
            cr.line_to(self.config[0].bbox[2] + 4, self.config[0].bbox[1] - 10)
            cr.line_to(self.config[0].bbox[2]    , self.config[0].bbox[1]     )
            cr.line_to(self.config[0].bbox[0]    , self.config[0].bbox[1]     )
            cr.close_path()
            cr.set_source_rgba(0.5, 1.0, 0.5, 0.8)
            cr.fill()
            cr.restore()

        # Show our alignment boxes
        if g.show_rectangles :
            cr.save()
            cr.set_line_width(2.0)
            cr.set_source_rgba(1.0, 0.5, 0.5, 0.4)
            cr.rectangle(self.config[0].bbox[0]-2, self.config[0].bbox[1]-2,
                         self.config[0].bbox[2]-self.config[0].bbox[0]+4,
                         self.config[0].bbox[3]-self.config[0].bbox[1]+4)
            cr.stroke()
            cr.set_source_rgba(1.0, 0.5, 1.0, 0.4)
            for j in (3,4,5) :
                cr.move_to(self.config[0].basebox[0]-5,
                           self.config[0].basebox[j])
                cr.line_to(self.config[0].basebox[2]+5,
                           self.config[0].basebox[j])
                for i in (0,2) :
                    cr.move_to(self.config[0].basebox[i],
                               self.config[0].basebox[j]-2)
                    cr.line_to(self.config[0].basebox[i],
                               self.config[0].basebox[j]+2)
                cr.stroke()
            cr.restore()
            if self.line_length > 0 :
                cr.save()
                cr.set_source_rgb(0.4, 1.0, 0.4)
                cr.move_to(self.config[0].bbox[0] + self.line_length,
                           self.config[0].basebox[3])
                cr.rel_line_to(0, self.get_basebox_height())
                cr.stroke()
                cr.restore()

        self.draw_topbaseline(cr)

        # Highlighting
        if self.get_attached() and g.additional_highlighting :
            cr.save()
            cr.move_to(self.config[0].bbox[0]-2, self.config[0].bbox[3]+2)
            draw.draw_blush(cr, self.config[0].bbox[2]-self.config[0].bbox[0]+4,
                            (0.5,0,0) )
            cr.restore()
    
    _num_recalcs = 0

    #FIXME: The paragraph of comments below is probably out of date - go through
    # We don't recalc the baseboxes until the end of this as recalc_bbox
    # shouldn't use them and they have  a significant overhead. However, if 
    # anything in here does need a row basebox, this should be considered.
    # Actually, inserting one at start of recalc_bbox to be safe. However,
    # recalc_row_basebox depends on entity baseboxes and, only if it has a row
    # full of invisible entities, row_bboxes so if the second dependency were
    # removed, this recalc_basebox call could be moved to child_bbox_changed,
    # provided that the one commented out in realign_children is readded
    def recalc_bbox(self, quiet=False, enact=True, realign=True,
                    sub_pos_search_dir=None, compare_rows=False,
                    in_feed_chain=False, do_reset=True) :
        # Don't allow this to run until we're fully initialized - this is a
        # slightly hacky check, but it's the key reason we don't
        if self.get_p('blank_ratio') is None :
            return

        # If we have to realign as well as recalc, check the baseboxes
        if realign :
            self.recalc_baseboxes()

        # If we're actually supposed to do the translation on this call, define
        # ourself as the top level. If not, we're in a recursive call -
        # increment the nesting counter
        if enact :
            self._num_recalcs = 0
        else :
            self._num_recalcs += 1
            # This has taken too many recursive calls, give up.
            if self._num_recalcs > g.max_recalcs :
                debug_print([e.format_me() for e in self.entities])
                raise RuntimeError('Exceeded maximum bbox recalculations for '+\
                                   str(self.format_me())+\
                                   '; probably some unending alignment loop')

        # Has a change occurred during this routine?
        change = False

        # Pick anchor coords
        l, b = (self.config[0].bbox[0], self.config[0].bbox[3])

        for c in self.config :
            config = self.config[c]
            bbox = list(config.bbox)

            # If this config is empty, give it a bbox of appropriate size and
            # shape - blank_ratio tells us what width this should be
            if self.get_visible_entities() == 0 :
                pad = self.padding
                bl_width = self.get_p('blank_ratio')*self.get_scaled_font_size()
                bbox = [bbox[0]+pad[0],
                        bbox[3]-0.6*self.get_scaled_font_size()-pad[3],
                        bbox[0]+bl_width+pad[0],
                        bbox[3]-pad[3]]

                # Adjust for local coords if ness
                lbbox = list(bbox)
                if self.get_local_space() :
                    lbbox[0] -= l; lbbox[1] -= b
                    lbbox[2] -= l; lbbox[3] -= b

                self.row_bboxes[0] = list(lbbox)
                self.col_bboxes[0] = list(lbbox)
            else :
                # Pick out the visible child configs of this config
                vis_cfgs = filter(lambda c : c.get_entity().get_visible(),
                                  config.child_configs)

                # Start with the first child config as a guess for the config
                # bbox
                bbox = list(vis_cfgs[0].bbox)

                row_ticks = []
                col_ticks = []
                recalc_rows = []
                for cfg in vis_cfgs :
                    ent = cfg.get_entity()
                    
                    # Extend our bbox around this entity
                    h_ig = ent.get_horizontal_ignore()
                    v_ig = ent.get_vertical_ignore()
                    if not h_ig and cfg.bbox[0] < bbox[0] :
                        bbox[0] = cfg.bbox[0]
                    if not v_ig and cfg.bbox[1] < bbox[1] :
                        bbox[1] = cfg.bbox[1]
                    if not h_ig and cfg.bbox[2] > bbox[2] :
                        bbox[2] = cfg.bbox[2]
                    if not v_ig and cfg.bbox[3] > bbox[3] :
                        bbox[3] = cfg.bbox[3]

                    # Factor this into our row & col bboxes
                    r = cfg.row
                    if r not in row_ticks :
                        self.row_bboxes[r] = list(cfg.bbox)
                        row_ticks.append(r)
                    else :
                      if not ent.get_horizontal_ignore() \
                            and cfg.bbox[0] < self.row_bboxes[r][0] :
                          self.row_bboxes[r][0] = cfg.bbox[0]
                      if not ent.get_vertical_ignore() \
                            and cfg.bbox[1] < self.row_bboxes[r][1] :
                          self.row_bboxes[r][1] = cfg.bbox[1]
                      if not ent.get_horizontal_ignore() \
                            and cfg.bbox[2] > self.row_bboxes[r][2] :
                          self.row_bboxes[r][2] = cfg.bbox[2]
                      if not ent.get_vertical_ignore() \
                            and cfg.bbox[3] > self.row_bboxes[r][3] :
                          self.row_bboxes[r][3] = cfg.bbox[3]
                    c = cfg.col

                    if c not in col_ticks :
                        self.col_bboxes[c] = list(cfg.bbox)
                        col_ticks.append(c)
                    else :
                      if not ent.get_horizontal_ignore() \
                            and cfg.bbox[0] < self.col_bboxes[c][0] :
                          self.col_bboxes[c][0] = cfg.bbox[0]
                      if not ent.get_vertical_ignore() \
                            and cfg.bbox[1] < self.col_bboxes[c][1] :
                          self.col_bboxes[c][1] = cfg.bbox[1]
                      if not ent.get_horizontal_ignore() \
                            and cfg.bbox[2] > self.col_bboxes[c][2] :
                          self.col_bboxes[c][2] = cfg.bbox[2]
                      if not ent.get_vertical_ignore() \
                            and cfg.bbox[3] > self.col_bboxes[c][3] :
                          self.col_bboxes[c][3] = cfg.bbox[3]
                
                # If necessary account for local coords
                if self.get_local_space() :
                    bbox[0] += l; bbox[1] += b
                    bbox[2] += l; bbox[3] += b

            d = (-1, -1, 1, 1)
            for i in range(0, 4) :
                bbox[i] += d[i]*self.padding[i]
            config.set_bbox(bbox)

        # Do any necessary realignment
        if realign :
            change = self._realign_children()

        # FIXME:This needs fixed
        #if self.keep_min_row_height :
        #    if bbox[3] - bbox[1] < self.get_scaled_line_size() :
        #        bbox[1] = bbox[3] - self.get_scaled_line_size()
        #    for r in self.rows :
        #        if self.row_bboxes[r][3] - self.row_bboxes[r][1] < \
        #        self.get_scaled_line_size() :
        #            self.row_bboxes[r][1] = self.row_bboxes[r][3] -\
        #        self.get_scaled_line_size()
        #config.update_basebox()

        # Do any mandatory entity recalcs. If it changes anything, we'll need to
        # run another recalc
        entity_recalc_change = False
        if realign :
         for ent in self.entities :
            if ent.get_always_recalc() :
                entity_recalc_change = ent.recalc_bbox(quiet=True) or\
                    entity_recalc_change

        #FIXME:isn't this redundant?
        if realign and entity_recalc_change :
            change = self._realign_children() or change
        change = change or entity_recalc_change

        # If our reference config isn't at our anchor and we're in local coords,
        # then we should move everything to make sure it is
        h, v = (self.config[0].bbox[0]-l, self.config[0].bbox[3]-b)
        if self.get_local_space() and (h,v) != (0,0) :
            ents = [c.get_entity() for c in self.sort_configs(rev=(h>0))]
            for ent in ents :
                ent.translate(-h, -v, quiet=True)
            change = True

        # Alignment shouldn't be dependent on the parent's bbox

        # If anything changed, recalc
        if change :
            self.recalc_bbox(quiet=True, enact=False)

        # If we're responsable for actually doing something, do so
        if realign and enact : 
            # Adjust to compensate for padding and visibility
            for c in self.config :
                config = self.config[c]
                config.width = config.bbox[2] - config.bbox[0]
                if not self.get_visible() :
                    config.bbox[2] = config.bbox[0]
                if not fc(config.bbox[0], config.old_bbox[0])\
                        and self.included() :
                    p = self.get_parent()
                    if sub_pos_search_dir is None :
                        sub_pos_search_dir = (config.bbox[0]<config.old_bbox[0])
                    config.sub_pos = p.get_free_sub_pos(config,
                                        search_dir_fwd=sub_pos_search_dir)

            # Recalc alignment box
            self.recalc_basebox()

            # Does this need to happen if bbox == old_bbox (and baseboxes same,
            # I guess)?
            if do_reset :
                self.feed_up(quiet=quiet, in_feed_chain=in_feed_chain)

        return change

    def recalc_basebox(self) :
        '''
        Recalculate our alignment box
        '''

        # Do standard stuff
        Entity.GlypherEntity.recalc_basebox(self)

        # Calc alignment box for each of the configs
        for c in self.config :
            cfg = self.config[c]
            m = cfg.get_basebox()

            # If we should be aligning to the middle of the config, do so
            if not self.get_p('align_as_entity') and \
                    0 in self.row_bboxes and \
                    self.row_bboxes[0] != None and \
                    self.get_visible_entities() != 0 and \
                    0 in cfg.baseboxes : 
                l = cfg.baseboxes[0]
                o = self.config[0].bbox[3] if self.get_local_space() else 0
                m = (m[0], m[1], m[2], m[3], l[4]+o, m[5])

            cfg.basebox = m

    def recalc_baseboxes(self, recalc=True) :
        '''
        Recalculate all of the per row alignment boxes
        '''

        for r in self.rows :
            self.recalc_row_basebox(r, recalc=recalc)

    def get_visible_entities(self, r = None) :
        '''
        Get the visible entities (possibly in a particular row)
        '''

        if r is None :
            ents = self.entities
        else :
            #FIXME: you wot?
            ents = list(set([c.get_entity() for c in self.get_row(r)]))

        return len(filter(lambda e: e.get_visible(), ents))

    def recalc_row_basebox(self, r, recalc = True) :
        '''
        Recalculate the row alignment of a given row
        '''

        # Take care of case where this row is empty of visible elements
        if self.get_visible_entities(r) == 0 :
            if len(self.rows) == 1 :
                if self.get_local_space() :
                    rbb = (self.padding[0], -self.get_height()+self.padding[1],
                           self.get_width()-self.padding[2], -self.padding[3])
                else :
                    bbox = self.config[0].bbox
                    pad = self.padding
                    rbb = (bbox[0]+pad[0], bbox[1]+pad[1], bbox[2]-pad[2],
                           bbox[3]-pad[3])
            else :
                rbb = self.row_bboxes[r]
            basebox = (rbb[0], 0.5*(rbb[0]+rbb[2]), rbb[2],
                       rbb[1], 0.5*(rbb[1]+rbb[3]), rbb[3])
        else :
            #FIXME: am I missing something or is it possible for c0 to be
            #FIXME: invisible and does it matter?
            c0 = self.get_row(r)[0]

            # Do the start with first and expand around trick
            basebox = list(c0.get_basebox())
            basebox[1] = 0; basebox[4] = 0
            n = 0
            for c in self.get_row(r) :
                if not c.get_entity().get_visible() :
                    continue
                eb = c.get_basebox()
                if eb[0] < basebox[0] : basebox[0] = eb[0]
                basebox[1] += eb[1]
                if eb[2] > basebox[2] : basebox[2] = eb[2]
                if eb[3] < basebox[3] : basebox[3] = eb[3]
                basebox[4] += eb[4]
                if eb[5] > basebox[5] : basebox[5] = eb[5]
                n += 1

            # This ensures that the middle and centre alignments are the average
            # of the configs
            basebox[1] /= n
            basebox[4] /= n

        # The basebox of the primary config is the de facto basebox of the
        # entity (IIRC)
        self.config[0].baseboxes[r] = tuple(basebox)
        
    def _realign_children(self) :
        '''
        Straighten out the kids.
        '''

        # Have we changed anything?
        change = False

        # Baseboxes of the primary config are always used for general alignment
        baseboxes = self.config[0].get_baseboxes()

        cfgs = self.sort_configs()
        for cfg in cfgs :
            ent = cfg.get_entity()
            basebox = baseboxes[cfg.row]

            # What way should this be aligned?
            al = ent.get_align()
            if al[1] == 'b' :
                mv = basebox[5]-cfg.get_basebox()[5]
                # These tolerances avoid us shuffling back indefinitely to
                # converge below a visually distinguishable error (actually we
                # need to converge a good bit lower than that, but 1e-5 seems a
                # good guess)
                if abs(mv) > sm_tol :
                    ent.translate(0, mv, quiet=True, config=cfg.index)
                    change = True
            elif al[1] == 'm' :
                mv = basebox[4]-cfg.get_basebox()[4]
                # Larger to avoid honing in slowing us down
                if abs(mv) > bg_tol :
                    ent.translate(0, mv, quiet=True, config=cfg.index)
                    change = True
            elif al[1] == 't' :
                mv = basebox[3]-cfg.get_basebox()[3]
                if abs(mv) > sm_tol :
                    ent.translate(0, mv, quiet=True, config=cfg.index)
                    change = True

        # Now realign the rows
        change = change or self._row_realign()

        return change
    
    # assume we want offset from previous col/row towards 0,0
    def _row_realign(self) :
        '''
        ...then line them up. Actually, this does columns too
        '''

        change = False

        row_bboxes = self.row_bboxes
        col_bboxes = self.col_bboxes

        refbbox = row_bboxes[0]

        row_baseboxes = self.config[0].get_baseboxes()

        refbasebox = row_baseboxes[0]

        # Order rows moving away from primary row
        self.rows.sort(key=abs)

        for r in self.rows :
            # Don't touch the primary row
            if r == 0 :
                continue

            # Direction
            d = 1 if r < 0 else -1;

            # Offset specifies additional gap from previous row - this is why
            # order is important
            offset = self.row_offsets[r]
            if offset is not None :
                gap = row_baseboxes[r][4] - row_baseboxes[r+d][4] - offset
            else :
                gap = row_bboxes[r][2+d] - row_bboxes[r+d][2-d]

            # Translate if needs be
            if abs(gap) > sm_tol :
              change = True
              self.row_translate(r, 0, -gap, quiet=True)

            # How to align rel to row?
            ra = self.row_aligns
            if   ra[r] == 'l' : mv = refbasebox[0]-row_baseboxes[r][0]
            elif ra[r] == 'c' : mv = refbasebox[1]-row_baseboxes[r][1]
            elif ra[r] == 'r' : mv = refbasebox[2]-row_baseboxes[r][2]

            if abs(mv) > sm_tol :
              change = True
              self.row_translate(r, mv, 0, quiet=True)

        for c in self.cols :
            if c == 0 :
                continue

            d = 1 if c < 0 else -1

            offset = self.col_offsets[c]
            if offset is not None :
                gap = col_bboxes[c][0] - col_bboxes[0][0] - offset
            else :
                gap = col_bboxes[c][1+d] - col_bboxes[c+d][1-d]

            if abs(gap) > sm_tol :
              change = True
              self.col_translate(c, -gap, 0, quiet=True)

        return change
    
    def col_translate(self, c, h, v, quiet=False) :
        '''
        Move a whole column
        '''

        for cfg in self.get_col(c) :
           cfg.get_entity().translate(h, v, quiet=True, config=cfg.index)

        # This is important as the row may not have any (visible) elements
        # so an automatic calculation of the row_bboxes will not respond
        # to any translation. Hence, to allow realigns of this row to occur, the
        # translation must be made in the row_bboxes also, so that, if
        # we have no visible elements, we can still resolve the alignment
        # FIXME: put it in - we currently assume every col has a non-zero elt
        self.col_bboxes[c][0] += h
        self.col_bboxes[c][1] += v
        self.col_bboxes[c][2] += h
        self.col_bboxes[c][3] += v

        if not quiet : # Note that this doesn't reset the config box if quiet
            self.feed_up()
 
    def row_translate(self, r, h, v, quiet=False) :
        '''
        Move a whole row
        '''

        for c in self.get_row(r) :
           c.get_entity().translate(h, v, quiet=True, config=c.index)

        # This is important as the row may not have any (visible) elements
        # so an automatic calculation of the row_bboxes will not respond
        # to any translation. Hence, to allow realigns of this row to occur, the
        # translation must be made in the row_bboxes also, so that, if
        # we have no visible elements, we can still resolve the alignment
        # Should col_bboxes recalc be added here?
        self.row_bboxes[r][0] += h
        self.row_bboxes[r][1] += v
        self.row_bboxes[r][2] += h
        self.row_bboxes[r][3] += v

        if not quiet : # Note that this doesn't reset the config box if quiet
            self.feed_up()
 
    def find_at_point(self, point) :
        '''
        Get the entity inside here closest to this point
        '''

        if self.IN() != self :
            return self.IN().find_at_point(point)

        if not self.contains(point) :
            return None

        for ent in self.get_entities() :
            closest = ent.find_at_point(point)
            if closest != None :
                return closest

        return self

    def find_in_dir(self, pos, left=True, exclude=None, row=None, col=None,
                    vertical_ignore=True, drop_down=True, self_attach=None,
                    must_move=True) :
        '''
        Find the first suitable entity moving in direction left/right from pos
        '''

        if self.IN() != self :
            return self.IN().find_in_dir(pos, left, exclude, row, col,
                                         vertical_ignore, drop_down,
                                         self_attach, must_move)

        closest = None
        d = 1 if left else -1

        # If we can't enter this, or look below, there's no point
        if not self.is_enterable() and not drop_down :
            return None

        for sym in self.entities :
            # Don't enter what you can't see
            if not sym.get_visible() :
                continue

            # We've been told to exclude this. So do.
            if sym == exclude or sym.IN() == exclude :
                continue

            # We definitely can't attach or go into this
            if not (sym.is_attachable() or drop_down) or \
                    (not self.is_enterable() and not sym.am('phrase')) :
                continue

            # Wrong row
            if row is not None and sym.config[0].row != row:
                continue

            # Wrong col
            if col is not None and sym.config[0].col != col:
                continue

            got_from_sub_phrase = False
            if drop_down and sym.am('phrase') :
                test_closest = sym.find_in_dir(\
                    pos=pos, left=left, exclude=exclude,\
                    row=None, col=None, vertical_ignore=vertical_ignore,
                    drop_down=True, self_attach=True, must_move=must_move)

                # If we've found a suitable entity in this child and it beats
                # out our current closest
                if test_closest is not None and \
                        (closest == None or \
                         d*(closest.config[0].bbox[2] -\
                            test_closest.config[0].bbox[2]) < 0 or \
                         (fc(test_closest.config[0].bbox[2],
                             closest.config[0].bbox[2]) and\
                          d*(closest.config[0].bbox[0] -\
                             test_closest.config[0].bbox[0]) < 0)) :
                     closest = test_closest
                     got_from_sub_phrase = True

            # If we haven't just picked up a closest and this sym fits better
            # than what we have (and we can attach to it where it is), then use
            # it as the new closest
            if not got_from_sub_phrase and \
                    (vertical_ignore or \
                     (sym.config[0].bbox[3] > pos[1]-self.get_height() or \
                      sym.config[0].bbox[1] < pos[1])) and \
                    (d*(sym.config[0].bbox[2] - pos[0]) < 0 or \
                     (fc(sym.config[0].bbox[2],pos[0]) and \
                      row!=None and col!=None) or \
                    (fc(sym.config[0].bbox[2],pos[0]) and \
                     d*(sym.config[0].bbox[0] - pos[0]) < 0)) :
                right_dist = d*(closest.config[0].bbox[2]-sym.config[0].bbox[2])
                left_dist = d*(closest.config[0].bbox[0]-sym.config[0].bbox[0])
                if closest == None or right_dist < 0 or\
                        (fc(sym.config[0].bbox[2],closest.config[0].bbox[2]) \
                         and left_dist < 0) :
                    if sym.is_attachable() and self.is_enterable() :
                        closest = sym

        # Default for self attaching
        if self_attach is None :
            self_attach = True

        # Check whether we are eligible ourselves if nothing else has been found
        if closest == None and self_attach and self.is_attachable() and \
                exclude != self and self.is_enterable() and \
                (d*(self.config[0].bbox[0] - pos[0]) < 0 or \
                 (not must_move and fc(self.config[0].bbox[0],pos[0]))):
            return self
        return closest

# Must be a better way!!
#FIXME: is this now redundant?
class GlypherExpression(GlypherPhrase) :
    '''
    Type of phrase that's got tailored defaults more appropriate to a
    full mathematical expression
    '''

    def __init__(self, parent, area=(0,0,0,0), line_size_coeff=1.0,
                 font_size_coeff=1.0, align=('l','m'), auto_fices=True) :
        GlypherPhrase.__init__(self, parent, area, line_size_coeff,
                               font_size_coeff, align, auto_fices)
        self.mes.append("expression")
    
class GlypherMainPhrase(GlypherPhrase) :
    '''
    Phrase that can act as a standalone parent for use in a widget
    '''

    # This member allows contact with the outside world; if a gobject signal is
    # to be fired, the _receiving_ GObject (e.g. GlyphEntry) should do so
    signal_recipient = None

    def set_is_caching(self, is_caching) :
        '''
        Whether or not this gets rid of object representation of children in
        favour of XML that it can parse, on change, to an ImageSurface
        '''
        self.is_caching = is_caching

    def set_by_bbox(self, by_bbox) :
        '''Align by bbox (or basebox)'''
        self.set_p('by_bbox', by_bbox)

    def get_by_bbox(self) :
        '''Align by bbox (or basebox)'''
        return self.get_p('by_bbox')

    def set_anchor(self, anchor) :
        '''Anchor alignment'''
        self.set_p('anchor', anchor)

    def get_anchor(self) :
        '''Anchor alignment'''
        return self.get_p('anchor')

    def set_anchor_point(self, anchor_point) :
        '''Fixed reference point'''
        self.set_p('anchor_point', anchor_point)

    def get_anchor_point(self) :
        '''Fixed reference point'''
        return self.get_p('anchor_point')

    def set_area(self, area) :
        '''
        Reset to a given area, which evaluates the anchor point based on the
        anchor (alignment).
        '''

        area = (0, 0, area[0], area[1])
        anchor = self.get_anchor()
        a1 = area[0] if anchor[0] == 'l' else \
             area[2] if anchor[0] == 'r' else \
             0.5*(area[0]+area[2])
        a2 = area[1] if anchor[1] == 't' else \
             area[3] if anchor[1] == 'b' else \
             0.5*(area[1]+area[3])

        self.set_anchor_point((a1, a2))

        # Do any necessary translation
        self.move()

    def __init__(self, signal_recipient, line_size, font_size, rgb_colour,
                 is_decorated=False, anchor=('l','c'), by_first_row=True,
                by_bbox=False) :

        # This just saves a bit of recalculation (I think?)
        trial_area = (0, 0, 0, line_size)
        GlypherPhrase.__init__(self, None, trial_area, align=('l','m'))

        self.add_properties({'anchor': ('l','c'), 'anchor_point': (0,0),
                             'deletable' : False, 'by_bbox' : False })

        self.set_p('is_decorated', is_decorated)
        self.set_by_bbox(by_bbox)

        # This member allows us to send rudimentary signals to a widget
        if signal_recipient :
            self.signal_recipient = lambda s, d=None : signal_recipient(self, s, d)

        self.set_anchor(anchor)

        self.mes.append('main_phrase')

        self.by_first_row = by_first_row

        self.set_area((0,line_size))
        self.set_line_size(line_size)
        self.set_font_size(font_size)
        self.set_rgb_colour(rgb_colour)

    def to_clipboard(self, auto_paste=False, who=None, contents=False) :
        '''
        Tell a widget that we have a copy request for who (default None : us?)
        '''

        if self.signal_recipient :
            self.signal_recipient("copy", (auto_paste, who, contents))
            return True
        return False

    def show_decoration(self) :
        '''
        Is this decorated?
        '''

        return self.get_p('is_decorated')

    background_colour = None
    cairo_cache_image_surface = None
    def _real_draw(self, cr) :
        '''
        If this isn't transparent, give it a bg colour. Then _real_draw as
        normal
        '''

        if self.background_colour is not None :
            cr.save()
            cr.set_source_rgba(*self.background_colour)
            for c in self.config :
                cfg = self.config[c]
                cr.rectangle(*self.config[c].bbox)
                cr.fill()
            cr.restore()

        if self.in_selected() :
            cr.save()
            cr.set_source_rgba(*glypher.selected_colour)
            for c in self.config :
                cfg = self.config[c]
                cr.rectangle(*self.config[c].bbox)
                cr.fill()
            cr.restore()

        GlypherPhrase._real_draw(self, cr)

    cached_xml = None

    def decorate(self, cr) :
        '''
        Do decoration for MainPhrase
        '''

        self.draw_topbaseline(cr)
        if g.show_rectangles :
            # Big surrounding line
            cr.save()
            cr.set_line_width(4.0)
            cr.set_source_rgba(0.3, 0.3, 0.3, 0.6)
            cr.rectangle(self.config[0].bbox[0]-2, self.config[0].bbox[1]-2,
                         self.config[0].bbox[2]-self.config[0].bbox[0]+4,
                         self.config[0].bbox[3]-self.config[0].bbox[1]+4)
            cr.stroke()
            cr.restore()

            # Cross at the anchor point
            cr.save()
            cr.set_line_width(2.0)
            cr.set_source_rgba(0.3, 0.3, 0.3, 0.8)
            a1, a2 = self.get_anchor_point()
            cr.move_to(a1 - 10, a2 - 10)
            cr.line_to(a1 + 10, a2 + 10)
            cr.move_to(a1 + 10, a2 - 10)
            cr.line_to(a1 - 10, a2 + 10)
            cr.stroke()
            cr.restore()

    def scale(self, s) :
        '''
        Execute a scaling, but make sure we also do the subsequent MainPhrase
        translation to align to anchor
        '''
        GlypherPhrase.scale(self, s)
        self.move()

    def child_change(self) :
        '''
        If any material changes occur, tell our signal recipient, do any
        necessary word wrapping, simplifying and translation to anchor.
        '''
        self.config[0].check()
        self.make_simplifications()
        self.word_wrap()
        self.move()
        if self.signal_recipient :
            self.signal_recipient("recalc")

    def child_altered(self, child=None) :
        '''
        If anything happens to a child, we still need to additionally do the
        child_change routine for MainPhrase, to make sure all alignment is tidy.
        '''
        GlypherPhrase.child_altered(self, child)
        self.child_change()

    # Note that this (currently) aligns to the first row's basebox
    def move(self, a1=None, a2=None) :
        '''
        Realign (by simple translation) to the anchor point. This may involve
        aligning using the basebox or bbox, according to settings. Default
        alignment is to current anchor point
        '''

        # Choose appropriate anchor point and
        if a1 is None :
            a1 = self.get_anchor_point()[0]
        if a2 is None :
            a2 = self.get_anchor_point()[1]

        anchor = self.get_anchor()
        if self.get_by_bbox() :
            bbox = self.config[0].bbox
            bb = (bbox[0], (bbox[0]+bbox[2])*0.5, bbox[2],
                  bbox[1], (bbox[1]+bbox[3])*0.5, bbox[3])
        else :
            if self.by_first_row :
                bb = self.config[0].baseboxes[0]
            else :
                bb = self.config[0].basebox

        # Which point do we need to translate to anchor?
        b1 = bb[
             0 if anchor[0]=='l' else\
             2 if anchor[0]=='r' else\
             1]
        b2 = bb[
             3 if anchor[1]=='t' else\
             5 if anchor[1]=='b' else\
             4]

        # Move (if ness)
        if not fc(a1, b1) :
            self.translate(a1-b1, 0, quiet=True)
        if not fc(a2, b2) :
            self.translate(0, a2-b2, quiet=True)

        # Update anchor
        self.set_anchor_point((a1,a2))

    def get_main_phrase(self) :
        '''
        Override upward calling routine to return ourselves
        '''

        return self
