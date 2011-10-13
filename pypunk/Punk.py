import random, math

DEG = -180 / math.pi
RAD = math.pi / -180

class ClassProperty(property):
	'''Subclass @property to make classmethod properties possible'''
	def __get__(self, cls, owner):
		return self.fget.__get__(None, owner)()

class Point(object):
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	
	def normalize(self, scale):
		norm = math.sqrt(self.x*self.x+self.y*self.y)
		if not norm == 0:
			self.x = scale * self.x / norm
			self.y = scale * self.y / norm
	
	@property
	def length(self):
		return math.sqrt((0-self.x)*(0-self.x)+(0-self.y)*(0-self.y))

#So we can use properties and such :3
class _punk(object):
	def __init__(self):
		self.Engine = None
		self.elapsed = 0
		self.FPS = 0

		self.width = 0
		self.height = 0

		self.camera = Point()
	
	def set_world(self, value):
		if self.Engine.World: self.Engine.WorldChanged()
		self.Engine.World = value
	world = property(lambda self: self.Engine.World, set_world)

	buffer = property(lambda self: self.Engine.App)

	screen = property(lambda self: self.Engine.App.Capture())

	# kind of useless because python already have a choice function
	# but we should keep it for compatibility with FlashPunk and for
	# users not used to python
	@staticmethod
	def choose(*args):
		'''Randomly chooses and returns one of the provided values.
		@param	...objs		The Objects you want to randomly choose from. Can be ints, Numbers, Points, etc.
		@return	A randomly chosen one of the provided parameters.
		'''
		return random.choice(args)

	@staticmethod
	def sign(value):
		'''Finds the sign of the provided value.
		@param	value		The Number to evaluate.
		@return	1 if value > 0, -1 if value < 0, and 0 when value == 0.
		'''
		return -1 if value < 0 else 1 if value > 0 else 0

	@staticmethod
	def approach(value, target, amount):
		'''Approaches the value towards the target, by the specified amount, without overshooting the target.
		@param	value	The starting value.
		@param	target	The target that you want value to approach.
		@param	amount	How much you want the value to approach target by.
		@return	The new value.
		'''
		if value < target:
			return target if target < value + amount else value + amount
		else:
			return target if target > value - amount else value - amount
	
	@staticmethod
	def lerp(a, b, t=1.0):
		'''Linear interpolation between two values.
		@param	a		First value.
		@param	b		Second value.
		@param	t		Interpolation factor.
		@return	When t=0, returns a. When t=1, returns b. When t=0.5, will return halfway between a and b. Etc.
		'''
		return a + (b - a) * t

	@staticmethod
	def colorLerp(fromColor, toColor, t=1.0):
		'''Linear interpolation between two colors.
		@param	fromColor		First color.
		@param	toColor			Second color.
		@param	t				Interpolation value. Clamped to the range [0, 1].
		return	RGB component-interpolated color value.
		'''
		if t <= 0: return fromColor
		if t >= 1: return toColor
		a = fromColor >> 24 & 0xFF
		r = fromColor >> 16 & 0xFF
		g = fromColor >> 8 & 0xFF
		b = fromColor & 0xFF
		dA = (toColor >> 24 & 0xFF) - a
		dR = (toColor >> 16 & 0xFF) - r
		dG = (toColor >> 8 & 0xFF) - g
		dB = (toColor & 0xFF) - b
		a += dA * t
		r += dR * t
		g += dG * t
		b += dB * t
		return a << 24 | r << 16 | g << 8 | b

	@staticmethod
	def stepTowards(obj, x, y, distance=1.0):
		'''Steps the object towards a point.
		@param	object		Object to move (must have an x and y property).
		@param	x			X position to step towards.
		@param	y			Y position to step towards.
		@param	distance	The distance to step (will not overshoot target).
		'''
		point = Point(x - obj.x, y - obj.y)
		if point.length <= distance:
			obj.x = x
			obj.y = y
			return
		point.normalize(distance)
		obj.x += point.x
		obj.y += point.y


	@staticmethod
	def anchorTo(obj, anchor, distance=0.0):
		'''Anchors the object to a position.
		@param	object		The object to anchor.
		@param	anchor		The anchor object.
		@param	distance	The max distance object can be anchored to the anchor.
		'''
		point = Point()
		point.x = obj.x - anchor.x
		point.y = obj.y - anchor.y
		if point.length > distance: point.normalize(distance)
		obj.x = anchor.x + point.x
		obj.y = anchor.y + point.y

	@staticmethod
	def angle(x1, y1, x2, y2):
		'''Finds the angle (in degrees) from point 1 to point 2.
		@param	x1		The first x-position.
		@param	y1		The first y-position.
		@param	x2		The second x-position.
		@param	y2		The second y-position.
		@return	The angle from (x1, y1) to (x2, y2).
		'''
		a = math.atan2(y2 - y1, x2 - x1) * DEG
		return a + 360 if a < 0 else a

	@staticmethod
	def angleXY(obj, angle, length=1.0, x=0.0, y=0.0):
		'''Sets the x/y values of the provided object to a vector of the specified angle and length.
		@param	object		The object whose x/y properties should be set.
		@param	angle		The angle of the vector, in degrees.
		@param	length		The distance to the vector from (0, 0).
		@param	x			X offset.
		@param	y			Y offset.
		'''
		angle *= RAD
		obj.x = math.cos(angle) * length + x
		obj.y = math.sin(angle) * length + y

	@staticmethod
	def rotateAround(obj, anchor, angle=0.0, relative=True):
		'''Rotates the object around the anchor by the specified amount.
		@param	object		Object to rotate around the anchor.
		@param	anchor		Anchor to rotate around.
		@param	angle		The amount of degrees to rotate by.
		'''
		if relative: angle += FP.angle(anchor.x, anchor.y, obj.x, obj.y)
		FP.angleXY(obj, angle, FP.distance(anchor.x, anchor.y, obj.x, obj.y), anchor.x, anchor.y)

	@staticmethod
	def angleDiff(a, b):
		'''Gets the difference of two angles, wrapped around to the range -180 to 180.
		@param	a	First angle in degrees.
		@param	b	Second angle in degrees.
		@return	Difference in angles, wrapped around to the range -180 to 180.
		'''
		diff = b - a
		while diff > 180: diff -= 360
		while diff <= -180: diff +=360
		return diff

	@staticmethod
	def distance(x1, y1, x2=0, y2=0):
		'''Find the distance between two points.
		@param	x1		The first x-position.
		@param	y1		The first y-position.
		@param	x2		The second x-position.
		@param	y2		The second y-position.
		@return	The distance.
		'''
		return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

	@staticmethod
	def distanceRects(x1, y1, w1, h1, x2, y2, w2, h2):
		'''Find the distance between two rectangles. Will return 0 if the rectangles overlap.
		@param	x1		The x-position of the first rect.
		@param	y1		The y-position of the first rect.
		@param	w1		The width of the first rect.
		@param	h1		The height of the first rect.
		@param	x2		The x-position of the second rect.
		@param	y2		The y-position of the second rect.
		@param	w2		The width of the second rect.
		@param	h2		The height of the second rect.
		@return	The distance.
		'''
		if x1 < x2 + w2 and x2 < x1 + w1:
			if y1 < y2 + h2 and y2 < y1 + h1:
				return 0
			if y1 > y2:
				return y1 - (y2 + h2)
			return y2 - (y1 + h1)
		if y1 < y2 + h2 and y2 < y1 + h1:
			if x1 > x2:
				return x1 - (x2 + w2)
			return x2 - (x1 + w1)
		if x1 > x2:
			if y1 > y2:
				return Punk.distance(x1, y1, (x2 + w2), (y2 + h2))
			return Punk.distance(x1, y1 + h1, x2 + w2, y2)
		if y1 > y2:
			return Punk.distance(x1 + w1, y1, x2, y2 + h2)
		return Punk.distance(x1 + w1, y1 + h1, x2, y2)

	@staticmethod
	def distanceRectPoint(px, py, rx, ry, rw, rh):
		'''Find the distance between a point and a rectangle. Returns 0 if the point is within the rectangle.
		 * @param	px		The x-position of the point.
		 * @param	py		The y-position of the point.
		 * @param	rx		The x-position of the rect.
		 * @param	ry		The y-position of the rect.
		 * @param	rw		The width of the rect.
		 * @param	rh		The height of the rect.
		 * @return	The distance.
		'''
		if px >= rx and px <= rx + rw:
			if py >= ry and py <= ry + rh:
				return 0
			if py > ry:
				return py - (ry + rh)
			return ry - py
		if py >= ry and py <= ry + rh:
			if px > rx:
				return px - (rx + rw)
			return rx - px
		if px > rx:
			if py > ry:
				return Punk.distance(px, py, rx + rw, ry + rh)
			return Punk.distance(px, py, rx + rw, ry)
		if py > ry:
			return Punk.distance(px, py, rx, ry + rh)
		return Punk.distance(px, py, rx, ry)

	@staticmethod
	def clamp(value, min_, max_):
		'''Clamps the value within the minimum and maximum values.
		@param	value		The Number to evaluate.
		@param	min			The minimum range.
		@param	max			The maximum range.
		@return	The clamped value.
		'''
		if min_ > max_:
			value = value if value < max_ else max_
			return value if value > min_ else min_
		value = value if value < min_ else min_
		return value if value > max_ else max_

	@staticmethod
	def clampInRect(obj, x, y, width, height, padding):
		'''Clamps the object inside the rectangle.
		@param	object		The object to clamp (must have an x and y property).
		@param	x			Rectangle's x.
		@param	y			Rectangle's y.
		@param	width		Rectangle's width.
		@param	height		Rectangle's height.
		'''
		obj.x = FP.clamp(obj.x, x + padding, x + width - padding)
		obj.y = FP.clamp(obj.y, y + padding, y + height - padding)

	@staticmethod
	def scale(value, min1, max1, min2, max2):
		'''Transfers a value from one scale to another scale. For example, scale(.5, 0, 1, 10, 20) == 15, and scale(3, 0, 5, 100, 0) == 40.
		@param	value		The value on the first scale.
		@param	min			The minimum range of the first scale.
		@param	max			The maximum range of the first scale.
		@param	min2		The minimum range of the second scale.
		@param	max2		The maximum range of the second scale.
		@return	The scaled value.
		'''
		return min2 + ((value - min1) / (max1 - min1)) * (max2 - min2)

	@staticmethod
	def scaleClamp(value, min1, max1, min2, max2):
		'''Transfers a value from one scale to another scale, but clamps the return value within the second scale.
		@param	value		The value on the first scale.
		@param	min			The minimum range of the first scale.
		@param	max			The maximum range of the first scale.
		@param	min2		The minimum range of the second scale.
		@param	max2		The maximum range of the second scale.
		@return	The scaled and clamped value.
		'''
		value = min2 + ((value - min1) / (max1 - min1)) * (max2 - min2)
		if max2 > min2:
			value = value if value < max2 else max2
			return value if value > min2 else min2
		value = value if value < min2 else min2
		return value if value > max2 else max2

	@staticmethod
	def randomizeSeed():
		'''Randomizes the random seed using Flash's Math.random() function.
		(simple wrapper around python's random.seed() for FlashPunk users)
		'''
		random.seed(2147483647 * random.random())

	@staticmethod
	def random():
		'''A pseudo-random Number produced using FP's random seed, where 0 <= Number < 1.
		(simple wrapper around python's random.random() for FlashPunk users)
		'''
		return random.random()

	@staticmethod
	def rand(amount):
		'''Returns a pseudo-random uint.
		@param	amount		The returned uint will always be 0 <= uint < amount.
		@return	The uint.
		(simple wrapper around python's random.uniform() for FlashPunk users)
		'''
		return random.uniform(0, amount)

	@staticmethod
	def getColorRGB(R, G, B):
		'''Creates a color value by combining the chosen RGB values.
		@param	R		The red value of the color, from 0 to 255.
		@param	G		The green value of the color, from 0 to 255.
		@param	B		The blue value of the color, from 0 to 255.
		@return	The color uint.
		'''
		return R << 16 | G << 8 | B

	@staticmethod
	def getColorHSV(h, s, v):
		'''Creates a color value with the chosen HSV values.
		@param	h		The hue of the color (from 0 to 1).
		@param	s		The saturation of the color (from 0 to 1).
		@param	v		The value of the color (from 0 to 1).
		@return	The color uint.
		'''
		h = 0 if h < 0 else 1 if h > 1 else h
		s = 0 if s < 0 else 1 if s > 1 else h
		v = 0 if v < 0 else 1 if v > 1 else h
		h = int(h * 360)
		hi = int(h / 60.0) % 6
		f = h / 60.0 - int(h / 60.0)
		p = v * (1 - s)
		q = v * (1 - f * s)
		t = v * (1 - (1 - f) * s)
		if hi == 0: return int(v * 255) << 16 | int(t * 255) << 8 | int(p *255)
		elif hi == 1: return int(q * 255) << 16 | int(v * 255) << 8 | int(p *255)
		elif hi == 2: return int(p * 255) << 16 | int(v * 255) << 8 | int(t *255)
		elif hi == 3: return int(p * 255) << 16 | int(q * 255) << 8 | int(v *255)
		elif hi == 4: return int(t * 255) << 16 | int(p * 255) << 8 | int(v *255)
		elif hi == 5: return int(v * 255) << 16 | int(p * 255) << 8 | int(q *255)
		else: return 0

	
	@staticmethod
	def getRed(color):
		'''Finds the red factor of a color.
		@param	color		The color to evaluate.
		@return	A uint from 0 to 255.
		'''
		return color >> 16 & 0xFF
	
	@staticmethod
	def getGreen(color):
		'''Finds the green factor of a color.
		@param	color		The color to evaluate.
		@return	A uint from 0 to 255.
		'''
		return color >> 8 & 0xFF
	
	@staticmethod
	def getBlue(color):
		'''Finds the blue factor of a color.
		@param	color		The color to evaluate.
		@return	A uint from 0 to 255.
		'''
		return color & 0xFF

	@staticmethod
	def timeFlag():
		'''Sets a time flag.
		@return	Time elapsed (in milliseconds) since the last time flag was set.
		'''
		pass

	@ClassProperty
	@classmethod
	def console(cls):
		'''The global Console object.
		'''
		pass

	@staticmethod
	def log():
		'''
		'''
		pass

	@staticmethod
	def watch():
		'''
		'''
		pass

	@staticmethod
	def tween():
		'''
		'''
		pass

	@staticmethod
	def alarm():
		'''
		'''
		pass

	@staticmethod
	def frames():
		'''
		'''
		pass

	@staticmethod
	def shuffle():
		'''
		'''
		pass

	@staticmethod
	def sort():
		'''
		'''
		pass

	@staticmethod
	def sortBy():
		'''
		'''
		pass

	@staticmethod
	def _quicksort():
		'''
		'''
		pass

	@staticmethod
	def _quicksortBy():
		'''
		'''
		pass



Punk = _punk()
