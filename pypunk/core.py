import sfml
from .geom import Rectangle, Point
from .util import Input, EventManager


class PP(object):
	"Static class to access global properties and functions"
	# Init variables as a safeguard
	width = 0
	height = 0
	assigned_frame_rate = 0
	title = ''

	engine = None
	screen = None
	bounds = None
	_world = None


class Engine(object):
	"Main game class. Manages game loop."
	
	def __init__(self, width, height, frame_rate=60, title="PyPunk"):
		# Public variables
		paused         = False
		max_elapsed    = 0.0333

		# Private variables
		self._running = True

		# Set global game properties
		PP.width = width
		PP.height = height
		PP.assigned_frame_rate = frame_rate
		PP.title = title

		# Global game objects
		PP.engine = self
		PP.screen = Screen()
		PP.bounds = Rectangle(0, 0, width, height)
		PP._world = World()
		#camera goes here
		#reset draw target?

		# Bind input and close events
		Input._bind_events()
		EventManager.register_event(sfml.Event.CLOSED, self.close)

	def begin(self):
		while self._running:
			# Clear the previous states, then dispatch Events
			Input._clear_key_states()
			EventManager.dispatch_events(PP.screen)

		PP.screen.close()

	def update(self):
		pass

	def render(self):
		pass

	def close(self, event=None):
		self._running = False


class Tweener(object):
	def __init__(self):
		# Public variables
		self.active = True
		self.auto_clear = False

	def update(self):
		pass


class World(Tweener):
	def __init__(self):
		super().__init__()
		
		# Public variables
		self.visible = True
		self.camera = Point()

	# Called when the world is switched to
	def begin(self):
		pass

	# Called when the world is switched away from
	def end(self):
		pass

	# Called by Engine game loop. Updates contained entities.
	def update(self):
		# Update entites
		pass

	# Called by Engine game loop. Renders contained entities
	def render(self):
		pass


class Screen(sfml.RenderWindow):
	def __init__(self):
		super().__init__(sfml.VideoMode(PP.width, PP.height), PP.title)
