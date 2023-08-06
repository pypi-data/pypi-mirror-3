# -*- coding:utf-8 -*-

import wx

from listctrl import CallListCtrl as DataList
from cakychartpanel import CakyChartPanel
	
import panel
	
class Panel(panel.NotebookPanel):
	def __init__(self, *a, **k):
		super(Panel, self).__init__(*a, **k)
		
		self.listctrl = DataList(self.notebook, wx.ID_ANY, \
			style = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE)
		self.chartctrl = CakyChartPanel(self.notebook, wx.ID_ANY)
		
		self.BuildPages()
		
	def BuildPages(self):
		self.notebook.AddPage(self.listctrl, 'Callers')
		self.notebook.AddPage(self.chartctrl, 'Caky Chart')
		
	def update(self, caky_title, data):
		#caky_title = 'Callers of ' + title
		self.listctrl.reset(data)
		self.chartctrl.reset(caky_title, data)