# -*- coding: utf-8 -*-

from glob import glob
from distutils.core import setup
import py2exe

from about import name, ver

setup(windows=["vpt.py", {'script':'vpt.py','icon_resources':[(1, 'res/Py.ico')]}], \
	options = {'py2exe':{'optimize':2}}, \
	name = name, \
	version = ver, \
	data_files = [('option', ['option/ui.cfg']), \
#		('', ['msvcp71.dll', 'gdiplus.dll']), \
		('', glob('*.dll')),
		('', glob('*.manifest')),
		('', ['licence']), \
		('res', ['res/Py.ico']), \
		('res/codectrl', glob('res/codectrl/*.png')), \
		('res/menu', glob('res/menu/*.png')), \
		('res/toolbar', glob('res/toolbar/*.png'))]
	)
