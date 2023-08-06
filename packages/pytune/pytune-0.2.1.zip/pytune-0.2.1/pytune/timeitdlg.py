# -*- coding: utf-8 -*- 

import wx
import subprocess, os, sys
from wx.lib.intctrl import IntCtrl
from codectrl.codeview import DemoCodeEditor as CodeEditor

dlgsize = (640, 480)

timeit_file_template = """
# -*- coding:utf-8 -*-
from timeit import Timer
t = Timer('''%s''', '''%s''')
n, r = %d, %d
try:
	print n, 'loops, best of ', r, ':', min(t.repeat(n, r)), 'sec per loop'
except:
	t.print_exc()
"""

class TimeitDlg(wx.Dialog):
	def __init__(self, *a, **k):
		self.pypath = k.pop('python_path')
		assert os.path.isfile(self.pypath)
		super(TimeitDlg, self).__init__(size = dlgsize, *a, **k)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		# --------------- statement ------------------------------------
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.stmtbtn = wx.Button(self, wx.ID_ANY, 'Statement <<')
		self.stmtbtn.closed = False
		hbox.Add(self.stmtbtn, \
			border = 10, \
			flag = wx.LEFT | wx.ALIGN_LEFT)
		hbox.Add(wx.StaticLine(self), \
			border = 10, \
			proportion = 1, \
			flag = wx.RIGHT  | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		#self.stmt = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_MULTILINE | wx.HSCROLL )
		self.stmt = CodeEditor(self)
		vbox.Add(self.stmt, \
			proportion = 1, \
			flag = wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND )
			
		# --------------- setup ----------------------------------------
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.setupbtn = wx.Button(self, wx.ID_ANY, 'Setup >>')
		self.setupbtn.closed = False
		hbox.Add(self.setupbtn, \
			border = 10, \
			flag = wx.LEFT | wx.ALIGN_LEFT)
		hbox.Add(wx.StaticLine(self), \
			border = 10, \
			proportion = 1, \
			flag = wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		#self.setup = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_MULTILINE | wx.HSCROLL )
		self.setup = CodeEditor(self)
		vbox.Add(self.setup, \
			proportion = 1, \
			flag = wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND )
		self.setup.Show(True)
			
		# --------------- arguments ------------------------------------
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.argsbtn = wx.Button(self, wx.ID_ANY, 'Arguments >>')
		self.argsbtn.closed = False
		hbox.Add(self.argsbtn, \
			border = 10, \
			flag = wx.LEFT | wx.ALIGN_LEFT)
		hbox.Add(wx.StaticLine(self), \
			border = 10, \
			proportion = 1, \
			flag = wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		self.argsbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Number: '), \
			flag = wx.ALIGN_LEFT)
		self.number = IntCtrl(self)
		hbox.Add(self.number, flag = wx.ALIGN_RIGHT | wx.EXPAND)
		self.argsbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Repeat: '), \
			flag = wx.ALIGN_LEFT)
		self.repeat = IntCtrl(self)
		hbox.Add(self.repeat, flag = wx.ALIGN_RIGHT | wx.EXPAND)
		self.argsbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		vbox.Add(self.argsbox, flag = wx.EXPAND)
		
#		# --------------- Python Path ------------------------------------
#		hbox = wx.BoxSizer(wx.HORIZONTAL)
#		self.pathbtn = wx.Button(self, wx.ID_ANY, 'Path <<')
#		self.pathbtn.closed = False
#		hbox.Add(self.pathbtn, \
#			border = 10, \
#			flag = wx.LEFT | wx.ALIGN_LEFT)
#		hbox.Add(wx.StaticLine(self), \
#			border = 10, \
#			proportion = 1, \
#			flag = wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
#		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
#		
#		self.pathbox = wx.BoxSizer(wx.VERTICAL)
#		hbox = wx.BoxSizer(wx.HORIZONTAL)
#		hbox.Add(wx.StaticText(self, wx.ID_ANY, 'Python Path: '), \
#			flag = wx.ALIGN_LEFT)
#		self.path = wx.TextCtrl(self)
#		hbox.Add(self.path, proportion = 1, flag = wx.ALIGN_RIGHT | wx.EXPAND)
#		self.dirbtn = wx.Button(self, wx.ID_ANY, '...', style = wx.BU_EXACTFIT )
#		hbox.Add(self.dirbtn, border = 10, flag = wx.LEFT | wx.ALIGN_CENTRE_VERTICAL)
#		self.pathbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
#		
#		vbox.Add(self.pathbox, flag = wx.EXPAND)
		
		# ---------------- error and output ----------------------------
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.resultbtn = wx.Button(self, wx.ID_ANY, 'Result >>')
		self.resultbtn.closed = False
		hbox.Add(self.resultbtn, \
			border = 10, \
			flag = wx.LEFT | wx.ALIGN_LEFT)
		hbox.Add(wx.StaticLine(self), \
			border = 10, \
			proportion = 1, \
			flag = wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL)
		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.EXPAND)
		
		self.result = wx.TextCtrl(self, \
			wx.ID_ANY, style = wx.TE_MULTILINE | wx.HSCROLL | wx.VSCROLL)
		self.result.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL, 0, ''))
		vbox.Add(self.result, \
			proportion = 1, \
			flag = wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND )
		# ---------------- buttons -------------------------------------
		self.clean = wx.Button(self, wx.ID_ANY, '&Clean')
		self.ok = wx.Button(self, wx.ID_ANY, '&OK')
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.clean, border = 10, flag = wx.LEFT | wx.ALIGN_RIGHT)
		hbox.Add(self.ok, border = 10, flag = wx.LEFT | wx.ALIGN_RIGHT)
		vbox.Add(hbox, border = 10, flag = wx.TOP | wx.ALIGN_RIGHT)
		
		self.SetSizer(vbox)
		
		self.stmtbtn.Bind(wx.EVT_BUTTON, self.OnStmtbtn)
		self.setupbtn.Bind(wx.EVT_BUTTON, self.OnSetupbtn)
		self.argsbtn.Bind(wx.EVT_BUTTON, self.OnArgsbtn)
#		self.pathbtn.Bind(wx.EVT_BUTTON, self.OnPathbtn)
		self.resultbtn.Bind(wx.EVT_BUTTON, self.OnResultbtn)
		
#		self.dirbtn.Bind(wx.EVT_BUTTON, self.OnDirbtn)
		self.clean.Bind(wx.EVT_BUTTON, self.OnClean)
		self.ok.Bind(wx.EVT_BUTTON, self.OnOk)
		
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.Reset()
		self.OnArgsbtn(None)
#		self.OnStmtbtn(None)
		self.OnSetupbtn(None)
		self.OnResultbtn(None)
		
#		self.pathoption = PathOptoin()
#		self.path.SetValue(self.pathoption.GetPath())
		
#	def OnPathbtn(self, evt):
#		if self.pathbtn.closed:
#			self.GetSizer().Show(self.pathbox, True, True)
#			self.pathbtn.SetLabel('Path <<')
#		else:
#			self.GetSizer().Show(self.pathbox, False, True)
#			self.pathbtn.SetLabel('Path >>')
#		self.Fit()
#		self.pathbtn.closed ^= True
		
	def OnArgsbtn(self, evt):
		if self.argsbtn.closed:
			self.GetSizer().Show(self.argsbox, True, True)
			self.argsbtn.SetLabel('Arguments <<')
		else:
			self.GetSizer().Show(self.argsbox, False, True)
			self.argsbtn.SetLabel('Arguments >>')
		self.Fit()
		self.argsbtn.closed ^= True
		
	def OnStmtbtn(self, evt):
		self.DoClose(self.stmtbtn, self.stmt, \
			('Statement >>', 'Statement <<'))
		
	def OnSetupbtn(self, evt):
		self.DoClose(self.setupbtn, self.setup, \
			('Setup >>', 'Setup <<'))
		
	def OnResultbtn(self, evt):
		self.DoClose(self.resultbtn, self.result, \
			('Result >>', 'Result <<'))
			
	def DoClose(self, btn, ctrl, lbls):
		ctrl.Show(btn.closed)
		btn.SetLabel(lbls[int(btn.closed)])
		self.Fit()
		btn.closed ^= True
		
#	def OnDirbtn(self, evt):
#		dlg = wx.FileDialog(self, \
#				message = "Choose python directory:",
#				defaultDir=os.getcwd(),
#				defaultFile="python*",
#				wildcard="python executable file (python*)|python*|" \
#							"All files (*.*)|*.*",
#				style=wx.OPEN | wx.CHANGE_DIR)
#		if dlg.ShowModal() == wx.ID_OK:
#			self.path.SetValue(dlg.GetPath())
#		dlg.Destroy()
		
	def OnClean(self, evt):
		self.Reset()
		
	def OnOk(self, evt):
#		path = self.path.GetValue()
#		if path == '' or not os.path.isfile(path):
#			wx.MessageDialog(self, \
#				message = 'Set python path first, please.', \
#				caption = 'Timeit', \
#				style = wx.OK | wx.ICON_EXCLAMATION).ShowModal()
#			return
		stmt = self.stmt.GetText()
		setup = self.setup.GetText()
		if not setup.strip():
			setup = 'pass'
#		cmd = '%s -m timeit -n %s -r %s '%( \
#			path, \
#			self.number.GetValue(), \
#			self.repeat.GetValue())
#		if setup:
#			cmd += '-s ' + '"%s"'%setup + ' '
#		cmd += '"%s"'%stmt
#		print cmd
#		p = subprocess.Popen(cmd, shell = True, \
#				cwd = os.path.dirname(path), \
#				stderr = subprocess.PIPE, \
#				stdout = subprocess.PIPE)
#		p.wait()
		
#		tmp_file = os.getcwd() + '%d.py'%self.GetId()
#		f = open(tmp_file, 'w')
#		f.write(timeit_file_template%(stmt, setup, \
#			self.number.GetValue(), \
#			self.repeat.GetValue()))
#		f.close()
#		p = subprocess.Popen('python '+tmp_file, \
#				shell = True, \
#				cwd = os.path.dirname(path), \
#				stderr = subprocess.PIPE, \
#				stdout = subprocess.PIPE)
#		p.wait()
#		

#		self.result.SetValue( \
#			'============ Error ============\n' \
#			+ p.stderr.read() \
#			+ '============== Output ==========\n' \
#			+ p.stdout.read() )
#		if self.resultbtn.closed:
#			self.OnResultbtn(None)
		import util
		tmp_file = util.GenWritablePath('%d.py'%self.GetId())
		f = open(tmp_file, 'w')
		f.write(timeit_file_template%(stmt, setup, \
			self.number.GetValue(), \
			self.repeat.GetValue()))
		f.close()
		
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
				self.result.SetValue( \
					'============ Error ============\n' \
					+ getstr(inst.GetErrorStream()) \
					+ '\n============ Output ============\n' \
					+ getstr(inst.GetInputStream()))
				self.result.ShowPosition(self.result.GetLastPosition())
				if self.resultbtn.closed:
					self.OnResultbtn(None)
				os.remove(tmp_file)
				
		if ' ' in tmp_file:
			tf = '"%s"'%(tmp_file, )
		else:
			tf = tmp_file
		cmd = '%s '%self.pypath + tf
		proc = TimeitProc(self)
		proc.Redirect()
		wx.Execute(cmd, process = proc)
		
	def OnClose(self, evt):
#		self.pathoption.SetPath(self.path.GetValue())
		self.Destroy()
		
	def Reset(self):
		self.stmt.SetValue('')
		self.setup.SetValue('')
		self.number.SetValue(1000000)
		self.repeat.SetValue(3)
		
	def Fit(self):
		if not self.IsShown():
			return
		self.GetSizer().Fit(self)
		self.SetSize(dlgsize)
		
def _ShowTimeitDlg(parent, pypath):
	dlg = TimeitDlg(parent, wx.NewId(), \
		'Timeit wizard (step 2: Timeit)', \
		python_path = pypath)
	dlg.Show()
	
def DoTimeit(parent):
	import util
	from askpypathdlg import AskPythonPathDlg
	pypathdlg = AskPythonPathDlg(parent, \
			wx.ID_ANY, \
			'Timeit wizard (step 1: setup python path)', \
			cfg = util.GenCfgPath('option', 'timeitpath.cfg'))
	retcode = pypathdlg.ShowModal()
	if retcode != wx.ID_OK:
		return
	pypath = pypathdlg.GetPath()
	pypathdlg.Destroy()
	_ShowTimeitDlg(parent, pypath)
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
#	ShowTimeitDlg(None)
	DoTimeit(None)
	app.MainLoop()