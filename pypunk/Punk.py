import random, math

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	
	def normalize(self, scale):
		norm = math.sqrt(self.x*self.x+self.y*self.y)
		if not norm == 0:
			self.x = scale * self.x / norm
			self.y = scale * self.y / norm

#So we can use properties and such :3
class _punk(object):
	def __init__(self):
		self.Engine = None
		self.elapsed = 0
		self.FPS = 0

		self.width = 0
		self.height = 0

		self.camera = Point()
	
	def set_world(self, value):
		if self.Engine.World: self.Engine.WorldChanged()
		self.Engine.World = value
	world = property(lambda self: self.Engine.World, set_world)

	buffer = property(lambda self: self.Engine.App)

	screen = property(lambda self: self.Engine.App.Capture())

	def choose(self, *args):
		return args[random.randint(0, len(args)-1)]
	
	def sign(self, value):
		return -1 if value < 0 else 1 if value > 0 else 0
	
	def distance(self, x1, y1, x2=0, y2=0):
		return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
	
	def stepTowards(self, object, x, y, distance=1):
		point = Point(x - object.x, y - object.y)
		if self.distance(0, 0, point.x, point.y) <= distance:
			object.x = x
			object.y = y
			return
		point.normalize(distance)
		object.x += point.x
		object.y += point.y

Punk = _punk()