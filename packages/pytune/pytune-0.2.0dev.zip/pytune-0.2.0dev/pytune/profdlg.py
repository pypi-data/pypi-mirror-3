# -*- coding: utf-8 -*- 

import wx
import os
dlgsize = (640, 480)

class ProfDlg(wx.Dialog):
	def __init__(self, *a, **k):
		self.pypath = k.pop('python_path')
		assert os.path.isfile(self.pypath)
		super(ProfDlg, self).__init__(size = dlgsize, *a, **k)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(vbox)
		
		def CreateEntryCtrls():
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add(wx.StaticText(self, wx.ID_ANY, 'App entry file: '), \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			self.entry = wx.TextCtrl(self, wx.ID_ANY)
			hbox.Add(self.entry, \
				border = 5, \
				proportion = 1, \
				flag = wx.LEFT | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			btn = wx.Button(self, wx.ID_ANY, '...', style = wx.BU_EXACTFIT)
			btn.Bind(wx.EVT_BUTTON, self.OnEntry)
			hbox.Add(btn, \
				border = 5, \
				flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
			vbox.Add(hbox, \
				border = 5, \
#				proportion = 1, \
				flag = wx.TOP | wx.EXPAND)
				
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add(wx.StaticText(self, wx.ID_ANY, 'App arguments: '), \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			self.app_args = wx.TextCtrl(self, wx.ID_ANY)
			hbox.Add(self.app_args, \
				border = 5, \
				proportion = 1, \
				flag = wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			vbox.Add(hbox, \
				border = 5, \
				flag = wx.TOP | wx.EXPAND)
		CreateEntryCtrls()
		
		def CreateStatsCtrls():
#			hbox = wx.BoxSizer(wx.HORIZONTAL)
#			self.savetofile = wx.CheckBox(self, wx.ID_ANY, 'Save to file: ')
#			self.savetofile.SetValue(True)
#			self.savetofile.Bind(wx.EVT_CHECKBOX, self.OnSavetofile)
#			hbox.Add(self.savetofile, \
#				border = 5, \
#				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Stats output file: '), \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			self.stats = wx.TextCtrl(self, wx.ID_ANY)
			hbox.Add(self.stats, \
				border = 5, \
				proportion = 1, \
				flag = wx.LEFT | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			self.btn_stats = wx.Button(self, wx.ID_ANY, '...', style = wx.BU_EXACTFIT)
			self.btn_stats.Bind(wx.EVT_BUTTON, self.OnOutput)
			hbox.Add(self.btn_stats, \
				border = 5, \
				flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
			vbox.Add(hbox, \
				border = 5, \
				flag = wx.TOP | wx.EXPAND)
			
#			hbox = wx.BoxSizer(wx.HORIZONTAL)
#			hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Sort by: '), \
#				border = 5, \
#				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
#			self.sortby = wx.ComboBox(self, wx.ID_ANY, \
#					value = 'cumulative (cumulative time)', \
#					choices = [
#						'calls (call count)',
#						'cumulative (cumulative time)',
#						'file (file name)',
#						'module (file name)',
#						'pcalls (primitive call count)',
#						'line (line number)',
#						'name (function name)',
#						'nfl (name/file/line)',
#						'stdname (standard name)',
#						'time (internal time)'])
#			self.sortby.Enable(False)
#			hbox.Add(self.sortby, \
#				border = 5, \
#				flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#			vbox.Add(hbox, \
#				border = 5, \
#				flag = wx.TOP | wx.ALIGN_CENTRE_VERTICAL)
		CreateStatsCtrls()
		
		def CreateProfCtrls():
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Profiler: '), \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			self.profiler = wx.ComboBox(self, wx.ID_ANY, \
				value = 'profile', \
				choices = ['profile (recommend)', 'hotshot', 'cProfile (Py2.5+ only)'])
			hbox.Add(self.profiler, \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			vbox.Add(hbox, \
				border = 5, \
				flag = wx.TOP | wx.EXPAND)
		CreateProfCtrls()
		
		def CreateStdoutCtrls():
			_vbox = wx.BoxSizer(wx.VERTICAL)
			_vbox.Add(wx.StaticText(self, wx.ID_ANY, 'Standant outpu: '), \
				border = 5, \
				flag = wx.LEFT)
			self.stdout = wx.TextCtrl(self, wx.ID_ANY, \
					style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
			self.stdout.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL, 0, ''))
			_vbox.Add(self.stdout, \
				border = 5, \
				proportion = 1, \
				flag = wx.ALL | wx.EXPAND)
			vbox.Add(_vbox, \
				border = 5, \
				proportion = 1, \
				flag = wx.TOP | wx.EXPAND)
		CreateStdoutCtrls()
		
		def CreateBtns():
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			self.btn_clear = wx.Button(self, wx.ID_ANY, '&Clear')
			self.btn_clear.Bind(wx.EVT_BUTTON, self.OnClear)
			self.btn_ok = wx.Button(self, wx.ID_ANY, '&OK')
			self.btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
			hbox.Add(self.btn_clear, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			hbox.Add(self.btn_ok, \
				border = 5, \
				flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
			vbox.Add(hbox, \
				border = 5, \
				flag = wx.ALL | wx.ALIGN_RIGHT)
		CreateBtns()
		
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
	def OnClose(self, evt):
		self.Destroy()
		
	def OnSavetofile(self, evt):
		if evt.IsChecked():
			self.stats.Enable(True)
			self.btn_stats.Enable(True)
			self.sortby.Enable(False)
		else:
			self.stats.Enable(False)
			self.btn_stats.Enable(False)
			self.sortby.Enable(True)
		
	def OnEntry(self, evt):
		dlg = wx.FileDialog(self, \
				message = "Choose application entry file:",
				defaultDir=os.getcwd(),
				wildcard="python script file (*.py)|*.py|" \
							"All files (*.*)|*.*",
				style=wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.entry.SetValue(dlg.GetPath())
		dlg.Destroy()
		
	def OnOutput(self, evt):
		dlg = wx.FileDialog(self, \
				message = "Save to:",
				defaultDir=os.getcwd(),
				wildcard="profile stats file (*.prof)|*.prof|" \
							"All files (*.*)|*.*",
				style=wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.stats.SetValue(dlg.GetPath())
		dlg.Destroy()
		
	def OnClear(self, evt):
		self.stats.SetValue('')
		self.entry.SetValue('')
		self.stdout.SetValue('')
	
	def OnOk(self, evt):
		app = '%s %s'%(self.entry.GetValue(), self.app_args.GetValue())
		stats = self.stats.GetValue()
#		sortby = self.sortby.GetValue().partition(' ')[0]
		profiler = self.profiler.GetValue().partition(' ')[0]
#		print 'profiler = ', profiler, 'sortby = ', sortby
		
		class TimeitProc(wx.Process):
			def OnTerminate(inst, pid, status):
				def getstr(stream):
					s = ''
					while True:
						c = stream.GetC()
						if 0 == stream.LastRead():
							break
						s += c
					return s
				self.stdout.SetValue( \
					getstr(inst.GetErrorStream()) \
					+ getstr(inst.GetInputStream()) \
					+ '\nProfiled .')
				self.stdout.ShowPosition(self.stdout.GetLastPosition())
				
		cmd = '%s -m %s '%(self.pypath, profiler)
#		if self.savetofile.IsChecked():
#			if stats:
#				cmd += '-o %s '%stats
#		else:
#			cmd += '-s %s '%sortby
		if stats:
			cmd += '-o %s '%stats
		cmd += app
#		print cmd
		self.stdout.SetValue('Pofiling, please wait ...')
		proc = TimeitProc(self)
		proc.Redirect()
		wx.Execute(cmd, process = proc)
		
def _ShowProfDlg(parent, pypath):
	dlg = ProfDlg(parent, wx.NewId(), \
		'Profile wizard (step 2: profiling)', \
		python_path = pypath)
	dlg.Show()
	
def DoPorf(parent):
	import util
	from askpypathdlg import AskPythonPathDlg
	pypathdlg = AskPythonPathDlg(parent, \
			wx.ID_ANY, \
			'Profile wizard (step 1: setup python path)', \
			cfg = util.GenCfgPath('option', 'prof.cfg'))
	retcode = pypathdlg.ShowModal()
	if retcode != wx.ID_OK:
		return
	pypath = pypathdlg.GetPath()
	pypathdlg.Destroy()
	_ShowProfDlg(parent, pypath)
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	DoPorf(None)
	app.MainLoop()