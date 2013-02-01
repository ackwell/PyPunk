# Miscellaneous Geomerty Classes

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y


class Rectangle(Point):
	def __init__(self, x=0, y=0, width=1, height=1):
		super().__init__(x, y)
		self.width = width
		self.height = height
