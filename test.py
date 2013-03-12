from pypunk.core import PP, Engine, World, Entity, Tween
from pypunk.graphics import Image, Spritemap, Text, Graphiclist
from pypunk.utils import Input, Key, Ease
from pypunk.geom import Rectangle
from pypunk.tweens.misc import ColorTween


class GameWorld(World):
	def __init__(self):
		super().__init__()
		self.game_entity = GameEntity()
		self.add(self.game_entity)

		self.add_graphic(Image('EntityImage2.png'), 0, 50, 50)

		self.colortween = ColorTween(_type = Tween.LOOPING)
		self.add_tween(self.colortween)
		self.colortween.tween(5, 0xFF0000, 0x0000FF, ease=Ease.bounce_in_out)

		self.test = Image.create_rect(100, 100, 0x993333, 0.75)
		self.test.x = 200
		self.test.y = 200

		text = Text('Hello', 100, 100, size=48)

		gl = Graphiclist(self.test, text)
		self.add_graphic(gl)

	def update(self):
		super().update()
		self.test.color = self.colortween.color


class GameEntity(Entity):
	def __init__(self):
		super().__init__()

		self._time_interval = 0
		self.graphic = Spritemap('EntitySheet.png', 40, 20, self.on_animation_end)
		self.graphic.add('Stopped', [0])
		self.graphic.add('Blinking', list(range(10)), 24) 

		Input.define('UP', Key.W, Key.UP)
		Input.define('DOWN', Key.S, Key.DOWN)
		Input.define('LEFT', Key.A, Key.LEFT)
		Input.define('RIGHT', Key.D, Key.RIGHT)

		self.type = 'GameEntity'

		self.graphic.play('Blinking')

	def on_animation_end(self):
		self.graphic.play('Stopped')
		self._time_interval = 0

	def update(self):
		self._time_interval += PP.elapsed
		if self._time_interval >= 3:
			self.graphic.play('Blinking')

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
	engine = Engine(800, 600, 60, 'PyPunk Test')
	PP.world = GameWorld()
	engine.begin()

