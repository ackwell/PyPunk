from pypunk.core import PP, Engine, World, Entity
from pypunk.graphics import Image
from pypunk.geom import Rectangle


class GameWorld(World):
	def __init__(self):
		super().__init__()
		PP.screen.color = 0x333333
		game_entity = GameEntity()
		self.add(game_entity)


class GameEntity(Entity):
	def __init__(self):
		super().__init__()
		self.x = 100
		self.y = 100
		self.graphic = Image('EntityImage.png', Rectangle(1, 1, 20, 20))
		self.graphic.center_origin()
		self.graphic.scale_y = 2
		self.graphic.scale = 0.5

	def update(self):
		pass#self.graphic.angle += 1


if __name__ == '__main__':
	# Create an instance of the Engine, add a world, start it up
	engine = Engine(800, 600, 60, "PyPunk Test")
	PP.world = GameWorld()
	engine.begin()

