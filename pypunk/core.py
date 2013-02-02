import sfml
from .geom import Rectangle, Point
from .util import Input, EventManager, Singleton


class PP(Singleton):
	"Static class to access global properties and functions"
	# Init variables as a safeguard
	width = 0
	height = 0
	assigned_frame_rate = 0
	title = ''
	elapsed = 0
	frame_rate = 0

	engine = None
	screen = None
	bounds = None
	_world = None
	_goto = None 


class Engine(object):
	"Main game class. Manages game loop."
	
	def __init__(self, width, height, frame_rate=60, title="PyPunk"):
		# Public variables
		self.paused         = False
		self.max_elapsed    = 0.0333

		# Private variables
		self._running = True
		self._clock = sfml.Clock()

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
		PP.camera = PP._world.camera
		#reset draw target?

		# Set FPS limit
		PP.screen.framerate_limit = PP.assigned_frame_rate

		# Bind input and close events
		Input._bind_events()
		EventManager.register_event(sfml.Event.CLOSED, self.close)

	def begin(self):
		# Switch worlds
		if (PP._goto):
			self._check_world()

		# Reset the clock just before starting the frame loop
		self._clock.restart()

		while self._running:
			# Set some variables
			try:
				PP.elapsed = self._clock.elapsed_time.as_seconds()
				PP.frame_rate = 1/PP.elapsed
			except ZeroDivisionError: pass
			self._clock.restart()

			Input._clear_key_states()
			EventManager.dispatch_events(PP.screen)

			#Update console?
			if not self.paused:
				self.update()
				self.render()

		PP.screen.close()

	def update(self):
		#PP._world.update_lists()
		if PP._goto:
			self._check_world()
		#if PP.tweener.active and PP.tweener._tween:
		#	PP.tweener.update_tweens()
		if PP._world.active:
			#if PP._world._tween:
			#	PP._world.update_tweens()
			PP._world.update()

	def render(self):
		# reset Draw target?
		PP.screen.clear() # SET BG COLOUR HERE
		if PP._world.visible:
			PP._world.render()
		PP.screen.display()

	def close(self, event=None):
		self._running = False

	def _check_world(self):
		if not PP._goto:
			return

		PP._world.end()
		#PP._world.update_lists()
		#if PP._world and PP._world.auto_clear and PP._world._tween:
		#	PP._world.clear_tweens()
		PP._world = PP._goto
		PP._goto = None
		PP.camera = PP._world.camera
		#PP._world.update_lists()
		PP._world.begin()
		#PP._world.update_lists()


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
	def begin(self): pass

	# Called when the world is switched away from
	def end(self): pass

	# Called by Engine game loop. Updates contained entities.
	def update(self):
		# Update entites
		pass

	# Called by Engine game loop. Renders contained entities
	def render(self):
		# Render wntities
		pass


class Screen(sfml.RenderWindow):
	def __init__(self):
		super().__init__(sfml.VideoMode(PP.width, PP.height), PP.title)
