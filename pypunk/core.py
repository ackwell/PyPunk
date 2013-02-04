import sfml
from . import graphics
from .geom import Rectangle, Point
from .utils import Input, EventManager, Singleton


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

	# Global objects for rendering/collision/etc
	point = Point()
	point2 = Point()
	zero = Point()
	rect = Rectangle()
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

			Input._clear_states()
			EventManager.dispatch_events(PP.screen)

			#Update console?
			if not self.paused:
				self.update()
				self.render()

		PP.screen.close()

	def update(self):
		PP._world._update_lists()
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
		PP.screen.clear(PP.screen._color)
		if PP._world.visible:
			PP._world.render()
		PP.screen.display()

	def close(self, event=None):
		self._running = False

	def _check_world(self):
		if not PP._goto:
			return

		PP._world.end()
		PP._world._update_lists()
		if PP._world and PP._world.auto_clear and PP._world._tween:
			PP._world.clear_tweens()
		PP._world = PP._goto
		PP._goto = None
		PP.camera = PP._world.camera
		PP._world._update_lists()
		PP._world.begin()
		PP._world._update_lists()


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
		self.complete = complete

		# Private variables
		# Tween info
		self._type = _type
		self._ease = ease
		self._t = 0
		# Timing info
		self._time = 0
		self._target = duration
		# List info
		self._finish = False
		self._parent = None
		self._prev = None
		self._next = None

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
		self._entity_names = {}

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

	mouse_x = property(lambda self:PP.screen.mouse_x+self.camera.x)
	mouse_y = property(lambda self:PP.screen.mouse_y+self.camera.y)

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

	def _update_lists(self):
		# Remove entities
		for e in self._remove:
			e.removed()
			e._world = None
			self._remove_layer(e)
			if e._type != '':
				self._remove_type(e)
			if e._name != '':
				self._unregister_name(e)
		self._remove = []

		# Add entities
		for e in self._add:
			# Add to the update/render whatsit
			self._add_layer(e)
			# If it has a type, add it to the typelist, likewise for name
			if e._type != '':
				self._add_type(e)
			if e._name != '':
				self._register_name(e)
			e._world = self
			e.added()
		self._add = []

	def _add_layer(self, e):
		if e.layer not in self._layers:
			self._layers[e.layer] = []
		self._layers[e.layer].append(e) 

	def _add_type(self, e):
		if e.type not in self._types:
			self._types[e.type] = []
		self._types[e.type].append(e)

	def _register_name(self, e):
		self._entity_names[e._name] = e

	def _remove_layer(self, e):
		# Possibly need to catch error? (according to old code)
		self._layers[e.layer].remove(e)

	def _remove_type(self, e):
		if e.type:
			self._types[e.type].remove(e)

	def _unregister_name(self, e):
		if e._name in self._entity_names and self._entity_names[e._name] == e:
			del self._entity_names[e._name]


class Entity(Tweener):
	def __init__(self, x=0, y=0, graphic=None, mask=None):
		super().__init__()

		# Public variables
		self.visible = True
		self.collidable = True
		self.x = x
		self.y = y
		self.width = 0
		self.height = 0
		self.origin_x = 0
		self.origin_y = 0
		self.render_target = None

		# Private variables
		self._class = self.__class__.__name__
		self._world = None
		self._type = ''
		self._name = ''
		self._layer = 0
		# hitbox?
		self._mask = None
		self._graphic = None
		self._point = PP.point
		self._camera = PP.point2

		if graphic:
			self.graphic = graphic
		if mask:
			self.mask = mask
		#self.HITBOX.assign_to(self)

	def added(self): pass

	def removed(self): pass

	def update(self): pass

	def render(self):
		if self._graphic and self._graphic.visible:
			if self._graphic.relative:
				self._point.x = self.x
				self._point.y = self.y
			else:
				self._point.x = self._point.y = 0
			self._camera.x = self._world.camera.x if self._world else PP.camera.x
			self._camera.y = self._world.camera.y if self._world else PP.camera.y
			self._graphic.render(self.render_target if self.render_target else PP.screen, self._point, self._camera)

	# COLLISION FUNCTIONS

	# onCamera

	world = property(lambda self:self._world)

	left = property(lambda self:self.x-origin_x)
	right = property(lambda self:self.left+self.width)
	top = property(lambda self:self.y-self.origin_y)
	bottom = property(lambda self:self.top+self.height)
	center_x = property(lambda self:self.left+self.width/2)
	center_y = property(lambda self:self.top+self.height/2)

	def _set_layer(self, value):
		if self._layer == value:
			return
		if not self._world:
			self._layer = value
			return
		self._world._remove_layer(self)
		self._layer = value
		self._world._add_layer(self)
	layer = property(lambda self:self._layer, _set_layer)

	def _set_type(self, value):
		if self.type == value:
			return
		if not self._world:
			self._type = value
			return
		if self._type:
			self._world._remove_type(self)
		self._type = value
		if self._type:
			self._world._add_type(self)
	# Bad code, i know. SOWEEEE (using 'type' as a variable)
	type = property(lambda self:self._type, _set_type)

	def _set_graphic(self, g):
		if self._graphic == g:
			return
		self._graphic = g
		if g and g.assign != None:
			g.assign()
	graphic = property(lambda self:self._graphic, _set_graphic)

	def add_graphic(g):
		raise NotImplementedError()

	# SET HITBOX, ETC

	def center_origin(self):
		self.origin_x = width/2
		self.origin_y = height/2

	# DISTANCE FUNCTIONS

	def __str__(self):
		return self._class

	# MOVE FUNCTIONS

	def _set_name(self, value):
		if self._name == value:
			return
		if self._name and self._world:
			self._world._unregister_name(self)
		self._name = value
		if self._name and self._world:
			self._world._register_name(self)
	name = property(lambda self: self._name, _set_name)

	def get_class(self):
		return self._class


class Screen(sfml.RenderWindow):
	def __init__(self):
		super().__init__(sfml.VideoMode(PP.width, PP.height), PP.title)
		self._color = sfml.Color(32, 32, 32)

	def _set_color(self, value):
		self._color = graphics.hex2color(value)
	color = property(lambda self: graphics.color2hex(self._color), _set_color)

	mouse_x = property(lambda _:Input.mouse_x)
	mouse_y = property(lambda _:Input.mouse_y)