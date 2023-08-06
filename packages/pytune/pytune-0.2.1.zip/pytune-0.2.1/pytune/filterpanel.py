# -*- coding:utf-8 -*-

import wx

class FilterPanel(wx.Panel):
	def __init__(self, *a, **k):
		super(FilterPanel, self).__init__(*a, **k)
		
		rbox = wx.BoxSizer(wx.HORIZONTAL)
		rbox.Add(wx.StaticText(self, wx.ID_ANY, 'Func Filter:'), \
			border = 10, \
			flag = wx.TOP | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
		
		self.func_filter = wx.TextCtrl(self, wx.ID_ANY)
		rbox.Add(self.func_filter, \
			border = 10, \
			proportion = 1, \
			flag = wx.TOP | wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		
		rbox.Add(wx.StaticText(self, wx.ID_ANY, 'File Filter:'), \
			border = 10, \
			flag = wx.TOP | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
			
		self.file_filter = wx.TextCtrl(self, wx.ID_ANY)
		rbox.Add(self.file_filter, \
			border = 10, \
			proportion = 1, \
			flag = wx.TOP | wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(rbox, proportion = 1, flag = wx.EXPAND | wx.ALIGN_RIGHT)
			
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.cpu_time = wx.StaticText(self, wx.ID_ANY,'0 function calls in 0.0 CPU seconds')
		vbox.Add(hbox, \
			border = 10, \
			proportion = 1, \
			flag = wx.RIGHT | wx.EXPAND)
		vbox.Add(self.cpu_time, \
			border = 10, \
			flag = wx.TOP | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
		vbox.Add(wx.StaticLine(self), \
			border = 10, \
			flag = wx.TOP | wx.BOTTOM | wx.EXPAND)
		
		self.SetSizer(vbox)
		
		self.ok_callback = None
		self.all_callback = None
		
		self.func_filter.Bind(wx.EVT_TEXT, self.OnInput)
		self.file_filter.Bind(wx.EVT_TEXT, self.OnInput)
		
	def OnInput(self, evt):
		if self.ok_callback:
			self.ok_callback( \
				self.func_filter.GetValue(), \
				self.file_filter.GetValue())
		evt.Skip()
		
	def Clear(self):
		self.func_filter.Clear()
		self.file_filter.Clear()
		
	def SetCPU(self, fn, pfn, ctime):
		self.cpu_time.SetLabel(str(fn) + ' function calls (' + str(pfn) + ' primitive calls) in ' + str(ctime) + ' CPU seconds')
		self.cpu_time.Update()
		self.Update()
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, wx.ID_ANY, 'Test FilterPanel')
	FilterPanel(frame)
	frame.Centre()
	frame.Show(True)
	app.MainLoop()
