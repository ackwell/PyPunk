import random

Engine = None

elapsed = 0
FPS = 0

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

def SetWorld(world):
	"""Set the world"""
	if Engine.World: Engine.WorldChanged()
	Engine.World = world

def SetBGColor(r, g, b):
	Engine.bgColor = (r, g, b)

def GetScreen():
	img = Engine.App.Capture()
	img.SetSmooth(False)
	return img

def choose(*args):
	return args[random.randint(0, len(args)-1)]
