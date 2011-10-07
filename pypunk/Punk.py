import random

Engine = None

elapsed = 0
FPS = 0

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