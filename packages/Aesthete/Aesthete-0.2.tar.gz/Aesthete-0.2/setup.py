import os, sys, imp

# We must have pangocairo for dependency checking. Abort if we don't have it
try :
	import pangocairo
except ImportError:
	sys.exit('The pangocairo module, required to build aesthete, is not present. Aborting build.')

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

# Thanks to pygtktree for version inspiration
try :
	with open('details') as info_file:
		name = info_file.readline().strip()
		version_name = info_file.readline().strip()
		version_number = info_file.readline().strip()
		description = info_file.readline().strip()
except IOError :
	sys.exit('Could not open version file')

help_files = map(lambda e : 'help/'+e, os.listdir('./help'))
defs_files = map(lambda e : 'defs/'+e, os.listdir('./defs'))
image_dirs = map(lambda e : 'images/'+e, os.listdir('./images'))
image_dirs.remove('images/icons')
icon_dirs = map(lambda e : 'images/icons/'+e, os.listdir('./images/icons'))

def list_from_dirs(image_dirs) :
    return [('share/aesthete/'+image_dir,
               map(lambda e : image_dir+'/'+e,
                os.listdir('./'+image_dir)))
              for image_dir in image_dirs]

image_list = list_from_dirs(image_dirs)
icon_list = list_from_dirs(icon_dirs)

# Check python dependencies, bail if not present
package_deps = [['numpy', '1.4.1'], ['scipy', '0.7.2'], ['sympy', '0.6.7'], ['cairo', '1.8.8'], ['gobject', '2.21.5'], ['gtk', '2.17.0'], \
			['Image', '1.1.7'], ['matplotlib', '1.0.1'], ['IPython', '0.10']]
for package_dep in package_deps :
	try :
		imp.find_module(package_dep[0])	
	except ImportError :
		sys.exit(package_dep[0] + ' ' + package_dep[1] + ' or higher is required to use aesthete. Aborting build.')

# Check font dependencies (uses pangocairo)
# (partially lifted from http://cairographics.org/pycairo_pango/)
font_map = pangocairo.cairo_font_map_get_default()
family_names = [f.get_name() for f in   font_map.list_families()]

linux_libertine_fonts_found = False
for font_name in family_names :
	if font_name.startswith('Linux Libertine') :
		linux_libertine_fonts_found = True
		break
if not linux_libertine_fonts_found :
	sys.exit('The Linux Libertine Font package is required to use aesthete. Aborting build.')

setup(name=name,\
      version=version_number,\
      description=description,\
      author='Phil Weir',\
      author_email='pweir@maths.otago.ac.nz',\
      url='http://www.philtweir.co.uk/aesthete',\
      packages=['aesthete', 'aesthete.glypher', 'aesthete.glancer',
                'aesthete.gluer', 'aesthete.sources', 'aesthete.test'],\
      license='LICENSE.txt',
      long_description=open('README.txt').read(),
      scripts=['bin/aesthete_ime.py'],\
      data_files=[('share/aesthete/unicode', ['unicode/cm.ucd', 'unicode/interpretations.ucd', 'unicode/combinations.ucd']),\
		  ('share/aesthete', ['preferences.default.xml','shortcuts.default.xml']),\
		  ('share/aesthete/defs', defs_files),\
		  ('share/aesthete/details', ['details']),\
		  ('share/aesthete/help', help_files)]+image_list+icon_list, \
	  requires=[
          'numpy (>=1.4.1)',
          'scipy (>=0.7.2)',
          'sympy (>=0.6.7)',
          'cairo (>=1.8.8)',
          'gobject (>=2.21.5)',
          'gtk (>=2.17.0)',
          'Image (>=1.1.7)',
          'matplotlib (>=1.0.1)',
          'IPython (>=0.10)'
      ]
     )
