from PySFML import sf
import math

TWEEN_PERSIST = 0	# Persistent Tween type, will stop when it finishes.
TWEEN_LOOP = 1		# Looping Tween type, will restart immediately when it finishes.
TWEEN_ONESHOT = 2	# Oneshot Tween type, will stop and remove itself from its core container when it finishes.

#maybe make an exists var so tweens can be removed?

class Timer:
	def __init__(self):
		"""Create new simple timer"""
		self.running = False
		self.value = 0
	
	#Not actually a tween but meh
	def updateTween(self):
		if self.running:
			self.value += Punk.elapsed
	
	#Start counting
	def start(self):
		self.running = True

	#Stop counting, reset
	def stop(self):
		self.running = False
		self.value = 0
	
	#Stop counting, stay at current value
	def pause(self):
		self.running = False

	#Continue counting, reset value
	def reset(self):
		self.value = 0

#Base class for other tweens
class Tween():
	def __init__(self, duration, type = 0, complete = None, ease = None):
		self._target = duration
		self._type = type
		self.complete = complete
		self._ease = ease

		self.active = False
		self._time = 0
		self._t = 0

		self._finish = False
		self._parent = None
		self._prev = None
		self._next = None
	
	def update(self):
		from Punk import Punk
		self._time += Punk.elapsed
		self._t = self._time / self._target
		if not self._ease == None and self._t > 0 and self._t < 1:
			self._t = self._ease(self._t)
		if self._time >= self._target:
			self._t = 1
			self._finish = True
	
	def start(self):
		self._time = 0
		if self._target == 0:
			self.active = False
			return
		self.active = True

	def cancel(self):
		self.active = False
		if self._parent:
			self._parent.removeTween(self)

	def finish(self):
		if self._type == TWEEN_PERSIST:
			self._time = self._target
			self.active = False
		elif self._type == TWEEN_LOOP:
			self._time %= self._target
			self._t = self._time / self._target
			if not self._ease == None and self._t > 0 and self._t < 1:
				self._t = self._ease(self._t)
			self.start()
		elif self._type == TWEEN_ONESHOT:
			self._time = self._target
			self.active = False
			self._parent.removeTween(self)
		self._finish = False
		if self.complete:
			self.complete()
	
	def get_percent(self):
		return self._time / self._target
	def set_percent(self, value):
		self._time = self._target * value
	percent = property(get_percent, set_percent)

	@property
	def scale(self): return self._t


class Tweener(object):
	'''Updateable Tween container.
	'''
	def __init__(self):
		self.active = True
		self.autoClear = False

		self._tween = None 	# private

	def update(self):
		pass

	def addTween(self, t, start=False):
		if t._parent: raise Exception("Cannot add a Tween object more than once.")
		t._parent = self
		t._next = self._tween
		if self._tween: self._tween._prev = t
		self._tween = t
		if (start): self._tween.start()
		return t
	
	def removeTween(self, t):
		if t._parent != self: raise Exception("Core object does not contain Tween.")
		if t._next: t._next._prev = t._prev
		if t._prev: t._prev._next = t._next
		else: self._tween = t._next
		t._next = t._prev = None
		t._parent = None
		t.active = False
		return t

	def clearTweens(self):
		t = self._tween
		while t:
			n = t._next
			removeTween(t)
			t = n

	def updateTweens(self):
		t = self._tween
		while t:
			n = t._next
			if (t.active):
				t.update()
				if t._finish: t.finish()
			t = n
			
class Alarm(Tween):
	'''A simple alarm, useful for timed events, etc.
	'''
	def __init__(self, duration, complete=None, type_=0):
		Tween.__init__(self, duration, type_, complete, None)

	def reset(self, duration):
		self._target = duration
		self.start()

	elapsed = property(lambda self: self._time)
	duration = property(lambda self: self._target)
	remaining = property(lambda self: self._target - self._time)

class NumTween(Tween):
	def __init__(self, complete = None, type = 0):
		Tween.__init__(self, 0, type, complete)
		self._start = 0
		self._range = 0
		self.value = 0
	
	def tween(fromValue, toValue, duration, ease = None):
		self._start = self.value = fromValue
		self._range = toValue - self.value
		self._target = duration
		self._ease = ease
		self.start()
	
	def updateTween(self):
		Tween.updateTween(self)
		self.value = self._start + self._range * self._t

class VarTween(Tween):
	def __init__(self, complete = None, type = 0):
		Tween.__init__(self, 0, type, complete)
		self._start = 0
		self._range = 0
		self._property = None
	
	def tween(self, obj, property_, toValue, duration, ease = None):
		self._object = obj
		self._property = property_
		self._ease = ease

		self._start = getattr(obj, property_)
		self._range = toValue - self._start
		self._target = duration
		self.start()
	
	def updateTween(self):
		Tween.updateTween(self)
		setattr(self._object, self._property, self._start + self._range * self._t)

class MultiVarTween(Tween):
	def __init__(self, complete = None, type = 0):
		Tween.__init__(self, 0, type, complete)
		self._vars = []
		self._start = []
		self._range = []
		self._object = None
	
	def tween(self, obj, values, duration, ease = None):
		self._object = obj
		self._target = duration
		self._ease = ease
		for k, v in values.iteritems():
			self._vars.append(k)
			self._start.append(getattr(obj, k))
			self._range.append(v - getattr(obj, k))
		self.start()
	
	def updateTween(self):
		Tween.updateTween(self)
		for i in range(len(self._vars)):
			setattr(self._object, self._vars[i], self._start[i] + self._range[i] * self._t)

class AngleTween(Tween):
	def __init__(self, complete = None, type = 0):
		Tween.__init__(self, 0, type, complete)
	
	def tween(self, fromAngle, toAngle, duration, ease = None):
		self._start = self.angle = fromAngle
		d = toAngle - self.angle
		a = math.fabs(d)
		if a > 181: self._range = (360 - a) * (-1 if d > 0 else 1)
		elif a < 179: self._range = d
		else: self._range = Punk.choose(180, -180)
		self._target = duration
		self._ease = ease
		self.start()
	
	def updateTween(self):
		Tween.updateTween(self)
		self.angle = (self._start + self._range * self._t) % 360
		if self.angle < 0: self.angle += 360

##### EASING #####

# QUAD #
def ease_quadIn(t): return t*t
def ease_quadOut(t): return -t*(t-2)
def ease_quadInOut(t): t2=t-1; return t*t*2 if t<=0.5 else 1-t2*t2*2

# CUBIC #
def ease_cubeIn(t): return t*t*t
def ease_cubeOut(t): t-=1; return 1+t*t*t
def ease_cubeInOut(t): t2=t-1; return t*t*t*4 if t<=0.5 else 1+t2*t2*t2*4

# QUART #
def ease_quartIn(t): return t*t*t*t
def ease_quartOut(t): t-=1; return 1-t*t*t*t
def ease_quartInOut(t): t2=t*2-2; return t*t*t*t*8 if t<=0.5 else (1-t2*t2*t2*t2)/2+0.5

# QUINT #
def ease_quintIn(t): return t*t*t*t*t
def ease_quintOut(t): t=-1; return t*t*t*t*t+1
def ease_quintInOut(t): t*=2; t2=t-2; return (t*t*t*t*t)/2 if t<1 else (t2*t2*t2*t2*t2+2)/2

# SINE #
def ease_sineIn(t): return -math.cos(PI2*t)+1
def ease_sineOut(t): return math.sin(PI2*t)
def ease_sineInOut(t): return -math.cos(PI*t)/2+0.5

# BOUNCE #
def ease_bounceIn(t):
	t=1-t
	if t<B1: return 1-7.5625*t*t;
	if t<B2: return 1-(7.5625*(t-B3)*(t-B3)+0.75)
	if t<B4: return 1-(7.5625*(t-B5)*(t-B5)+0.9375)
	return 1-(7.5625*(t-B6)*(t-B6)+0.984375)
def ease_bounceOut(t):
	if t<B1: return 7.5625*t*t;
	if t<B2: return 7.5625*(t-B3)*(t-B3)+0.75
	if t<B4: return 7.5625*(t-B5)*(t-B5)+0.9375
	return 7.5625*(t-B6)*(t-B6)+0.984375
def ease_bounceInOut(t):
	if t<0.5:
		t=1-t*2
		if t<B1: return (1-7.5625*t*t)/2
		if t<B2: return (1-(7.5625*(t-B3)*(t-B3)+0.75))/2
		if t<B4: return (1-(7.5625*(t-B5)*(t-B5)+0.9375))/2
		return (1-(7.5625*(t-B6)*(t-B6)+0.984375))/2
	t=t*2-1
	if t<B1: return (7.5625*t*t)/2+0.5
	if t<B2: return (7.5625*(t-B3)*(t-B3)+0.75)/2+0.5
	if t<B4: return (7.5625*(t-B5)*(t-B5)+0.9375)/2+0.5
	return (7.5625*(t-B6)*(t-B6)+0.984375)/2+0.5

# CIRCLE #
def ease_circIn(t): return -(math.sqrt(1-t*t)-1)
def ease_circOut(t): return math.sqrt(1-(t-1)*(t-1))
def ease_circInOut(t): return (math.sqrt(1-t*t*4)-1)/-2 if t<=0.5 else (math.sqrt(1-(t*2-2)*(t*2-2))+1)/2

# EXPONENTIAL #
def ease_expoIn(t): return math.pow(2, 10*(t-1))
def ease_expoOut(t): return -math.pow(2, -10*t)+1
def ease_expoInOut(t): return math.pow(2, 10*(t*2-1))/2 if t<0.5 else (-math.pow(2, -10*(t*2-1))+2)/2

# BACK #
def ease_backIn(t): return t*t*(2.70158*t-1.70158)
def ease_backOut(t): t-=1; return 1-t*t*(-2.70158*t-1.70158)
def ease_backInOut(t):
	t*=2;
	if t<1: return t*t*(2.70158*t-1.70158)/2
	t-=2; return (1-t*t*(-2.70158*t-1.70158))/2+0.5

# VARS #
PI=math.pi
PI2=math.pi/2
EL=2*PI/0.45
B1=1/2.75;
B2=2/2.75;
B3=1.5/2.75;
B4=2.5/2.75;
B5=2.25/2.75;
B6=2.625/2.75;
