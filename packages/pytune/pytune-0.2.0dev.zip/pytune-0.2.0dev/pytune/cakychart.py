# -*- coding:utf-8 -*-

import wx
from sector import Sector, Vector, PI

PI2 = PI * 2

MAX_WIDTH = 600
MAX_HEIGHT = 800

TEXT_COLOR = "BLACK",

COLORS = (
	"BLUE",
	"BLUE VIOLET",
	"BROWN",
	"CYAN",
	"DARK GREY",
	"GOLD",
	"GREY",
	"GREEN",
	"MAGENTA",
	"NAVY",
	"PINK",
	"RED",
	"SKY BLUE",
	"VIOLET",
	"YELLOW",
	"DARK GREEN",
	)
	
ROUND_OFFSET = 10

TITLE_FONT_SIZE = 14

TITLE_HEIGHT = 0

ROW_SPACING = 5

def attr_defend(getters, setters):
	def func_decorator(func):
		def defender(self, obj, *a, **k):
			values = [getter(obj) for getter in getters]
			ret = func(self, obj, *a, **k)
			for setter, arg in zip(setters, values):
				setter(obj, arg)
			return ret
		return defender
	return func_decorator
	
class CakyChart(wx.Panel):
	def __init__(self, parent, ID, size = wx.DefaultSize, *a, **k):
		super(CakyChart, self).__init__(parent, ID, (0, 0),*a, **k) 
		
		self.tooltip = wx.ToolTip('')
		self.SetToolTip(self.tooltip)
		
		self.update_param()
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LEFT_UP, self.LeftUp)
		
		self.names = []
		self.angles = []
		self.sectors = []
		self.label_pos = []
		self.func_name = []
		
		self.selected_callback = None
		self.undo_callback = None
		self.redo_callback = None

	def update_param(self):
		'''
		if width >= height:
			|----------------------------------|
			|            Title Rect            |
			|----------------------------------|
			|                 |                |
			|     Caky        |     Label      |
			|     Rect        |     Rect       |
			|                 |                |
			|                 |                |
			|                 |                |
			|                 |                |
			|----------------------------------|
		else:
			|-----------------------|
			|       Title Rect      |
			|-----------------------|
			|                       |
			|                       |
			|                       |
			|       Caky Rect       |
			|                       |
			|                       |
			|                       |
			|-----------------------|
			|                       |
			|                       |
			|                       |
			|      Label Rect       |
			|                       |
			|                       |
			|                       |
			|-----------------------|
		'''
		w, h = self.GetClientSizeTuple()
		mid = w/4*3
		self.back_rect = (mid, 0, TITLE_HEIGHT*2, TITLE_HEIGHT)
		self.forward_rect = (mid + TITLE_HEIGHT*2, 0, TITLE_HEIGHT*2, TITLE_HEIGHT)
		self.title_rect = (0, 0, mid, TITLE_HEIGHT)
		
		if w >= h:
			width, height = w // 2, h - TITLE_HEIGHT
			self.caky_rect = (0, TITLE_HEIGHT, width, height)
			self.label_rect = (width, TITLE_HEIGHT, width, height)
		else:
			width, height = w, h // 2
			self.caky_rect = (0, TITLE_HEIGHT, width, height)
			self.label_rect = (0, TITLE_HEIGHT + height, width, height)
			
	def LeftUp(self, evt):
		x, y = evt.GetPosition()
		rt = self.label_rect
		if x>self.back_rect[0] and x<self.back_rect[0]+self.back_rect[2] and \
		   y>self.back_rect[1] and y<self.back_rect[1]+self.back_rect[3]:
			self.undo_callback()

		if x>self.forward_rect[0] and x<self.forward_rect[0]+self.forward_rect[2] and \
		   y>self.forward_rect[1] and y<self.forward_rect[1]+self.forward_rect[3]:
			self.redo_callback()
			
		if x<rt[0] or x>rt[0]+rt[2] or y<rt[1] or y>rt[1]+rt[3]:
			return
		for i in xrange(len(self.label_pos)):
			if y<self.label_pos[i]+self.line_height and y>self.label_pos[i] and self.selected_callback:
				self.selected_callback(self.func_name[i][0])
		
	def OnPaint(self, evt):
		dc = wx.PaintDC(self)
		self.PrepareDC(dc)
		dc.BeginDrawing()
		if (not self.names) or (not self.sectors):
			self.draw_bg(dc)
		else:
			self.draw(dc)
		dc.EndDrawing()
		
	def OnMotion(self, evt):
		self.mouse = Vector(evt.m_x, evt.m_y)
		for i, sec in enumerate(self.sectors):
			if sec.is_in(self.mouse):
				self.tooltip.SetTip(self.names[i])
				return
		self.tooltip.SetTip('')
		
	def OnSize(self, evt):
		self.update_param()
		
		self.Refresh()
		
	def reset(self, title_text, data):
		self.func_name = [ (a, data[a][3]) for (a) in data.iterkeys() ]
		self.func_name.sort(cmp = lambda x, y: cmp(x[1], y[1]), reverse = True)
		from statsmodel import make_chart_data
		
		data = make_chart_data(data)
		self.title_text = title_text
		
		data.sort(cmp = lambda x, y: cmp(x[1], y[1]), reverse = True)
		self.names = [i[0] for i in data]
		data = [i[1] for i in data]
		
		data_sum = sum(data)
		if data_sum == 0:
			self.angles = [0 for i in data]
			for i, (name, d) in enumerate(zip(self.names, data)):
				if name == self.title_text:
					name = '===internal==='
				self.names[i] = '%.2f%% %s'%( 0, name)
		else:
			self.angles = [PI2 * (i / data_sum) for i in data]
			for i, (name, d) in enumerate(zip(self.names, data)):
				if name == self.title_text:
					name = '===internal==='
				self.names[i] = '%.2f%% %s'%( d / data_sum * 100, name)
		self.make_sectors(self.angles)
		
		self.Update()
		self.Refresh(True)
		
	def Clear(self):
		self.reset('',{})
		
	def make_sectors(self, angles):
		l, t, w, h = self.caky_rect
		half_w, half_h = w // 2, h // 2
		centre = Vector(l + half_w, t + half_h)
		radius = min(half_w, half_h) - ROUND_OFFSET
		if radius < 0:
			self.radius = 0
		start = Vector(centre.x, centre.y - radius)
		self.sectors = []
		for angle in angles:
			sec = Sector(centre, angle, start)
			start = sec.end.copy()
			self.sectors.append(sec)
		self.make_data_valid()
		
	def make_data_valid(self):
		c_len = len(COLORS)
		if len(self.names) <= c_len:
			return
		#tiny_sec = self.sectors[c_len-1:]
		#print tiny_sec
		#tiny_sec_sum = sum(tiny_sec)
		
		#self.name = self.names[:c_len]
		#self.names[-1] = 'Other'
		#self.sectors = self.sectors[:c_len]
		#self.angles[-1] = tiny_sec_sum
		#assert len(self.sectors) == c_len == len(self.names)
		
	def draw(self, dc):
		self.make_sectors(self.angles)
		self.draw_bg(dc)
		#self.draw_title(dc)
		self.draw_caky(dc)
		self.draw_label(dc)
		
	@attr_defend( \
		(wx.PaintDC.GetPen, wx.PaintDC.GetBrush), \
		(wx.PaintDC.SetPen, wx.PaintDC.SetBrush))
	def draw_bg(self, dc):
		w, h = self.GetClientSizeTuple()
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.SetPen(wx.Pen(wx.Colour(0xFF, 0xFF, 0xFF), 1, wx.SOLID))
		dc.DrawRectangle(0, 0, w, h)
		
	@attr_defend((wx.PaintDC.GetFont,), (wx.PaintDC.SetFont,))
	def draw_title(self, dc):
		dc.SetFont(wx.Font(TITLE_FONT_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD))
		w = self.GetClientSizeTuple()[0]
		dc.DrawLabel(self.get_valid_text(self.title_text, dc, w), \
			wx.Rect(*self.title_rect), wx.ALIGN_CENTRE)
		#dc.SetBrush(wx.BLUE_BRUSH)
		#print self.title_rect
		#dc.SetBrush(wx.BLUE_BRUSH)
		#dc.DrawRectangle(*self.back_rect)
		#dc.SetBrush(wx.GREEN_BRUSH)
		#dc.DrawRectangle(*self.forward_rect)
		dc.DrawLabel('<<<',wx.Rect(*self.back_rect), wx.ALIGN_CENTRE)
		dc.DrawLabel('>>>',wx.Rect(*self.forward_rect), wx.ALIGN_CENTRE)
		
	@attr_defend( \
		(wx.PaintDC.GetPen, wx.PaintDC.GetBrush), \
		(wx.PaintDC.SetPen, wx.PaintDC.SetBrush))
	def draw_caky(self, dc):
		for name, sec, color in zip(self.names, self.sectors, COLORS):
			dc.SetPen(wx.Pen(color))
			dc.SetBrush(wx.Brush(wx.NamedColour(color)))
			if sec.start == sec.end and color != COLORS[0]: # not first sector
				break
			dc.DrawArc(sec.start.x, sec.start.y, \
						sec.end.x, sec.end.y, \
						sec.center.x, sec.center.y)
	@attr_defend( \
		(wx.PaintDC.GetBrush, ), \
		(wx.PaintDC.SetBrush, ))
	def draw_label(self, dc):
		from itertools import count, izip
		
		side = max(dc.GetCharWidth(), dc.GetCharHeight())
		text_pos_x_offset = side + ROW_SPACING
		self.line_height = side + ROW_SPACING
		while len(self.label_pos)>0:
			self.label_pos.pop()
		l, t, w, h = self.label_rect
		l += ROUND_OFFSET
		
		max_lines_cnt = h // self.line_height
		lines_cnt = len(self.names)
		need_more_spaces = max_lines_cnt <= lines_cnt
		if not need_more_spaces:
			t += int((max_lines_cnt - lines_cnt) / 2.0 * self.line_height)
			
		for i, (top, name, color) in \
				enumerate(izip(count(), self.names, COLORS)):
			top = top * self.line_height + t
			if need_more_spaces and i >= max_lines_cnt:
				old_color = dc.GetTextForeground()
				dc.SetTextForeground(color)
				dc.DrawText('Need more spaces...', l, top)
				dc.SetTextForeground(old_color)
				break
			# draw mark
			dc.SetBrush(wx.Brush(wx.NamedColour(color)))
			dc.DrawRectangle(l, top, side, side)
			
			# draw text
			name = self.get_valid_text(name, dc, w - text_pos_x_offset)
			self.label_pos.append(top)
			dc.DrawText(name, l + text_pos_x_offset, top)
		
	def get_max_str_len(self):
		return len(max(self.names, key = len))
		
	def get_valid_text(self, text, dc, w):
		cc = int(w / dc.GetCharWidth()) - 2
		if len(text) <= cc:
			return text
		return text[:cc - 3]+'...'
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, wx.ID_ANY, size = (600,400))
	cc = CakyChart(frame, wx.ID_ANY, (0,0), style=wx.SUNKEN_BORDER)
	cc.reset('Lai Yonghao \'s Caky Chart', \
		[('str', 0.3), ('foo', 0.5), ('bar', 0.4)])
	#cc = wx.ScrolledWindow(frame, wx.ID_ANY, (0,0), style=wx.SUNKEN_BORDER)
	frame.Centre()
	frame.Show(True)
	app.MainLoop()