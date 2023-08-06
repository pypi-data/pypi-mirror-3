# -*- coding:utf-8 -*-

import wx
import os

import image_path as IP
	
def show(func):
	def show_func(*a, **k):
		obj = func(*a, **k)
		obj.Show(True)
		return obj
	return show_func

def centre(func):
	def centre_func(*a, **k):
		obj = func(*a, **k)
		obj.Centre()
		return obj
	return centre_func
	
def fullscreen(func):
	def fullscreen_func(*a, **k):
		obj = func(*a, **k)
		obj.ShowFullScreen(True)
		return obj
	return fullscreen_func
	
def maximize(func):
	def maximize_func(*a, **k):
		k['style'] = wx.MAXIMIZE
		obj = func(*a, **k)
		return obj
	return maximize_func

def createToolbar(frm):
	frm.toolbar = frm.CreateToolBar()
	frm.toolbar.SetToolBitmapSize(wx.Size(32, 32))
	frm.toolbar.AddSeparator()
	
def createStatusbar(frm):
	frm.CreateStatusBar()

def createMenu(frm):
	def createFileMenu(mb):
		menu = wx.Menu()
		
		# insert Open menu
		def _open(evt):
			dlg = wx.FileDialog( \
				frm, message = 'Open profile stats file', \
				defaultDir = frm.GetDirCtrlFilePath(), defaultFile = '', \
				wildcard = 'All files (*.*) | *.*', \
				style = wx.OPEN | wx.CHANGE_DIR )
			if dlg.ShowModal() != wx.ID_OK:
				return
			path = dlg.GetPath()
			if path:
				frm.OpenFile(path)
				frm.SetDirCtrlFilePath(os.path.dirname(path))
		ID_OPEN = wx.NewId()
		item_open = wx.MenuItem(menu, ID_OPEN, \
			'&Open...\tCtrl+O', 'Open profile stats file.')
		item_open.SetBitmap(wx.Bitmap(IP.Menu.open))
		menu.AppendItem(item_open)
		frm.Bind(wx.EVT_MENU, _open, id = ID_OPEN)
		# add toolbar button
		frm.toolbar.AddLabelTool(ID_OPEN, '', \
			wx.Bitmap(IP.Toolbar.open), \
			shortHelp = 'Open profile stats file.')
		frm.toolbar.Realize()
		
		# insert Dump Stats menu
		def save(evt):
			dlg = wx.FileDialog( \
				frm, message = 'Save profile stats in a plain text file.', \
				defaultDir = frm.GetDirCtrlFilePath(), defaultFile = '', \
				wildcard = \
					'Text file (*.txt)|*.txt|All files (*.*)|*.*', \
				style = wx.SAVE)
			if dlg.ShowModal() != wx.ID_OK:
				return
			path = dlg.GetPath()
			if path:
				frm.SaveStats(path)
		ID_SAVE = wx.NewId()
		item_save = wx.MenuItem(menu, ID_SAVE, \
			'&Save...\tCtrl+S', 'save profile stats to text file.')
		item_save.SetBitmap(wx.Bitmap(IP.Menu.save))
		menu.AppendItem(item_save)
		frm.Bind(wx.EVT_MENU, save, id = ID_SAVE)
		# add toolbar button
		frm.toolbar.AddLabelTool(ID_SAVE, '', \
			wx.Bitmap(IP.Toolbar.save), \
			shortHelp = 'Save profile stats to text file.')
			
		frm.toolbar.Realize()
		
		# insert Separator
		menu.AppendSeparator()
		frm.toolbar.AddSeparator()
		
		# insert Quit menu
		def quit(event):
			frm.Close()
		
		ID_QUIT = wx.NewId()
		item_quit = wx.MenuItem(menu, ID_QUIT, '&Quit\tCtrl+Q', 'Quit Application!')
		item_quit.SetBitmap(wx.Bitmap(IP.Menu.quit))
		menu.AppendItem(item_quit)
		frm.Bind(wx.EVT_MENU, quit, id = ID_QUIT)
		
		mb.Append(menu, 'File')
		
	def createToolsMenu(mb):
		menu = wx.Menu()
		
		mb.Append(menu, '&Tools')
		
		def prof(evt):
			from profdlg import DoPorf
			DoPorf(frm)
		ID_PROF = wx.NewId()
		item_prof = wx.MenuItem(menu, ID_PROF, '&Profile\tCtrl+P')
		item_prof.SetBitmap(wx.Bitmap(IP.Menu.prof))
		menu.AppendItem(item_prof)
		menu.AppendSeparator()
		frm.Bind(wx.EVT_MENU, prof, id = ID_PROF)
		frm.toolbar.AddLabelTool(ID_PROF, '', \
			wx.Bitmap(IP.Toolbar.prof), \
			shortHelp = 'Profile')
		
		def timeit(evt):
			from timeitdlg import DoTimeit
			DoTimeit(frm)
		
		ID_TIMEIT = wx.NewId()
		item_timeit = wx.MenuItem(menu, ID_TIMEIT, '&Time It\tCtrl+T')
		item_timeit.SetBitmap(wx.Bitmap(IP.Menu.timeit))
		menu.AppendItem(item_timeit)
		frm.Bind(wx.EVT_MENU, timeit, id = ID_TIMEIT)
		frm.toolbar.AddLabelTool(ID_TIMEIT, '', \
			wx.Bitmap(IP.Toolbar.timeit), \
			shortHelp = 'Time it')
			
		frm.toolbar.AddSeparator()
		frm.toolbar.Realize()
		
#	def createOptionMenu(mb):
#		menu = wx.Menu()
#		
#		mb.Append(menu, '&Option')
		
	def createHelpMenu(mb):
		menu = wx.Menu()
		
		#insert help menu
		def help(evt):
			import webbrowser
			webbrowser.open_new('http://code.google.com/p/visualpytune/wiki/onlinedoc')
		ID_HELP = wx.NewId()
		item_help = wx.MenuItem(menu, ID_HELP, 'Online &Help\tCtrl+H')
		item_help.SetBitmap(wx.Bitmap(IP.Menu.help))
		menu.AppendItem(item_help)
		frm.Bind(wx.EVT_MENU, help, id = ID_HELP)
		# add toolbar button
		frm.toolbar.AddLabelTool(ID_HELP, '', \
			wx.Bitmap(IP.Toolbar.help), \
			shortHelp = 'Online Help')
		
		frm.toolbar.Realize()		
		
		#insert separator
		menu.AppendSeparator()
		
		# insert about menu
		def about(evt):
			def ShowAbout():
				from about import name, ver, url, author
				info = wx.AboutDialogInfo()
				
				#lic = open('./licence','rt')
				#info.SetLicence(''.join(lic.readlines()))
				#lic.close()
				
				info.SetIcon(wx.Icon(IP.PY_ICO, wx.BITMAP_TYPE_ICO))
				info.SetName(name)
				info.SetVersion(ver)
				info.SetDescription( \
					'VisualPyTune is a python program performance tuning tool, based on wxPython.\n'
					+ 'It can show you a callgraph(doing), stats report, callees, callers, and caky charts.\n'
					+ 'finaly, you can remove inessential information very easy. ')
				info.SetWebSite(url)

				info.AddDeveloper(author)
#				info.AddDocWriter('Yonghao Lai')
#				info.AddArtist('Yonghao Lai')
#				info.AddTranslator('Yonghao Lai')

				wx.AboutBox(info)
			ShowAbout()
		ID_ABOUT = wx.NewId()
		item_about = wx.MenuItem(menu, ID_ABOUT, '&About...')
		menu.AppendItem(item_about)
		frm.Bind(wx.EVT_MENU, about, id = ID_ABOUT)
		
		mb.Append(menu, '&Help')
		
	mb = wx.MenuBar()
	frm.SetMenuBar(mb)
	
	createFileMenu(mb)
	createToolsMenu(mb)
#	createOptionMenu(mb)
	createHelpMenu(mb)
	
def createMainUI(frm):
	from viewpanel import Panel as vp
	from statspanel import Panel as sp
	from callerspanel import Panel as cp
	from calleespanel import Panel as cep
	from historypanel import Panel as hp
	from uicfg import UIConfig
	#-------- splitter
	from proportionalsplitter import ProportionalSplitter
	splitter = ProportionalSplitter(frm, wx.ID_ANY, \
		proportion = UIConfig.inst().getLeftSplitProp())

	lsplitter = ProportionalSplitter(splitter, wx.ID_ANY, \
		proportion = UIConfig.inst().getUpSplitProp(), \
		style = wx.BORDER_NONE)
	
	usplitter = ProportionalSplitter(splitter, wx.ID_ANY, \
		proportion = UIConfig.inst().getUpSplitProp(), \
		style = wx.BORDER_NONE)
	
	rsplitter = ProportionalSplitter(usplitter, wx.ID_ANY, \
		proportion = UIConfig.inst().getRightSplitProp(), \
		style = wx.BORDER_NONE)
	#-------- panel

	frm.viewpanel = vp(lsplitter)
	frm.historypanel = hp(lsplitter)
	frm.statspanel = sp(usplitter)
	frm.callerspanel = cp(rsplitter)
	frm.calleespanel = cep(rsplitter)
	
	#----------- split
	
	splitter.SplitVertically(lsplitter, usplitter)
	lsplitter.SplitHorizontally(frm.viewpanel, frm.historypanel)
	usplitter.SplitHorizontally(frm.statspanel, rsplitter)
	rsplitter.SplitVertically(frm.callerspanel, frm.calleespanel)
	
	def OnStatsSelected(evt):
		idx = evt.GetIndex()
		evt_list = frm.statspanel.listctrl
		idx = int(evt_list.GetItemText(idx))
		func = frm.model.get_func_by_idx(idx)
		title = frm.model.get_fln_by_func(func)
		frm.calleespanel.update(title, frm.model.stats.get_callees(func))
		frm.callerspanel.update(title, frm.model.stats.get_callers(func))
		if frm.historypanel.listctrl.isHistoryHit == False:
			frm.historypanel.insert(func)
		frm.historypanel.listctrl.isHistoryHit = False
		
	def OnCharSelected(func):
		idx = frm.model.get_idx_by_func(func)
		tidx = idx
		idx = frm.statspanel.listctrl.FindItem(0, str(idx))
		if idx == -1 :
			frm.statspanel.ClearFilter()
			idx = frm.statspanel.listctrl.FindItem(0, str(tidx))
		frm.statspanel.listctrl.Focus(idx)
		frm.statspanel.listctrl.Select(idx)

	def OnLoadedStatsSelected(stats):
		frm.calleespanel.chartctrl.Clear()
		frm.callerspanel.chartctrl.Clear()
		frm.calleespanel.listctrl.Clear()
		frm.callerspanel.listctrl.Clear()
		frm.historypanel.listctrl.Clear()
		frm.model = stats
		frm.statspanel.callpanel.init_data(frm.model.stats)
		frm.statspanel.listctrl.reset(frm.model.get_data())
		frm.statspanel.SetCpuTime(frm.model.stats.nc, frm.model.stats.pnc, frm.model.stats.cpu_time)
	
	frm.statspanel.listctrl.selected_callback = OnStatsSelected
	frm.calleespanel.chartctrl.cc.selected_callback = OnCharSelected
	frm.callerspanel.chartctrl.cc.selected_callback = OnCharSelected
	frm.calleespanel.listctrl.selected_callback = OnCharSelected
	frm.callerspanel.listctrl.selected_callback = OnCharSelected
	frm.historypanel.listctrl.selected_callback = OnCharSelected
	frm.viewpanel.statsctrl.selected_callback = OnLoadedStatsSelected
	
	#frm.calleespanel.chartctrl.cc.undo_callback = frm.historypanel.listctrl.Undo
	#frm.callerspanel.chartctrl.cc.undo_callback = frm.historypanel.listctrl.Undo
	frm.calleespanel.chartctrl.actionpanel.undo_callback = frm.historypanel.listctrl.Undo
	frm.callerspanel.chartctrl.actionpanel.undo_callback = frm.historypanel.listctrl.Undo

	#frm.calleespanel.chartctrl.cc.redo_callback = frm.historypanel.listctrl.Redo
	#frm.callerspanel.chartctrl.cc.redo_callback = frm.historypanel.listctrl.Redo
	frm.calleespanel.chartctrl.actionpanel.redo_callback = frm.historypanel.listctrl.Redo
	frm.callerspanel.chartctrl.actionpanel.redo_callback = frm.historypanel.listctrl.Redo
	
	def OnDirCtrlSelChanged(evt):
		frm.calleespanel.chartctrl.Clear()
		frm.callerspanel.chartctrl.Clear()
		frm.calleespanel.listctrl.Clear()
		frm.callerspanel.listctrl.Clear()
		frm.historypanel.listctrl.Clear()
		p = frm.viewpanel.dirctrl.GetFilePath()
		if p and os.path.isfile(p):
			frm.OpenFile(p)
		evt.Skip()
#	frm.viewpanel.dirctrl.GetTreeCtrl().Bind(wx.EVT_TREE_SEL_CHANGED, \
#								OnDirCtrlSelChanged)
	wx.EVT_TREE_SEL_CHANGED(frm.viewpanel.dirctrl, \
		frm.viewpanel.dirctrl.GetTreeCtrl().GetId(), \
		OnDirCtrlSelChanged)
	
	def OnSize(evt):
		size = evt.GetSize()
		UIConfig.inst().setWindowSize((size.x, size.y))
		evt.Skip()
	frm.Bind(wx.EVT_SIZE, OnSize, frm)
		
	def OnClose(evt):
		path = frm.viewpanel.dirctrl.GetPath()
		UIConfig.inst().setLastDir( \
			path if os.path.isdir(path) else os.path.dirname(path))
		UIConfig.inst().setMaximized( \
			frm.IsMaximized())
		UIConfig.inst().setWindowPos(frm.GetPositionTuple())
		UIConfig.inst().setLeftSplitProp(splitter.proportion)
		UIConfig.inst().setUpSplitProp(usplitter.proportion)
		UIConfig.inst().setRightSplitProp(rsplitter.proportion)
		UIConfig.inst().release()
#		frm.Destroy()
		evt.Skip()
	frm.Bind(wx.EVT_CLOSE, OnClose, frm)
		
def AddMiscFunc(frm):
	def GetDirCtrlFilePath():
		path = frm.viewpanel.dirctrl.GetPath()
		if path:
			if os.path.isdir(path):
				return path
			else:
				return os.path.dirname(path)
		return os.getcwd()
	frm.GetDirCtrlFilePath = GetDirCtrlFilePath
	
	def SetDirCtrlFilePath(path):
		frm.viewpanel.dirctrl.SetPath(path)
	frm.SetDirCtrlFilePath = SetDirCtrlFilePath	
	
	def OpenFile(path):
		assert path
		print 'open', path
		from statsmodel import StatsModel
		try:
			frm.model = StatsModel(path)
		except:
			import sys
			from traceback import print_exc
			print_exc(file = sys.stdout)
			wx.MessageBox('Analysis failure.', 'Failed', wx.OK|wx.ICON_INFORMATION, frm)
			return
		#print frm.model.get_data()
		frm.viewpanel.statsctrl.insert((os.path.split(path)[1], os.path.split(path)[0]), frm.model)
		frm.statspanel.callpanel.init_data(frm.model.stats)
		frm.statspanel.listctrl.reset(frm.model.get_data())
		frm.statspanel.SetCpuTime(frm.model.stats.nc, frm.model.stats.pnc, frm.model.stats.cpu_time)

	frm.OpenFile = OpenFile
	
	def SaveStats(path):
		assert path
		frm.model.save_stats(path)
	frm.SaveStats = SaveStats
		
def AddDragAndDropSupport(frm):
	class FileDrop(wx.FileDropTarget):
		def OnDropFiles(self, x, y, fns):
			if len(fns) > 1:
				wx.MessageDialog(frm, "Drop too many files !").ShowModal()
				return
			frm.OpenFile(fns[0])
	
	dt = FileDrop()
	frm.SetDropTarget(dt)
	
#@centre
#@fullscreen
@show
def createUI(*a, **k):
	from uicfg import UIConfig

	if UIConfig.inst().getMaximized():
		if 'style' in k:
			k['style'] |= wx.MAXIMIZE
		else:
			k['style'] = wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE
	else:
		k['size'] = UIConfig.inst().getWindowSize()
		k['pos'] = UIConfig.inst().getWindowPos()
		
	obj = wx.Frame(*a, **k)
	
	obj.SetIcon(wx.Icon(IP.PY_ICO, wx.BITMAP_TYPE_ICO))
	createToolbar(obj)
	createMenu(obj)
	createStatusbar(obj)
	createMainUI(obj)
	AddMiscFunc(obj)
	AddDragAndDropSupport(obj)
	
	if UIConfig.inst().getMaximized():
#		wx.CallAfter(obj.Maximize)
		obj.Maximize()
	
	return obj
	
