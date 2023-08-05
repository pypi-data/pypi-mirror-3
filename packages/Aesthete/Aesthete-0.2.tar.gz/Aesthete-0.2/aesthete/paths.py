import os

#FIXME: This doesn't account for --install-lib, etc.

where_am_i = os.path.dirname(__file__)
def get_share_location() :
	return os.path.join(where_am_i, "../../../../share/aesthete") + '/'
def get_user_location() :
	return os.path.expanduser('~/.aesthete') + '/'
def get_user_home() :
	return os.path.expanduser('~') + '/'
