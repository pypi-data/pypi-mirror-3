# -*- coding: utf-8 -*-

from distutils.core import setup
from glob import glob
from about import *

setup(name= name,
	  version=ver,
	  author = author, 
	  author_email = author_email, 
	  url = url, 
	  package_dir={'VisualPyTune': '.'},
	  data_files = [ \
		('option', ['option/ui.cfg']), \
		('', glob('*.py')), \
	  	('codectrl', glob('codectrl/*.py')), \
		('', ['licence']), \
		('res', ['res/Py.ico']), \
		('res/codectrl', glob('res/codectrl/*.png')), \
		('res/menu', glob('res/menu/*.png')), \
		('res/toolbar', glob('res/toolbar/*.png'))
	  	]
	  )
