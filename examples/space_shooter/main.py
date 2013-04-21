import os, sys
pypunk_path = os.path.abspath('../..')
sys.path.append(os.path.join(pypunk_path))

import random
from pypunk.core import PP, Engine, World, Entity
from pypunk.graphics import Graphiclist, Text
from pypunk.utils import Input, Key
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
		self.hud = self.add(HUD())

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


class HUD(Entity):
	font = 'assets/nokiafc22.ttf'

	def __init__(self):
		super().__init__()

		self.score = 0
		self._game_over = False
		self.layer = -1

		self.score_text = Text(str(self.score), 10, 8, **{
				'font': HUD.font,
				'color': 0x6B6B6B,
				'size': 32
			})

		self.game_over_text_1 = Text('', PP.screen.width/2 - 55, PP.screen.height/2 - 8, **{
				'font': HUD.font,
				'color': 0x6B6B6B,
				'size': 16
			})

		self.game_over_text_2 = Text('', PP.screen.width/2 - 138, PP.screen.height/2 + 8, **{
				'font': HUD.font,
				'color': 0x6B6B6B,
				'size': 16
			})

		self.graphic = Graphiclist(self.score_text, self.game_over_text_1, self.game_over_text_2)

	def update(self):
		self.score_text.text = str(self.score)

		if self._game_over and Input.check(Key.RETURN):
			PP.world = GameRoom()

	def game_over(self):
		self.game_over_text_1.text = "GAME OVER"
		self.game_over_text_2.text = "PRESS RETURN TO PLAY AGAIN"
		self._game_over = True


if __name__ == '__main__':
	main()
