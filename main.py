from pypunk.Base import *
from pypunk.Graphics import *
from pypunk.Tweens import *
from pypunk.Event import *
from pypunk.Audio import *
from pypunk import Punk
import math, random

def start():
	print "Starting up"

	#Create new Engine
	e = Engine(640, 480, 60, "FP Tests")
	e.bgColor = (194, 194, 194)

	#Set world
	Punk.SetWorld(GameRoom())

	#Start the engine
	e.Begin()

class GameRoom(World):
	def __init__(self):
		World.__init__(self)

		self.spawnTimer = 0
		self.spawnInterval = 2.5

		ship = Ship()
		self.add(ship)
		self.add(HUD())

		self.resetSpawnTimer()
	
	def update(self, App):
		self.spawnTimer -= Punk.elapsed
		if self.spawnTimer < 0:
			self.spawnAlien()
			self.resetSpawnTimer()

		World.update(self, App)
	
	def spawnAlien(self):
		x = Punk.Engine.width
		y = random.random() * (Punk.Engine.height - 100) + 50
		alien = Alien(x, y)
		self.add(alien)
	
	def resetSpawnTimer(self):
		self.spawnTimer = self.spawnInterval
		self.spawnInterval *= 0.95
		if self.spawnInterval < 0.1:
			self.spawnInterval = 0.1

class Ship(Entity):
	speed = 250

	def __init__(self):
		Entity.__init__(self)
		self.x = 50.0
		self.y = 50

		self.width = 40
		self.height = 16
		self.type = "ship"

		#Set up the image
		self.graphic = Image("./Assets/Ship.png")

		#Timer for shoot'n
		self.shootTimer = Timer()
		self.shootTimer.start()
		self.addTween(self.shootTimer)

		#Register functions
		RegisterEvent(Event.KeyReleased, self.onRelease)
		RegisterEvent(Event.KeyPressed, self.onPressed)

		#input
		self.input = Punk.Engine.Input

		#Sounds
		self.shipDie = Sfx("./Assets/ExplosionShip.wav")
		self.bulletShoot = Sfx("./Assets/Bullet.wav")
	
	def update(self):
		self.move()
		self.constrain()
		self.shoot()
		self.collision()
	
	def move(self):
		if self.input.IsKeyDown(Key.Right):
			self.x += self.speed * Punk.elapsed
		if self.input.IsKeyDown(Key.Left):
			self.x -= self.speed * Punk.elapsed
		if self.input.IsKeyDown(Key.Down):
			self.y += self.speed * Punk.elapsed
		if self.input.IsKeyDown(Key.Up):
			self.y -= self.speed * Punk.elapsed
	
	def constrain(self):
		if self.x > Punk.Engine.width - self.width - 16:
			self.x = Punk.Engine.width - self.width - 16
		elif self.x < 16:
			self.x = 16
		if self.y > Punk.Engine.height - self.height - 16:
			self.y = Punk.Engine.height - self.height - 16
		elif self.y < 16:
			self.y = 16
	
	def shoot(self):
		#make sure the timer is running
		if self.input.IsKeyDown(Key.Space) and self.shootTimer.value > 0.2:
			self.world.add(Bullet(self.x+36, self.y+12))
			self.bulletShoot.Play()
			self.shootTimer.reset()
	def onRelease(self, args):
		if args["Code"] == Key.Space:
			self.shootTimer.stop()
	def onPressed(self, args):
		if args["Code"] == Key.Space and not self.shootTimer.running:
			self.shootTimer.start()
			self.world.add(Bullet(self.x+36, self.y+12))
			self.bulletShoot.Play()
	
	def collision(self):
		alien = self.collide("alien", self.x, self.y)
		if alien:
			self.shipDie.Play()
			self.world.remove(alien)
			self.world.remove(self)
			HUD.gameOver = True
	
	def removed(self):
		#although not always neccesary, generally good idea just in case
		DeregisterEvent(Event.KeyReleased, self.onRelease)
		DeregisterEvent(Event.KeyPressed, self.onPressed)

class Alien(Entity):
	speed = 200

	def __init__(self, x , y):
		Entity.__init__(self)
		self.x = x
		self.y = y
		self.width = 36
		self.height = 32
		self.type = "alien"
		self.graphic = Image("./Assets/Alien.png")

		self.alienDie = Sfx("./Assets/ExplosionAlien.wav")

	def update(self):
		self.x -= self.speed * Punk.elapsed
		self.y += (math.cos(self.x / 50) * 50) * Punk.elapsed

		bullet = self.collide("bullet", self.x, self.y)
		if bullet:
			self.alienDie.Play()
			self.world.remove(bullet)
			self.world.remove(self)
			HUD.score += 1

		if self.x < -40:
			self.world.remove(self)

class Bullet(Entity):
	speed = 1000

	def __init__(self, x, y):
		Entity.__init__(self)
		self.x = x
		self.y = y
		self.type = "bullet"

		img = Shape()
		img.createRect(16, 4, Color(107, 107, 107))
		self.graphic = img
	
	def update(self):
		self.x += self.speed * Punk.elapsed
		if self.x > Punk.Engine.width:
			self.world.remove(self)

class HUD(Entity):
	score = 0
	gameOver = False

	def __init__(self):
		Entity.__init__(self)
		self.layer = -1

		fnt = "./Assets/nokiafc22.ttf"

		self.scoreText = Text(fnt, size=32)
		self.scoreText.text = str(HUD.score)
		self.scoreText.color = (107, 107, 107)
		self.scoreText.x = 10
		self.scoreText.y = 8

		self.gameOverText1 = Text(fnt, size=16)
		self.gameOverText1.color = (107, 107, 107)
		self.gameOverText1.x = Punk.Engine.width/2-55
		self.gameOverText1.y = Punk.Engine.height/2-8

		self.gameOverText2 = Text(fnt, size=16)
		self.gameOverText2.color = (107, 107, 107)
		self.gameOverText2.x = Punk.Engine.width/2-138
		self.gameOverText2.y = Punk.Engine.height/2+8

		gfxlist = Graphiclist(self.scoreText, self.gameOverText1, self.gameOverText2)
		self.graphic = gfxlist

		self.input = Punk.Engine.Input

	def update(self):
		self.scoreText.text = str(HUD.score)

		if HUD.gameOver:
			self.gameOverText1.text = "GAME OVER"
			self.gameOverText2.text = "PRESS ENTER TO PLAY AGAIN"

			if self.input.IsKeyDown(Key.Return):
				HUD.score = 0
				HUD.gameOver = False
				Punk.SetWorld(GameRoom())

#ENTRY POINT
if __name__ == "__main__":
	start()