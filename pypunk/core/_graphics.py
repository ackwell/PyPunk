import sfml
from ..geom import Point

class Graphic(object):
	def __init__(self):
		# Private Variables
		self._point = Point()

		# Public Variables
		self.active = False
		self.visible = True
		self.x = 0
		self.y = 0
		self.scroll_x = 1
		self.scroll_y = 1
		self.relative = True
		self.assign = None

	def update(self): pass

	def render(self, target, point, camera): pass

	# Utility functions
	@staticmethod
	def hex2color(_hex):
		b = _hex & 255
		g = (_hex >> 8) & 255 
		r = (_hex >> 16) & 255
		return sfml.graphics.Color(r, g, b)
	@staticmethod
	def color2hex(color):
		return color.r*65536 + color.g*256 + color.b