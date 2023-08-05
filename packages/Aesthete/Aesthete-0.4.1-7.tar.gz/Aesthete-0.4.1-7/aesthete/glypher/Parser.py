import os
import string
from aobject.paths import *
import glypher as g
import gtk

from Spacer import *
import Mirror
import Dynamic
import Function
import Word
import Symbol
from glypher import \
    GLYPHER_PG_LEAD_ALL, \
    GLYPHER_PG_LEAD_VERT, \
    GLYPHER_PG_LEAD_HORI

import lxml.etree as ET

GLYPHER_IS_PG = 1
GLYPHER_IS_ENTITY = 2

phrasegroups = g.phrasegroups
entities = {\
    'space' : GlypherSpace,
    'phrase' : GlypherPhrase,
    'horizontal_line' : GlypherHorizontalLine,
    'vertical_line' : GlypherVerticalLine,
    'symbol' : Symbol.GlypherSymbol,
    'word' : Word.GlypherWord,
    }
phrasegroup_trees = {}
user_phrasegroup_trees = {}
formula_trees = {}
latex_to_name = {}
latex_to_shape = {}

shortcuts = {}
shortcuts_saved = {}
content_mathml_operations = {}
binary_expression_names = {}
binary_expression_properties_for_symbol = {}

def load_shortcuts(shortcut_file) :
    if not os.path.exists(shortcut_file) :
        return False
    tree = ET.parse(shortcut_file)
    for node in tree.getroot() :
        p = gtk.accelerator_parse(node.get('shortcut'))
        keyname = gtk.gdk.keyval_name(p[0]).lower()
        shortcut = (keyname,
                    bool(p[1] & gtk.gdk.CONTROL_MASK),
                    bool(p[1] & gtk.gdk.SHIFT_MASK),
                    bool(p[1] & gtk.gdk.MOD1_MASK),
                    bool(p[1] & gtk.gdk.SUPER_MASK))
        shortcuts[shortcut] = node.get('phrasegroup')
    return True
def is_named(name) :
    if name in phrasegroup_trees or\
       name in user_phrasegroup_trees or\
       name in phrasegroups :
           return GLYPHER_IS_PG
    elif name in entities or name in Word.constants or name in Word.units :
        return GLYPHER_IS_ENTITY
    return False

def get_name_from_latex (latex) :
    '''Find a registered name from a LaTeX-style shortcut.'''

    if latex in latex_to_name :
        return latex_to_name[latex]

def get_shape_from_latex (latex) :
    '''Find a registered shape from a LaTeX-style shortcut.'''

    if latex in latex_to_shape :
        return latex_to_shape[latex]

    return None

def make_val(value, ty) :
    return (value=='True') if ty == 'bool' else \
         int(value) if ty == 'int' else \
         float(value) if ty == 'float' else \
         value

def add_formula_tree(name, tree) :
    formula_trees[name] = tree

def make_formula(parent, name) :
    root = formula_trees[name].getroot()
    content = root.find('content')[0]
    content = ET.ElementTree(content)
    pg = parse_phrasegroup(parent, content, top=False)

    do_info_parsing(pg, root, top=True)
    return pg

def add_phrasegroup_tree(name, tree, user=True, latex=None, shortcut=True) :
    '''
    Adds a PG XML tree to the list, for building and inserting on the fly.

    Arguments :
        tree - the XML tree
        user - whether or not this should be included as a userdir tree (default
               True)
        latex - LaTeX-style shortcut (e.g. \\frac)
        shortcut - whether to store a keyboard shortcut, if found (default
                   True). Also affects MathML operation storage.

    '''

    # Make sure the name and type are correct
    tree.getroot().tag = name
    #tree.getroot().set('type', name)

    # Add to the appropriate dictionary
    (user_phrasegroup_trees if user else phrasegroup_trees)[name] = tree

    # Add LaTeX-style shortcut
    if latex is not None :
        latex_to_name[latex] = name

    # If this is a binary expression, note it for Caret
    if tree.getroot().get('type') == 'binary_expression' :
        root = tree.getroot()
        op = root.get('operator')
        binary_expression_names[name] = op
        sympy_code = root.find('sympy')
        binary_expression_properties_for_symbol[op] = {
            'sympy' : compile(sympy_code.text.strip(), '<string>', 'eval'),
            'variable_ops' : root.get('variable_ops') == 'True',
            'name' : name,
            'gravity' : root.get('gravity') == 'Up',
                                                      }

    if shortcut :
        # Add keyboard shortcut
        sc = tree.getroot().find('shortcut')
        if sc is not None :
            p = gtk.accelerator_parse(sc.text)
            keyname = gtk.gdk.keyval_name(p[0]).lower()
            shortcut = (keyname,
                        bool(p[1] & gtk.gdk.CONTROL_MASK),
                        bool(p[1] & gtk.gdk.SHIFT_MASK),
                        bool(p[1] & gtk.gdk.MOD1_MASK),
                        bool(p[1] & gtk.gdk.SUPER_MASK))
            shortcuts[shortcut] = name

        # Try for Content MathML
        op = tree.getroot().get('mathml')
        if op is not None :
            content_mathml_operations[op] = name

    alternatives_cat = tree.getroot().find('alternatives')
    if alternatives_cat is not None :
        if alternatives_cat.text not in g.phrasegroup_alternatives :
            g.phrasegroup_alternatives[alternatives_cat.text] = []
        g.phrasegroup_alternatives[alternatives_cat.text].append(name)

def try_key_press(event) :
    '''Checks whether a given keyname/state pair is allocated to a named
    entity.'''

    keyname = gtk.gdk.keyval_name(event.keyval).lower()
    shortcut = (keyname,
                bool(event.state & gtk.gdk.CONTROL_MASK),
                bool(event.state & gtk.gdk.SHIFT_MASK),
                bool(event.state & gtk.gdk.MOD1_MASK),
                bool(event.state & gtk.gdk.SUPER_MASK))


    if shortcut in shortcuts_saved :
        return shortcuts_saved[shortcut]
    if shortcut in shortcuts :
        return shortcuts[shortcut]

    return None

def make_phrasegroup(parent, name, operands=None, properties=None, args=None) :
    if name in entities :
        pg = entities[name](parent)
    elif name in Word.constants :
    	pg = Word.constants[name](parent)
    elif name in Word.units :
    	pg = Word.units[name](parent)
    else :
        if name in phrasegroup_trees :
            pg = parse_phrasegroup(parent, phrasegroup_trees[name], operands,
                                   args=args)
        elif name in user_phrasegroup_trees :
            pg = parse_phrasegroup(parent, user_phrasegroup_trees[name],
                                   operands, args=args)
        elif name in phrasegroups :
            if args is not None :
                pg = phrasegroups[name](parent, **args)
            else :
                pg = phrasegroups[name](parent)
        else :
            raise(RuntimeError('Required XML PhraseGroup not loaded! '+name))

        if operands is not None and pg.am('phrasegroup') :
            missing_left = True
            missing_right = True
            if pg.lhs_target is not None and len(operands) > 0 and operands[0] is not None :
                operands[0].orphan()
                pg.set_lhs(operands[0])
                missing_left = False
            if pg.rhs_target is not None and len(operands) > 1 and operands[1] is not None :
                operands[1].orphan()
                pg.set_rhs(operands[1])
                missing_right = False

            if missing_left and pg.lhs_target is not None :
                pg.set_recommending(pg[pg.lhs_target])
            elif missing_right and pg.rhs_target is not None :
                pg.set_recommending(pg[pg.rhs_target])

    if properties is not None :
        for p in properties : pg.set_p(p, properties[p])

    #debug_print(pg.format_me())
    #debug_print(pg.format_entities())
    #if len(pg.entities) > 0 :
    #    debug_print(pg.get_entities()[0].format_entities())
    return pg

def make_phrasegroup_by_filename(parent, filename, operands = None, properties = None) :
    tree = ET.parse(filename)
    pg = parse_phrasegroup(parent, tree, operands)
    if properties is not None :
        for p in properties : pg.set_p(p, properties[p])
    return pg

#def parse_phrasegroups() :
#    defs_files = os.listdir(get_share_location() + 'defs')
#    with open(get_share_location() + "defs/order.txt") as order :
#        lines = order.readlines()
#        for line in lines :
#            filename = get_share_location() + "defs/" + line.strip() + ".xml"
#            tree = ET.parse(filename)
#            add_phrasegroup_tree(tree.getroot().tag.lower(), tree, user=False, latex=tree.getroot().get('latex_name'))
#    for line in defs_files :
#        line = line.strip()
#        if line[-3:] != "xml" : continue
#        filename = get_share_location() + "defs/" + line
#        try :
#            tree = ET.parse(filename)
#        except ET.XMLSyntaxError as e :
#            debug_print("Couldn't parse : "+str(filename) + " : " + str(e))
#            continue
#        name = tree.getroot().tag.lower()
#        if name in phrasegroup_trees : continue
#        add_phrasegroup_tree(name, tree, user=False, latex=tree.getroot().get('latex_name'))

def parse_phrasegroup(parent, tree, ops = None, top = True, args=None) :
    root = tree.getroot()

    ty = root.get('type')

    operands = None
    recommending = None

    if root.tag == 'main_phrase' or (ty is not None and ty == 'main_phrase') :
        ents = root.find('entities')
        if ents is None or len(ents) != 1 :
            return None
        root = ents[0]

    names = {}
    targets = {}
    operands = {}
    recommending = []
    lead = []
    add_entities = {}
    new_phrasegroup = parse_element(parent, root, names, targets, operands,
                                    recommending, lead, add_entities, top=top,
                                    args=args)
    for name in add_entities :
        pairs = add_entities[name]
        for pg, prop in pairs :
            pg.set_p(prop, names[name])
    for t in targets :
        new_phrasegroup.add_target(targets[t], t)
    if len(lead) > 0 :
        alt = lead[len(lead)-1][1]
        new_phrasegroup.set_lead(lead[len(lead)-1][0], GLYPHER_PG_LEAD_BOTH if alt=='a' else\
                                   GLYPHER_PG_LEAD_HORI if alt=='h' else\
                                   GLYPHER_PG_LEAD_VERT)
    if top and new_phrasegroup.am('phrasegroup') :
        new_phrasegroup.mes.append(root.tag)
        new_phrasegroup.set_default_entity_xml()

    if operands is None :
        operands = {}
        n = 0
        if new_phrasegroup.lhs_target is not None :
            operands[n] = new_phrasegroup[new_phrasegroup.lhs_target]
            n += 1
        if new_phrasegroup.rhs_target is not None :
            operands[n] = new_phrasegroup[new_phrasegroup.rhs_target]
            n += 1

    if recommending is None :
        recommending = [new_phrasegroup.get_recommending()]

    if ops is not None :
     for o in operands :
        n = int(o)
        if len(ops) > n and ops[n] is not None :
            ops[n].orphan()
            operands[o].adopt(ops[n])
    if len(recommending) > 0 :
        new_phrasegroup.set_recommending(recommending[len(recommending)-1])
    return new_phrasegroup

def parse_element(parent, root, names, targets, operands, recommending, lead,
                  add_entities, am = None, top = True, args=None) :
    new_phrasegroup = am
    if new_phrasegroup is None :
        tag = root.tag.lower()
        ty = root.get('type')
        #if ty is not None :
        #    ty = ty.lower()

        default_args = {}
        num_ops = root.get('num_ops')
        if num_ops is not None :
            default_args = {'num_ops' : int(num_ops) }
        if len(default_args) == 0 :
            default_args = None

        if args is not None :
            default_args.update(args)
        args = default_args

        if ty in g.parse_element_fns :
            new_phrasegroup = g.parse_element_fns[root.get('type')](new_phrasegroup,
                                                               root, names, targets, operands,
                                recommending, lead, add_entities, top=False,
                                                                    args=args)
        elif tag == 'word' or ty == 'word' :
            new_phrasegroup = Word.GlypherWord(parent)
        elif tag == 'phrase' or ty == 'phrase' :
            new_phrasegroup = GlypherPhrase(parent)
        elif tag == 'script' or ty == 'script' :
            available = [(site_av=='True') for site_av in \
                          root.get('available').split(",")]
            new_phrasegroup = g.phrasegroups['script'](parent, available=available)
        elif tag == 'space' or ty == 'space' :
            dims = (float(root.get('width')), float(root.get('height')))
            new_phrasegroup = GlypherSpace(parent, dims=dims)
        elif tag == 'verticalspacer' or ty == 'verticalspacer' :
            tied_to = names[root.get('tied_to')]
            scaling = float(root.get('scaling'))
            sutract_other_children = root.get('subtract_other_children') =='True'
            new_phrasegroup = GlypherVerticalSpacer(parent, tied_to=tied_to,
                                                    scaling=scaling,
                                                    subtract_other_children=True)
        elif tag == 'mirror' or ty == 'mirror' :
            tied_to = names[root.get('tied_to')]
            new_phrasegroup = Mirror.make_mirror(parent, tied_to)
        else :
            if ty == 'phrase' :
                new_phrasegroup = GlypherPhrase(parent)
            elif ty in Word.constants :
                new_phrasegroup = Word.constants[ty](parent)
            elif ty in Word.units :
                new_phrasegroup = Word.units[ty](parent)
            elif ty in entities :
                new_phrasegroup = entities[ty](parent)
            elif ty in user_phrasegroup_trees :
                new_phrasegroup = make_phrasegroup(parent, ty, args=args)
            elif ty in phrasegroups and ty != 'phrasegroup':
                if args is not None :
                    new_phrasegroup = phrasegroups[ty](parent, **args)
                else :
                    new_phrasegroup = phrasegroups[ty](parent)
            elif top or ty == 'phrasegroup' or ty is None :
                new_phrasegroup = make_phrasegroup(parent, 'phrasegroup', args=args)
                if root.get('lhs') is not None :
                    new_phrasegroup.lhs_target = root.get('lhs')
                if root.get('rhs') is not None :
                    new_phrasegroup.rhs_target = root.get('rhs')
            elif ty in phrasegroup_trees :
                new_phrasegroup = make_phrasegroup(parent, ty, args=args)
            else :
                raise(RuntimeError("Couldn't find a class of type "+str(ty)+" for "+str(tag)))

        if ty is not None :
            new_phrasegroup.set_name(tag)
        if root.get('name') is not None : new_phrasegroup.set_name(root.get('name'))
        if new_phrasegroup.get_name() is not None : names[new_phrasegroup.get_name()] = new_phrasegroup
    
    els = root.find("entities")
    if els is not None :
     for e in els :
         pg_els = filter(lambda pe : pe.get_name() == e.tag,
                         new_phrasegroup.entities)
         if len(pg_els) > 0 :
             el = pg_els[0]
         else :
             el = parse_element(new_phrasegroup, e, names, targets, operands,
                                recommending, lead, add_entities, top=False)
         if e.get('recommending') == 'True' : recommending.append(el)
         if e.get('target') is not None :
             targets[e.get('target')] = el
             el.name = e.get('target')
         if e.get('operand') is not None : operands[e.get('operand')] = el
         if e.get('size_scaling') is not None : el.set_size_scaling(float(e.get('size_scaling')))
         if e.get('lead') is not None :
             lead.append((el, e.get('lead')))
         row = int(e.get('row')) if e.get('row') is not None else 0
         col = int(e.get('col')) if e.get('col') is not None else 0
         el.recalc_bbox()
         if el not in pg_els :
             new_phrasegroup.append(el, row=row, col=col)
         if e.get('padding') is not None :
             p = string.split(e.get('padding'), ' ')
             for i in range(0,4) :
                 el.set_padding(i, float(p[i]))

         if hasattr(el, 'after_append') :
             for a in el.after_append : a()
    
    tgts = root.find("targets")
    if tgts is not None :
     for t in tgts :
        name = t.get('name')
        phr = targets[name] if top else new_phrasegroup.get_target(name)
        parse_element(new_phrasegroup, t, names, targets, operands,
                      recommending, lead, add_entities, am=phr, top=False)
    
    props = root.find("properties")
    if props is not None:
     for p in props :
         name = p.get('name')
         value = p.get('value')
         ty = p.get('type')
         if ty == 'tuple' :
          entries = p.findall('ti')
          tup = []
          for e in entries :
              tup.append(make_val(e.get('value'), e.get('type')))
          val = tuple(tup)
         else :
          val = make_val(value, ty)
          if ty == 'entity' :
              if value not in add_entities :
                  add_entities[val] = []
              add_entities[val].append((new_phrasegroup, name))
              # We don't want to set this just yet.
              continue
         new_phrasegroup.set_p(name, val)
    
    props = root.find("inherited_properties_overrides")
    if props is not None :
     for p in props :
         name = p.get('name')
         value = p.get('value')
         ty = p.get('type')
         if ty == 'tuple' :
          entries = p.findall('ti')
          tup = []
          for e in entries : tup.append(make_val(e.get('value'), e.get('type')))
          val = tuple(tup)
         else :
          val = make_val(value, ty)
         new_phrasegroup.set_ip(name, val)
    
    scaling = root.get('scaling')
    if scaling is not None : new_phrasegroup.set_size_scaling(float(scaling))
    
    acts = root.find('actions')
    new_phrasegroup.after_append = []
    if acts is not None :
     for a in acts :
         if a.tag == 'translate' :
            new_phrasegroup.after_append.append(lambda :\
            new_phrasegroup.translate(float(a.get('h'))*new_phrasegroup.get_scaled_font_size(),\
                          float(a.get('v'))*new_phrasegroup.get_scaled_font_size(), quiet=True))
    
    rows = root.find('rows')
    if rows is not None :
     for r in rows :
         n = int(r.get('id'))
         if r.get('offset') is not None : new_phrasegroup.row_offsets[n] = float(r.get('offset')); new_phrasegroup.recalc_bbox()
         if r.get('align') is not None : new_phrasegroup.set_row_align(n, r.get('align'))
    
    sympy_code = root.find("sympy")
    #FIXME: it strikes me that this isn't very safe
    if sympy_code is not None and new_phrasegroup.get_sympy_code is None : 
        new_phrasegroup.get_sympy_code = compile(sympy_code.text.strip(), '<string>', 'eval')

    do_info_parsing(new_phrasegroup, root, top=top)

    return new_phrasegroup

def do_info_parsing(new_phrasegroup, root, top=False) :
    string_code = root.find("string")
    #FIXME: it strikes me that this isn't very safe
    if string_code is not None : 
        new_phrasegroup.to_string_code = compile(string_code.text.strip(), '<string>', 'eval')
    latex_code = root.find("latex")
    #FIXME: it strikes me that this isn't very safe
    if latex_code is not None : 
        new_phrasegroup.to_latex_code = compile(latex_code.text.strip(), '<string>', 'eval')
    info_text = root.find("info")
    if info_text is not None :
        if top :
            new_phrasegroup.indicate_info = True
        new_phrasegroup.set_info_text(info_text.text.strip())
    title_text = root.get("title")
    if title_text is not None :
        new_phrasegroup.set_title(title_text)
    wiki_link = root.find("wiki")
    if wiki_link is not None :
        new_phrasegroup.set_wiki_link(wiki_link.text.strip())

    alternatives_cat = root.find("alternatives")
    if alternatives_cat is not None :
        new_phrasegroup.alternatives_cat = alternatives_cat.text
