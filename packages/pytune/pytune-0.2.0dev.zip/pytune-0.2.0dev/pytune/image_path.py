# -*- coding:utf-8 -*-

import util
import os, sys

exe = sys.executable
if exe.endswith('vpt.exe'):
	curr_path = os.path.dirname(sys.executable)
else:
	curr_path = os.path.dirname(__file__)
	
join = os.path.join

RES = 'res'
RES_MENU = join(curr_path, RES, 'menu')
RES_TOOLBAR = join(curr_path, RES, 'toolbar')
RES_CODECTRL = join(curr_path, RES, 'codectrl')

PY_ICO = join(curr_path, RES, 'Py.ico')

class Toolbar(object):
	open = join(RES_TOOLBAR, 'document-open.png')
	save = join(RES_TOOLBAR, 'document-save.png')
	help = join(RES_TOOLBAR, 'help-browser.png')
	quit = join(RES_TOOLBAR, 'process-stop.png')
	prof = join(RES_TOOLBAR, 'utilities-system-monitor.png')
	timeit = join(RES_TOOLBAR, 'image-loading.png')
	
class Menu(object):
	open = join(RES_MENU, 'document-open.png')
	save = join(RES_MENU, 'document-save.png')
	help = join(RES_MENU, 'help-browser.png')
	quit = join(RES_MENU, 'process-stop.png')
	prof = join(RES_MENU, 'utilities-system-monitor.png')
	timeit = join(RES_MENU, 'image-loading.png')
	
class Codectrl(object):
	new = join(RES_CODECTRL, 'document-new.png')
	open = join(RES_CODECTRL, 'document-open.png')
	save = join(RES_CODECTRL, 'document-save.png')
	saveas = join(RES_CODECTRL, 'document-save-as.png')
	copy = join(RES_CODECTRL, 'edit-copy.png')
	cut = join(RES_CODECTRL, 'edit-cut.png')
	find = join(RES_CODECTRL, 'edit-find.png')
	replace = join(RES_CODECTRL, 'edit-find-replace.png')
	paste = join(RES_CODECTRL, 'edit-paste.png')
	redo = join(RES_CODECTRL, 'edit-redo.png')
	undo = join(RES_CODECTRL, 'edit-undo.png')
	run = join(RES_CODECTRL, 'media-playback-start.png')
	tabnew = join(RES_CODECTRL, 'tab-new.png')
	windownew = join(RES_CODECTRL, 'window-new.png')