import os
import sys
import utils

pkgname = None
where_am_i = os.path.dirname(__file__)

share_loc = None

#FIXME: This doesn't account for --install-lib, etc.
def _set_share_loc() :
    global share_loc

    share_loc = os.path.join(where_am_i, "../../../../share/", pkgname) + '/'

    egg_share_loc = os.path.join(where_am_i, "../share/", pkgname) + '/'
    if not os.path.exists(share_loc) and os.path.exists(egg_share_loc) :
        share_loc = egg_share_loc

    sys_share_loc = os.path.join(sys.prefix, "share/", pkgname) + '/'
    if not os.path.exists(share_loc) and os.path.exists(sys_share_loc) :
        share_loc = sys_share_loc

def get_share_location() :
    if pkgname is None :
        raise RuntimeError(\
        'AObject has not been setup : have you called paths.setup(PKGNAME)?')
    return share_loc

def get_user_location() :
    if pkgname is None :
        raise RuntimeError(\
        'AObject has not been setup : have you called paths.setup(PKGNAME)?')
    return os.path.expanduser('~/.%s' % pkgname) + '/'

def get_user_home() :
    return os.path.expanduser('~') + '/'

def setup(pkgname_new) :
    global pkgname
    pkgname = pkgname_new
    _set_share_loc()
    try_make_subdir('')

def try_make_subdir(subdir) :
    loc = get_user_location() + subdir

    if os.path.exists(loc) :
        return

    try :
        os.mkdir(loc)
    except OSError as e:
        utils.debug_print(str(e))
