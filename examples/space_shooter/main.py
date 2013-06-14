# Adding the pypunk directory to the system path
# This is only needed due to the fact PyPunk is in a different
# directory
import os, sys
pypunk_path = os.path.abspath('../..')
sys.path.append(os.path.join(pypunk_path))

# Library imports
import random
from pypunk.core import PP, Engine, World, Entity
from pypunk.graphics import Graphiclist, Text
from pypunk.utils import Input, Key

# Game module imports
from player import Ship
from enemy import Alien


# Main function, run when script is executed
def main():
	# Create the Engine, setting up various window paramaters
	engine = Engine(640, 480, 60, 'Space Shooter')
	# Create a new GameRoom object, and set it to be the current world.
	# Setting PP.world is the 'correct' way of switching worlds.
	PP.world = GameRoom()
	# Start PyPunk!
	engine.start()

# GameRoom inherits from pypunk.core.World
# Worlds are like a context - you can have as many as you like,
# but only one  is active at a time.
class GameRoom(World):
	# The begin function is called when the world becomes the Engine's
	# active world - you should do setup in here.
	def begin(self):
		self.spawn_timer = 0
		self.spawn_interval = 2.5

		# Sets the screen background colour. Value is an RGB hex.
		PP.screen.color = 0xC2C2C2 #0xRRGGBB

		# Add entities to the World to be updated and rendered
		self.add(Ship())
		# I'm storing a reference to the hud in the world so I can access it later.
		self.hud = self.add(HUD())

		self.reset_spawn_timer()

	# update is called every frame as part of the game loop
	def update(self):
		# Alien spawner
		self.spawn_timer -= PP.elapsed
		if self.spawn_timer <= 0:
			self.spawn_alien()
			self.reset_spawn_timer()

		# If you have an update() function on a World, make sure
		# to call this, else the Entities won't be updates
		super().update()

	# Spawn an alien at a random position off the right hand side of the screen.
	def spawn_alien(self):
		x = PP.screen.width
		y = random.randint(50, PP.screen.height-50)
		self.add(Alien(x, y))

	# Reset the spawn timer, and reduce the interval between spawns slightly.
	def reset_spawn_timer(self):
		self.spawn_timer = self.spawn_interval
		self.spawn_interval *= 0.95
		if self.spawn_interval < 0.1:
			self.spawn_interval = 0.1


# HUD is a pypunk.core.Entity
# Entities are the core interactive object, they update and are drawn to the
# screen.
# HUD is a group of text graphics that display the score and game over text.
class HUD(Entity):
	# Location of the font to use
	font = 'assets/nokiafc22.ttf'

	# added() is called when the Entity has been added to the screen, usually
	# good place to put the Entity's setup. Similar to World.begin
	def added(self):
		# Initialise a few vars
		self.score = 0
		self._game_over = False
		self.layer = -1

		# Set up the text box settings.
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
		# Use a Graphiclist so a single Entity can display multiple graphics
		self.graphic = Graphiclist(self.score_text, self.game_over_text_1, self.game_over_text_2)

	# Update function, called every frame
	def update(self):
		# Update the score text to reflect the current score
		self.score_text.text = str(self.score)

		# Restart the game if they died and press enter.
		if self._game_over and Input.check(Key.RETURN):
			PP.world = GameRoom()

	# Called by the player instance. Sets game over text, etc.
	def game_over(self):
		self.game_over_text_1.text = "GAME OVER"
		self.game_over_text_2.text = "PRESS RETURN TO PLAY AGAIN"
		self._game_over = True


# This if statement will only be executed if the file was directly
# executed. In this case i use it to call the main() function.
if __name__ == '__main__':
	main()
