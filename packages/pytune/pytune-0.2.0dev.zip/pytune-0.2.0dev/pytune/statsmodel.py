# -*- coding:utf-8 -*-

import my_stats

fln_str_func = lambda fln:('%s'%fln[2], '%s:%d'%fln[:2])

def make_data(stats):
	data = []
	for k, v in stats.iteritems():
		idx, fln, d = v
		if d[0] == 0:
			continue
		d = ('%d/%d'%(d[3],d[0]),	# ncalls
			'%8.5f'%d[1], 			# tottime
			'%8.5f'%(d[1]/d[0],), 	# t_percall
			'%8.5f'%d[2],			# cumtime
			'%8.5f'%(d[2]/d[0],), 	# c_percall
			)
		data.append((str(idx),) + fln_str_func(fln) + d)
	return data
	
def make_calls_data(stats):
	data = [ \
		((str(i),) + fln_str_func(fln) + ('%d'%cnt, '%8.5f'%ct)) \
		for (i, fln, cnt, ct) in stats.itervalues() ]
	return data
	
def make_chart_data(stats):
	fln_str_func2 = lambda fln:'%s(%s:%d)'%(fln[2], fln[0], fln[1])
	data = [ \
		(fln_str_func2(fln), ct) for (i, fln, cnt, ct) in stats.itervalues() ]
	return data

class StatsModel(object):
	def __init__(self, fn = None):
		if fn:
			self.reset_stats(fn)
		else:
			self.stats = None
		
	def add_stats(self, *a):
		if not self.stats:
			self.reset_stats(*a)
			return
		self.stats.add_stats(*a)
		self.data = self.__make_data(self.stats.get_stats())
		
	def reset_stats(self, *a):
		self.stats = my_stats.Stats()
		self.stats.add_stats(*a)
		self.stats_data = self.stats.get_stats()
		self.data = make_data(self.stats_data)
		
	def get_data(self):
		return self.data
		
	def get_stats_data(self):
		return self.stats_data
		
	def get_callees(self, idx):
		return self.stats.get_callees( \
			self.get_func_by_idx(idx))
		
	def get_callers(self, idx):
		return self.stats.get_callers( \
			self.get_func_by_idx(idx))
		
	def get_fln_by_idx(self, idx):
		f, l, n = self.get_func_by_idx(idx)
		f = f.rpartition('\\')[-1]
		return '%s(%s:%s)'%(n, f, l)
		
	def get_func_by_idx(self, idx):
		for func, v in self.stats_data.iteritems():
			if v[0] == idx:
				return func
		return None
	
	def get_fln_by_func(self,func):
		f, l, n = func
		f = f.rpartition('\\')[-1]
		return '%s(%s:%s)'%(n, f, l)

	def get_idx_by_func(self,func):
		return self.stats_data[func][0]
	
	def save_stats(self, path):
		self.stats.save(path)