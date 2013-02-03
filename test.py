from pypunk.core import PP, Engine, World, Entity
from pypunk.graphics import Image
from pypunk.utils import Input, Key


class GameWorld(World):
	def __init__(self):
		super().__init__()
		PP.screen.color = 0x202020
		game_entity = GameEntity()
		self.add(game_entity)


class GameEntity(Entity):
	def __init__(self):
		super().__init__()
		self.graphic = Image('EntityImage.png')

		Input.define('UP', Key.W, Key.UP)
		Input.define('DOWN', Key.S, Key.DOWN)
		Input.define('LEFT', Key.A, Key.LEFT)
		Input.define('RIGHT', Key.D, Key.RIGHT)

		self.type = 'GameEntity'


	def update(self):
		if Input.check('LEFT'):
			self.x -= 50 * PP.elapsed
		if Input.check('RIGHT'):
			self.x += 50 * PP.elapsed
		if Input.check('UP'):
			self.y -= 50 * PP.elapsed
		if Input.check('DOWN'):
			self.y += 50 * PP.elapsed


if __name__ == '__main__':
	# Create an instance of the Engine, add a world, start it up
	engine = Engine(800, 600, 60, "PyPunk Test")
	PP.world = GameWorld()
	engine.begin()

