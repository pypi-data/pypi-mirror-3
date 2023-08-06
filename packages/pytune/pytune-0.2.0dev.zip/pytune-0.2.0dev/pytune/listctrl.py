# -*- coding:utf-8 -*-

import wx
import wx.lib.mixins.listctrl as listmix
from list_mixin import ListCtrlSortMixin, FilterMixin, int_cmp, str_cmp, float_cmp
import os
import re

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		self._createColumn()
		self.itemMap = []
		self.ref_dict = {}

		
		
	def _createColumn(self):
		raise NotImplementedError, 'ListCtrl is a abstract class.'
		
	def reset(self, data):
		self.DeleteAllItems()
		self.itemMap = []
		self.ref_dict = {}
		data.sort(cmp = lambda x, y: cmp(int(x[0]), int(y[0])))
		for idx, row in enumerate(data):
			self.ref_dict[int(row[0])] = idx
			self.itemMap.append(row)
			self.insert_data(idx, row)
		
	def insert_data(self, idx, data):
		self.InsertStringItem(idx, str(data[0]))
		self.SetItemData(idx, idx)	# for sort
		for col, txt in enumerate(data):
			if col == 0:
				continue
			self.SetStringItem(idx, col, str(txt))
			
def fl_cmp(l, r):
	l = l.split(':')
	r = r.split(':')
	cmpVal = cmp(l[0], r[0])
	if 0 == cmpVal:
		return cmp(int(l[1]), int(r[1]))
	return cmpVal
	
def ncalls_cmp(l, r):
	l = l.split('/')
	r = r.split('/')
	cmpVal = cmp(int(l[0]), int(r[0]))
	if 0 == cmpVal:
		return cmp(int(l[1]), int(r[1]))
	return cmpVal
	
class StatsListCtrl(ListCtrl, ListCtrlSortMixin):
	ID = 'ID'
	FUNC_NAME = 'func_name'
	FL = 'file:line'
	NCALLS = 'ncalls'
	TOTTIME = 'tottime'
	T_PERCALL = 't_percall'
	CUMTIME = 'cumtime'
	C_PERCALL = 'c_percall'
	columns = (ID, FUNC_NAME, FL, NCALLS, TOTTIME, \
		T_PERCALL, CUMTIME, C_PERCALL)
	sorters = (int_cmp, str_cmp, fl_cmp, ncalls_cmp, \
		float_cmp, float_cmp, float_cmp, float_cmp)
	
	
	
	def __init__(self, *a, **k):
		super(StatsListCtrl, self).__init__(*a, **k)
		ListCtrlSortMixin.__init__(self, StatsListCtrl.sorters)	# for sort
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_func, self)
		self.selected_callback = None
		
	def reset(self, data):
		super(StatsListCtrl, self).reset(data)
		# set func_name and file:line columns autosize
		self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		# sort by cumtime
		self.SortListItems(6, False)
		
	def _createColumn(self):
		for i, col in enumerate(StatsListCtrl.columns):
			self.InsertColumn(i, col)
	
	def selected_func(self, evt):
		if self.selected_callback:
			self.selected_callback(evt)

class FilterStatsListCtrl(StatsListCtrl, FilterMixin):
	def __init__(self, *a, **k):
		StatsListCtrl.__init__(self, *a, **k)
		FilterMixin.__init__(self)
		
	def reset(self, data, needreplace = True):
		FilterMixin.reset(self, data, needreplace)
		StatsListCtrl.reset(self, data)
	
	def OnFilter(self, func_rest, file_rest):
		if func_rest:
			data = self.generic_filter(func_rest, self.data, 1, None)
		else:
			data = self.data
			
		if file_rest:
			def getfilename(s):
				return s.partition(':')[0]
			data = self.generic_filter(file_rest, data, 2, getfilename)

		self.reset(data, False)
				
	def OnAll(self):
		self.reset(self.data, False)
		
	def generic_filter(self, rest, data, col, getdata = None):
		try:
			p = re.compile(rest, re.I)
		except:
			from traceback import print_exc
			import sys
			print_exc(file = sys.stdout)
			return data
		if getdata:
			ret = [i for i in data if p.match(getdata(i[col]))]
		else:
			ret = [i for i in data if p.match(i[col])]
		return ret
		
class CallListCtrl(ListCtrl, ListCtrlSortMixin):
	ID = 'ID'
	FUNC_NAME = 'func_name'
	FL = 'file:line'
	NCALLS = 'ncalls'
	TOTTIME = 'tottime'
	columns = (ID, FUNC_NAME, FL, NCALLS, TOTTIME)
	sorters = (int_cmp, str_cmp, fl_cmp, ncalls_cmp, float_cmp)
	
	def __init__(self, *a, **k):
		super(CallListCtrl, self).__init__(*a, **k)
		ListCtrlSortMixin.__init__(self, CallListCtrl.sorters)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_func, self)
		
		self.data_list = []
	
	def reset(self, data):
		tmp_data = []
		for i in data:
			tmp_data.append(i)
			
		from statsmodel import make_calls_data
		data = make_calls_data(data)
		
		self.data_list = [0]*(len(data)+1)
		for i,a in enumerate(data):
			self.data_list[int(a[0])] = tmp_data[i]
			
		super(CallListCtrl, self).reset(data)
		self.SortListItems(4, False)
		
	def Clear(self):
		self.reset({})
		
	def _createColumn(self):
		for i, col in enumerate(CallListCtrl.columns):
			self.InsertColumn(i, col)
		
	def selected_func(self, evt):
		if self.selected_callback:
			idx = int(self.GetItemText(evt.GetIndex()))
			self.selected_callback(self.data_list[idx])

			
class HistoryListCtrl(wx.ListCtrl):
	ID = 'ID'
	FUNC_NAME = 'func_name'
	FL = 'file:line'
	columns = (ID, FUNC_NAME, FL)
	widths = (50,150,150)

	def __init__(self, *a, **k):
		super(HistoryListCtrl, self).__init__(*a, **k)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_func, self)
		self.data_list = []
		self.length = 0
		self.isHistoryHit = False
		self.iterator = 0
		self.focus_id = 0
		self._createColumn()
	
	def insert_data(self, idx, data):
		self.InsertStringItem(0, str(idx))
		self.SetStringItem(0, 1, str(data[0]))
		self.SetStringItem(0, 2, str(data[1]))
		
	def my_focus(self, itemid):
		self.focus_id = itemid
		self.Focus(self.focus_id)
		self.Select(self.focus_id)
		
	def insert(self, data):
		while self.iterator + 1 < self.length:
			self.pop()
		self.data_list.append(data)
		data = (data[2], os.path.basename(data[0]) + ':' + str(data[1]))
		self.insert_data(self.length, data)
		self.my_focus(0)
		self.length += 1
		self.iterator = self.length
		
	def Clear(self):
		while self.length > 0:
			self.pop()
		self.iterator = 0
		self.focus_id = 0
		
	def pop(self):
		self.data_list.pop()
		self.length -= 1
		self.DeleteItem(0)
		
	def _createColumn(self):
		for i, col in enumerate(HistoryListCtrl.columns):
			self.InsertColumn(i, col, width = HistoryListCtrl.widths[i])
			
	def Redo(self):
		if self.iterator >= self.length-1:
			return
		self.iterator += 1
		self.my_focus(self.focus_id - 1)
	
	def Undo(self):
		if self.iterator <= 0:
			return
		self.iterator -= 1
		self.my_focus(self.focus_id + 1)
		
	def selected_func(self, evt):
		if self.selected_callback:
			self.isHistoryHit = True
			self.focus_id = int(evt.GetIndex())
			idx = int(self.GetItemText(evt.GetIndex()))
			self.iterator = idx
			self.selected_callback(self.data_list[idx])

class LoadedListCtrl(wx.ListCtrl):
	ID = 'ID'
	FILE_NAME = 'file_name'
	PATH = 'path'
	columns = (ID, FILE_NAME, PATH)
	widths = (50,100,200)

	def __init__(self, *a, **k):
		super(LoadedListCtrl, self).__init__(*a, **k)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_func, self)
		self.stats_list = []
		self.data_list = []
		self.file_dict = {}
		self.lenght = 0
		self.iterator = 0
		self.focus_id = 0
		self._createColumn()

	def insert(self, data, stats):
		print data
		if self.file_dict.has_key(data):
			self.stats_list[self.file_dict[data]] = stats
		else:
			self.file_dict[data] = self.lenght
			self.data_list.append(data)
			self.stats_list.append(stats)
			self.lenght += 1
			self.insert_data(self.lenght, data)

	def insert_data(self, idx, data):
		self.InsertStringItem(idx-1, str(idx))
		self.SetStringItem(idx-1, 1, str(data[0]))
		self.SetStringItem(idx-1, 2, str(data[1]))
		
	def selected_func(self, evt):
		self.focus_id = int(evt.GetIndex())
		idx = int(self.GetItemText(evt.GetIndex()))
		self.selected_callback(self.stats_list[idx-1])

	def _createColumn(self):
		for i, col in enumerate(LoadedListCtrl.columns):
			self.InsertColumn(i, col, width = LoadedListCtrl.widths[i])