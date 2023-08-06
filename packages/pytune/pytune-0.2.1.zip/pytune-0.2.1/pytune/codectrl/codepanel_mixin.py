# -*- coding:utf-8 -*-

import wx

class FindReplaceMixin(object):
	def __init__(self):
		self.Bind(wx.EVT_FIND, self.OnFind)
		self.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
		self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
		self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
		self.Bind(wx.EVT_FIND_CLOSE, self.OnFindReplaceClose)
		
	def GetEditor(self):
		raise NotImplementedError
		
	def ShowFindDlg(self):
		data = wx.FindReplaceData()
		dlg = wx.FindReplaceDialog(self, data, "Find")
		dlg.data = data  # save a reference to it...
		dlg.Show(True)
		
	def ShowFindReplaceDlg(self):
		data = wx.FindReplaceData()
		dlg = wx.FindReplaceDialog(self, data, \
			"Find & Replace", wx.FR_REPLACEDIALOG)
		dlg.data = data  # save a reference to it...
		dlg.Show(True)
		
	def OnFind(self, evt):
		editor = self.GetEditor()
		if wx.FR_DOWN & evt.GetFlags():
			start, end = editor.GetSelectionEnd(), editor.GetLength()
		else:
			start, end = editor.GetSelectionStart(), 0
		ret = self.__do_find(editor, start, end, evt.GetFindString(), evt.GetFlags())
		if ret < 0:
			wx.MessageDialog(self, \
				'"%s" not found.'%(evt.GetFindString(), ), \
				'Find', \
				wx.OK | wx.ICON_EXCLAMATION).ShowModal()
				
	def OnFindNext(self, evt):
		return self.OnFind(evt)
		
	def OnReplace(self, evt):
		self.__do_replace(evt)
		self.OnFind(evt)
		
	def OnReplaceAll(self, evt):
		editor = self.GetEditor()
		cnt = 0
		while self.__do_find(editor, \
				0, \
				editor.GetLength(), \
				evt.GetFindString(), \
				evt.GetFlags()) >= 0:
			cnt += 1
			self.__do_replace(evt)
		if cnt == 0:
			wx.MessageDialog(self, \
				'"%s" not found.'%(evt.GetFindString(), ), \
				'Find & Replace', \
				wx.OK | wx.ICON_EXCLAMATION).ShowModal()
		else:
			wx.MessageDialog(self, \
				'%d substitutions.'%(cnt, ), \
				'Find & Replace', \
				wx.OK | wx.ICON_EXCLAMATION).ShowModal()
		
	def OnFindReplaceClose(self, evt):
		evt.GetDialog().Destroy()
		
	def __do_find(self, editor, start, end, findstr, flags):
		pos = editor.FindText(start, end, findstr, flags)
		print pos
		if pos >= 0:
			editor.SetSelection(pos, pos + len(findstr))
			
		return pos
		
	def __do_replace(self, evt):
		editor = self.GetEditor()
		sel = editor.GetSelectedText()
		if sel == evt.GetFindString():
			editor.ReplaceSelection(evt.GetReplaceString())	