import paths

with open(paths.get_share_location() + 'details/details') as info_file:
       name = info_file.readline().strip()
       version_name = info_file.readline().strip()
       version_number = info_file.readline().strip()
       description = info_file.readline().strip()

def get_command() : return 'aesthete_ime.py'
def get_name() : return name
def get_version() : return version_name + '(' + version_number + ')'
def get_version_name() : return version_name
def get_version_number() : return version_number
def get_description() : return description
