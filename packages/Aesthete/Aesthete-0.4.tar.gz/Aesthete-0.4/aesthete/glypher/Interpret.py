from ..utils import debug_print
import PhraseGroup
import Dynamic
from Word import *
import Commands as C
import glypher as g
import InterpretBackend

from sympy.series.order import Order
from sympy.printing.mathml import mathml
from sympy.utilities.mathml import c2p

try :
    import sympy
    have_sympy = True
except ImportError :
    have_sympy = False

def parse_command(caret, command, *args) :
    '''Take a command as string and a series of Glypher arguments and try to
    turn it into an executable sympy function (and arguments).'''

    # Try the specifically defined functions
    if command in g.commands :
        return g.commands[command](caret, *args)
    # Try the specifically picked out sympy functions
    elif command in g.operation_commands :
        return C.operation_command(g.operation_commands[command], caret, *args)

    # See if there's a standard function
    func = Dynamic.get_sympy_function(command.lower())
    if func is not None :
        return C.operation_command(func, caret, *args)

    # See if there's a loaded library function
    func = Dynamic.get_library_function(command.lower())
    if func is not None :
        return C.operation_command(func, caret, *args)

    # Give up
    return None
    #return "Command not found (are all the necessary dynamic libraries loaded?)"

def parse_space_array(space_array, caret) :
    args = space_array.get_args()
    if space_array.get_op_count() == 1 :
        if len(args) == 0 :
            return (None,None)
        return (args[0], interpret_sympy(None, args[0].get_sympy()))
    elif space_array.get_op_count() == 3 and args[1].to_string() == 'at' :
        args = C.get_arg_innards(args)
        if isinstance(args, str) :
            debug_print(args)
            return (None, None)
        debug_print(args[0])
        subs = C.do_substitutions_from_list(args[0], args[2])
        if isinstance(subs, str) :
            debug_print(subs)
            return (None, None)
        return (space_array, interpret_sympy(None, subs))
    else :
        command = args[0]
        if not command.am('word') : return "Expected first token to be command"

        response = parse_command(caret, command.to_string(), *args[1:])

        if response is None :
            debug_print(space_array['pos0'].IN())
            raise PhraseGroup.GlypherTargetPhraseError(space_array['pos0'].IN(),
                "Command not found (are all the necessary dynamic libraries loaded?)")
        return (space_array, response)

def interpret_sympy(parent, result) :
    """Return a GlypherEntity representation of a sympy object. If possible,
    this is rendered via MathML, but as not all sympy objects successfully
    output MathML, we have a fall-back option to direct parsing."""

    return InterpretBackend._generic_to_entity(parent, result)
    if not have_sympy : return

    # Check whether this is a dictionary before going on; sympify can't handle
    # dictionaries itself.
    if isinstance(result, dict) :
        try :
            d = dict()
            for a in result.keys() :
                tree_key = mathml(a)
                tree_val = mathml(result[a])
                d[tree_key] = tree_val
        except TypeError :
            debug_print("""
                        Resorted to old-style sympy->glypher rendering, as
                        some sympy object not available in MathML.
                        """)
            return InterpretBackend._sympy_to_entity(parent, result)
        else :
            return interpret_mathml(parent, d)

    try :
        content = mathml(result)
    except TypeError :
        debug_print("""
                    Resorted to old-style sympy->glypher rendering, as
                    some sympy object not available in MathML.
                    """)
        return InterpretBackend._sympy_to_entity(parent, result)
    else :
        return interpret_mathml(parent, content)

def interpret_mathml(parent, content) :
    processor = InterpretBackend._mathml_to_entity

    if isinstance(content, dict) :
        d = dict()
        for a in content.keys() :
            tree_key = ET.fromstring(a)
            tree_val = ET.fromstring(content[a])
            d[tree_key] = tree_val
        return processor(parent, d)

    debug_print(content)

    #FIXME: dirty hack to ensure mml namespace has been declared.
    # We should be getting Content MathML, so this is technically wrong, but the
    # passed XML from sympy may contain Presentation MathML elements under the
    # mml namespace
    #content = "".join(("<math xmlns:mml='http://www.w3.org/1998/Math/MathML'>\n",
    #                   content,
    #                   "</math>"))
    content = sympy.utilities.mathml.add_mathml_headers(content)

    tree = ET.fromstring(content)
    return processor(parent, tree)
