import math
import random
from ..debug import Console
from ..geom import Point, Rectangle
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

		# Global objects for rendering/collision/etc
		cls.point = Point()
		cls.point2 = Point()
		cls.zero = Point()
		cls.rect = Rectangle()

	def _set_world(cls, world):
		if cls._world == world:
			return
		cls._goto = world
	world = property(lambda cls:cls._world, _set_world)

	def choose(cls, *objs):
		c = objs[0] if len(objs) == 1 and isinstance(objs[0], list) else objs
		return random.choice(c)

	def _get_console(cls):
		if not cls._console:
			cls._console = Console()
		return cls._console
	console = property(_get_console)
PP = _pp()