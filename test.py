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
		self.graphic = Image('EntityImage.png')
		self.graphic.center_origin()
		self.graphic.smooth = True
		self.graphic.scale = 1.5

	def update(self):
		self.graphic.alpha = (self.graphic.alpha + 0.02)%1
		self.graphic.scale = (self.graphic.scale-1 + 0.1)%2 + 1
		print(self.graphic.scale)


if __name__ == '__main__':
	# Create an instance of the Engine, add a world, start it up
	engine = Engine(800, 600, 60, "PyPunk Test")
	PP.world = GameWorld()
	engine.begin()

