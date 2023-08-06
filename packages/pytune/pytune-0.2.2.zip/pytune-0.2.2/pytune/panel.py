# -*- coding:utf-8 -*-

import wx

class NotebookPanel(wx.Panel):
	def __init__(self, *a, **k):
		super(NotebookPanel, self).__init__(*a, **k)
		
		self.notebook = wx.Notebook(self, wx.ID_ANY, \
				style = wx.BORDER_NONE)
		
		box = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(box)
		box.Add(self.notebook, 1, wx.EXPAND | wx.ALL)
		
	def BuildPages(self):
		raise NotImplementedError