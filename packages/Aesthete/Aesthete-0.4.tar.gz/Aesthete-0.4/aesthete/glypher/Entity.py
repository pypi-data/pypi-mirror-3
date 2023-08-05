import traceback
import xml.etree.ElementTree as ET
import copy
import sympy
import math
from ..utils import *
import glypher as g
import gutils
from sympy.core.sympify import SympifyError

ac = gutils.array_close
fc = gutils.float_close

def _ipu_font_size_combined_coeff(s) :
    '''Inherited property updater for fscc'''
    if s.get_parent() is None :
        return 1.

    par_fscc = s.get_parent().get_ip('font_size_combined_coeff')
    par_fsc = s.get_parent().get_ip('font_size_coeff')
    return par_fscc * par_fsc

class GlypherConfiguration :
    '''
    Each entity is split over one (normally) or more Configs. These allow
    entities to be built of multiple bboxes, and not necessarily be rectangular.
    Particularly useful for word-wrapping, where an entity is split into two
    configs and its parent keeps one config on one row and moves the other to
    the next.
    '''

    # Link to our parent
    entity = None

    # Who is the subsequent config (for our assoc. entity)?
    next = None

    # Track changes to our bounding box
    bbox = None
    old_bbox = None
    invisible_bbox = None

    sub_pos = None
    old_sub_pos = None

    row = None
    old_row = None

    col = None
    old_col = None

    # AXIOM OF HOPE:
    # If that basebox hasn't changed,
    # neither will the alignment of
    # children (assuming that any
    # change in the children will
    # generate a realignment anyhow)
    basebox = None
    old_basebox = None

    # The associated entity stores alignment info about the rows in the
    # baseboxes of the first config, elsewhere they're redundant
    #FIXME: shouldn't these be in the same object as the row bboxes?
    baseboxes = None
    old_baseboxes = None

    index = 0
    # Which of our parent's configs do we reside in?
    parent_config_index = 0

    width = 0

    def __init__(self, obj, index) :
        # We can initialize either from an Entity (which will subsequently need
        # to have a recalc) or by copying another Config
        if isinstance(obj, GlypherEntity) :
            self.entity = obj
            self.bbox = [0,0,0,0]
            self.old_bbox = [0,0,0,0]
            self.invisible_bbox = None
            self.sub_pos = 0
            self.old_sub_pos = 0
            self.basebox = (0,0,0,0,0,0)
            self.old_basebox = (0,0,0,0,0,0)
            self.old_baseboxes = {}
            self.row = 0
            self.old_row = 0
            self.col = 0
            self.old_col = 0
            if obj.am('phrase') :
                self.baseboxes = {}
        elif isinstance(obj, GlypherConfiguration) :
            self.copy_new(obj)
            self.old_bbox = list(obj.old_bbox)
            self.old_basebox = obj.old_basebox
            self.old_baseboxes = {}
            self.set_baseboxes(self.old_baseboxes, obj.old_baseboxes)
            self.old_sub_pos = obj.old_sub_pos
            self.old_row = obj.old_row
            self.old_col = obj.old_col
        else :
            raise(RuntimeError("!!! wrong constructor type for GlypherConfiguration"))

        # Add ourselves to our entity as config 'index'
        self.entity.config[index] = self

        self.index = index
    
    def get_entity(self) :
        '''Return associated entity'''
        return self.entity

    def to_string(self) :
        '''
        If we are associated with a phrase, we may have child configs - join
        them to make a string, otherwise return the string rep of our associated
        entity.
        '''
        if self.get_entity().am('phrase') :
            return "".join([a.to_string() for a in self.child_configs])
        return self.get_entity().to_string()

    _full_changes = False
    def get_changes(self) :
        '''
        Produce a string representation of the geometrical changes since the
        last time this was reset.
        '''

        chgs = ""
        if not ac(self.bbox, self.old_bbox) :
            chgs += str(self.old_bbox)+" -> "+str(self.bbox)+"\n"
        if self.sub_pos != self.old_sub_pos :
            chgs += ":" + str(self.old_sub_pos)+" -> "+str(self.sub_pos)+"\n"
        if self.row     != self.old_row :
            chgs += "---"+str(self.old_row)+" -> "+str(self.row)+"\n"
        if self.col     != self.old_col :
            chgs += "|||"+str(self.old_col) + " -> "+str(self.col)+"\n"
        if not ac(self.basebox, self.old_basebox) :
            chgs += " basebox: "+str(self.old_basebox)+\
                    " -> "+str(self.basebox)+"\n"

        short = (chgs != "" and not self._full_changes)
        n = 0

        if self.baseboxes :
         for r in self.baseboxes :
            if r not in self.old_baseboxes :
                if short :
                    n += 1
                else :
                    chgs += " no old basebox for row "+str(r)+"\n"
            elif self.baseboxes[r] != self.old_baseboxes[r] :
                if short :
                    n += 1
                else :
                    chgs +=" basebox["+str(r)+"]: "+str(self.old_baseboxes[r])+\
                            " -> " + str(self.baseboxes[r]) + "\n"
        if n > 0 :
            chgs += " & "+str(n)+" of "+str(len(self.baseboxes))+" baseboxes\n"
        chgs = chgs[:-1]

        return chgs

    def scale_baseboxes(self, s) :
        '''
        Rescale the baseboxes by a factor of s with respect to the bottom left
        corner of the bbox (in local space, origin for rows)
        '''

        # Scale the master alignment basebox
        self.basebox = self._scale_basebox(self.basebox,
                                           self.bbox[0], self.bbox[3], s)
        
        # If we're in local space, scale internal baseboxes wrt the origin
        if self.entity.get_local_space() :
            l, b = (0, 0)
        else :
            l, b = (self.bbox[0], self.bbox[3])

        # Scale internal (row) baseboxes
        if self.baseboxes :
         for r in self.baseboxes :
            self.baseboxes[r] = self._scale_basebox(self.baseboxes[r],
                                                    l, b, s)
    
    def _scale_basebox(self, B, l, b, s) :
        '''
        The actually mechanics of scaling a given bbox
        '''

        return (l+(B[0]-l)*s, l+(B[1]-l)*s, l+(B[2]-l)*s,
                b+(B[3]-b)*s, b+(B[4]-b)*s, b+(B[5]-b)*s)
    
    def move_baseboxes(self, h, v) :
        '''
        Translate the baseboxes
        '''

        # Master alignment is simple translate
        self.basebox = self._move_basebox(self.basebox, h, v)

        # If we're not in local space, we'll need to move internal ones too
        if self.baseboxes and not self.entity.get_local_space() :
         for r in self.baseboxes :
            self.baseboxes[r] = self._move_basebox(self.baseboxes[r], h, v)
    
    def _move_basebox(self, b, h, v) :
        '''
        The actually mechanics of moving a given bbox
        '''

        return (b[0]+h, b[1]+h, b[2]+h, b[3]+v, b[4]+v, b[5]+v)

    def get_row(self) :
        '''What row are we?'''
        return self.row
    
    def get_col(self) :
        '''What col are we?'''
        return self.col

    def get_bbox(self) :
        '''Return the bbox'''
        return tuple(self.bbox)
    
    def get_sub_pos(self) :
        '''Return the config's subpos in parent'''
        return self.sub_pos
    
    def get_basebox(self) :
        '''Return the master alignment bbox'''
        return self.basebox
    
    def get_baseboxes(self) :
        '''Return the internal alignment baseboxes'''
        return self.baseboxes
    
    def set_sub_pos(self, sub_pos) :
        '''Set the config's subpos in parent'''
        self.sub_pos = sub_pos
    
    def set_bbox(self, bbox) :
        '''Copy the bbox values to our bbox'''
        for i in range(0,4) :
            self.bbox[i] = bbox[i]
        self.width = self.bbox[2] - self.bbox[0]
    
    def update_basebox(self, only_recalc_self=False) :
        '''Get the entity to recalc our basebox.'''

        self.entity.recalc_basebox(config=self)

        if self.entity.am('phrase') and not self.baseboxes :
            self.baseboxes = {}

    def check(self) :
        '''Checks for basic geometric changes.'''

        if not ac(self.bbox, self.old_bbox) or \
           self.row != self.old_row or \
           self.col != self.old_col or \
           not ac(self.basebox, self.old_basebox) :
               return True
        return False
    
    def copy_new(self, config) :
        '''
        Copy the members of config into our structure (deep)
        '''

        self.entity = config.entity
        self.bbox = list(config.bbox)
        self.basebox = config.basebox # this should always be a tup
        if config.baseboxes :
            self.baseboxes = {}
            self.set_baseboxes(self.baseboxes, config.baseboxes)
        self.sub_pos = config.sub_pos
        self.row = config.row
        self.col = config.col
    
    def reset(self, only_recalc_self = False) :
        '''
        Reharmonize the old and current members, e.g. bbox->old_bbox. Note that
        once this is called, the config will show no changes have occurred until
        the next change.
        '''

        self.old_bbox = list(self.bbox)
        self.old_sub_pos = self.sub_pos
        self.old_row = self.row
        self.old_col = self.col
        self.old_basebox = self.basebox
        if self.baseboxes :
            self.set_baseboxes(self.old_baseboxes, self.baseboxes)
    
    def set_baseboxes(self, baseboxes1, baseboxes2) :
        '''
        Copy a series of (tuple) baseboxes from bb2 to bb1
        '''

        for bsb in baseboxes2 :
            if bsb not in baseboxes1 or baseboxes1[bsb] != baseboxes2[bsb] :
                baseboxes1[bsb] = tuple(baseboxes2[bsb])

class GlypherEntity :
    '''
    Basic class for all Glypher components that can be combined into phrases,
    etc.
    '''

    @staticmethod
    def xml_copy(ent) :
        '''Create a new entity from old via XML'''

        # Extract relevant XML
        ent_xml = ET.ElementTree(ent.get_xml(\
                            targets={}, top=False, full=False))
        # Build a new entity
        new_ent = parse_phrasegroup(ent, ent_xml, top=False)

        return new_ent

    parent = None

    # For compat. with Phrase - None unless overridden
    entities = None

    # Used for the Caret if it wants to obtain a suggestion from this entity
    recommending = None

    # Set of names indicating what kind of entity I am
    #FIXME: couldn't this just be replaced with isinstance ?
    mes = None

    # Gap around the entity
    padding = None

    # Property dictionary for the entity
    properties = None

    # Default properties - used if not set in 'properties'
    default_properties = None

    # Which inherited properties does this entity override by default?
    default_inherited_properties_overrides = None

    # (+Inherited) Properties which shouldn't appear in the XML
    hidden_properties = None

    # Edit mode can be used to override attachability/enterability(?) settings
    # temporarily, without actually changing them
    edit_mode = False

    # Indicates cache invalidated
    redraw_required = False

    # Dictionary of component configs
    config = None

    # Is this entity selected?
    selected = False

    error = False
    _error_text = None
    def set_error_note(self, text = None) :
        '''Indicate an error has occurred.'''

        if text is None :
            self.error = False
        elif text != self._error_text :
            self.error = True
            self._error_text = text
            debug_print(text)
            debug_print_stack()
            debug_print(self.format_me())

    def clear_all_errors(self) :
        '''Hide any error message.'''

        self.error = False

    def get_selected(self) :
        '''Whether this entity is selected (!= in a selection)'''
        return self.selected

    def set_selected(self, selected) :
        '''Set whether this entity is selected (!= in a selection)'''
        self.selected = selected
    def in_selected(self) :
        '''Whether this entity is in a selection'''
        if self.included() :
            return self.get_selected() or self.get_parent().in_selected()
        return self.get_selected()

    def set_p(self, name, val) :    
        '''Set a property'''
        if self.get_p(name) == val :
            return
        self.properties_changes[name] = self.properties_changes.get(name, 0) + 1
        self.properties[name] = val

    def get_p(self, name) :
        '''Get a property'''

        if name in self.properties :
            return self.properties[name]
        elif name in self.default_properties :
            return self.default_properties[name]

        return None

    def set_bodmas_level(self, bodmas_level) :
        '''Set BODMAS level'''
        self.set_p('bodmas_level', bodmas_level)

    def get_bodmas_level(self) :
        '''Get BODMAS level'''
        return self.get_p('bodmas_level')

    #FIXME: remove cousin on entity deletion
    def add_cousin(self, cousin) :
        '''
        A cousin is an entity that needs informed of a size change, but isn't
        in the parent chain, e.g. a mirror entity
        '''
        self.cousins.append(cousin)

    #FIXME: Should this be moved to Phrase?
    def get_local_space(self) :
        '''Is this entity evaluating internally in local space?'''
        return self.get_p('local_space')

    def get_name(self) :
        '''Get string name for this entity'''
        return self.get_p('name')

    def set_name(self, name) :
        '''Set string name for this entity'''
        return self.set_p('name', name)

    def get_align(self) :
        '''Which direction should we align to parent?'''
        return self.get_p('align')

    def set_align(self, align) :
        '''Which direction should we align to parent?'''
        return self.set_p('align', align)

    def get_visible(self) :
        '''Are we visible?'''
        return self.get_p('visible')

    def set_visible(self, visible) :
        '''Are we visible?'''
        return self.set_p('visible', visible)

    def get_blank(self) :
        '''Do we skip draw? Unlike 'visible', this preserves space'''
        return self.get_p('blank')

    def set_blank(self, blank) :
        '''Do we skip draw? Unlike 'visible', this preserves space'''
        return self.set_p('blank', blank)

    def get_breakable(self) :
        '''Can this entity be broken into smaller configs?'''
        return self.get_p('breakable')

    def set_breakable(self, breakable) :
        '''Can this entity be broken into smaller configs?'''
        ret = self.set_p('breakable', breakable)
        return ret

    def get_attachable(self) :
        '''Can this entity be attached to by the Caret?'''
        return self.get_p('attachable')

    def set_attachable(self, attachable, children_too=False) :
        '''Can this entity be attached to by the Caret?'''

        if self.am('phrase') and children_too :
            for ent in self.get_entities() :
                ent.set_attachable(attachable, children_too=True)

        return self.set_p('attachable', attachable)

    _IN = None
    _OUT = None
    def get_IN(self) :
        '''
        Should high-level inward facing actions be given to another entity
        representing our interior?
        '''
        return self._IN

    def set_IN(self, IN) :
        '''
        Should high-level inward facing actions be given to another entity
        representing our interior?
        '''
        self._IN = IN

    def get_OUT(self) :
        '''
        Should high-level outward facing actions be given to another entity
        representing our exterior?
        '''
        return self._OUT

    def set_OUT(self, OUT) :
        '''
        Should high-level outward facing actions be given to another entity
        representing our exterior?
        '''
        self._OUT = OUT

    def get_have_alternatives(self) :
        '''
        Do we have alternatives to switch through?
        '''
        return self.get_p('have_alternatives')

    def set_have_alternatives(self, have_alternatives) :
        '''
        Do we have alternatives to switch through?
        '''
        return self.set_p('have_alternatives', have_alternatives)

    def get_always_recalc(self) :
        '''
        Should we always recalc when our parent does?
        '''
        return self.get_p('always_recalc')

    def set_always_recalc(self, always_recalc) :
        '''
        Should we always recalc when our parent does?
        '''
        return self.set_p('always_recalc', always_recalc)

    def get_runted(self) :
        '''
        Do we have a parent that does not own us? That is, we inherit
        properties, etc. but are not in the entities list
        '''
        return self.runted

    def set_runted(self, runted) :
        '''
        Do we have a parent that does not own us? That is, we inherit
        properties, etc. but are not in the entities list
        '''
        self.runted = runted

    attached = False
    def get_attached(self) :
        '''
        Are we the entity currently attached to the Caret
        '''
        return self.attached

    def set_attached(self, attached) :
        '''
        Are we the entity currently attached to the Caret
        '''
        self.attached = attached

    def get_vertical_ignore(self) :
        '''
        Should we ignore this entity when calculating vertical bbox/basebox
        extents in the parent?
        '''
        return self.get_p('vertical_ignore')

    def set_vertical_ignore(self, vertical_ignore) :
        '''
        Should we ignore this entity when calculating vertical bbox/basebox
        extents in the parent?
        '''
        return self.set_p('vertical_ignore', vertical_ignore)
    
    def get_horizontal_ignore(self) :
        '''
        Should we ignore this entity when calculating horizontal bbox/basebox
        extents in the parent?
        '''
        return self.get_p('horizontal_ignore')

    def set_horizontal_ignore(self, horizontal_ignore) :
        '''
        Should we ignore this entity when calculating horizontal bbox/basebox
        extents in the parent?
        '''
        return self.set_p('horizontal_ignore', horizontal_ignore)

    def get_enterable(self) :
        '''
        Can the Caret attach inside us (possibly to a child)?
        '''
        return self.IN().get_p('enterable')

    def set_enterable(self, enterable, children_too=False) :
        '''
        Can the Caret attach inside us (possibly to a child)?
        '''

        if self.am('phrase') and children_too :
            for ent in self.get_entities() :
                ent.set_enterable(enterable, children_too=True)

        return self.IN().set_p('enterable', enterable)

    target_name = None
    def get_xml(self, name=None, top=True, targets=None, full=False) :
        '''
        Return an XML representation of this entity
        '''

        if name is None :
            name = self.get_name()

        root = ET.Element(name)

        # The final me in mes is the 'type'
        root.set('type', self.mes[-1])

        # If we have been asked to give a target name, do so.
        if self.target_name is not None :
            root.set('target', self.target_name)

        self.bind_xml(root, top=top)

        return root
    
    def _xml_add_property(self, root, val) :
        '''
        Turn a property value into XML attributes of root
        '''

        if isinstance(val, tuple) :
            root.set('type', type(val).__name__)
            for t in val :
                te = ET.SubElement(root, 'ti')
                te.set('value', str(t))
                te.set('type', type(t).__name__)
        elif isinstance(val, GlypherEntity) :
            root.set('type', 'entity')
            root.set('value', val.get_name())
        else :
            root.set('value', str(val))
            root.set('type', type(val).__name__)

    def bind_xml(self, root, top=True) :
        '''
        Attach XML properties of this entity to root
        '''

        inherited_props_overrides = ET.Element('inherited_properties_overrides')
        props = ET.Element('properties')

        # We need extra information if we're at the top (top is more like
        # saying, provide all information and don't assume we've heard of this
        # type of entity)
        if top :
            mes = ET.Element('mes')
            inherited_props = ET.Element('inherited_properties')
            chs = ET.Element('characteristics')

            # Make sure all our types are provided
            for p in self.mes :
               me = ET.SubElement(mes, 'me')
               me.set('name', p)

            # Add in any inherited_properties (at top, so none to be inherited
            # above)
            for p in self.inherited_properties :
               if self.inherited_properties[p] is None :
                   continue
               inherited_prop = ET.SubElement(inherited_props, 'ip')
               inherited_prop.set('name', p)
               self._xml_add_property(inherited_prop,
                                      self.inherited_properties[p])

            # Add in any characteristics - flags indicating particular
            # properties
            for p in self.characteristics :
               ch = ET.SubElement(chs, 'ch')
               ch.set('name', p)

            # Only append these if necessary
            if len(mes) > 0 :
                root.append(mes)
            if len(chs) > 0 :
                root.append(chs)
            if len(inherited_props) > 0 :
                root.append(inherited_props)

        # Deal with any overrides of inherited properties
        for p in self.inherited_properties_overrides :
            # Certain situations where we still don't want to include XML for
            # this
            if self.inherited_properties_overrides[p] is None or \
                    p in self.hidden_properties or \
                    (p in self.default_inherited_properties_overrides and \
                     self.inherited_properties_overrides[p] ==\
                      self.default_inherited_properties_overrides[p]) :
                continue

            inherited_prop = ET.SubElement(inherited_props_overrides, 'ipo')
            inherited_prop.set('name', p)
            self._xml_add_property(inherited_prop,
                                   self.inherited_properties_overrides[p])

        if len(inherited_props_overrides) > 0 :
            root.append(inherited_props_overrides)

        # Deal with our own properties
        for p in self.properties :
            if self.properties[p] is None or \
                    p in self.hidden_properties or \
                    (p in self.default_properties and \
                        self.properties[p] == self.default_properties[p]) :
                continue
            prop = ET.SubElement(props, 'property')
            prop.set('name', p)
            self._xml_add_property(prop, self.properties[p])

        if len(props) > 0 :
            root.append(props)

        # This is a common attribute that is tidier to include as a tag
        # attribute rather than a def. IP override
        if self.get_size_scaling() != \
                self.default_inherited_properties_overrides['font_size_coeff'] :
            root.set('scaling', str(self.get_size_scaling()))

        # The padding is most efficiently included thusly
        padd_string = ",".join(map(str,self.padding))
        if padd_string != "0.0,0.0,0.0,0.0" :
            root.set('padding', padd_string)
        
    # Use with caution
    #FIXME: don't use at all.
    draw_offset = (0,0)

    def IN(self) :
        '''
        Define the real object with which you should be dealing. Useful for
        compound phrases where only one component is publically usable. Interior
        component.
        '''
        if self.get_IN() is None :
            return self
        else :
            return self.get_IN().IN()

    def OUT(self) :
        '''
        Define the real object with which you should be dealing. Useful for
        compound phrases where only one component is publically usable. Exterior
        component.
        '''
        if self.get_OUT() is None :
            return self
        else :
            return self.get_OUT().OUT()

    def get_up(self) :
        '''
        Return our parent (or exterior's parent)
        '''
        return self.OUT().get_parent()

    def recalc_basebox(self) :
        '''
        Recalculate our alignment basebox for each cfg
        '''

        for c in self.config :
            cfg = self.config[c]
            b = cfg.get_bbox()
            cfg.basebox = (b[0], (b[0]+b[2])*0.5, b[2],
                           b[1], (b[1]+b[3])*0.5, b[3])

    def set_padding_all(self, quant) :
        '''
        Set the padding the whole way around to a single value
        '''

        for i in range(0,4):
            self.set_padding(i, quant, quiet=True)

        self.recalc_bbox()

    def set_padding(self, ind, quant, quiet = False) :
        '''
        Set padding of an individual side
        '''

        if quant == self.padding[ind] :
            return

        self.padding[ind] = quant

        if not quiet :
            self.recalc_bbox()

    def is_edit_mode(self) :
        '''
        Whether we temporarily override attachability (and enterability?)
        restrictions.
        '''
        ret = self.edit_mode or \
               (self.included() and self.parent.is_edit_mode())
        #debug_print((self.format_me(), ret))
    
        return ret

    def is_attachable(self) :
        '''
        Can we attach to this entity?
        '''

        val = (self.get_attachable() or self.is_edit_mode()) and \
              self.get_visible() and not self.get_blank()
        return val

    def get_pow_options(self) :
        '''
        What ways can we raise this to a power? e.g. how do we execute this^3 in
        a glypher expression
        '''

        return ('python',)
    
    def get_caret_position(self, inside=False, pos=None) :
        '''
        Supposing the caret is attached to us, where should it display? Use
        global coordinates
        '''

        if inside and self != self.IN() :
            return self.IN().get_caret_position(inside=True, pos=pos)
        
        if pos is None :
            if inside :
                l = self.config[0].get_basebox()[0] + self.padding[0]
            else :
                l = self.config[0].get_basebox()[2] - self.padding[2]
            pos = [l, self.config[0].get_basebox()[5] - self.padding[3]]

        if self.parent :
            local_off = self.parent.get_local_offset()
            pos = list(pos)
            pos[0] += local_off[0]
            pos[1] += local_off[1]

        return pos

    def blank(self) :
        '''
        Make this entity transparent.
        '''
        self.set_blank(True)

    def unblank(self) :
        '''
        Unmake this entity transparent.
        '''
        self.set_blank(False)

    def set_name(self, name) :
        '''
        Give this entity a name (appears in XML and some debug output).
        '''
        self.set_p('name', name)
    
    def get_recommending(self) :
        '''
        Who do we recommend the caret attaches to if it asks?
        '''
        return self.recommending
    
    _suspend_recommending = False
    def suspend_recommending(self) :
        '''
        Ignore future requests for us to store new recommendations for caret
        location
        '''
        self._suspend_recommending = True
    def resume_recommending(self) :
        '''
        Resume acceptance of requests for us to store new recommendations for
        caret location
        '''
        self._suspend_recommending = False

    def set_recommending(self, recommending) :
        '''
        Set our recommendation for caret location in case it wants a suggestion
        at some point.
        '''

        if self._suspend_recommending :
            return

        self.recommending = recommending

        if self.included() :
            self.get_parent().set_recommending(recommending)
    
    def copy(self) :
        '''
        .. deprecated:: 0.2
        Create a deep copy of this entity.
        '''

        # Remove links that may cause include parent phrases
        p = self.parent
        self.set_parent(None)
        self.set_OUT(None)
        self.cairo_cache_context = None
        self.cairo_cache_image_surface = None

        #cop = copy.deepcopy(self)
        cop = GlypherEntity.xml_copy(self)

        if cop.am('phrase') :
            cop.config_collapse()

        self.set_parent(p)

        return cop

    def get_main_phrase_property(self, prop) :
        '''
        Convenience routine to get a property from the main phrase rather than
        the present entity.
        '''

        mp = self.get_main_phrase()
        if mp is not None :
            return mp.get_p(prop)
        return None

    def added(self) :
        '''
        Called once we've been added to a Phrase. This is a good place to put
        process heavy stuff that we don't want to check every recalc, like
        material changes (e.g. make_simplifications)
        '''

        if self.included() :
            self.make_simplifications()

    def make_simplifications(self) :
        '''
        Override to perform simplification checks, where a certain combination
        of children, juxtaposition of child with parent, etc. may lead us to
        want to materially change something. As an example, GlypherAdd checks
        for 1 + (a+b) [nested sum] and simplifies it to 1 + a + b. Be
        particularly careful of introducing infinite recursion.
        '''
        pass
    
    # This is for finding PhraseGroups only so ignores entities (and phrases)
    def inside_a(self, what, ignore=()) :
        '''
        Check upwards to see if we're in a 'what'. 'ignore' tells us what type
        of *PhraseGroup* we're going to ignore. If we meet a PG that *isn't* one
        of these, or we reach the top parent, we give up and declare defeat.
        '''
        if self.included() :
            return self.get_parent().inside_a(what, ignore)
        return None

    x_offset = 0
    y_offset = 0
    def get_anchor(self, bbox = None) :
        '''
        Provides a nominal anchor for the entity (actually used less than you'd
        think).
        '''

        if bbox == None :
            bbox = self.config[0].get_bbox()

        pos = [0,0]
        al = self.get_align()
        if al[0] == 'l' :
            pos[0] = bbox[0]
        elif al[0] == 'c' :
            pos[0] = (bbox[0]+bbox[2])/2
        else :
            pos[0] = bbox[2]

        if al[1] == 'b' :
            pos[1] = bbox[3]
        elif al[1] == 'm' :
            pos[1] = (bbox[1]+bbox[3])/2
        else :
            pos[1] = bbox[1]

        return pos
    
    def get_local_offset(self) :
        '''
        Gets the 2-vec to add to internal coordinates to give global
        coordinates. If neither we nor any of our parents are in local space,
        this is just a zero vector.
        '''

        local_off = [0,0]

        # Account for our own local space
        if self.get_local_space() :
            local_off = [self.config[0].bbox[0], self.config[0].bbox[3]]

        # Request upwards
        if self.parent :
            local_up = self.parent.get_local_offset()
            local_off[0] += local_up[0]
            local_off[1] += local_up[1]

        return tuple(local_off)

    def draw_topbaseline(self, cr, shade=(1.0,1.0,1.0), force=False) :
        '''
        Draws our alignment guidelines onto cr (under bbox_mode)
        '''

        if not g.bbox_mode and not force :
            return

        cr.save()
        cr.move_to(self.config[0].bbox[0], self.get_baseline())
        cr.line_to(self.config[0].bbox[2], self.get_baseline())
        cr.move_to(self.config[0].bbox[0], self.get_topline())
        cr.line_to(self.config[0].bbox[2], self.get_topline())

        col = [len(self.get_ancestors())*0.2]*3
        col = [col[i]*shade[i] for i in range(0,2)]+[1.0]
        cr.set_source_rgba(*col)
        cr.stroke()

        abox = self.config[0].get_bbox()
        abox[2] -= abox[0]
        abox[3] -= abox[1]

        cr.rectangle(*abox)
        col = [len(self.get_ancestors())*0.1]*3
        col = [col[i]*shade[i] for i in range(0,2)]+[1.0]
        cr.set_source_rgba(*col)
        cr.stroke()

        col = [len(self.get_ancestors())*0.1]*3
        col = [col[i]*shade[i] for i in range(0,2)]+[1.0]
        col[2] = 0
        cr.set_source_rgba(*col)

        anchor = self.get_anchor()
        cr.move_to(anchor[0], anchor[1]+3)
        cr.arc(anchor[0], anchor[1], 3, 0, math.pi*2)
        cr.fill()
        cr.restore()

    def get_topline(self) :
        '''
        Get a topline alignment for this entity (bbox top unless overridden)
        '''

        bbox = self.config[0].get_bbox()
        return bbox[1]

    def get_baseline(self) :
        '''
        Get a baseline alignment for this entity (bbox bottom unless overridden)
        '''

        bbox = self.config[0].get_bbox()
        return bbox[3]

    def realign(self, quiet=False) :
        '''
        Override to do some realignment
        '''
        return

    def set_in(self, innermost) :
        '''
        Set an innermost inside (you're more likely to want this than 
        :py:method::`set_IN`).
        '''

        innermost.set_OUT(self.IN())
        self.IN().set_IN(innermost)

    def get_deletable(self) :
        '''
        Can this entity be deleted?
        '''
        return self.get_p('deletable')

    def set_deletable(self, deletable) :
        '''
        Can this entity be deleted?
        '''
        return self.set_p('deletable', deletable)

    def get_parent(self) :
        '''
        Who is our parent?
        '''
        return self.parent

    ref_width = 0
    def get_ref_width(self) :
        '''
        What width are we? Not so useful for phrases, as they calc themselves,
        but this should be updated before standard entity recalcs.
        '''
        return self.ref_width

    def set_ref_width(self, ref_width) :
        '''
        What width are we? Not so useful for phrases, as they calc themselves,
        but this should be updated before standard entity recalcs.
        '''
        self.ref_width = ref_width

    ref_height = 0
    def get_ref_height(self) :
        '''
        What height are we? Not so useful for phrases, as they calc themselves,
        but this should be updated before standard entity recalcs.
        '''
        return self.ref_height
    def set_ref_height(self, ref_height) :
        '''
        What height are we? Not so useful for phrases, as they calc themselves,
        but this should be updated before standard entity recalcs.
        '''
        self.ref_height = ref_height

    def add_properties(self, supp_dict, supp_ipo_dict=None) :
        '''
        Add new properties to the element (and possibly inherited properties)
        setting the given values as defaults (i.e. won't be included in XML if
        unchanged). If you include an already existing property, it updates the
        default value to whatever you've given.
        '''

        self.default_properties.update(supp_dict)

        if supp_ipo_dict is not None :
            self.default_inherited_properties_overrides.update(supp_ipo_dict)
    
    def is_wordlike(self) :
        '''Should this be treated, in simplifications, etc. as a Word?'''
        return self.get_p('wordlike')

    def to_latex(self) :
        '''
        Provide a LaTeX representation. Note that this doesn't get called by
        Word, so won't be used often without being overridden.
        '''

        me_str = self.to_string()
        if me_str in g.interpretations :
            me_str = g.interpretations[me_str]["latex"]

        return str(me_str)

    def __init__(self, parent = None) :
        self.properties_changes = {}
        self.default_properties = \
                  {'align' : ('l','m'),
                   'always_recalc' : False,
                   'auto_contract_premultiplication' : True,
                   'attachable' : True,
                   'visible' : True,
                   'blank' : False,
                   'horizontal_ignore' : False,
                   'override_keys' : False,
                   'local_space' : False,
                   'wordlike' : False,
                   'breakable' : False,
                   'deletable' : 1,
                   'have_alternatives' : False,
                   'force_no_bracket' : False}
        self.properties = {}

        # Font size coeff is complicated...
        self.hidden_properties = [ 'font_size_coeff' ]

        # Make up an erstwhile unique name. This may be overridden in inheritor
        # inits
        self.set_name('entity_'+str(id(self)))
        
        # Whatever else I am, I'm an entity
        self.mes = []
        self.mes.append('entity')

        # Entities that need kept in the loop about size changes
        self.cousins = []

        self.inherited_properties = {
            'bold' : False,
            'font_size' : 45.0,
            'rgb_colour' : (0.0,0.0,0.0),
            'font_name' : None,
            'font_size_combined_coeff' : 1.0,
            'font_size_coeff' : 1.0 }

        self.inherited_properties_overrides = {}
        self.default_inherited_properties_overrides = {
            'font_size_coeff' : 1.0 }
        self.inherited_properties_updaters = {
            'font_size_combined_coeff': _ipu_font_size_combined_coeff }

        # If the weight changes, we may change size
        #NB: we don't recalc for a font size change as that should be all
        # handled by scaling functions. In other words, don't change font_size*
        # directly!!
        self.inherited_properties_recalc_on_change = [
            'bold' ]

        self.inherited_properties_change = {}

        self.config = {}

        self.set_OUT(None)
        self.set_IN(None)

        self.characteristics = []

        # If the caret wants to know who we think it should attach to, tell it
        # to attach to us
        self.set_recommending(self)

        self.padding = [0., 0., 0., 0.]

        # This adds a cfg to us
        GlypherConfiguration(self, 0)

        self.recalc_basebox()

        self.config[0].reset()

        # Use for properties but don't communicate
        # until we're told to
        self.set_parent(parent, runted=True)

    def who_am_i(self) :
        '''String expression of the mes'''
        return "; ".join(self.mes)
    
    def config_reset(self) :
        '''
        Tell all the configs to reset their old_bboxes (etc) to the current
        versions (as we claim we've done any necessary consequent rejigging).
        '''

        for c in self.config :
            self.config[c].reset()

    def config_check(self) :
        '''
        Check whether any of the configs have changed since last reset.
        '''

        chk = False
        for c in self.config :
            chk = chk or self.config[c].check()

        return chk
        
    def feed_up(self, quiet=False, in_feed_chain=False) :
        '''
        Inform parents that we have changed and to adjust accordingly, then we
        reset our configs and raise the redraw required flag
        '''

        do_feed_up = not quiet and \
                (self.config_check() or g.anal_retentive_mode2) and \
                self.included()

        if do_feed_up :
            self.get_parent().child_bbox_change(self)
            self.config_reset()
            if not in_feed_chain : self.child_altered(self)

            # Make sure the cousins know of any size changes
            for cousin in self.cousins :
                cousin.recalc_bbox()
        else :
            self.config_reset()

        self.set_redraw_required()

    def set_redraw_required(self) :
        '''
        Invalidate any caching and require a redraw (feeds up)
        '''

        self.redraw_required = True
        if self.included() :
            self.parent.set_redraw_required()
    
    def child_altered(self, child=None) :
        '''
        A child ('child') has changed. Tell parent (override to do more)
        '''

        if self.included() :
            self.get_parent().child_altered(self)

    def show(self, quiet=False) :
        '''
        Makes this entity visible again; as invisibility involves zero width,
        this also makes the necessary bbox/basebox alterations and feeds up.
        '''

        if self.get_visible() :
            return

        self.set_visible(True)

        for c in self.config :
            cfg = self.config[c]
            cfg.bbox[2] = cfg.bbox[0] + cfg.width

        self.recalc_basebox()
        self.feed_up(quiet=quiet)

    def hide(self, quiet=False) :
        '''
        Makes this entity invisible, which involves zeroing the width, recalcing
        the basebox and feeding up
        '''

        if not self.get_visible() :
            return

        self.set_visible(False)

        for c in self.config :
            self.config[c].bbox[2] = self.config[c].bbox[0]

        self.recalc_basebox()
        self.feed_up(quiet=quiet)

    def format_loc(self) :
        '''Return a string expression of the location.'''
        return str(self.config[0].get_bbox())+':'+\
               str(self.config[0].get_sub_pos())+'|'+\
               str(self.config[0].get_row())+','+str(self.config[0].get_col())

    def format_old_loc(self) :
        '''Return a string expression of the previous location.'''
        return str(self.config[0].old_bbox)+':'+\
               str(self.config[0].old_sub_pos)+'|('+\
               str(self.config[0].old_row)+','+str(self.config[0].get_col())+')'

    def recalc_bbox(self, quiet=False) :
        '''Recalculate the bounding box (from ref_width & ref_height)'''

        config = self.config[0]
        pad = self.padding

        config.bbox[2] = config.bbox[0] + self.get_ref_width() +(pad[0]+pad[2])
        config.bbox[1] = config.bbox[3] - self.get_ref_height() -(pad[1]+pad[3])
        config.width = config.bbox[2]-config.bbox[0]

        # If we moved the left side, we may need to get a new sub pos
        if not fc(config.bbox[0],config.old_bbox[0]) and self.included() :
            config.set_sub_pos(\
                self.get_parent().get_free_sub_pos(config,
                search_dir_fwd=(config.bbox[0]<config.old_bbox[0])))

        # Account for (in)visibility
        if not self.get_visible() :
            config.bbox[2] = config.bbox[0]

        # Update alignment
        self.recalc_basebox()

        change = config.check()

        self.feed_up(quiet=quiet)

        return change

    def format_me(self) :
        '''Return a string expression of self.'''

        name = unicode('')
        if self.get_name() is not None :
            name = unicode(self.get_name()+':')

        return u' \u25aa '.join([name+self.to_string(), self.who_am_i(),
               '-'.join([o.mes[len(o.mes)-1] for o in self.get_ancestors()]),
               str(self.get_scaled_font_size()),
               self.format_loc()])

    def get_main_phrase(self) :
        '''Return overarching main phrase.'''

        anc = self.get_ancestors()
        top = anc[len(anc)-1]

        if top.am('main_phrase') :
            return top
        
        return None

    def get_ancestors(self) :
        '''Return a list of ancestors, beginning with self.'''

        anc = [self]
        if self.get_parent() :
            anc += self.get_parent().get_ancestors()

        return anc

    def set_parent(self, parent, runted=False) :
        '''
        Set parent as our parent; normally this shouldn't be called directly
        but by append or by constructor. Can be useful for causing an entity to
        take on properties of a parent without actually adding it (runted w.
        parent)
        '''

        if parent == self :
            raise StandardError("Can't make entity its own parent")
        elif parent == None :
            self.parent = None
            self.set_runted(True)
        else :
            self.parent = parent
            self.set_runted(runted)

        # Tell this entity and all its parents that one of their children has
        # changed (unless runted is True)
        self.children_check()
    
    def to_string(self, mode="string") :
        '''
        Return a *UNICODE* representation of this entity. Empty string unless
        overridden.
        '''
        return unicode('')
    
    def width(self) :
        '''Width of bbox of first config.'''
        return self.config[0].bbox[2] - self.config[0].bbox[0]

    def height(self) :
        '''Height of bbox of first config.'''
        return self.config[0].bbox[3] - self.config[0].bbox[1]

    def orphan(self) :
        '''Remove from parent.'''

        if self.included() :
            self.get_parent().remove(self)
    
    def included(self) :
        '''
        Is this a child entity and are we included in the parent (i.e. not
        runted)?
        '''
        return self.get_parent() is not None and not self.get_runted()

    def delete(self, if_empty=False) :
        '''
        Cleanly remove this entity from its environment. Returns its old parent
        if one exists. Note that deletability is a property and not guaranteed.
        '''

        if self != self.OUT() :
            return self.OUT().delete()

        old_parent = None
        if self.included() :
            old_parent = self.get_parent()

        # If we are deleteable and should orphan
        if self.get_deletable() == 1 or self.get_deletable() == 3 :
            self.squash()
            self.orphan()
        # If we are supposed to pass this delete request to our parent
        if (self.get_deletable() == 2 or self.get_deletable() == 3) and \
                old_parent is not None :
            old_parent = old_parent.delete(sender=self)

        return old_parent

    # Ignores visibility setting if no parent (as not being included in a \
    # longer string, so we must be being asked for a good reason!)
    def string_compile(self, body, mode="string") :
        '''Return body depending on visibility.'''
        return body if (self.get_visible() or not self.included()) else ''
    
    def am(self, what) :
        '''Is 'what' in mes?'''
        return what in self.mes

    def am_c(self, what) :
        '''Is 'what' in characteristics?'''
        return what in self.characteristics

    def get_line_size(self) :
        '''What is the master font size (not inc. scalings)'''
        return self.get_ip('font_size')

    def get_scaled_line_size(self) :
        '''What is the scaled font size? Probably what you're looking for!'''
        fs = self.get_line_size() * self.get_line_size_coeff()
        return fs
    
    def get_line_size_coeff(self) :
        '''
        What is the scaling factor for font size? That is, what do we
        multiply the font size by?
        '''
        return self.get_font_size_combined_coeff()
    
    def show_decoration(self) :
        '''Do we show decoration when drawing?'''
        return self.included() and self.get_parent().show_decoration()

    def get_size_scaling(self) :
        '''What is the font size coeff (not inc our own setting)'''
        return self.get_ip('font_size_coeff')

    def set_size_scaling(self, scale) :
        '''Set our own font size scaling'''
        self.set_font_size_scaling(scale, quiet=True)

    def set_line_size(self, size) :
        '''Set the master font size.'''
        self.set_font_size(size)

    def get_font_size(self) :
        '''What is the master font size (not inc. scalings)'''
        return self.get_ip('font_size')

    def get_scaled_font_size(self) :
        '''What is the scaled font size? Probably what you're looking for!'''
        fs = self.get_font_size() * self.get_font_size_combined_coeff()
        return fs
    
    def get_font_size_combined_coeff(self) :
        '''What is the font size coeff (inc our own setting)'''
        lc = self.get_ip('font_size_coeff')
        lc *= self.get_ip('font_size_combined_coeff')
        return lc
    
    def set_font_size_scaling(self, scale, quiet=False) :
        '''Set our own scaling of the font size.'''

        a = self.get_scaled_font_size()

        self.set_ip('font_size_coeff', scale, quiet=quiet)

        # What is the ratio of old to new final font size?
        a = self.get_scaled_font_size()/a

        # Scaling contents accordingly
        if not fc(a, 1.0) :
            self.scale(a)
    
    def set_font_name(self, name) :
        '''What font do we use?'''
        self.set_ip('font_name', name)

    def set_font_size(self, size) :
        '''Set the master font size.'''

        a = self.get_scaled_font_size()

        self.set_ip('font_size', size)

        # What is the ratio of change?
        a = self.get_scaled_font_size()/a

        if not fc(a, 1.0) :
            self.scale(a)

    def check_inherited_properties(self) :
        '''
        Find out whether any of our inherited properties have changed. Update in
        them in the process.
        '''

        resp = 0
        for i in self.inherited_properties :
            o = self.inherited_properties[i]
            # Check whether our inherited version has changed and, post
            # updating, whether an override exists such that we don't care
            if self.inherited_properties[i] != \
                        self.update_inherited_property(i) and\
                    i not in self.inherited_properties_overrides :
                # Set resp to 1, unless we, or a previous iteration, should
                # express the need for a recalc
                if resp != 2 and \
                        i not in self.inherited_properties_recalc_on_change :
                    resp = 1
                else :
                    resp = 2

        return resp
    
    def __nonzero__(self) :
        """Ensure that __len__ does not invalidate our if statements."""
        return True

    def update_inherited_property(self, i) :
        '''
        Get the latest version of an inherited property and record it, returning
        the result.
        '''

        # Nothing changes if we don't have a parent. Note that runted=True has
        # no impact here (i.e. we don't write 'if self.included()')
        if self.get_parent() is not None :
            # If we don't have a special routine for updating, just grab our
            # parent's value (NB: this makes it important that our parent is
            # updated first)
            if i not in self.inherited_properties_updaters :
                ip = self.get_parent().get_ip(i)
            else :
                ip = self.inherited_properties_updaters[i](self)

            # If there's a special routine for executing a change in this IP,
            # run it, otherwise just set it directly in the IP dict. Note that
            # this means any IP change routine is responsible for updating the
            # IP dict.
            if i in self.inherited_properties_change :
                self.inherited_properties_change[i](ip)
            else :
                self.inherited_properties[i] = ip

        return self.inherited_properties[i]

    def _set_font_size_for_ip(self, n) :
        '''IP change routine for font_size.'''
        #FIXME: redundant
        self.inherited_properties['font_size'] = n
    
    def _set_font_size_coeff_for_ip(self, n) :
        '''IP change routine for font_size_coeff.'''
        self.inherited_properties['font_size_coeff'] = n
    
    def _set_font_size_combined_coeff_for_ip(self, n) :
        '''IP change routine for font_size_combined_coeff.'''
        self.inherited_properties['font_size_combined_coeff'] = n
    
    def get_ip(self, i, ignore_override=False) :
        '''Get the value of an inherited property (includes overrides, etc.)'''

        # If this is as easy as returning the override, do so
        if i in self.inherited_properties_overrides and not ignore_override :
            return self.inherited_properties_overrides[i]
        # If there is a default override, same deal
        elif i in self.default_inherited_properties_overrides and not ignore_override :
            return self.default_inherited_properties_overrides[i]
        # Otherwise we want the real deal
        else :
            return self.inherited_properties[i]

    def set_ip(self, i, val, quiet=False) :
        '''
        Override an IP and call children_check to see if that has implications
        down the road. Use val=None to cancel an override
        '''

        # Are we being asked to remove the IP override?
        if val is None and i in self.inherited_properties_overrides :
            del self.inherited_properties_overrides[i]
            self.children_check(force=True, quiet=quiet)

        # Are we being asked to add an IP override and does this change
        # anything?
        if val is not None and \
                (i not in self.inherited_properties_overrides or \
                 self.inherited_properties_overrides[i] != val) :
            self.inherited_properties_overrides[i] = val
            self.children_check(force=True, quiet=quiet)

    def children_check(self, parent_change=False, quiet=False, force=False) :
        '''
        Check whether any changes are required to our children. In practice,
        this means check whether we have any outstanding changes to our IPs that
        need to be filtered down, and consequent recalcs that need to be
        executed.
        '''

        resp = self.check_inherited_properties()

        # No harm, no foul.
        if not force and resp == 0 :
            return

        # Derived classes should really override this if a parent change
        # would directly affect them (other than a simple translate)
        if not quiet and resp == 2 and (not parent_change or g.anal_retentive) :
            self.recalc_bbox(quiet=quiet)

        self.set_redraw_required()

    def get_rgb_colour(self) :
        '''What colour is this [IP]?'''
        return self.get_ip('rgb_colour')
    
    def set_rgb_colour(self, rgb_colour) :
        '''Set colour [IP]'''
        self.set_ip('rgb_colour', rgb_colour)

    def next_alternative(self) :
        '''If this entity has multiple alternatives, more to the next one.'''
        self.change_alternative(1)

    def prev_alternative(self) :
        '''If this entity has multiple alternatives, more to the prev one.'''
        self.change_alternative(-1)

    alternatives = None
    def alt_to_ent(self, a) :
        '''
        Create an actual entity from a member of the alternatives
        dictionary
        '''
        return make_phrasegroup(self.get_parent(), a)

    def change_alternative(self, dir=1) :
        '''
        Change the current entity to one of its alternatives
        '''

        altable = self.get_have_alternatives()

        # If we can't, we maybe our parent can?
        if not altable or len(self.alternatives) == 0 :
            if self.included() :
                return self.get_parent().change_alternative(dir)
            else :
                return False

        # What's the index of the alternative in given dir?
        n = self.alternatives.index(self.altname)
        n += dir
        n = n % len(self.alternatives)

        # Create the alternative
        alt = self.alt_to_ent(self.alternatives[n])
        alt.alternatives = self.alternatives
        alt.set_have_alternatives(True)

        # Add the alternative and remove ourselves
        #FIXME: why doesn't this use the exchange member of Phrase?
        self.get_parent().append(alt, after=self)
        self.get_parent().remove(self)

        return True

    def check_combination(self, shape) :
        '''
        This shape is to be added, if anyone wants to combine with it, speak
        now.
        '''

        if self.included() :
            return self.get_parent().check_combination(shape)

        return False

    def draw_alternatives(self, cr) :
        '''
        .. deprecated:: 0.2
        '''
        return False

    active = False
    def process_key(self, name, event, caret) :
        '''
        Check whether this key combination has a special meaning for this entity
        or, if not, any of its parents
        '''

        altable = self.active and self.get_have_alternatives()

        # By default we expect Up and Down to change the alternative; note this
        # isn't necessary Up & Down without modifiers as Caret will only call
        # this routine if it has reason to believe we want Entity specific
        # handling, normally indicated by Super
        if name == 'Up' and altable :
            self.prev_alternative()
        elif name == 'Down' and altable : 
            self.next_alternative()
        elif name == 'k' and 'main_phrase' in self.mes :
            ET.dump(gutils.xml_indent(self.get_xml()))

        if self.included() :
            return self.get_parent().process_key(name, event, caret)

        return False
    
    def to_clipboard(self, auto_paste=False, who=None, contents=False) :
        '''
        Call upwards to add ourselves (or 'who') to the clipboard; ultimately
        calls the rudimentary signal handler of main phrase.
        '''

        if who is None :
            who = self

        if self.included() :
            return self.get_parent().to_clipboard(auto_paste, who, contents)

        return False

    def process_button_release(self, event) :
        '''
        What should we do if asked to process a button release? Ask parent if
        not overridden.
        '''

        if self.included() :
            return self.get_parent().process_button_release(event)

        return False

    def process_button_press(self, event) :
        '''
        What should we do if asked to process a button press? Ask parent if
        not overridden.
        '''

        if self.included() :
            return self.get_parent().process_button_press(event)
        return False

    def process_scroll(self, event) :
        '''
        What should we do if asked to process a scroll? Ask parent if
        not overridden.
        '''

        if self.included() :
            return self.get_parent().process_scroll(event)
        return False

    def contains(self, point) :
        '''
        Is this point inside this entity's first config?
        '''
        #FIXME: extend to all configs (but check implications of that first)
        
        return self.config[0].bbox[3] > point[1] and \
               self.config[0].bbox[1] < point[1] and \
               self.config[0].bbox[0] < point[0] and \
               self.config[0].bbox[2] > point[0]
    
    # from_nought is the converse of squash, where we act as if this magically appeared.
    def from_nought(self, quiet = False) :
        '''
        This is a slightly optimized (as called from high-use function append)
        way to tell the configs that they have gone from zero to full (normal)
        width without resorting to a hide then a show.
        '''

        # Problems can occur with these fiddly functions, so check in
        # anal_retentive mode.
        if g.anal_retentive_mode and self.am('phrase') :
            self.consistency_check_sub_poses()
            self.recalc_bbox(quiet=True)

        # Is this is currently visible, we've got a very quick way of doing this
        if self.get_visible() :
            for c in self.config :
                self.config[c].old_bbox[2] = self.config[c].bbox[0]
            self.feed_up(quiet=quiet)
        # Otherwise, we expect the correct width to still be available
        else :
            self.set_visible(True)
            for c in self.config :
                cfg = self.config[c]
                cfg.bbox[2] = cfg.bbox[0] + cfg.width
            self.feed_up(quiet=quiet)

    def squash(self, quiet = False) :
        '''
        Make the width zero (and do necessary calls). In current
        implementation, this is equivalent to calling hide.
        '''
        self.hide(quiet=quiet)
    
    def get_bodmas_level(self) :
        '''What's the BODMAS level (if one exists)'''

        if self.am_c('_bodmasable') :
            return self.get_p('bodmas_level')
        return None

    def find_nearest(self, point, fall_through=True,
                     enterable_parent=False,
                     attachable=False,
                     row=0,
                     avoid=None) :
        '''
        Return the nearest attachable entity; in this case, it's self or
        there isn't one.
        '''

        # Return fail if we have to avoid ourselves
        if self == avoid :
            return (-1, self)

        dist = self.find_distance(point)

        # If this is usable, return so.
        if (enterable_parent and \
                (self.get_parent() is None or \
                 not self.get_parent().is_enterable())) or \
               (attachable and not self.is_attachable()) :
            print ':('
            return (-1, self)

        return (dist, self)
    
    def get_width(self) :
        '''Get width of first config.'''
        return self.config[0].bbox[2] - self.config[0].bbox[0]

    def get_height(self) :
        '''Get height of first config.'''
        return self.config[0].bbox[3] - self.config[0].bbox[1]

    def get_basebox_height(self) :
        '''Get height of alignment basebox (of first config).'''
        return self.config[0].basebox[5] - self.config[0].basebox[3]

    def draw(self, cr) :
        print 'GlypherEntity is an abstract class!'
    
    def scale(self, s, quiet=False) :
        '''Scale this entity (from the bottom left)'''

        if fc(s, 1.0) :
            return

        self._scale_enact(s)

        self.feed_up(quiet=quiet)
    
    def _scale_enact(self, s) :
        '''Do the hard word of scaling this entity.'''

        # Do the bbox scaling for each config
        #FIXME: shouldn't this be relative to the BL of the first cfg?
        for c in self.config :
            cfg = self.config[c]
            cfg.width *= s
            bb = cfg.bbox
            bb[2] = bb[0] + (bb[2]-bb[0])*s
            bb[1] = bb[3] - (bb[3]-bb[1])*s

        # Scale baseboxes (of the first config) accordingly
        self.config[0].scale_baseboxes(s)

        # Update the reference dimensions
        self.set_ref_height(self.get_ref_height()*s)
        self.set_ref_width(self.get_ref_width()*s)

        # Update the padding
        for i in range(0,4) :
            self.padding[i] *= s

    def move_to(self, x, y) :
        '''Move to a point (in local coords)'''
        self.translate(x - self.config[0].bbox[0], y - self.config[0].bbox[1])

    def translate(self, h, v, quiet=False, by_offset=True, after=None,
                  config=None, do_reset=True) :
        '''Move this entity by h, v'''

        if after is None :
            after = (h<0)

        self._translate_enact(h, v, after, config=config)

        if do_reset :
            self.feed_up(quiet=quiet)
        
    def config_collapse(self, quiet = False) :
        '''Collapse any configs. [not impl]'''
        #FIXME: why does this not do anything? Should entity only ever have one?
        pass
    def config_break(self, x_pos, quiet = False, do_break = False) :
        '''Split any configs. [not impl]'''
        #FIXME: why does this not do anything? Should entity only ever have one?
        return None

    def _translate_enact(self, h, v, search_dir_fwd=True, config=None) :
        '''Do the hard work of translation.'''

        cfgs = self.config if config is None else (config,)
        for c in cfgs :
            cfg = self.config[c]
            cfg.bbox[0] += h
            cfg.bbox[2] += h
            cfg.bbox[1] += v
            cfg.bbox[3] += v
            
            cfg.move_baseboxes(h, v)

            # If we need to update the subpos, do so
            if abs(h) > 1e-5 and self.included() :
                cfg.old_sub_pos = cfg.sub_pos
                cfg.sub_pos = self.get_parent().get_free_sub_pos(cfg,
                                  search_dir_fwd=search_dir_fwd)

    def find_distance(self, point) :
        '''How far from point are we? L2 norm.'''

        dist = 0
        # If we're between the ends
        if point[0] > self.config[0].bbox[0] and \
                point[0] < self.config[0].bbox[2] :
            # and we're between the sheets
            if point[1] > self.config[0].bbox[1] and \
                      point[1] < self.config[0].bbox[3] :
                dist = 0
            # but we're not between the sheets
            else :
                # Measure from closest end
                dist = min(abs(point[1]-self.config[0].bbox[1]),
                           abs(point[1]-self.config[0].bbox[3]))
        # If we're only between the sheets
        elif point[1] > self.config[0].bbox[1] and \
                point[1] < self.config[0].bbox[3] :
            dist = min(abs(point[0]-self.config[0].bbox[0]),
                       abs(point[0]-self.config[0].bbox[2]))
        # If this is off on a diagonal, shortest distance to a corner
        else :
          dists = []; corns = ( (0,1), (0,3), (2,1), (2,3) )
          for c in corns :
              dists.append(math.sqrt((point[0]-self.config[0].bbox[c[0]])**2 + \
                                     (point[1]-self.config[0].bbox[c[1]])**2 ) )
          dist = min(dists)

        return dist

    def get_repr(self) :
        '''
        Get a string (not unicode) representation of this object directly
        from the Sympy object.
        '''

        try :
            val = self.get_sympy()
            return str(val)
        except SympifyError as e :
            debug_print(str(e))
            return None

    title = None
    def set_title(self, title) :
        '''Provide a pretty, usu. for type.'''
        self.title = title

    def get_title(self) :
        '''Provide a pretty, usu. for type.'''
        return self.title

    # Normally we won't want the caret to flag up existence of info
    indicate_info = False

    info_text = None
    def set_info_text(self, info_text) :
        '''Provide some user documentation for this entity.'''
        self.info_text = info_text

    def get_info_text(self) :
        '''Provide some user documentation for this entity.'''
        return self.info_text

    wiki_link = None
    def set_wiki_link(self, wiki_link) :
        '''Provide a wiki link for this entity.'''
        self.wiki_link = wiki_link

    def get_wiki_link(self) :
        '''Provide a wiki link for this entity.'''
        return self.wiki_link

import Parser
def parse_phrasegroup(parent, tree, ops=None, top=True) :
    '''Calls Parser.parse_phrasegroup'''
    return Parser.parse_phrasegroup(parent, tree, ops, top)
def make_phrasegroup(parent, name, operands=None, properties=None) :
    '''Calls Parser.make_phrasegroup'''
    return Parser.make_phrasegroup(parent, name, operands, properties)
