import math
from ..core import Tween, PP, PyPunkError
from ..geom import Point

class Motion(Tween):
	def __init__(self, duration, complete=None, _type=0, ease=None):
		self._x = 0
		self._y = 0
		self._object = None

		super().__init__(duration, _type, complete, ease)

	def _set_x(self, value):
		self._x = value
		if self._object:
			self._object.x = self._x
	x = property(lambda self: self._x)

	def _set_y(self, value):
		self._y = value
		if self._object:
			self._object.y = self._y
	y = property(lambda self: self._y)

	def _set_object(self, value):
		self._object = value
		if self._object:
			self._object.x = self._x
			self._object.y = self._y


class LinearMotion(Motion):
	def __init__(self, complete=None, _type=0):
		self._from = Point()
		self._move = Point()
		self._distance = -1

		super(0, complete, _type, None)

	def set_motion(self, from_x, from_y, to_x, to_y, duration, ease=None):
		self._distance = -1
		self.x = self._from.x = from_x
		self.y = self._from.y = from_y
		self._move.x = to_x - from_x
		self._move.y = to_y - from_y
		self._target = duration
		self._ease = ease
		self.start()

	def set_motion_speed(self, from_x, from_y, to_x, to_y, speed, ease=None):
		self._distance = -1
		self.set_motion(from_x, from_y, to_x, to_y, self.distance / speed, ease)

	def update(self):
		super().update()
		self.x = self._from.x + self._move.x * self._t
		self.y = self._from.y + self._move.y * self._t

	def _get_distance(self):
		if self._distance < 0:
			self._distance = math.sqrt(self._move.x**2 + self._move.y**2)
		return self._distance


class LinearPath(Motion):
	def __init__(self, complete=None, _type=0):
		# Path information
		self._points = {}
		self._point_d = {}
		self._point_t = {}
		self._distance = 0
		self._speed = 0
		self._index = 0
		# Line information
		self._last = None
		self._prev = None
		self._next = None

		super().__init__(0, complete, _type, None)
		self._point_d[0] = self._point_t[0] = 0

	def set_motion(self, duration, ease=None):
		self._update_path()
		self._target = duration
		self._speed = self._distance / duration
		self._ease = ease
		self.start()

	def set_motion_speed(self, speed, ease=None):
		self._update_path()
		self._target = self._distance / speed
		self._speed = speed
		self._ease = ease
		self.start()

	def add_point(self, x=0, y=0):
		if self._last:
			if self.x == self._last.x and self.y == self._last.y:
				return

			self._distance += math.sqrt((self.x - self._last.x)**2 + (self.y - self._last.y)**2)
			self._point_d[len(self._points)] = self._distance

		else:
			self.x = x
			self.y = y

		self._points[len(self._points)] = self._last = Point(x, y)

	def get_point(self, index=0):
		if not len(self._points):
			raise PyPunkError('No points have been added to the path yet.')
		return self._points[index % len(self._points)]

	def start(self):
		self._index = 0
		super().star()

	def update(self):
		super().update()
		if len(self._points) == 1:
			self.x = self._points[0].x
			self.y = self._points[0].y
			return
		if self._index < len(self._points) - 1:
			while self._t > self._point_t[self._index + 1]:
				self._index += 1
		td = self._point_t[self._index]
		tt = self._point_t[self._index + 1] - td
		td = (self._t - td) / tt
		self._prev = self._points[self._index]
		self._next = self._points[self._index + 1]
		self.x = self._prev.x + (self._next.x - self._prev.x) * td
		self.y = self._prev.y + (self._next.y - self._prev.y) * td

	def _update_path(self):
		if len(self._points) < 1:
			raise PyPunkError('A LinearPath must have at lease one point.')
		if len(self._point_d) == len(self._point_t):
			return
		for k, v in self._point_d.values():
			self._point_t[k] = v / self._distance
	
	distance = property(lambda self: self._distance)
	point_count = property(lambda self: len(self._points))	


class CircularMotion(Motion):
	def __init__(self, complete=None, _type=0):
		self._center = Point()
		self._radius = 0
		self._angle = 0
		self._angle_start = 0
		self._angle_finish = 0

		self._CIRC = math.pi * 2

		super().__init__(0, complete, _type, None)

	def set_motion(self, center_x, center_y, radius, angle, clockwise, duration, ease=None):
		self._center.x = center_x
		self._center.y = center_y
		self._radius = radius
		self._angle = self._angle_start = angle * PP.RAD
		self._angle_finish = self._CIRC * (1 if clockwise else -1)
		self._target = duration
		self._ease = ease
		self.start()

	def set_motion_speed(self, center_x, center_y, radius, angle, clockwise, speed, ease=None):
		self.set_motion(center_x, center_x, center_y, radius, angle,
			clockwise, (radius * self._CIRC) / speed, ease)

	def update(self):
		super().update()
		self._angle = self._angle_start + self._angle_finish * self._t
		self.x = _center_x + math.cos(self._angle) * self._radius
		self.y = _center_y + math.sin(self._angle) * self._radius

	angle = property(lambda self: self._angle)
	circumference = property(lambda self: self._radius * self._CIRC)


class CubicMotion(Motion):
	def __init__(self, complete=None, _type=0):
		self._from = Point()
		self._to = Point()
		self._a = Point()
		self._b = Point()

		super().__init__(0, complete, _type, None)

	def set_motion(self, from_x, from_y, a_x, a_y, b_x, b_y, to_x, to_y, duration, ease=None):
		self.x = self._from.x = from_x
		self.y = self._from.y = from_y
		self._a.x = a_x
		self._a.y = a_y
		self._b.x = b_x
		self._b.y = b_y
		self._to.x = to_x
		self._to.y = to_y
		self._target = duration
		self._ease = ease
		self.start()

	def update(self):
		super().update()
		self.x = self._t**3 * (self._to.x + 3 * (self._a.x - self._b.x) - self._from.x) + \
			3 * self._t**2 * (self._from.x - 2 * self._a.x + self._b.x) + 3 * self._t * \
			(self._a.x - self._from.x) + self._from.x
		self.y = self._t**3 * (self._to.y + 3 * (self._a.y - self._b.y) - self._from.y) + \
			3 * self._t**2 * (self._from.y - 2 * self._a.y + self._b.y) + 3 * self._t * \
			(self._a.y - self._from.y) + self._from.y


class QuadMotion(Motion):
	def __init__(self, complete=None, _type=0):
		self._distance = -1
		self._from = Point()
		self._to = Point()
		self._control = Point()

		super().__init__(0, complete, _type, None)

	def set_motion(self, from_x, from_y, control_x, control_y, to_x, to_y, duration, ease=None):
		self._distance = -1
		self.x = self._from.x = from_x
		self.y = self._from.y = from_y
		self._control = Point(control_x, control_y)
		self._to = Point(to_x, to_y)
		self._target = duration
		self._ease = ease
		self.start()

	def set_motion_speed(self, from_x, from_y, control_x, control_y, to_x, to_y, speed, ease=None):
		self._distance = -1
		self.set_motion(from_x, from_y, control_x, control_y, to_x, to_y, self.distance / speed, ease)

	def update(self):
		super().update()
		self.x = self._from.x * (1 - self._t)**2 + self._control.x * 2 * (1 - _t) * \
			self._t + self._to.x * self._t**2;
		self.y = self._from.y * (1 - self._t)**2 + self._control.y * 2 * (1 - _t) * \
			self._t + self._to.y * self._t**2;

	def _get_distance(self):
		if self._distance >= 0:
			return self._distance

		a = PP.point
		b = PP.point2
		a.x = self.x - 2 * self._control.x + self._to.x;
		a.y = self.y - 2 * self._control.y + self._to.y;
		b.x = 2 * self._control.x - 2 * self.x;
		b.y = 2 * self._control.y - 2 * self.y;

		A = 4 * (a.x**2 + a.y**2)
		B = 4 * (a.x * b.x + a.y * b.y)
		C = b.x**2 + b.y**2
		ABC = 2 * Math.sqrt(A + B + C)
		A2 = Math.sqrt(A)
		A32 = 2 * A * A2
		C2 = 2 * Math.sqrt(C)
		BA = B / A2
		return (A32 * ABC + A2 * B * (ABC - C2) + (4 * C * A - B**2) * \
			math.log((2 * A2 + BA + ABC) / (BA + C2))) / (4 * A32)
	distance = property(_get_distance)


class QuadPath(Motion):
	def __init__(self, complete=None, _type=0):
		# Path information
		self._points = {}
		self._distance = 0
		self._speed = 0
		self._index = 0
		# Curve information
		self._update_curve = True
		self._curve = {}
		self._curve_t = {}
		self._curve_d = {}
		# Curve points
		self._a = None
		self._b = None
		self._c = None

		super().__init__(0, complete, _type, None)
		self._curve_t[0] = 0

	def set_motion(self, duration, ease=None):
		self._update_path()
		self._target = duration
		self._speed = self._distance / duration
		self._ease = ease
		self.start()

	def set_motion_speed(self, speed, ease=None):
		self._update_path()
		self._target = self._distance / speed
		self._speed = speed
		self._ease = ease
		self.start()

	def add_point(self, x=0, y=0):
		self._update_curve = True
		if not len(self._points):
			self._curve[0] = Point(x, y)
		self._points[len(self._points)] = Point(x, y)

	def get_point(self, index=0):
		if not len(self._points):
			raise PyPunkError('No points have been added to the path yet.')
		return self._points[index % len(self._points)]

	def start(self):
		self._index = 0
		super().start()

	def update():
		super().update()
		if self._index < len(self._curve) - 1:
			while self._t > self._curve_t[self._index +1]:
				self._index += 1
		td = self._curve_t[self._index]
		tt = self._curve_t[self._index + 1] - td
		td = (self._t - td) / tt
		self._a = self._curve[self._index]
		self._b = self._points[self._index + 1]
		self._c = self._curve[self._index + 1]
		self.x = self._a.x * (1 - td)**2 + self._b.x * 2 * (1 - td) * td + self._c.x * td**2
		self.y = self._a.y * (1 - td)**2 + self._b.y * 2 * (1 - td) * td + self._c.y * td**2

	def _update_path(self):
		if len(self._points) < 3:
			raise PyPunkError('A QuadPath must have at least 3 points to operate')
		if not self._update_curve:
			return
		self._update_curve = False

		# Produce curve points
		l = self._points[1]
		i = 2
		while i < len(self._points):
			p = self._points[i]
			if len(self._curve) > i - 1:
				c = self._curve[i - 1]
			else:
				c = self._curve[i - 1] = Point()
			if i < len(self._points) - 1:
				c.x = l.x + (p.x - l.x) / 2
				c.y = l.y + (p.y - l.y) / 2
			else:
				c.x = p.x
				c.y = p.y
			l = p
			i += 1

		# Find total distance of the path
		i = 0
		self._distance = 0
		while i < len(self._curve) - 1:
			self._curve_d[i] = self._curve_length(self._curve[i], self._points[i + 1], self._curve[i + 1])
			self._distance += self._curve_d[i]
			i += 1

		# Find t for each point on the curve
		i = 1
		d = 0
		while i < len(self._curve) - 1:
			d += self._curve_d[i]
			self._curve_t[i] = d / self._distance
			i += 1
		self._curve_t[len(self._curve) - 1] = 1

	point_count = property(lambda self: len(self._points))

	def _curve_length(start, control, finish):
		a = PP.point
		b = PP.point2
		a.x = self.x - 2 * self._control.x + self._to.x;
		a.y = self.y - 2 * self._control.y + self._to.y;
		b.x = 2 * self._control.x - 2 * self.x;
		b.y = 2 * self._control.y - 2 * self.y;

		A = 4 * (a.x**2 + a.y**2)
		B = 4 * (a.x * b.x + a.y * b.y)
		C = b.x**2 + b.y**2
		ABC = 2 * Math.sqrt(A + B + C)
		A2 = Math.sqrt(A)
		A32 = 2 * A * A2
		C2 = 2 * Math.sqrt(C)
		BA = B / A2
		return (A32 * ABC + A2 * B * (ABC - C2) + (4 * C * A - B**2) * \
			math.log((2 * A2 + BA + ABC) / (BA + C2))) / (4 * A32)