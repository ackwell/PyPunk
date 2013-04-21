
from pypunk.core import PP, Entity
from pypunk.graphics import Image
from pypunk.utils import Input, Key

class Ship(Entity):
	spr_ship = 'assets/ship.png'

	def __init__(self):
		super().__init__(50, 50)

		self.speed = 250

		self.graphic = Image(Ship.spr_ship)
		self.width = 40
		self.height = 16
		self.type = 'ship'

	def update(self):
		self.move()
		self.constrain()
		self.shoot()

	def move(self):
		if Input.check(Key.RIGHT):
			self.x += self.speed * PP.elapsed
		if Input.check(Key.LEFT):
			self.x -= self.speed * PP.elapsed
		if Input.check(Key.DOWN):
			self.y += self.speed * PP.elapsed
		if Input.check(Key.UP):
			self.y -= self.speed * PP.elapsed

	def constrain(self):
		# print(self.height, self.width)
		self.clamp_horizontal(16, PP.screen.width - 16)
		self.clamp_vertical(16, PP.screen.height - 16)

	def shoot(self):
		if Input.pressed(Key.SPACE):
			self.world.add(Bullet(self.x + 36, self.y + 12))

	def destroy(self):
		self.world.remove(self)


class Bullet(Entity):
	def __init__(self, x, y):
		super().__init__(x, y)

		self.speed = 1000

		self.graphic = Image.create_rect(16, 4, 0x6B6B6B)
		self.width = 16
		self.height = 4
		self.type = 'bullet'

	def update(self):
		self.x += self.speed * PP.elapsed
		if self.x > PP.screen.width:
			self.destroy()

	def destroy(self):
		self.world.remove(self)
