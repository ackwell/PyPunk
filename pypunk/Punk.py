import random

Engine = None

def SetWorld(world):
	"""Set the world"""
	if Engine.World: Engine.WorldChanged()
	Engine.World = world

def SetBGColor(r, g, b):
	Engine.bgColor = (r, g, b)

#Timing
elapsed = 0
FPS = 0

def choose(*args):
	return args[random.randint(0, len(args)-1)]