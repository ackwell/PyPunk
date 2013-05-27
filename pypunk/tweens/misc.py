from ..core import Tween, PP, PyPunkError


class Alarm(Tween):
	def __init__(self, duration, complete=None, _type=0):
		Tween.__init__(self,duration, _type, complete, None)

	def reset(self, duration):
		self._target = duration
		self.start()

	elapsed = property(lambda self: self._time)
	duration = property(lambda self: self._target)
	remaining = property(lambda self: self._target - self._time)


class AngleTween(Tween):
	def __init__(self, complete=None, _type=0):
		self.angle = 0

		self._start = 0
		self._range = 0

		Tween.__init__(self,0, _type, complete)

	def tween(self, from_angle, to_angle, duration, ease=None):
		self._start = self.angle = from_angle
		d = to_angle - self.angle
		a = abs(d)
		if a > 181:
			self._range = (360 - a) * (-1 if d > 0 else 1)
		elif a < 179:
			self._range = d
		else:
			self._range = PP.choose(180, -180)
		self._target = duration
		self._ease = ease
		self.start()

	def update(self):
		Tween.update(self)
		self.angle = (self._start + self._range * self._t) % 360
		if self.angle < 0:
			self.angle += 360


class ColorTween(Tween):
	def __init__(self, complete=None, _type=0):
		self.color = 0
		self.alpha = 1

		self._r = 0
		self._g = 0
		self._b = 0
		self._start_a = 0
		self._start_r = 0
		self._start_g = 0
		self._start_b = 0
		self._range_a = 0
		self._range_r = 0
		self._range_g = 0
		self._range_b = 0

		Tween.__init__(self, 0, _type, complete)

	def tween(self, duration, from_color, to_color, from_alpha=1, to_alpha=1, ease=None):
		from_color &= 0xFFFFFF
		to_color &= 0xFFFFFF
		self.color = from_color
		self._r = from_color >> 16 & 0xFF
		self._g = from_color >> 8 & 0xFF
		self._b = from_color & 0xFF
		self._start_r = self._r / 255
		self._start_g = self._g / 255
		self._start_b = self._b / 255
		self._range_r = ((to_color >> 16 & 0xFF) / 255) - self._start_r
		self._range_g = ((to_color >> 8 & 0xFF) / 255) - self._start_g
		self._range_b = ((to_color & 0xFF) / 255) - self._start_b
		self._start_a = self.alpha = from_alpha
		self._range_a = to_alpha - self.alpha
		self._target = duration
		self._ease = ease
		self.start()

	def update(self):
		Tween.update(self)
		self.alpha = self._start_a + self._range_a * self._t
		self._r = int((self._start_r + self._range_r * self._t) * 255)
		self._g = int((self._start_g + self._range_g * self._t) * 255)
		self._b = int((self._start_b + self._range_b * self._t) * 255)
		self.color = self._r << 16 | self._g << 8 | self._b

	red = property(lambda self: self._r)
	green = property(lambda self: self._g)
	blue = property(lambda self: self_b)


class NumTween(Tween):
	def __init__(self, complete, _type=0):
		self.value = 0

		self._start = 0
		self._range = 0

		Tween.__init__(self,0, _type, complete)

	def tween(self, from_value, to_value, duration, ease=None):
		self._start = self.value = from_value
		self._range = to_value - self.value
		self._target = duration
		self._ease = ease
		self.start()

	def update(self):
		Tween.update(self)
		self.value = self._start + self._range * self._t


class VarTween(Tween):
	def __init__(self, complete, _type=0):
		self._object = None
		self._property = ''
		self._start = 0
		self._range = 0

		Tween.__init__(self,0, _type, complete)

	def tween(self, _object, _property, to, duration, ease=None):
		self._object = _object
		self._property = _property
		self._ease = ease
		if not object.hasattr(_property):
			raise PyPunkError('The Object does not have the property "' + _property + '".')
		self._start = float(self._object.getattr(_property))
		self._range = to - self._start
		self._target = duration
		self._ease = ease
		start()

	def update(self):
		Tween.update(self)
		self._object.setattr(self._property, self._start + self._range * self._t)


class MultiVarTween(Tween):
	def __init__(self, complete, _type=0):
		self._object = None
		self._vars = []
		self._start = []
		self._range = []

		Tween.__init__(self,0, _type, complete)

	def tween(self, _object, values, duration, ease=None):
		self._object = _object
		self._vars = []
		selg._start = []
		self._range = []
		self._target = duration
		self._ease = ease
		for k, v in values.values():
			if not _object.hasattr(k):
				raise PyPunkError('The Object does not have the property "' + k + '".')
			self._vars.append(k)
			self._start.append(float(self._object.getattr(k)))
			self._range.append(v - self._start)
		self.start()

	def update(self):
		Tween.update(self)
		i = len(self._vars)
		while i:
			self._object.setattr(self._vars[i], self._start[i] + self.range[i] * self._t)
			i -= 1
