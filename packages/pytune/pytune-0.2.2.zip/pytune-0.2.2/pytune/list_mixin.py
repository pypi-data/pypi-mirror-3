# -*- coding:utf-8 -*-

import wx
import cStringIO

#----------------------------------------------------------------------
def getSmallUpArrowData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00<IDAT8\x8dcddbf\xa0\x040Q\xa4{h\x18\xf0\xff\xdf\xdf\xffd\x1b\x00\xd3\
\x8c\xcf\x10\x9c\x06\xa0k\xc2e\x08m\xc2\x00\x97m\xd8\xc41\x0c \x14h\xe8\xf2\
\x8c\xa3)q\x10\x18\x00\x00R\xd8#\xec\xb2\xcd\xc1Y\x00\x00\x00\x00IEND\xaeB`\
\x82' 

def getSmallUpArrowBitmap():
    return wx.BitmapFromImage(getSmallUpArrowImage())

def getSmallUpArrowImage():
    stream = cStringIO.StringIO(getSmallUpArrowData())
    return wx.ImageFromStream(stream)

#----------------------------------------------------------------------
def getSmallDnArrowData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00HIDAT8\x8dcddbf\xa0\x040Q\xa4{\xd4\x00\x06\x06\x06\x06\x06\x16t\x81\
\xff\xff\xfe\xfe'\xa4\x89\x91\x89\x99\x11\xa7\x0b\x90%\ti\xc6j\x00>C\xb0\x89\
\xd3.\x10\xd1m\xc3\xe5*\xbc.\x80i\xc2\x17.\x8c\xa3y\x81\x01\x00\xa1\x0e\x04e\
?\x84B\xef\x00\x00\x00\x00IEND\xaeB`\x82" 

def getSmallDnArrowBitmap():
    return wx.BitmapFromImage(getSmallDnArrowImage())

def getSmallDnArrowImage():
    stream = cStringIO.StringIO(getSmallDnArrowData())
    return wx.ImageFromStream(stream)

DESCENDING = True

class ListCtrlSortMixin(object):
	def __init__(self, sorters):
		self.sorters = sorters
		self.sort_flag = [DESCENDING] * len(sorters)
		self._col = 0
		
		self.il = wx.ImageList(16, 16)
		self.arrow_images = ( \
			self.il.Add(getSmallDnArrowBitmap()),
			self.il.Add(getSmallUpArrowBitmap()))
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
		
	def SortListItems(self, col, ascending = True):
		self.ClearColumnImage(self._col)
		self._col = col
		self.sort_flag[col] = ascending
		self.SortItems(self._ColSorter)
		self.SetColumnImage(col, self.arrow_images[self.sort_flag[col]])
		
		
	def OnColClick(self, evt):
		self.ClearColumnImage(self._col)
		self._col = col= evt.GetColumn()
		self.sort_flag[col] ^= True
		self.SortItems(self._ColSorter)
		self.SetColumnImage(col, self.arrow_images[self.sort_flag[col]])
		
	def _ColSorter(self, key1, key2):
		text1 = self.itemMap[key1][self._col]
		text2 = self.itemMap[key2][self._col]
		cmpVal = self.sorters[self._col](text1, text2)
		
		
		return cmpVal if self.sort_flag[self._col] else -cmpVal
	def _GetText(self, idx, col):
		return self.GetItem(idx, col).GetText()
		
str_cmp = cmp

def int_cmp(str1, str2):
	return cmp(int(str1), int(str2))
	
def float_cmp(str1, str2):
	return cmp(float(str1), float(str2))
	
class FilterMixin(object):
	def __init__(self):
		self.data = []
		
	def reset(self, data, needreplace = True):
		if needreplace:
			self.data = data