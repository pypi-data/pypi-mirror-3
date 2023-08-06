# -*- coding: utf-8 -*-

from codeview import DemoCodeEditor as CodeEditor
from codepanel_mixin import FindReplaceMixin

import wx

class CodePanel(wx.Panel, FindReplaceMixin):
	def __init__(self, *a, **k):
		in_tab = k.pop('in_tab', False)
		super(CodePanel, self).__init__(*a, **k)
		FindReplaceMixin.__init__(self)
		
		self.toolbar = self.CreatToolBar(in_tab)
		
		self.editor = CodeEditor(self)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar, \
			border = 10, \
			flag = wx.BOTTOM | wx.EXPAND)
#		vbox.Add(wx.StaticLine(self), \
#			border = 5, \
#			flag = wx.ALL | wx.EXPAND)
		vbox.Add(self.editor, \
			proportion = 1, \
			flag = wx.ALL | wx.EXPAND)
		self.SetSizer(vbox)
		
		self.new_callback = None
		self.new_tabnew_callback = None
		self.new_wndnew_callback = None
		
		self.open_callback = None
		self.open_tabnew_callback = None
		self.open_wndnew_callback = None
		
		self.run_callback = None
	
	def GetEditor(self):
		return self.editor
		
	def CreatToolBar(self, in_tab):
		'''
		New
			open inplace
			open in new tab
			open in new window
		Open
			open inplace
			open in new tab
			open in new window
		Save
			Save
			Save as
		Edit
			copy
			paste
			cut
			find
			replace
			redo
			undo
		Run
		'''
		self.in_tab = in_tab
		
		toolbar = wx.ToolBar(self, wx.ID_ANY)
		toolbar.AddSeparator()
		
		def NewSeries():
			ID_NEW = wx.NewId()
			ID_NEW_TABNEW = wx.NewId()
			ID_NEW_WNDNEW = wx.NewId()
			
			def New(callback):
				# save modified file
				callback()
				# reset flags, such as title, modified, etc.
			
			def OnNew(evt):
				if self.new_callback:
					New(self.new_callback)
			def OnNewTabNew(evt):
				if self.new_tabnew_callback:
					New(self.new_tabnew_callback)
			def OnNewWndNew(evt):
				if self.new_wndnew_callback:
					New(self.new_wndnew_callback)
				
			toolbar.AddLabelTool(ID_NEW, '', \
				wx.Bitmap('../res/codectrl/document-new.png'), \
				shortHelp = 'New document.')
			self.Bind(wx.EVT_TOOL, OnNew, id = ID_NEW)
			
			if in_tab:
				toolbar.AddLabelTool(ID_NEW_TABNEW, '', \
					wx.Bitmap('../res/codectrl/tab-new.png'), \
					shortHelp = 'New document in new tab.')
				self.Bind(wx.EVT_TOOL, OnNewTabNew, id = ID_NEW_TABNEW)
			
			toolbar.AddLabelTool(ID_NEW_WNDNEW, '', \
				wx.Bitmap('../res/codectrl/window-new.png'), \
				shortHelp = 'New document in new window.')
			self.Bind(wx.EVT_TOOL, OnNewWndNew, id = ID_NEW_WNDNEW)
			
			toolbar.AddSeparator()
			
		def OpenSeries():
			ID_OPEN = wx.NewId()
			ID_OPEN_TABNEW = wx.NewId()
			ID_OPEN_WNDNEW = wx.NewId()
			
			def Open(callback):
				# ask for file
				# open file
				callback()
				# reset flags, such as title, modified, etc.
				
			def OnOpen(evt):
				# save modified file
				if self.editor.GetModified():
					save()
				if self.open_callback:
					Open(self.open_callback)
			def OnOpenTabNew(evt):
				if self.open_tabnew_callback:
					Open(self.open_tabnew_callback)
			def OnOpenWndNew(evt):
				if self.open_wndnew_callback:
					Open(self.open_wndnew_callback)
					
			toolbar.AddLabelTool(ID_OPEN, '', \
				wx.Bitmap('../res/codectrl/document-open.png'), \
				shortHelp = 'Open document.')
			self.Bind(wx.EVT_TOOL, OnOpen, id = ID_OPEN)
			
			if in_tab:
				toolbar.AddLabelTool(ID_OPEN_TABNEW, '', \
					wx.Bitmap('../res/codectrl/document-open.png'), \
					shortHelp = 'Open document in new tab.')
				self.Bind(wx.EVT_TOOL, OnOpenTabNew, id = ID_OPEN_TABNEW)
			
			toolbar.AddLabelTool(ID_OPEN_WNDNEW, '', \
				wx.Bitmap('../res/codectrl/document-open.png'), \
				shortHelp = 'Open document in new window.')
			self.Bind(wx.EVT_TOOL, OnOpenWndNew, id = ID_OPEN_WNDNEW)
			
			toolbar.AddSeparator()
		
		def SaveSeries():
			ID_SAVE = wx.NewId()
			ID_SAVEAS = wx.NewId()
			def OnSave(evt):
				pass
				
			def OnSaveAs(evt):
				pass
				
			toolbar.AddLabelTool(ID_SAVE, '', \
				wx.Bitmap('../res/codectrl/document-save.png'), \
				shortHelp = 'Save document.')
			self.Bind(wx.EVT_TOOL, OnSave, id = ID_SAVE)
			
			toolbar.AddLabelTool(ID_SAVEAS, '', \
				wx.Bitmap('../res/codectrl/document-save-as.png'), \
				shortHelp = 'Save document in custom format.')
			self.Bind(wx.EVT_TOOL, OnSaveAs, id = ID_SAVEAS)
			
			toolbar.AddSeparator()
				
		def EditSeries():
			ID_COPY = wx.NewId()
			ID_CUT = wx.NewId()
			ID_PASTE = wx.NewId()
			ID_UNDO = wx.NewId()
			ID_REDO = wx.NewId()
			ID_FIND = wx.NewId()
			ID_REPLACE = wx.NewId()
			
			# ----------- Operate Clipboard ----------------
			def OnCopy(evt):
				self.editor.Copy()
			def OnCut(evt):
				self.editor.Cut()
			def OnPaste(evt):
				if self.editor.CanPaste():
					self.editor.Paste()
					
			# ------------ Undo & Redo ----------------
			def OnUndo(evt):
				if self.editor.CanUndo():
					self.editor.Undo()
			def OnRedo(evt):
				if self.editor.CanRedo():
					self.editor.Redo()
					
			# ---------- Find & Replace ----------------
			def OnFind(evt):
				self.ShowFindDlg()
			def OnReplace(evt):
				self.ShowFindReplaceDlg()
			
			# ------------ Add Label -------------------
			toolbar.AddLabelTool(ID_COPY, '', \
				wx.Bitmap('../res/codectrl/edit-copy.png'), \
				shortHelp = 'Copy selected text.')
			self.Bind(wx.EVT_TOOL, OnCopy, id = ID_COPY)
			
			toolbar.AddLabelTool(ID_CUT, '', \
				wx.Bitmap('../res/codectrl/edit-cut.png'), \
				shortHelp = 'Cut Selected text.')
			self.Bind(wx.EVT_TOOL, OnCut, id = ID_CUT)
			
			toolbar.AddLabelTool(ID_PASTE, '', \
				wx.Bitmap('../res/codectrl/edit-paste.png'), \
				shortHelp = 'Paste text from clipboard.')
			self.Bind(wx.EVT_TOOL, OnPaste, id = ID_PASTE)
			
			toolbar.AddSeparator()
			
			toolbar.AddLabelTool(ID_UNDO, '', \
				wx.Bitmap('../res/codectrl/edit-undo.png'), \
				shortHelp = 'Undo')
			self.Bind(wx.EVT_TOOL, OnUndo, id = ID_UNDO)
			
			toolbar.AddLabelTool(ID_REDO, '', \
				wx.Bitmap('../res/codectrl/edit-redo.png'), \
				shortHelp = 'Redo')
			self.Bind(wx.EVT_TOOL, OnRedo, id = ID_REDO)
			
			toolbar.AddSeparator()
			
			toolbar.AddLabelTool(ID_FIND, '', \
				wx.Bitmap('../res/codectrl/edit-find.png'), \
				shortHelp = 'Find')
			self.Bind(wx.EVT_TOOL, OnFind, id = ID_FIND)
			
			toolbar.AddLabelTool(ID_REPLACE, '', \
				wx.Bitmap('../res/codectrl/edit-find-replace.png'), \
				shortHelp = 'Replace')
			self.Bind(wx.EVT_TOOL, OnReplace, id = ID_REPLACE)
			
			toolbar.AddSeparator()
			
		def RunSeries():
			ID_RUN = wx.NewId()
			def OnRun(evt):
				if self.run_callback:
					self.run_callback()
				
			toolbar.AddLabelTool(ID_RUN, '', \
				wx.Bitmap('../res/codectrl/media-playback-start.png'), \
				shortHelp = 'Run')
			self.Bind(wx.EVT_TOOL, OnRun, id = ID_RUN)
			
			toolbar.AddSeparator()
			
		NewSeries()
		OpenSeries()
		SaveSeries()
		EditSeries()
		RunSeries()
		
		toolbar.Realize()
		return toolbar
		
	def UpdateTitle(self):
		pass
	
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, wx.ID_ANY)
	view = CodePanel(frame, in_tab = False)
	
	frame.Centre()
	frame.Show()
	app.MainLoop()
	