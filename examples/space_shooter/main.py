import os, sys
pypunk_path = os.path.abspath('../..')
sys.path.append(os.path.join(pypunk_path))

import random
from pypunk.core import PP, Engine, World
from player import Ship
from enemy import Alien

def main():
	engine = Engine(640, 480, 60, 'Space Shooter')
	PP.world = GameRoom()
	engine.begin()

class GameRoom(World):
	def __init__(self):
		super().__init__()

		self.spawn_timer = 0
		self.spawn_interval = 2.5

		PP.screen.color = 0xC2C2C2

		self.add(Ship())

		self.reset_spawn_timer()

	def update(self):
		self.spawn_timer -= PP.elapsed
		if self.spawn_timer <= 0:
			self.spawn_alien()
			self.reset_spawn_timer()

		super().update()

	def spawn_alien(self):
		x = PP.screen.width
		y = random.randint(50, PP.screen.height-50)
		self.add(Alien(x, y))

	def reset_spawn_timer(self):
		self.spawn_timer = self.spawn_interval
		self.spawn_interval *= 0.95
		if self.spawn_interval < 0.1:
			self.spawn_interval = 0.1

if __name__ == '__main__':
	main()
