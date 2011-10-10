import random

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

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
Punk = _punk()