# -*- coding:utf-8 -*-

import wx
from wx import xrc

class SaveDlg(wx.Dialog):
	def __init__(self, parent, *a, **k):
		super(SaveDlg, self).__init__(parent, *a, **k)
		
	def OnInit(self):
		self.res = xrc.XmlRescource('save_stats_dlg.xrc')
		self.init_ui()
		return True
		
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	dlg = SaveDlg(None, wx.ID_ANY, size = (640, 480))
	dlg.ShowModal()
	dlg.Destroy()
	app.MainLoop()