import os, sys

from distutils.core import setup
from distutils.errors import DistutilsError

from py2exe2msi import __version__ as VERSION

PACKAGE_NAME='py2exe2msi'

if sys.version_info < (2, 6):
	raise DistutilsError('this package requires Python 2.6 or later')

setup(
	name 		= PACKAGE_NAME,
	version 	= VERSION,
	description	= 'An easy way to create Windows standalone applications in Python',
	author		= 'Artem Andreev',
	author_email = 'just.wow@gmail.com',
	url			= 'http://code.google.com/p/py2exe2msi/',
	packages	= ['py2exe2msi'],
	long_description = '''py2exe2msi is an extension to distutils which creates 
	MSI packages for py2exe-compiled applications''',
	classifiers = [
		'License :: OSI Approved',
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python',
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Operating System :: Microsoft',
		'Operating System :: Microsoft :: Windows',
		'Topic :: Software Development',
		'Topic :: Software Development :: Build Tools',
		'Topic :: System',
		'Topic :: System :: Archiving',
		'Topic :: System :: Archiving :: Packaging',
		'Topic :: System :: Software Distribution'
	],
	keywords	= 'windows installer msi py2exe executable',
	requires = [
		'py2exe (>=0.6.9)'
	],
)
#
