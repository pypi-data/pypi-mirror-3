import os
import utils

#FIXME: This doesn't account for --install-lib, etc.

pkgname = ""
where_am_i = os.path.dirname(__file__)
def get_share_location() :
    return os.path.join(where_am_i, "../../../../share/%s" % pkgname) + '/'
def get_user_location() :
    return os.path.expanduser('~/.%s' % pkgname) + '/'
def get_user_home() :
    return os.path.expanduser('~') + '/'
def setup(pkgname_new) :
    global pkgname
    pkgname = pkgname_new
    try_make_subdir('')

def try_make_subdir(subdir) :
    loc = get_user_location() + subdir

    if os.path.exists(loc) :
        return

    try :
        os.mkdir(loc)
    except OSError as e:
        utils.debug_print(str(e))
