# -*- coding:utf-8 -*-

class Singleton(object):
	"""
	>>> class SingleSpam(Singleton):
	... 	def __init__(self, s): self.s = s
	... 	def __str__(self): return self.s
	>>> s1 = SingleSpam('spam')
	>>> print str(s1)
	spam
	>>> s2 = SingleSpam('eggs')
	>>> print str(s2)
	eggs
	>>> print id(s1) == id(s2)
	True
	
	>>> obj = Singleton()
	Traceback (most recent call last):
		...
	NotImplementedError: Don't call Singleton.__init__
	
	Don't call super(...).__init__()
	>>> class OtherSingleton(Singleton):
	... 	def __init__(self):
	... 		super(OtherSingleton, self).__init__()
	>>> OtherSingleton()
	Traceback (most recent call last):
		...
	NotImplementedError: Don't call Singleton.__init__
	"""
	def __new__(cls, *args, **kwargs):
		if '_inst' not in vars(cls):
			cls._inst = object.__new__(cls, *args, **kwargs)
		return cls._inst
		
	def __init__(self, *a, **k):
		raise NotImplementedError, 'Don\'t call Singleton.__init__'
		
	@classmethod
	def inst(self):
		return self._inst
		
if __name__ == '__main__':
	import doctest
	doctest.testmod()