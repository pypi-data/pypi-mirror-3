"""Caret module for Glypher"""
import gobject
import gtk
from sympy.parsing import mathematica

import glypher as g
from .. import aobject
from ..utils import debug_print
from BinaryExpression import *
from Parser import *
from Decoration import *
from Entity import *
from Phrase import *
from PhraseGroup import *
from Renderers import *
from Summation import *
from Symbol import *
from Table import *
from Word import *
from Fraction import *
from Function import *
from References import *
from Interpret import *
from Alternatives import *
import sympy.printing as printing

    
# The keynames listed below all trigger binary
# expressions.
binary_keynames = [
    'asterisk',
    'semicolon',
    'plus',
    'minus',
    'comma',
    'equal',
    'slash',
    'less',
    'greater',
    'space'
]

# The following keynames are translated to their
# corresponding symbols
swap_keynames = { \
    'asterisk' : u'\u00B7',\
    'equal' : '=',\
    'plus' : '+',\
    'semicolon' : ';',\
    'minus' : '-',\
    'percent' : '%',\
    'period' : '.',\
    'parenleft' : '(',\
    'space' : ' ',\
    'parenright' : ')',\
    'comma' : ',',\
    'slash' : '/',\
    'less' : '<',
    'greater' : '>',
    'at' : u'\u2218'
}

class GlypherCaret (gobject.GObject) :
    """Caret to control insertion and entity-wise operations"""

    # We add three signals
    #   changed-phrased-to : phrased_to has changed; send who_am_i and list of
    #       ancestors or ("None", "None") if phrased_to is None
    #   changed-attached-to : sim. for attached_to
    #   content-changed : the caret has done something requiring a redraw

    __gsignals__ =     { 
        "changed-phrased-to" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                (gobject.TYPE_STRING,gobject.TYPE_STRING)),
        "changed-attached-to" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                 (gobject.TYPE_STRING,gobject.TYPE_STRING)),
        "content-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    position = None
    attached_to = None
    phrased_to = None
    symbol_active = False
    main_phrase = None
    clipboard = None
    container = None
    glypher = None
    boxes = None
    selected = None
    editor_mode = False

    def __init__(self, main_phrase, interactive=True, container=None,
                 glypher=None):
        """
        Arguments :
            main_phrase - inside which our Caret shall live
            interactive - whether this Caret behaves in a edit-friendly way
            container - GTK widget to which GTK widgets may be added as overlays
            glypher - GlypherEntry instance which manages this Caret
        """
        gobject.GObject.__init__(self)

        self.position = [0., 0.]
        self.interactive = interactive
        self.main_phrase = main_phrase
        self.clipboard = []
        self.boxes = []
        self.selected = []
        self.container = container
        self.glypher = glypher
        self.find_left()

    def remove_boxes(self) :
        """Clear any overlay boxes from the drawing queue."""
        for b in self.boxes :
            if isinstance(b, GlypherWidgetBox) :
                self.container.remove(b.gw.ebox)

        self.boxes = []
    
    def go_near(self, point, main_phrase=None, change=False) :
        """Attached to closest entity in main_phrase (changes Caret's linked
        main_phrase if supplied).
        """
        m = self.main_phrase if main_phrase is None else main_phrase

        # Avoid attached if we must
        if change :
            avoid = self.attached_to
        else :
            avoid = None

        target = m.find_nearest\
            (point=point, fall_through=True, enterable_parent=True, avoid=avoid)

        self.main_phrase = m
        self.change_attached(target[1])

    def is_inside(self, phr) :
        """Returns bool indicating whether the Caret is, at some level, inside
        phrase phr.
        """
        return phr in self.phrased_to.get_ancestors()

    def process_key_release(self, keyname, event) :
        """
            Handles a key release event.
            Should only be called by a GlyphEntry.
        """
        mask = event.state
        m_control = bool(mask & gtk.gdk.CONTROL_MASK)
        m_shift = bool(mask & gtk.gdk.SHIFT_MASK)
        m_alt = bool(mask & gtk.gdk.MOD1_MASK)
        m_super = bool(mask & gtk.gdk.SUPER_MASK)

        if keyname == 'Super_L' or keyname == 'Super_R' :
            self.set_active(False)
        # Select something
        elif not m_alt and not m_super and \
                keyname == 'Shift_L'  :
            if self.prep_selected and self.attached_to != None and \
                    self.attached_to.am('phase') :
                if m_control :
                    self.add_selected(self.attached_to)
                else :
                    self.set_selected(self.attached_to)

    def find_end(self) :
        """Find the end of the main_phrase."""

        # As default if we can't find a suitable location, detach
        self.change_attached(None)
        self.adopt_phrase(None)

        ents = self.main_phrase.entities
        # Choose A & P as theoretical end-points and find the first leftward
        # valid position
        if len(ents) > 0 :
            A = ents[len(ents)-1]
        else :
            A = self.main_phrase
        P = self.main_phrase

        self.find_in_dir(left=True, A=A, P=P)

    def process_key_press(self, keyname, event) :
        """Handles a key press event. Should only be called by a GlyphEntry."""

        #FIXME: rewrite this for XML key definitions
        mask = event.state
        m_control = bool(mask & gtk.gdk.CONTROL_MASK)
        m_shift = bool(mask & gtk.gdk.SHIFT_MASK)
        m_alt = bool(mask & gtk.gdk.MOD1_MASK)
        m_clear = not (m_control or m_shift)
        m_ordinary = not m_alt and not m_control
        m_super = bool(mask & gtk.gdk.SUPER_MASK)

        self.prep_selected = False

        # Literal key entry; no parsing, just insert as given
        if m_control and m_super :
            kv = gtk.gdk.keyval_from_name(keyname)
            uc = unichr(gtk.gdk.keyval_to_unicode(kv))
            debug_print((uc,kv))
            if uc == u'\u0000' :
                return
            self.insert_shape(uc)
            return True

        # If the attached entity wants us to give it supered keys,
        # instead of dealing with them ourselves, do so
        if m_super or (self.attached_to != None and \
                       self.attached_to.get_p('override_keys')) :
            debug_print('entity handling '+keyname)

            if self.attached_to != None :
              ret = self.attached_to.process_key(keyname, event, self)
            elif self.phrased_to != None :
              ret = self.phrased_to.process_key(keyname, event, self)

            self.try_suggestion()

            return True

        if m_ordinary :
            # First make sure this isn't a combination for something
            if self.attached_to and \
                self.attached_to.check_combination(\
                    swap_keynames[keyname] if keyname in swap_keynames else\
                                                   keyname) :
                return True

        # Try the loaded named entities
        entity_name = try_key_press(event)
        if entity_name is not None :
            self.insert_named(entity_name)
        # Then try directional instructions
        elif m_clear and keyname == 'Home' and self.phrased_to is not None :
            ancs = self.phrased_to.get_ancestors()
            self.enter_phrase(ancs[-1], at_start=True)
        elif m_clear and keyname == 'End' and self.phrased_to is not None :
            self.find_end()
        # Select something
        elif not m_alt and not m_super and \
                keyname == 'Shift_L'  :
            self.prep_selected = True
        # Clear selection
        elif m_clear and keyname == 'Escape' :
            self.clear_selection()
            self.remove_boxes()
            self.glypher.main_phrase.clear_all_errors()
        # - (at front of phrase) - negate
        elif m_clear and keyname == 'minus' and \
                self.attached_to == self.phrased_to :
            debug_print(self.attached_to.format_me())
            self.insert_named('negative')
        # [prime] - do prime differentiation
        elif m_clear and keyname == 'apostrophe' :
            self.insert_named('prime')
        # Ctrl+[altkey] - Word has some characters corresponding to Word-groups
        elif m_control and not m_alt and keyname in Word.alternatives_keys :
            debug_print(keyname)
            alts_index = Word.alternatives_keys[keyname]

            # Prepare default package
            alts_current_defaults = Word.alternatives_current_defaults
            if alts_index not in alts_current_defaults :
                alts_current_defaults[alts_index] = 0

            self.insert_named(Word.alternatives[alts_index]\
                              [alts_current_defaults[alts_index]])
        # Ctrl+Alt+p - insert pi
        elif m_control and not m_alt and keyname == 'p' :
            self.insert_named('pi')
        # Alt+( - open a matrix
        elif not m_control and m_alt and keyname == 'parenleft' :
            self.insert_named('matrix')
        # ( - show no-user-parentheses tip
        elif m_ordinary and keyname == 'parenleft' :
            self.glypher.do_bracket_warning()
        elif m_ordinary and keyname == 'question' :
            if self.attached_to is not None :
                self.glypher.do_info(self.attached_to)
        # Ctrl+y - paste
        elif m_control and not m_alt and not m_super and keyname == 'y' :
            debug_print('x')
            self.paste()            
        # Ctrl+( - insert function (unless named)
        elif m_control and keyname == 'parenleft' :
            cur = str(self.phrased_to.to_string())
	    debug_print(cur)
            if self.phrased_to.am('word') and Parser.is_named(cur) :
                a, b = self.exit_phrase()
	    	debug_print(cur)
                if a is not None :
                    self.change_attached(a.get_parent())
                    a.orphan()
                if b is not None :
                    self.change_attached(b.get_parent())
                    b.orphan()
                self.insert_named(cur)
                self.try_suggestion()
            else :
                self.insert_named('function')
        # ^ - superscript
        elif keyname == 'asciicircum' :
            self.superscript_mode()
        # _ - subscript
        elif keyname == 'underscore' :
            self.subscript_mode()
        # Switch alternatives up/down
        elif m_super and self.symbol_active and keyname == 'Up' :
            if self.symbol_active :
                self.prev_alternative()
            else :
                self.jump_row(up=True)
        elif m_super and self.symbol_active and keyname == 'Down':
            if self.symbol_active :
                self.next_alternative()
            else :
                self.jump_row(up=False)
        # Ctrl+: - open range reference (to spreadsheet)
        elif keyname == 'colon' and m_control :
            ref = self.insert_named('range_reference')
        # Backspace - delete current shape (usu to left)
        elif m_clear and keyname == 'BackSpace' :
            self.delete_shape()
        # Backspace - delete rightward shape
        elif m_clear and keyname == 'Delete' :
            self.delete_shape_right()
        # Ctrl+Right - jump right
        elif m_control and not m_alt and keyname == 'Right' :
            self.find_right(gobbet_mode=True)
        # Right - walk right
        elif m_clear and keyname == 'Right' :
            self.find_right()
        # Ctrl+Left - jump left
        elif m_control and not m_alt and keyname == 'Left' :
            self.find_left(gobbet_mode=True)
        # Left - walk left
        elif m_clear and keyname == 'Left' :
            self.find_left()
        # Down - jump down a row
        elif m_clear and keyname == 'Down' :
            self.jump_row(up=False)
        # Up - jump up a row
        elif m_clear and keyname == 'Up' :
            self.jump_row(up=True)
        # Tab - change attached alternative
        elif m_ordinary and keyname == 'Tab':
            self.set_active(True)
            if self.attached_to :
                self.prev_alternative() if m_shift \
                 else self.next_alternative()
            self.set_active(False)
        # FIXME : surely one of this and the previous is redundant?
        elif m_ordinary and keyname == 'ISO_Left_Tab':
            self.set_active(True)
            if self.attached_to and self.attached_to.get_have_alternatives() :
                self.next_alternative() if m_shift \
                 else self.prev_alternative()
            self.set_active(False)
        # Return - down a row
        elif m_clear and keyname == 'Return':
            self.jump_row(up=False)
        # # - insert a shortcut combination
        elif keyname == 'numbersign' :
            w = GlypherSymbolShortener(widget_parent=self.container, caret=self)
            self.boxes.append(w)
            debug_print(w.parent)
        # \ - insert an entity/phrasegroup by TeX-style name
        elif keyname == 'backslash' :
            w = GlypherTeXEntry(widget_parent=self.container, caret=self)
            self.boxes.append(w)
            debug_print(w.parent)
        # $ - insert a Word with verbatim text-entry text
        elif keyname == 'dollar' :
            w = GlypherEntry(widget_parent=self.container, caret=self)
            self.boxes.append(w)
            debug_print(w.parent)
        # : - insert a colon as part of a Word
        elif m_ordinary and keyname == 'colon' :
            self.insert_shape(':', no_split=m_super)
        # [char] - insert len-1 char (use super to avoid any braking)
        elif m_ordinary and len(keyname) == 1 :
            self.insert_shape(keyname, no_split=m_super)
        # [binary key] - open a binary (or nary) expression
        elif m_ordinary and keyname in binary_keynames :
            shape = keyname
            if keyname in swap_keynames :
                shape = swap_keynames[shape]
            self.binary_expression_mode(shape)
        # [swap keyname] - insert specific shape for this symbol
        elif m_ordinary and keyname in swap_keynames :
            self.insert_shape(swap_keynames[keyname])
        # Super - show alternatives
        elif not m_control and keyname == 'Super_L' or keyname == 'Super_R' :
            self.set_active(True)
        # Give up (and admit it)
        else :
            return False

        # Make sure caret in the right position
        self.reset()

        # Tell caller we found a combo
        return True

    def return_focus(self) :
        """Bring the GTK focus back to the linked GlyphEntry widget."""
        if self.glypher :
            self.glypher.grab_focus()

    #FIXME: stupid argument style
    def grab_an_entity(self, want_rhs = True, leave_lhs = False) :
        """
        Detach entries on the left and right (if available) and split a word if
        necessary.

        Returns a pair representing entities on LHS and RHS of Caret, with None
        provided where appropriate.

        Keyword arguments :
            want_rhs - should take RHS? (default False)
            leave_lhs - should take LHS? (default False)
        """

        lhs = None
        parent = None
        rhs = None

        # Split the situation into one of three manageable possibilites (in
        # order of precedence) :
        #   a) we are attached to a phrase (at the end) and are expected to take
        #      the LHS,
        #   b) we are attached to a non-empty phrase (at the beginning) and want
        #      the RHS,
        #   c) we are phrased to a word.
        if self.attached_to is not None and self.attached_to.am('phrase') and \
                self.attached_to != self.phrased_to and not leave_lhs:
            lhs = self.attached_to
            parent = lhs.get_up()
            lhs.orphan()
        elif want_rhs and \
                self.attached_to is not None and \
                self.attached_to.am('phrase') and \
                self.attached_to == self.phrased_to and \
                len(self.phrased_to.get_entities()) > 0 :
            # word exemption allows us to avoid differentiating between the
            # identical visual positions of being attached to the front of a
            # word and attached to the front of a phrase beginning with a word.
            if not self.phrased_to.am('word') :
                rhs = self.phrased_to.get_entities()[0]
            else :
                rhs = self.phrased_to
            # Preempt the potential disappearance of this, attached, entity.
            # Ultimately breaks if we can't move off this attached_to, i.e.
            # attach to anything leftwards
            self.find_left()
            rhs.orphan()
        elif self.phrased_to is not None and self.phrased_to.am('word') :
            # Break the word.
            lhs, rhs = self.exit_phrase()

            # If we didn't find anything on the left and have a redundant
            # word-part on the right, use it.
            if lhs is None and not want_rhs :
                lhs = rhs

            if lhs is not None and not leave_lhs :
                lhs.orphan()
            if want_rhs and rhs is not None :
                rhs.orphan()

        #if lhs and parent is not None :
        #    self.find_left()

        return (lhs, rhs)

    def _try_binary_expression(self, name, make_me, symbol = None) :
        """
        Actually make the binary expression requested by binary_expression_mode.
        """

        ancs = self.phrased_to.get_ancestors()
        found_at_level = -1
        # Search upwards for a binary expression of the same type. Stop
        # searching as soon as we hit any kind of PhraseGroup that is not
        # designated as a stop point for this type of expression.
        for i in range(0, len(ancs)) :
            ancestor = ancs[i]
            if ancestor.am(name) and (symbol is None or \
                                      ancestor.get_symbol_shape() == symbol):
                found_at_level = i
                bin_exp = ancs[i]
                break
            elif ancestor.stop_for_binary_expression(name) :
                break

        # If we did not find such an instance of the binary expression, or it is
        # using the wrong symbol, just make a new one where we stand. Otherwise,
        # find out which argument we're inside and add a new one after it.
        if found_at_level == -1 :
            lhs, rhs = self.grab_an_entity(want_rhs=True)
            bin_exp = make_me(l=lhs, r=rhs)
            self.new_phrase(bin_exp, enter=False)
        else :
            # See BinaryExpressions.py for info on BE.poss list; essentially it
            # is the outermost phrase of an operand.
            pos = ancs[i-1]
            for r in bin_exp.poss.iterkeys() :
                if bin_exp.poss[r] == pos :
                    ret = bin_exp.add_operand(after=r)
                    lhs, rhs = self.grab_an_entity(want_rhs=True,leave_lhs=True)
                    if rhs :
                        ret.adopt(rhs)
                        bin_exp.set_recommending(bin_exp.poss[r])
                    else :
                        bin_exp.set_recommending(ret.IN())
                    return

    def binary_expression_mode(self, operator_shape) :
        """Create, or insert an additional operand into, a binary expression of
        this shape.

        Arguments :
            operator_shape - string to be used for interstitial symbol.
        """

        # Unless we have a BinaryExpression (BE) that doesn't take multiple 
        if operator_shape == '/' :
            lhs, rhs = self.grab_an_entity()
            bie = GlypherSideFraction(self.phrased_to, lhs=lhs, rhs=rhs)
            self.new_phrase(bie)
        else :
            # if we have a specific LHS/RHS constructor we wish to use, pass it.
            symbol_for_try_func = None
            if operator_shape == '+' :
                name='add'
                make_me = lambda l,r : GlypherAdd(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == '<' :
                name='less_than'
                make_me = lambda l,r : GlypherLessThan(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == '>' :
                name='greater_than'
                make_me = lambda l,r : GlypherGreaterThan(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == '=' :
                name='equality'
                make_me = lambda l,r : \
                        GlypherEquality(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == u'\u00B7' :
                name='mul'
                make_me = lambda l,r : GlypherMul(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == '-' :
                name=None
                make_me = lambda l,r : \
                        GlypherAdd(self.phrased_to, lhs=l, rhs=r, subtract=True)
            elif operator_shape == ' ' :
                name='space_array'
                make_me = lambda l,r : \
                        GlypherSpaceArray(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == ';' :
                name='semicolon_array'
                make_me = lambda l,r : \
                        GlypherSemicolonArray(self.phrased_to, lhs=l, rhs=r)
            elif operator_shape == ',' :
                name='comma_array'
                make_me = lambda l,r : \
                        GlypherCommaArray(self.phrased_to, lhs=l, rhs=r)
            else :
                name='binary_expression'
                symbol_for_try_func=operator_shape
                make_me = lambda l,r : \
                    GlypherBinaryExpression(self.phrased_to,
                                            GlypherSymbol(self.phrased_to,
                                                          operator_shape),
                                            lhs=l, rhs=r)

            self._try_binary_expression(name, make_me,
                                        symbol=symbol_for_try_func)

        # Find any recommended site
        self.try_suggestion()

    def try_suggestion(self) :
        """See whether the main_phrase has been given a suggested target for
        when control returns to the Caret."""

        where_to = self.main_phrase.get_recommending()

        # If we have a recommendation: if its an enterable phrase, then enter
        # it, otherwise, attach to it. If not: move rightward.
        if where_to is not None :
            if where_to.am('phrase') and where_to.IN().is_enterable() :
                self.enter_phrase(where_to.IN(), at_end=True)
            else : self.change_attached(where_to)
        else : self.find_right()
    
    def superscript_mode(self) :
        '''Adds superscript (a specified setup of Script)'''
        base, wing = self.grab_an_entity()
        superscript = GlypherScript(self.phrased_to, expression=base,
                                    available=(False, False, True, False))
        self.new_phrase(superscript, enter=False)
        self.try_suggestion()
    
    def subscript_mode(self) :
        '''Adds subscript (a specified setup of Script)'''
        base, wing = self.grab_an_entity()
        subscript = GlypherScript(self.phrased_to, expression=base,
                                  available=(True, False, False, False))
        self.new_phrase(subscript, enter=False)
        self.try_suggestion()
    
    def insert_named(self, name, properties = None) :
        """Insert a PhraseGroup or entity by name.

        Arguments :
            name - string name of entity
            properties - additional properties to be applied on loading (default
                         None)
        """

        n = is_named(name)
        if n == GLYPHER_IS_ENTITY :
            return self.insert_named_entity(name, properties)
        elif n == GLYPHER_IS_PG :
            return self.insert_phrasegroup(name, properties)
        else :
            raise(RuntimeError(\
                name + " is neither a (loaded) named entity nor a PhraseGroup"))

    def insert_phrasegroup(self, name, properties=None, grab_entities=True) :
        """Insert a PhraseGroup by name.

        Arguments :
            name - string name of PhraseGroup
            properties - properties to be applied on loading (default None)
            grab_entities - uses grab_an_entity() to fill targets (default True)
        """

        lhs, rhs = self.grab_an_entity() if grab_entities else (None,None)
        phrasegroup = make_phrasegroup(self.phrased_to, name, [lhs, rhs],
                                       properties=properties)
        self.new_phrase(phrasegroup, enter=False)
        self.try_suggestion()
        self.emit('content-changed')
        return phrasegroup

    def new_word(self) :
        """Add a new word into the current phrase."""

        if not self.phrased_to : return
        self.phrased_to.set_active(False)

        word = GlypherWord(self.phrased_to)

        if len(self.phrased_to) > 0 and not self.editor_mode :
            p = self.phrased_to
            mult = GlypherMul(p)
            p.elevate_entities(mult['pos0'])
            mult['pos2'].adopt(word)
            p.adopt(mult)
        else :
            self.phrased_to.IN().append(word, after=self.attached_to)

        self.phrased_to = word
        self.phrased_to.set_active(True)

        self.try_suggestion()
            
    def new_phrase(self, parent, enter = True) :
        """Add a new phrase (parent) into the current phrase."""

        # Break a word first if we're in the middle of one. We don't want to add
        # a phrase into it.
        if self.phrased_to :
            self.phrased_to.set_active(False)
            if self.phrased_to.am('word') :
                lhs, rhs = self.exit_phrase()
                if lhs is not None :
                    self.change_attached(lhs)

        # If the new phrase has been given as None, create a vanilla Phrase.
        if parent is None :
            parent = GlypherPhrase(self.phrased_to)

        # Add the phrase
        if self.phrased_to :
            self.phrased_to.IN().append(parent, after=self.attached_to)

        if enter :
            self.enter_phrase(parent)

        return parent
            
    def exit_phrase(self) :
        """Move up a level, splitting a word if necessary to stay where we
        are. Returns whatever is on each side (e.g. (None, GlypherPhrase))."""

        if not self.phrased_to or not self.phrased_to.get_up() :
            return (None, None)

        self.phrased_to.set_active(False)
        parent = self.phrased_to.get_up()

        # Start by assuming we're at beginning or end
        if self.phrased_to==self.attached_to :
            sides = (None, self.phrased_to)
        else :
            sides = (self.phrased_to, None)

        # Check whether we are in the middle of a word. We use
        # get_caret_position to ensure that we have the global coordinates of
        # the word's bbox.
        word = self.phrased_to.OUT()
        word_left = word.get_caret_position(pos=(word.config[0].bbox[0], 0))[0]
        word_right = word.get_caret_position(pos=(word.config[0].bbox[2], 0))[0]

        if self.phrased_to.am('word') and \
                self.position[0] < word_right and self.position[0] > word_left :
            # Recognize that parent is going to be a level higher now
            parent = word.get_up()

            # Find position of Caret relative to word before its bbox changes
            wpos = self.position[0]-\
                   (word.config[0].bbox[0]+word.get_local_offset()[0])

            # Orphan the word
            word.delete()

            # Use convenient GlypherWord method to generate two words
            words = word.split(wpos)

            # Add the words into our parent
            map(parent.IN().append, words)

            sides = tuple(words)

        self.enter_phrase(parent, upward=True, fall_through=False)

        return sides

    def insert_named_entity(self, name, properties=None) :
        """Add a named entity (not PhraseGroup) to the current phrase.

        Arguments :
            name - string name of entity
            properties - properties to be applied after loading (default None)
        """
        debug_print(name)
        ent = make_phrasegroup(self.phrased_to, name, operands=None,
                               properties=properties)
        debug_print(ent)
        debug_print(ent.to_string())
        self.insert_entity(ent)
        return ent

    def insert_entity(self, entity) :
        """Insert a GlypherEntity at the Caret."""

        if entity is None :
            return

        p = self.phrased_to.IN()
        # Make sure we're not putting a non-symbol into a word
        if p.am('word') and not entity.am('symbol') :
            l = self.exit_phrase()
            self.change_attached(l[0])
            p = self.phrased_to

            op = []
            if l[0] is not None :
                l[0].orphan()
                op.append(l[0])
            op.append(entity)
            if l[1] is not None :
                l[1].orphan()
                op.append(l[1])

            mult = GlypherMul(p)
            p.adopt(mult)
            mult.set_lhs(op[0])
            mult.set_rhs(op[1])
            if len(op) > 2 :
                mult.add_operand()
                mult['pos4'].adopt(op[2])
            self.change_attached(entity)
        elif not p.am('word') and len(p) > 0 and not self.editor_mode :
            mult = GlypherMul(p)
            p.elevate_entities(mult['pos0'])
            mult['pos2'].adopt(entity)
            p.adopt(mult)
            self.change_attached(entity)
        else :
            self.phrased_to.IN().append(entity, after=self.attached_to)
            self.try_suggestion()
        self.emit('content-changed')

    def insert_shape(self, shape, code = None, no_split = False) :
        """Insert a shape (string, usu. character) at the Caret."""

        # Ensure that we have a word to which to add the new symbol.
        if not self.phrased_to.am('word') :
            self.new_word()

        self.reset()

        # Create symbol
        symbol = GlypherSymbol(self.phrased_to, shape, code=code, text=shape)
        self.insert_entity(symbol)
    
    def delete_shape(self) :
        """Delete the entity to which the Caret is attached."""

        if self.attached_to == None :
            return

        # Make a note of the target entity
        to_del = self.attached_to

        # Find another entity before we remove the current one (assumes
        # possible! However, we should always be in some enterable undeletable
        # phrase, if a few levels removed)
        self.find_left()

        to_del_ancs = list(to_del.get_ancestors())

        parent = to_del.delete()

        debug_print(self.attached_to.format_me())
        # If we took the last symbol out of a word, delete it
        #FIXME: could this be handled by deletable=3 and new method in Word?
        if to_del.am('symbol') and parent.am('word') and \
                len(parent.get_entities())==0 :
            parent = parent.delete()

        # If we've lost the main_phrase, i.e. been orphaned at some level up
        # then continue back through to_del's (previous) ancestors until we find
        # one that hasn't been orphaned. If the entity we're attached to has
        # been moved, make sure we're phrased in the right place.
        if self.attached_to.get_main_phrase() != self.main_phrase :
            for anc in to_del_ancs :
                if anc.get_main_phrase() == self.main_phrase :
                    A = anc
                    break
            # Suppose we're attached to the end of ancestor A, unless it doesn't
            # have a parent (so, by the selection process, must be
            # self.main_phrase).
            P = A if A.parent is None else A.parent

            self.change_attached(A)

            # While we've no idea whether A, P are attachable or enterable,
            # resp., we can use find_in_dir to ask "if we were attached to A,
            # and phrased to P, and what is the first valid Caret position to
            # the left?".
            A, P = self.find_in_dir(left=True, A=A, P=P)
        else :
            # Make sure that, if our attached_to has moved, we are correctly
            # phrased by reattaching. If we can no longer attach to it, find
            # left to the nearest valid point.
            if not self.change_attached(self.attached_to) :
                self.find_in_dir(left=True, A=self.attached_to,
                                 P=self.attached_to.get_up())


    def delete_shape_right(self) :
        """Run delete_shape for the entity to the Caret's right."""
        self.find_right()
        self.reset()
        self.delete_shape()

    def delete_from_shape(self) :
        """Delete from end of main_phrase to current shape."""
        cur = self.position
        ancs = self.phrased_to.get_ancestors()
        self.enter_phrase(ancs[len(ancs)-1], at_end=True)
        while (self.position > cur) :
            self.delete_shape()
            
    def delete_to_shape(self) :
        """Delete from beginning to current shape."""
        start = self.phrased_to.get_caret_position(True)
        while (self.position > start) :
            self.find_right()
            oldpos = self.attached_to
            self.find_left()
            self.delete_shape()
            self.change_attached(oldpos)
            self.find_left()
            self.reset()
            debug_print(self.position)

    def set_active(self, active) :
        """Set the current active state of the attached entity. Usually relevant
        for Alternatives."""
        if self.attached_to :
            self.attached_to.active = active
        self.symbol_active = \
                active and self.attached_to and \
                self.attached_to.get_have_alternatives()

    def change_attached(self, new_att, outside = False) :
        """Change the attached entity to new_att, if possible. Returns True if
        successful."""

        # Default return value
        ret = False

        # Make sure that we aren't in an active state
        self.set_active(False)

        # Inform currently attached entity that its services are no longer
        # required
        if self.attached_to is not None :
            self.attached_to.set_attached(False)
            self.attached_to = None

        # Make sure we've been handed the outside iff. we aren't phrased to
        # new_att (relevant for CompoundPhrases). If we are phrased to it, we
        # want the inside, as we'll be attaching at the front.
        if new_att is not None :
            if self.phrased_to != new_att.IN() or outside :
                new_att = new_att.OUT()
            else :
                new_att = new_att.IN()

            if not new_att.is_attachable() :
                return False

            # Make the change
            self.attached_to = new_att
            new_att.set_attached(True)

            # Update our return variable
            ret = True

            # Make sure we're in a phrase that will let us attach. If we can't
            # go to the outside but we can go inside, do so.
            if new_att != self.phrased_to or outside :
                if new_att.included() and new_att.get_up().is_enterable() :
                    self.adopt_phrase(new_att.get_up())
                elif new_att.am('phrase') and new_att.is_enterable() :
                    self.adopt_phrase(new_att)
                else :
                    return False

            # Update our Caret position
            self.reset()

            ancs = self.attached_to.get_ancestors() if self.attached_to else []
            self.emit("changed-attached-to", self.attached_to.who_am_i(),
                      '-'.join([o.mes[len(o.mes)-1] for o in ancs]))
        else :
            self.attached_to = None
            self.emit("changed-attached-to", 'None', 'None')

        return ret
    
    def reset (self) :
        """Ensure we're attached to something and update the position."""

        if self.phrased_to.get_main_phrase() != self.main_phrase :
            debug_print('Lost main_phrase')
            # Scan right from end if we've been orphaned
            self.find_in_dir(left=False, A=self.main_phrase, P=self.main_phrase)
            if self.attached_to is None :
                self.change_attached(None)

        # Update properties for current phrased_to (e.g. row_height but none at
        # present)

        # Set position from attached (dependent on whether we're attaching
        # inside, or from phrased_to if, for some reason, we aren't attached but
        # are phrased)
        if self.attached_to != None :
            self.position = self.attached_to.get_caret_position(\
                self.attached_to==self.phrased_to)
        else :
            self.position = self.phrased_to.get_caret_position(True)

    def find_left (self, gobbet_mode=False) :
        """Convenience function for find_in_dir."""
        self.find_in_dir(True, gobbet_mode=gobbet_mode)

    def find_right (self, gobbet_mode=False) :
        """Convenience function for find_in_dir."""
        self.find_in_dir(False, gobbet_mode=gobbet_mode)
                
    def enter_phrase(self, phrase, fall_through=True, at_start=False,
                     at_end=False, upward=False) :
        """
        Find somewhere in the given Phrase to attach to, with the given
        constraints. Returns True if it finds somewhere to go.

        Arguments
            phrase - phrase to go into
            fall_through - whether we can drop down further levels to get
                           closest entity
            at_start - go near start
            at_end - go near end
            upward - if needs be, move up levels
        """

        # Where in the phrase should we aim for? Get a location, using the caret
        # position
        bbox = phrase.config[0].bbox
        if at_start :
            if phrase.is_enterable() :
                self.adopt_phrase(phrase)
                self.change_attached(phrase)
                return True
            pos = (bbox[0]-1,0.5*(bbox[1]+bbox[3]))
            pos = phrase.get_caret_position(pos=pos)
        elif at_end :
            pos = (bbox[2]+1,0.5*(bbox[1]+bbox[3]))
            pos = phrase.get_caret_position(pos=pos)
        else :
            pos = self.position

        # Entity provides this useful method for finding the closest (nested)
        # entity in a phrase
        (dist, nearest) = phrase.find_nearest(pos, fall_through,
                                              enterable_parent=True)

        # If we didn't find anything at all, try upwards.
        if dist == -1 :
            if not upward : return False
            while not phrase.get_up().is_enterable() : phrase = phrase.get_up()
            nearest = phrase
            phrase = phrase.get_up()

        # If we can fall through, join the nearest Entity. If not, see if we can
        # just jump in here.
        if fall_through :
            if nearest.am('phrase') and nearest.is_enterable() :
                self.adopt_phrase(nearest)
            else:
                self.adopt_phrase(nearest.get_up())
        elif phrase.is_enterable() :
            self.adopt_phrase(phrase)
        else :
            return False

        # Give ourselves an attached Entity
        self.change_attached(nearest)

        return True

    def find_in_dir (self, left = True, dropdown = True, enact = True, A = None,
                     P = None, row = 0, gobbet_mode = False) :
        """
        Tries to find the first Entity/Phrase pair we can attach to in a given
        direction. Returns an attached_to, phrased_to pair; (None, None) if none
        can be found.

        Arguments :
            left - True/False for left/right search
            dropdown - whether we must stay in this level
            enact - whether this is just a search mission or should we attach at
                    end
            A - supposing that we start search from A; if None uses
                    currently attached Entity
            P - supposing that we start search in P; if None uses
                    currently phrased Phrase
        """

        # Define an integer representing direction
        d = -1 if left else 1

        # Use i as our index through the current Phrase
        i = 0
        if A is None :
            A = self.attached_to
        if P is None :
            P = self.phrased_to
            # If not currently phrased, try starting at the very end of this
            # main_phrase
            if P is None :
                self.find_end()
                P = self.phrased_to
            # Otherwise, give up.
            if P is None :
                return (None, None)

        # If we aren't attached to anything, lets hide out at the front of our
        # (temporary) phrased_to
        if A is None : A = P

        # If we're inside the front of P, let the index be -1 and our collection
        # of sites be all of those in P. Otherwise, we're at position index(A)
        # in the visible Entities of P.
        if P == A :
            if not left :
                i = -1
                sites = P.get_row(row, only_visible=True)
        else :
            cs = A.config
            attcfg = cs[len(cs)-1]
            sites = P.get_row(attcfg.row, only_visible=True)
            i = sites.index(attcfg)

        # If we are at the start and we want to go left, or end and go right,
        # then we'll need to go up. Otherwise, we will be going down or across.
        if (P==A and left) or i+d == len(sites) :
            p = P.OUT()
            q = p.get_parent()
            if q is None :
                return (None, None)

            # If we're going up, depending on the direction, we want to attach
            # to the first or last config in the Entity (usually only one
            # exists). We find out where our phrase is in that config and then
            # go left/right
            m = 0 if left or len(p.config)==1 else 1
            sites_above = q.get_row(p.config[-m].row, only_visible=True)
            index_above = sites_above.index(p.config[-m])
            if left :
                if index_above > 0 :
                    A = sites_above[index_above-1].get_entity()
                else :
                    A = q
            else :
                A = p
            P = q
        else :
            m = 0 if left else 1
            cfg = sites[i+m]
            # It may be that we wish to go inwards
            if cfg.get_entity().am('phrase') :
                new_P= cfg.get_entity().IN()
                row = new_P.get_row(0, only_visible=True)
                new_A = row[len(row)-1].get_entity().OUT() \
                        if left and len(row)>0 else new_P

                # If our first inward guess doesn't work, try a different row
                if not new_P.is_enterable() or not new_A.is_attachable() :
                    rows = list(new_P.rows)
                    rows.sort(key=abs)
                    for rn in rows :
                        r = new_P.get_row(rn, only_visible=True)
                        new_A = r[len(r)-1].get_entity().OUT() \
                                if left and len(r)>0 else new_P

                        A, P = self.find_in_dir(left=left, dropdown=True,
                                                enact=False, A=new_A, P=new_P,
                                                row=rn)

                        if P is not None and new_P in P.get_ancestors() :
                            break
                    new_A = A
                    new_P = P
                A = new_A
                P = new_P
            # or maybe we should go to the beginning of P
            elif i+d < 0 :
                A = P
            # or simply attach to an element
            else :
                newcfg = sites[i+d]
                ent = newcfg.get_entity()
                A = ent

        # Check whether we're attached to a gobbet (empty TargetPhrase or PG)
        keep_gobbet_searching = False
        if gobbet_mode :
            if ((P.am('target_phrase')) or \
                             A.am('phrase_group')) :
                debug_print('found_gobbet')
            else :
                keep_gobbet_searching = True

        # If we haven't arrived somewhere commodious, keep going.
        if not A.is_attachable() or not P.is_enterable() \
                or keep_gobbet_searching :
            A, P = self.find_in_dir(left=left, dropdown=dropdown,\
                enact=False, A=A, P=P, gobbet_mode=gobbet_mode)

        # Enact if needs be
        if enact and None not in (A, P) :
            self.adopt_phrase(P)
            self.change_attached(A)
        return (A, P)

    def jump_row(self, up=True) :
        """Move from current attached element in a given vertical direction."""

        # Get int representing direction
        d = 1 if up else -1

        phrase = self.phrased_to
        ent = None
        phrase_prev = self.attached_to

        # Keep looping until something happens...
        while ent == None :
            while ent == None and phrase != None :
                # If we have multiple rows, or any row redirects, try switching
                if len(phrase.rows)+len(phrase.get_row_redirects()) > 1 :
                    # Establish the row possibilities and current row index
                    if len(phrase.rows) > 1 :
                        rows = phrase.rows; rows.sort()
                        rowi = rows.index(phrase_prev.config[0].row)
                    else :
                        rows = [0]
                        rowi = 0
                    
                    # Keep going (away from middle row) until we hit the last
                    # index in either direction.
                    while (rowi if up else len(rows)-1-rowi) > 0 :
                        rowi -= d
                        row = rows[rowi]
                        
                        # What's the nearest element to the current Caret
                        # position in this row?
                        di, s = phrase.find_nearest(self.position,
                                                    enterable_parent=True,
                                                    attachable=True,
                                                    row=row)

                        if di != -1 :
                            ent = s
                        if ent is not None : break

                    # if we didn't find anything, try the redirects
                    if ent is None and d in phrase.get_row_redirects() :
                        ent = phrase.get_row_redirects()[d]
                        break

                # If there's still no joy in the current phrase, lets move out a
                # level and see if we've multiple available rows there
                phrase_prev = phrase.OUT()
                phrase = phrase.get_up()

            # This should never be run as phrase=main_phrase=>ent=main_phrase,
            # so phrase should never be None. Unless this is orphaned...
            if ent == None : 
                self.enter_phrase(phrase_prev, at_start=True)
                break
            elif ent.am('phrase') and\
                    self.enter_phrase(ent, at_start=(phrase_prev==ent)) :
                # if ent is a phrase, either it is phrase (well, phrase_prev
                # now) and find_in_dir knows ent.expr() is enterable at the
                # start, or it is completely to the left of pos, as with any
                # other entity, so we can safely attach at to its end
                break
            # "if not a phrase that we can enter (at some depth)..."
            elif ent.get_up().is_enterable() :
                self.change_attached(ent)
                break;
            # if the parent=phrase_prev is not enterable, we need to keep
            # ascending until something is (top phrase will be)
            if phrase.get_up() == None : break
            ent = None

    def adopt_phrase(self, phrase) :
        """
        Sets our phrased_to, without considering attachment (whereas
        enter_phrase finds somewhere for you to go to. Returns True on success
        """

        if phrase != None and not phrase.is_enterable() :
            return False
        
        # Inform our current phrased_to that it doesn't need to be active
        if self.phrased_to != None :
            self.phrased_to.set_active(False)

        # If we have a phrase set it as active. Inform our listeners of any
        # upshot.
        if phrase is not None :
            self.phrased_to = phrase.IN()
            self.phrased_to.set_active(True)
            ancs = self.phrased_to.get_ancestors()
            self.emit("changed-phrased-to", self.phrased_to.who_am_i(),
                      '-'.join([o.mes[len(o.mes)-1] for o in ancs]))
        else :
            self.phrased_to = None
            self.emit("changed-phrased-to", "None", "None")
        return True

    def prev_alternative(self) :
        """Try switching to previous alternative on current Entity."""

        if self.attached_to :
            self.attached_to.prev_alternative()
            self.try_suggestion()
        self.reset()
    
    def next_alternative(self) :
        """Try switching to previous alternative on current Entity."""

        if self.attached_to :
            self.attached_to.next_alternative()
            self.try_suggestion()
        self.reset()
    
    def draw(self, cr) :
        """Draw the Caret and any associated boxes onto the Cairo context,
        cr."""

        self.reset()

        # If we're interactive, we need to see a Caret
        if self.interactive :
            cr.save()
            cr.set_line_width(2.0)
            rgb_colour = (0.5,0.5,1.0)

            # If we're attached to a symbol, nothing, or the front of a phrase,
            # all we need is a line. Otherwise, (right emphasized) square
            # brackets are required.
            if self.attached_to == self.phrased_to or self.attached_to is None \
                    or self.attached_to.am("symbol") :
                cr.move_to(*self.position)
                cr.set_source_rgb(rgb_colour[0]*0.8,
                                  rgb_colour[1]*0.8,
                                  rgb_colour[2]*0.8)
                if self.attached_to is not None :
                    cr.rel_line_to(0, -self.attached_to.get_height())
                else :
                    cr.rel_line_to(0, -self.phrased_to.get_height())
                cr.stroke()
            else :
                cr.set_source_rgb(rgb_colour[0]*0.8,
                                  rgb_colour[1]*0.8,
                                  rgb_colour[2]*0.8)
                pos = self.attached_to.get_caret_position(\
                    pos=(self.attached_to.config[0].bbox[2],
                         self.attached_to.config[0].bbox[3]))
                cr.move_to(*pos)
                cr.rel_move_to(0, 5)
                cr.rel_line_to(5, 0)
                cr.rel_line_to(0, -self.attached_to.get_height()-10)
                cr.rel_line_to(-5, 0)
                cr.stroke()
                cr.set_source_rgba(rgb_colour[0]*0.8,
                                   rgb_colour[1]*0.8,
                                   rgb_colour[2]*0.8, 0.3)
                pos = self.attached_to.get_caret_position(\
                    pos=(self.attached_to.config[0].bbox[0],
                         self.attached_to.config[0].bbox[3]))
                cr.move_to(*pos)
                cr.rel_move_to(0, 5)
                cr.rel_line_to(-5, 0)
                cr.rel_line_to(0, -self.attached_to.get_height()-10)
                cr.rel_line_to(5, 0)
                cr.stroke()
            cr.restore()

        # Show a help icon if there's info
        if self.attached_to is not None and \
                self.attached_to.indicate_info and \
                self.attached_to.get_info_text() is not None :
            qn_loc = (self.position[0]+5,
                      self.position[1]-5-self.attached_to.get_height())
            cr.save()
            cr.set_font_size(0.25*self.attached_to.get_scaled_font_size())
            cr.select_font_face("sans")
            exts = cr.text_extents('?')
            cr.rectangle(qn_loc[0] + exts[0] - 2,
                         qn_loc[1] + exts[1] - 2,
                         exts[2] + 4, exts[3] + 4)
            cr.set_source_rgba(0.0, 0.0, 1.0, 0.5)
            cr.stroke_preserve()
            cr.set_source_rgba(1.0, 1.0, 0.5, 0.5)
            cr.fill()
            cr.move_to(qn_loc[0], qn_loc[1])
            cr.set_source_rgb(0.8, 0, 0)
            cr.show_text('?')
            cr.restore()

        # Draw any Caret-managed boxes (e.g. error messages or floating entries)
        for b in self.boxes :
            b.draw(cr)
    
    # FIXME: doesn't quite work with symbols
    def copy(self, cut=False, fmt='xml') :
        """Copy/cut the currently attached item."""

        if not self.attached_to :
            return

        item = self.attached_to

        # Get sympy, if possible
        need_sympy = False
        sy = None
        if hasattr(item, 'get_sympy') :
            sy = item.get_sympy()

        # Format by type. For those using Sympy, we must have valid Sympy
        # output. For others, if we don't, don't worry.
        if fmt == 'xml' :
            # Extract relevant XML
            debug_print(item.format_me())
            item = ET.ElementTree(item.get_xml(\
                            targets={}, top=False, full=False))
        elif fmt == 'mathml' :
            if sy is None :
                need_sympy = True
            else :
                item = printing.mathml(sy)
        elif fmt == 'python' :
            if sy is None :
                need_sympy = True
            else :
                item = printing.python(sy)
        elif fmt == 'latex' :
            item = item.to_latex()
        elif fmt == 'unicode' :
            item = item.to_string()
        elif fmt == 'text' :
            item = item.get_repr()
        else :
            raise RuntimeError('Unrecognized format')

        if need_sympy :
            raise RuntimeError("Need Sympy for this element to copy %s" % fmt)

        if cut :
            item.orphan()
            item.set_parent(None)
            self.find_left()

        return item
    
    def paste_text(self, text,
                   verbatim = False,
                   alternative = False,
                   xml = False) :
        """Convert plain text to entities. Defaults to sympify
        
        Arguments:
            verbatim - no interpretation
            alternative - tries SymPy's Mathematica parser
            xml - redirects to paste_xml
        """

        # Make sure we have somewhere to put this.
        if not self.phrased_to : return

        # This should act as if an alphanumeric key with value [text] had been
        # pressed, if verbatim.
        if xml :
            tree = ET.ElementTree(ET.XML(text))
            self.paste_xml(tree)
        elif verbatim :
            text = unicode(text)
            for t in text :
                self.insert_shape(t)
        else :
            if alternative :
                sympy_output = mathematica.mathematica(text)
            else :
                sympy_output = sympy.core.sympify(text)
            debug_print(str(sympy_output))
            if isinstance(sympy_output, str) :
                self.aes_append_status(None, "[Couldn't parse] "+sympy_output)
            else :
                self.phrased_to.append(\
                    interpret_sympy(self.main_phrase, sympy_output))
            debug_print(text)

    def paste_xml(self, xml) :
        """Paste an Entity."""

        if not self.phrased_to :
            return

        # Create phrasegroup from XML
        pg = parse_phrasegroup(self.phrased_to, xml, top=False)

        # Do the pasting
        self.phrased_to.append(pg, after=self.attached_to)

        # Find somewhere sensible to attach
        self.try_suggestion()

    def set_selected(self, entity) :
        """Sets this entity as being _the_ selected entity."""

        self.clear_selection()
        self.add_selected(entity)

    def get_selected(self, include_out_of_tree = False) :
        """Returns the selected list. Assumes you just want the ones that are
        still part of the main_phrase unless you say otherwise."""

        if include_out_of_tree :
            return self.selected
        else :
            return filter(lambda s : s.get_main_phrase() == self.main_phrase,
                          self.selected)

    def add_selected(self, entity) :
        """Identifies an additional entity as being selected."""

        if entity is None :
            return

        if entity not in self.selected :
            self.selected.append(entity)
            entity.set_selected(True)

        # Force a redraw
        self.emit('content-changed')

    def clear_selection(self) :
        """Empties the selection list."""

        for entity in self.selected :
            entity.set_selected(False)
        self.selected = []
        self.emit('content-changed')
