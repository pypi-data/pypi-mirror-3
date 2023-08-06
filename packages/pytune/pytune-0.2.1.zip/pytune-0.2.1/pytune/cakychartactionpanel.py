# -*- coding:utf-8 -*-

import wx

class CakyChartActionPanel(wx.Panel):
        def __init__(self, *a, **k):
		super(CakyChartActionPanel, self).__init__(*a, **k)
		box = wx.BoxSizer(wx.HORIZONTAL)
		self.st = wx.StaticText(self, wx.ID_ANY, '', style = wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
		box.Add(self.st, \
				border = 5, \
				proportion = 1, \
				flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL)

		ID_UNDO = wx.NewId()
		self.UndoButton = wx.Button(self, ID_UNDO, '<< back')
		box.Add(self.UndoButton, \
				border = 5, \
				flag = wx.ALL |wx.ALIGN_CENTER_VERTICAL)
		self.Bind(wx.EVT_BUTTON, self.OnUndo, id = ID_UNDO)

		ID_REDO = wx.NewId()
		self.RedoButton = wx.Button(self, ID_REDO, 'forward >>')
		box.Add(self.RedoButton, \
				border = 5, \
				flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL)
		self.Bind(wx.EVT_BUTTON, self.OnRedo, id = ID_REDO)

		self.SetSizer(box)

		self.redo_callback = None
		self.undo_callback = None

	def resetTitle(self, title):
		self.st.SetLabel(title)

        def OnRedo(self, evt):
                self.redo_callback()

        def OnUndo(self, evt):
                self.undo_callback()

