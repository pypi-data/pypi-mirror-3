import os, sys, imp
import subprocess
from distutils.command.install_data import install_data
import glob

# Couple of tips from terminator

# We must have pangocairo for dependency checking. Abort if we don't have it
try :
	import pangocairo
except ImportError:
	sys.exit('The pangocairo module, required to build aesthete, is not present. Aborting build.')

from setuptools import setup
from distutils.command.install import INSTALL_SCHEMES

# Thanks to pygtktree for version inspiration
try :
	with open('details') as info_file:
		name = info_file.readline().strip()
		version_name = info_file.readline().strip()
		version_number = info_file.readline().strip()
                command = info_file.readline().strip()
		description = info_file.readline().strip()
except IOError :
	sys.exit('Could not open version file')

# Thanks to terminator (Chris Jones)
class InstallData(install_data):
  def run (self):
    install_data.run (self)
    try:
        subprocess.call(["gtk-update-icon-cache", "-q", "-f", "-t", os.path.join(self.install_dir, "share/icons/hicolor")])
    except :
        pass

help_files = map(lambda e : 'share/help/'+e, os.listdir('./share/help'))
defs_files = map(lambda e : 'share/defs/'+e, os.listdir('./share/defs'))
formulae_files = map(lambda e : 'share/formulae/'+e, os.listdir('./share/formulae'))

def do_share_walk(subdir) :
    toppath = 'share/%s' % subdir
    share_list = []
    for dirpath, dirnames, filenames in os.walk(toppath) :
        relpath = dirpath[len(toppath)+1:]
        if len(filenames) > 0 :
            share_list.append(('share/aesthete/'+subdir+'/'+relpath,map(lambda f: os.path.join(dirpath,f),filenames)))
    return share_list
image_list = do_share_walk('images')
template_list = do_share_walk('templates')
help_list = do_share_walk('help')
unicode_list = do_share_walk('unicode')

# Check python dependencies, bail if not present
non_pypi_package_deps = [
                ['rsvg','2.30.0'],
                ['pygtk', '2.17'],
]
for package_dep in non_pypi_package_deps :
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

#setup(name='aobject',\
#      version=version_number,\
#      description=description,\
#      author='Phil Weir',\
#      author_email='pweir@maths.otago.ac.nz',\
#      url='http://www.philtweir.co.uk/aesthete',\
#      packages=['aobject'],\
#      license='LICENSE.txt',
#      long_description=open('README.txt').read(),
#      requires=[
#      ],
#      cmdclass={'install_data':InstallData}
#     )

setup(name=name,\
      version=version_number,\
      description=description,\
      author='Phil Weir',\
      author_email='pweir@maths.otago.ac.nz',\
      url='http://www.philtweir.co.uk/aesthete',\
      packages=['aesthete', 'aesthete.glypher', 'aesthete.glancer',
                'aesthete.gluer', 'aesthete.sources', 
                'aesthete.glosser', 'aesthete.third_party', 'aobject'],\
      license='LICENSE.txt',
      classifiers = [
          "Programming Language :: Python",
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: X11 Applications",
          "Environment :: X11 Applications :: GTK",
          "Intended Audience :: Science/Research",
          "Intended Audience :: Education",
          "Topic :: Scientific/Engineering :: Mathematics",
      ],
      long_description=open('README.txt').read(),
      scripts=['bin/aesthete_ime'],\
      data_files=[
          ('share/applications', glob.glob('share/aesthete.desktop')),
          ('share/icons/hicolor/scalable/apps/', glob.glob('share/icons/scalable/apps/*.svg')),
		  ('share/aesthete', ['share/preferences.default.xml',
                              'share/shortcuts.default.xml']),\
		  ('share/aesthete/defs', defs_files),\
		  ('share/aesthete/formulae', formulae_files),\
		  ('share/aesthete/details', ['details'])]+\
          image_list+template_list+help_list+unicode_list,
      install_requires=[
          'numpy>=1.4.1',
          'scipy>=0.7.2',
          'sympy>=0.7.1',
          'PIL>=1.1.7',
          'matplotlib>=1.0.1',
          'IPython>=0.10',
          'argparse>=1.1',
          'lxml>=2.3',
      ],
      #install_requires+=['pygtk>=2.17.0',
      #'pycairo>=1.8.8',
      cmdclass={'install_data':InstallData}
     )
