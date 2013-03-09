import sfml
# Miscellaneous Geometry Classes

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y


class Rectangle(sfml.IntRect):
	def __init__(self, x=0, y=0, width=1, height=1):
		super().__init__(x, y, width, height)

	def _set_x(self, value): self.left = value
	x = property(lambda self: self.left, _set_x)
	def _set_y(self, value): self.top = value
	y = property(lambda self: self.top, _set_y)
