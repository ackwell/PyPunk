
import math

from pypunk.core import PP, Entity
from pypunk.graphics import Image

class Alien(Entity):
	spr_alien = 'assets/alien.png'

	def __init__(self, x, y):
		super().__init__(x, y)

		self.speed = 200

		self.width = 36
		self.height = 32
		self.graphic = Image(Alien.spr_alien)
		self.type = 'alien'

	def update(self):
		self.x -= self.speed * PP.elapsed
		self.y += (math.cos(self.x / 50) * 50) * PP.elapsed
		if self.x < -40:
			self.destroy()

		bullet = self.collide('bullet', self.x, self.y)
		if bullet:
			self.world.hud.score += 1
			bullet.destroy()
			self.destroy()

	def destroy(self):
		self.world.remove(self)
