# -*- coding:utf-8 -*-

import wx
import panel

from listctrl import HistoryListCtrl as HisList
from historyactionpanel import HistoryActionPanel as HaPanel

class HistoryPanel(wx.Panel):
	def __init__(self, *a, **k):
		super(HistoryPanel, self).__init__(*a, **k)
		
		self.listctrl = HisList(self, wx.ID_ANY, \
			style = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER)
		
		self.actionpanel = HaPanel(self, wx.ID_ANY)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.actionpanel, \
			flag = wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_TOP)
		vbox.Add(self.listctrl, \
			proportion = 1, \
			flag = wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM)
		
		self.actionpanel.Redo_callback = self.listctrl.Redo
		self.actionpanel.Undo_callback = self.listctrl.Undo
		self.actionpanel.Clear_callback = self.listctrl.Clear
		
		
		self.SetSizer(vbox)
	
	
class Panel(panel.NotebookPanel):
	def __init__(self, *a, **k):
		super(Panel, self).__init__(*a, **k)
		self.historypanel = HistoryPanel(self.notebook, wx.ID_ANY)
		self.listctrl = self.historypanel.listctrl
		self.BuildPages()
		
	def BuildPages(self):
		self.notebook.AddPage(self.historypanel, 'History')
	
	def insert(self, func):
		self.listctrl.insert(func)