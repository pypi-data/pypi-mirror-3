# -*- coding: utf-8 -*- 

import wx
import os

class PathOption(object):
	def __init__(self, cfg):
		assert cfg
		self.cfg = cfg
		try:
			fd = open(self.cfg,'r')
		except IOError:
			self.path = ''
			return
		self.path = fd.read()
		fd.close()
		
	def GetPath(self):
		return self.path
		
	def SetPath(self, path):
		if not path:
			return
		if path == self.path:
			return
		self.path = path
		fd = open(self.cfg,'w')
		fd.write(path)
		fd.close()

class AskPythonPathDlg(wx.Dialog):
	def __init__(self, *a, **k):
		cfg = k.pop('cfg')
		self.pathoption = PathOption(cfg)
		
		super(AskPythonPathDlg, self).__init__(*a, **k)
				
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(vbox)
		
		vbox.Add(wx.StaticText(self, wx.ID_ANY, 'Setup python path: '), \
			border = 10, \
			flag = wx.TOP | wx.LEFT | wx.ALIGN_LEFT)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.path = wx.TextCtrl(self, wx.ID_ANY)
		self.path.SetValue(self.pathoption.GetPath())
		hbox.Add(self.path, \
			proportion = 10, \
			flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
		self.pathbtn = wx.Button(self, wx.ID_ANY, '...', style = wx.BU_EXACTFIT)
		self.pathbtn.Bind(wx.EVT_BUTTON, self.OnPath)
		hbox.Add(self.pathbtn, \
			flag = wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, \
			border = 10, \
			flag = wx.ALL | wx.EXPAND)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox.Add(wx.StaticLine(self, wx.ID_ANY), \
			proportion = 1, \
			flag = wx.ALIGN_CENTRE_VERTICAL)
		
		okbtn = wx.Button(self, wx.ID_OK, '&Ok')
		okbtn.Bind(wx.EVT_BUTTON, self.OnOK)
		hbox.Add(okbtn, \
			flag = wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
		cancelbtn = wx.Button(self, wx.ID_CANCEL, '&Cancel')
		hbox.Add(cancelbtn, \
			border = 5, \
			flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, \
			border = 5, \
			flag =  wx.ALIGN_RIGHT)
		
	def GetPath(self):
		return self.path.GetValue()
		
	def OnPath(self, evt):
		dlg = wx.FileDialog(self, \
				message = "Choose python directory:",
				defaultDir=os.getcwd(),
				wildcard="python executable file (*)|*|" \
							"All files (*.*)|*.*",
				style=wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.path.SetValue(dlg.GetPath())
		
	def OnOK(self, evt):
		self.pathoption.SetPath(self.path.GetValue())
		evt.Skip()
		
if __name__ == "__main__":
	import util
	app = wx.PySimpleApp()
	print AskPythonPathDlg(None, cfg = util.GenCfgPath('option', 'timeit.cfg')).ShowModal()
#	app.MainLoop()