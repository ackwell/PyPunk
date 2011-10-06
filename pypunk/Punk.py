Engine = None

def SetWorld(world):
	"""Set the world"""
	if Engine.World: Engine.WorldChanged()
	Engine.World = world

#Timing
elapsed = 0
FPS = 0