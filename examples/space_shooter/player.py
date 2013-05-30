
# Library imports
from pypunk.core import PP, Entity, Sfx
from pypunk.graphics import Image
from pypunk.utils import Input, Key

# The player's ship.
class Ship(Entity):
	# Paths to resources.
	spr_ship = 'assets/ship.png'
	snd_ship_die = 'assets/explosion-ship.wav'
	snd_bullet_shoot = 'assets/bullet.wav'

	def added(self):
		# Keeping track of how fast it should be able to move, in this case,
		# 250 units (pixels per second)
		self.speed = 250

		# Set the initial location of the sprite
		self.x = self.y = 50
		# Set the graphic to render onto screen to a new Image instance.
		self.graphic = Image(Ship.spr_ship)
		# Width and Height are primarily used for collision detection.
		# should be indicative of the size of the sprite (in most cases.)
		self.width = 40
		self.height = 16
		# The type of an entity is an arbitrary string that categorises what it is
		# Types are used for several things, most predominantly collision checking,
		# where you can specify a type, which then will restrict collisions detected
		# to Entities of that type.
		self.type = 'ship'

		# Some sound resources to sound cool with
		self.ship_die = Sfx(Ship.snd_ship_die)
		self.bullet_shoot = Sfx(Ship.snd_bullet_shoot)

	# I've delegated the update code into a few smaller functions to make
	# it more readable.
	def update(self):
		self.move()
		self.constrain()
		self.shoot()
		self.collision()

	# Check if the keys are being pressed, and if they are, move in the appropriate
	# direction. The self.speed * PP.elapsed is used to make sure the object moves at
	# a steady rate, rather than something that will change depending on the FPS
	def move(self):
		if Input.check(Key.RIGHT):
			self.x += self.speed * PP.elapsed
		if Input.check(Key.LEFT):
			self.x -= self.speed * PP.elapsed
		if Input.check(Key.DOWN):
			self.y += self.speed * PP.elapsed
		if Input.check(Key.UP):
			self.y -= self.speed * PP.elapsed 

	# Make sure the ship doesn't go off-screen.
	def constrain(self):
		self.clamp_horizontal(16, PP.screen.width - 16)
		self.clamp_vertical(16, PP.screen.height - 16)

	# If the user pressed space, create a new bullet instance, add it to the world,
	# and play a cool sound effect
	def shoot(self):
		if Input.pressed(Key.SPACE):
			self.world.add(Bullet(self.x + 36, self.y + 12))
			self.bullet_shoot.play()

	# Check to see if we have collided with an alien (notice usage of type to
	# filter collision check). If we have collided, it's game over, play the
	# appropriated SFX to imply as such.
	def collision(self):
		alien = self.collide('alien', self.x, self.y)
		if alien:
			alien.destroy()
			self.destroy()
			self.ship_die.play()
			self.world.hud.game_over()

	# Removes the entity from the world.
	def destroy(self):
		self.world.remove(self)

# A bullet object, shot by the player.
class Bullet(Entity):
	# Because we are passing data to the constructor, need to pass it along
	# The Entity constructor takes an X and Y value to move the Entity to when created.
	def __init__(self, x, y):
		super().__init__(x, y)

	def added(self):
		# Bullets move faster that ships, so the pixels per second is higher.
		self.speed = 1000

		# This time, instead of using a static resource, we create a new rectangular graphic
		# at runtime.
		self.graphic = Image.create_rect(16, 4, 0x6B6B6B)
		self.width = 16
		self.height = 4
		self.type = 'bullet'

	def update(self):
		# If the bullet is off-screen, remove it.
		self.x += self.speed * PP.elapsed
		if self.x > PP.screen.width:
			self.destroy()

	def destroy(self):
		self.world.remove(self)
