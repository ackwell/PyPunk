# -*- coding: utf-8 -*-

from Punk import Point

class Graphic(object):
	def __init__(self):
		# If the graphic should update
		self.active = False

		# if the graphic should render
		self.visible = True

		# X offset
		self.x = 0

		# Y offset
		self.y = 0

		# If the graphic should render at its position relative to its parent Entity's position.
		self.relative = True

		# X scrollfactor, effects how much the camera offsets the drawn graphic.
		# Can be used for parallax effect, eg. Set to 0 to follow the camera,
		# 0.5 to move at half-speed of the camera, or 1 (default) to stay still.
		self.scollX = 1

		# Y scrollfactor, effects how much the camera offsets the drawn graphic.
		#  Can be used for parallax effect, eg. Set to 0 to follow the camera,
		# 0.5 to move at half-speed of the camera, or 1 (default) to stay still.
		self.scrollY = 1

		# Graphic information
		self._assign = None		# private
		self._scroll = True		# private
		self._point = Point()	# private


	def update(self):
		pass

	def render(self, target, point, camera):
		pass

	@property
	def assign(self):
		return self._assign

	@assign.setter
	def assign(self, value):
		self._assign = value
