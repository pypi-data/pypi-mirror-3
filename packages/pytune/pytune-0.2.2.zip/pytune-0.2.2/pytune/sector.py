# -*- coding:utf-8 -*-
import math

PI = math.pi

class Vector(object):
	def __init__(self, x, y):
		super(Vector, self).__init__()
		self.x = x
		self.y = y
		self.r = math.sqrt(self.x**2 + self.y**2)
		if self.r:
			self.theta = math.acos(self.x/self.r)
			if self.y < 0:
				self.theta = -self.theta
		else:
			self.theta = 0.0

	def copy(self):
		return Vector(self.x, self.y)

	def dot(self, other):
		return self.x*other.x + self.y*other.y

	def theta(self):
		return self.theta

	def rotate(self, rad):
		self.theta -= rad
		self.x = int(round(self.r*math.cos(self.theta)))
		self.y = int(round(self.r*math.sin(self.theta)))

	def __abs__(self):
		return self.r

	def __add__(self, other):
		return Vector(self.x+other.x, self.y+other.y)

	def __sub__(self, other):
		return Vector(self.x-other.x, self.y-other.y)

	def __str__(self):
		return "(%s, %s)"%(str(self.x), str(self.y))
	
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y
		
class Sector(object):
	def __init__(self, center, rad, start_point):
		super(Sector, self).__init__()
		assert 0 <= rad <= 2*PI
		self.center = center
		self.rad = rad
		self.start = start_point
		self.radius = math.sqrt((self.center.x-self.start.x)**2 + (self.center.y-self.start.y)**2)
		self.start_vector = self.start - self.center
		
		self.end = self.start_vector.copy()
		self.end.rotate(self.rad)
		self.end = self.end + self.center
		
		self.key_point = self.start_vector.copy()
		self.key_point.rotate(self.rad/2)
		self.key_point.x = self.key_point.x/2
		self.key_point.y = self.key_point.y/2
		self.key_point = self.key_point + self.center
		
		#print "sector theta: %s"%(str(self.start_vector.theta))

	def is_in(self, point):
		p = point - self.center
		if abs(p) > self.radius:
			return False
		delta_theta = p.theta - self.start_vector.theta
		if delta_theta > 0:
			return (2*PI - self.rad) <= delta_theta
		else:
			return self.rad >= abs(delta_theta)

	def __str__(self):
		return "sector info: %s, start: %s, end: %s, rad: %s"%(self.center, self.start, self.end, str(self.rad))
	
	def __radd__(self, other):
		return other + self.rad

if __name__ == "__main__":
	s = Sector(Vector(1, 0), PI, Vector(2, 2))
	print s
	print "end: %s"%(s.end)
	print "key: %s"%(s.key_point)
	print s.is_in(Vector(2, 2))
	print s.is_in(Vector(2, 3))
	print s.is_in(Vector(1, 2))
	print s.is_in(Vector(-2, 2))
	print s.is_in(Vector(-2, -2))
	print s.is_in(Vector(-2, -2))
	
