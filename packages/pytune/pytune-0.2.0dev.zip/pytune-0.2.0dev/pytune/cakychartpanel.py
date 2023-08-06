# -*- coding:utf-8 -*-

import wx
import panel

from cakychart import CakyChart as cc
from cakychartactionpanel import CakyChartActionPanel as ccaPanel

class CakyChartPanel(wx.Panel):
	def __init__(self, *a, **k):
		super(CakyChartPanel, self).__init__(*a, **k)
		
		self.cc = cc(self, wx.ID_ANY, \
			style = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER)
		
		self.actionpanel = ccaPanel(self, wx.ID_ANY)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.actionpanel, \
			flag = wx.RIGHT | wx.EXPAND | wx.ALIGN_TOP)
		vbox.Add(self.cc, \
			proportion = 1, \
			flag = wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM)
		
		self.SetSizer(vbox)

	def Clear(self):
		self.cc.Clear()

	def reset(self, title_text, data):
		self.cc.reset(title_text, data)
		self.actionpanel.resetTitle(title_text)