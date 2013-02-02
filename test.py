from pypunk.core import PP, Engine, World, Entity

class GameWorld(World):
	def __init__(self):
		super().__init__()
		game_entity = GameEntity()
		self.add(game_entity)


class GameEntity(Entity):
	def __init__(self):
		super().__init__()

	def added(self):
		print('added')

	def update(self):
		print('update')


if __name__ == '__main__':
	# Create an instance of the Engine, add a world, start it up
	engine = Engine(800, 600, 60, "PyPunk Test")
	PP.world = GameWorld()
	engine.begin()
