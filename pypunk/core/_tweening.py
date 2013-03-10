from ._pp import PP

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