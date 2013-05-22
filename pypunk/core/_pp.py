import math
import random
from ..utils import Singleton

class _pp(Singleton):
	"Static class to access global properties and functions"
	def __init__(cls):
		cls.VERSION = '2.DEV'

		# Init variables as a safeguard
		cls.width = 0
		cls.height = 0
		cls.assigned_frame_rate = 0
		cls.title = ''
		cls.elapsed = 0
		cls.frame_rate = 0

		cls.engine = None
		cls.screen = None
		cls.bounds = None

		cls._world = None
		cls._goto = None

		cls._console = None

		# Rad/deg conversion
		cls.DEG = -180 / math.pi
		cls.RAD = math.pi / -180

		cls._point = None
		cls._point2 = None
		cls._zero = None
		cls._rect = None
		cls._entity = None

	def _set_world(cls, world):
		if cls._world == world:
			return
		cls._goto = world
	world = property(lambda cls:cls._world, _set_world)

	def choose(cls, *objs):
		c = objs[0] if len(objs) == 1 and isinstance(objs[0], list) else objs
		return random.choice(c)

	def clamp(cls, value, _min, _max):
		if _max > _min:
			if value < _min: return _min
			if value > _max: return _max
			return value
		else:
			if value < _max: return _max
			if value > _min: return _min
			return value

	# Global objects for rendering/collision/etc
	# Only created when first requested to prevent circular imports
	def _get_point(cls):
		if not cls._point:
			from ..geom import Point
			cls._point = Point()
		return cls._point
	point = property(_get_point)

	def _get_point2(cls):
		if not cls._point2:
			from ..geom import Point
			cls._point2 = Point()
		return cls._point2
	point2 = property(_get_point2)

	def _get_zero(cls):
		if not cls._zero:
			from ..geom import Point
			cls._zero = Point()
		return cls._zero
	zero = property(_get_zero)

	def _get_rect(cls):
		if not cls._rect:
			from ..geom import Rectangle
			cls._rect = Rectangle()
		return cls._rect
	rect = property(_get_rect)

	def _get_entity(cls):
		if not cls._entity:
			from ._entity import Entity
			cls._entity = Entity()
		return cls._entity
	entity = property(_get_entity)

	def _get_console(cls):
		if not cls._console:
			from ..debug import Console
			cls._console = Console()
		return cls._console
	console = property(_get_console)
PP = _pp()