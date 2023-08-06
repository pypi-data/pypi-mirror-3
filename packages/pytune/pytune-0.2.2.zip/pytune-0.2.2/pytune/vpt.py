# -*- coding:utf-8 -*-

import wx
import profile
import ui
from about import name, ver
#from . import __version__
#ver = __version__

def try_psyco():
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass


def main():
	try_psyco()
	app = wx.PySimpleApp()
	frame = ui.createUI(None, wx.ID_ANY, name + ' ' + ver)
#	frame = ui.createUI(None, wx.ID_ANY, name)
	app.MainLoop()
	
if __name__ == '__main__':
	main()
