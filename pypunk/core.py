import sfml
from .geom import Rectangle, Point
from .util import Input, EventManager, Singleton


# Errors
class PyPunkError(Exception): pass


class _pp(Singleton):
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

	def _set_world(cls, world):
		if cls._world == world:
			return
		cls._goto = world
	world = property(lambda cls:cls._world, _set_world)
PP = _pp()

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
		PP._world.update_lists()
		if PP._goto:
			self._check_world()
		#if PP.tweener.active and PP.tweener._tween:
		#	PP.tweener.update_tweens()
		if PP._world.active:
			if PP._world._tween:
				PP._world.update_tweens()
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
		PP._world.update_lists()
		if PP._world and PP._world.auto_clear and PP._world._tween:
			PP._world.clear_tweens()
		PP._world = PP._goto
		PP._goto = None
		PP.camera = PP._world.camera
		PP._world.update_lists()
		PP._world.begin()
		PP._world.update_lists()


class Tweener(object):
	def __init__(self):
		# Public variables
		self.active = True
		self.auto_clear = False

		# Private variables
		self._tween = None

	def update(self):
		pass

	def add_tween(self, t, start=False):
		if t._parent:
			raise PyPunkError('Cannot add a Tween object more than once')
		t._parent = self
		t._next = self._tween
		if self._tween:
			self._tween._prev = t
		self._tween = t
		if start:
			self._tween.start()
		return t

	def remove_tween(self, t):
		if t._parent != self:
			raise PyPunkError('Core object does not contain Tween')
		if t._next:
			t._next._prev = t._prev
		if t._prev:
			t._prev._next = t._next
		else:
			self._tween = t._next
		t._next = t._prev = t._parent = None
		t.active = False
		return t

	def clear_tweens(self):
		t = self._tween
		while t:
			n = t._next
			self.remove_tween(t)
			t = n

	def update_tweens(self):
		t = self._tween
		while t:
			n = t._next
			if t.active:
				t.update()
				if t._finish:
					t.finish()
			t = n


class Tween(object):
	# Tween type constants
	PERSIST = 0
	LOOPING = 1
	ONESHOT = 2

	def __init__(self, duration, _type=0, complete=None, ease=None):
		# Public variables
		self.active = False
		self.complete = None

		# Private variables
		# Tween info
		self._type = 0
		self._ease = None
		self._t = 0
		# Timing info
		self._time = 0
		self._target = 0
		# List info
		self._finish = False
		self._parent = None
		self._prev = None
		self._next = None

		# Finally, the init
		self._target = duration
		self._type = _type
		self.complete = complete
		self._ease = ease

	def update(self):
		self._time += PP.elapsed
		self._t = self._time / self._target
		if (self._time >= self._target):
			self._t = 1
			self._finish = True
		if self._ease != None:
			self._t = self._ease(self._t)

	def start(self):
		self._time = 0
		if self._target == 0:
			self.active = False
			return
		self.active = True

	def cancel(self):
		self.active = False
		if self._parent:
			self._parent.remove_tween(self)

	def finish(self):
		if self._type == self.PERSIST:
			self._time = self._target
			self.active = False
		elif self._type == self.LOOPING:
			self._time %= self._target
			self._t = self._time / self._target
			if self._ease != None:
				self._t = self._ease(self._t)
			self.start()
		elif self._type == self.ONESHOT:
			self._time = self._target
			self.active = False
			self._parent.remove_tween(self)
		self._finish = False
		if self.complete != None:
			self.complete()

	def _set_percent(self, value):
		self._time = self._target * value
	percent = property(lambda self:self._time/self._target, _set_percent)

	scale = property(lambda self:self._t)



class World(Tweener):
	def __init__(self):
		super().__init__()
		
		# Public variables
		self.visible = True
		self.camera = Point()

		# Private variables
		# Adding/removal
		self._add = []
		self._remove = []
		# Layers/types
		self._layers = {}
		self._types = {}

	# Called when the world is switched to
	def begin(self): pass

	# Called when the world is switched away from
	def end(self): pass

	# Called by Engine game loop. Updates contained entities.
	def update(self):
		for e in self._iter_entities():
			if e.active:
				if e._tween:
					e.update_tweens()
				e.update()

	# Called by Engine game loop. Renders contained entities
	def render(self):
		for e in self._iter_entities():
			if e.visible:
				e.render()

	def _iter_entities(self):
		for layer in sorted(self._layers.keys(), reverse=True):
			for e in self._layers[layer]:
				yield e

	#mouse_x = property(lambda self:PP.screen.mouse_x+self.camera.x)
	#mouse_y = property(lambda self:PP.screen.mouse_y+self.camera.y)

	def add(self, e):
		self._add.append(e)
		return e

	def remove(self, e):
		self._remove.append(e)
		return e

	def remove_all(self):
		pass #TODO

	def add_list(self, *entities):
		if entities[0] is list:
			for e in entities[0]:
				self.add(e)
			return
		for e in entities:
			self.add(e)

	def remove_list(self, *entities):
		if entities[0] is list:
			for e in entities[0]:
				self.remove(e)
			return
		for e in entities:
			self.remove(e)

	def update_lists(self):
		# Remove entities
		for e in self._remove:
			self.remove_layer(e)
			if e.type != '':
				self.remove_type(e)
			e.removed()
			e._world = None
		self._remove = []

		# Add entities
		for e in self._add:
			# Add to the update/render whatsit
			self.add_layer(e)
			# If it has a type, add it to the typelist
			if e.type != '':
				self.add_type(e)
			e._world = self
			e.added()
		self._add = []

	def add_layer(self, e):
		if e.layer not in self._layers:
			self._layers[e.layer] = []
		self._layers[e.layer].append(e) 

	def add_type(self, e):
		if e.type not in self._types:
			self._types[e.type] = []
		self._types[e.type].append(e)

	def remove_layer(self, e):
		# Possibly need to catch error? (according to old code)
		self._layers[e.layer].remove(e)

	def remove_type(self, e):
		if e.type:
			self._types[e.type].remove(e)


class Entity(Tweener):
	def __init__(self):
		super().__init__()


class Screen(sfml.RenderWindow):
	def __init__(self):
		super().__init__(sfml.VideoMode(PP.width, PP.height), PP.title)
