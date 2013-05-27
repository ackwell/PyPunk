from ..core._graphics import Graphic
from ..geom import Point

class Graphiclist(Graphic):
	def __init__(self, *graphics):
		Graphic.__init__(self)

		# Private variables
		self._graphics = []
		self._camera = Point()

		for g in graphics:
			self.add(g)

	def update(self):
		for g in self._graphics:
			if g.active:
				g.update()

	def render(self, target, point, camera):
		point.x += self.x
		point.y += self.y
		camera.x *= self.scroll_x
		camera.y *= self.scroll_y
		for g in self._graphics:
			if g.visible:
				if g.relative:
					self._point.x = point.x
					self._point.y = point.y
				else:
					self._point.x = self._point.y = 0
				self._camera.x = camera.x
				self._camera.y = camera.y
				g.render(target, self._point, self._camera)

	def add(self, graphic):
		self._graphics.append(graphic)
		if not self.active:
			self.active = graphic.active
		return graphic

	def remove(self, graphic):
		if graphic not in self._graphics:
			return graphic
		while graphic in self._graphics:
			self._graphics.remove(graphic)
		self._update_check()
		return graphic

	def remove_at(self, index=0):
		if not len(self._graphics):
			return
		index %= len(self._graphics)
		graphic = self._graphics.pop(index)
		self._update_check()
		return graphic

	def remove_all(self):
		self._graphics = []
		self.active = False

	children = property(lambda self: self._graphics)

	count = property(lambda self: len(self._graphics))

	def _update_check(self):
		self.active = False
		for g in self._graphics:
			if g.active:
				self.active = True
				return
