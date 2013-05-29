
# Library imports
import math
from pypunk.core import PP, Entity, Sfx
from pypunk.graphics import Image

class Alien(Entity):
	spr_alien = 'assets/alien.png'
	snd_alien_die = 'assets/explosion-alien.wav'

	def __init__(self, x, y):
		super().__init__(x, y)

	def added(self):
		# Slightly slower than the player
		self.speed = 200

		self.width = 36
		self.height = 32
		self.graphic = Image(Alien.spr_alien)
		self.type = 'alien'

		self.alien_die = Sfx(Alien.snd_alien_die)

	def update(self):
		# Constantly move to the left
		self.x -= self.speed * PP.elapsed
		# Just a bit of math to make them do pretty waves as
		# they come across the screen
		self.y += (math.cos(self.x / 50) * 50) * PP.elapsed
		# Destoy it if it does offscreen.
		if self.x < -40:
			self.destroy()

		# If it's collided with a bullet, remove both, and increase the score.
		bullet = self.collide('bullet', self.x, self.y)
		if bullet:
			self.world.hud.score += 1
			bullet.destroy()
			self.destroy()
			self.alien_die.play()

	def destroy(self):
		self.world.remove(self)
