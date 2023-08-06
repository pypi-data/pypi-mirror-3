# -*- coding:utf-8 -*-

import wx

class HistoryActionPanel(wx.Panel):
        def __init__(self, *a, **k):
                super(HistoryActionPanel, self).__init__(*a, **k)
                box = wx.BoxSizer(wx.HORIZONTAL)

                ID_UNDO = wx.NewId()
                self.UndoButton = wx.Button(self, ID_UNDO, '<< back')
                box.Add(self.UndoButton, \
                        border = 5, \
                        flag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
                self.Bind(wx.EVT_BUTTON, self.OnUndo, id = ID_UNDO)

                ID_REDO = wx.NewId()
                self.RedoButton = wx.Button(self, ID_REDO, 'forward >>')
                box.Add(self.RedoButton, \
                        border = 5, \
                        flag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
                self.Bind(wx.EVT_BUTTON, self.OnRedo, id = ID_REDO)

                ID_CLEAR = wx.NewId()
                self.ClearButton = wx.Button(self, ID_CLEAR, '&Clear')
                box.Add(self.ClearButton, \
                        border = 5, \
                        flag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
                self.Bind(wx.EVT_BUTTON, self.OnClear, id = ID_CLEAR)

                self.SetSizer(box)
                
                self.Redo_callback = None
                self.Undo_callback = None
                self.Clear_callback = None

        def OnRedo(self, evt):
                self.Redo_callback()

        def OnUndo(self, evt):
                self.Undo_callback()

        def OnClear(self, evt):
                self.Clear_callback()
