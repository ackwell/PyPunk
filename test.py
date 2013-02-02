from pypunk.core import PP, Engine, World

class GameWorld(World):
	def __init__(self):
		super().__init__()


if __name__ == '__main__':
	# Create an instance of the Engine, add a world, start it up
	engine = Engine(800, 600, 60, "PyPunk Test")
	PP.world = GameWorld()
	engine.begin()
