# -*- coding:utf-8 -*-

import wx

from listctrl import LoadedListCtrl
from uicfg import UIConfig

def Notebook(parent, *a, **k):
	obj = wx.Notebook(parent, *a, **k)
	
	parent.dirctrl = wx.GenericDirCtrl(obj, \
						wx.ID_ANY, \
						dir=UIConfig.inst().getLastDir(), \
						style = wx.BORDER_NONE)
						
	parent.statsctrl = LoadedListCtrl(obj, wx.ID_ANY, \
			style = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER)

	obj.AddPage(parent.dirctrl, 'Files')
	obj.AddPage(parent.statsctrl, 'loaded pf')
	
	
	def OnDirctrlContextMenu(evt):
		def OnRefresh(evt):
			path = parent.dirctrl.GetPath()
			parent.dirctrl.ReCreateTree()
			parent.dirctrl.SetPath(path)

		menu = wx.Menu()
		menu.AppendSeparator()
		ID_REFRESH = wx.NewId()
		item_refresh = wx.MenuItem(menu, ID_REFRESH, 'Refresh')
		obj.Bind(wx.EVT_MENU, OnRefresh, id = ID_REFRESH)
		menu.AppendItem(item_refresh)
		
		parent.dirctrl.PopupMenu(menu)
		menu.Destroy()
		
	parent.dirctrl.Bind(wx.EVT_CONTEXT_MENU, OnDirctrlContextMenu)
	
	return obj
	
def Panel(parent, *a, **k):

	obj = wx.Panel(parent, wx.ID_ANY, *a, **k)
	# create sizer for panel
	box = wx.BoxSizer(wx.VERTICAL)
	obj.SetSizer(box)
	
	obj.notebook = Notebook(obj, wx.ID_ANY, style = wx.BORDER_NONE)
	
	box.Add(obj.notebook, 1, wx.EXPAND | wx.ALL)
		
	return obj 