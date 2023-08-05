import paths
import os
import sys

def get_command() : return os.path.basename(sys.argv[0])
def get_name() : return name
def get_pkgname() : return pkgname
def get_version() : return version_name + '(' + version_number + ')'
def get_version_name() : return version_name
def get_version_number() : return version_number
def get_description() : return description

def get_details() :
    return { 
        'name' : get_name(),
             'command' : get_command(),
             'pkgname' : get_pkgname(),
             'version' : get_version(),
             'version_name' : get_version_name(),
             'description' : get_description(),
          }

def setup() :
    global name, version_name, version_number, pkgname, description

    with open(paths.get_share_location() + 'details/details') as info_file:
           name = info_file.readline().strip()
           version_name = info_file.readline().strip()
           version_number = info_file.readline().strip()
           pkgname = info_file.readline().strip()
           description = info_file.readline().strip()
    
    if paths.pkgname != pkgname :
        raise RuntimeError("Wrong package name in details or set in paths!")

setup()
