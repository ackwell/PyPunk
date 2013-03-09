import math
import random
import sfml
from .geom import Point, Rectangle


class Graphic(object):
	def __init__(self):
		# Public Variables
		self.active = False
		self.visible = True
		self.x = 0
		self.y = 0
		self.scroll_x = 1
		self.scroll_y = 1
		self.relative = True
		self.assign = None

		# Private Variables
		self._point = Point()

	def update(self): pass

	def render(self, target, point, camera): pass


class Image(Graphic):
	def __init__(self, source, clip_rect=None, cache=True):
		super().__init__()
		
		# Private Variables
		self._scale = 1
		self._scale_x = 1
		self._scale_y = 1

		# Might be no source (Shapes, etc)
		if source:
			# Set the pixels in case I need them down the road (pixel perfect, etc)
			texture, self.pixels = get_image(source, cache)
			self.sprite = sfml.Sprite(texture)

			# Set the cliprect if it's been passed
			_source_rect = self.sprite.local_bounds
			if clip_rect:
				if not clip_rect.width:
					clip_rect.width = _source_rect.width
				if not clip_rect.height:
					clip_rect.height = _source_rect.height
				self.sprite.set_texture_rect(clip_rect)

	def render(self, target, point, camera):
		self._point.x = point.x + self.x - self.origin_x - camera.x * self.scroll_x
		self._point.y = point.y + self.y - self.origin_y - camera.y * self.scroll_y

		# position the sprite
		self.sprite.position = (self._point.x, self._point.y)

		# Draw eet
		target.draw(self.sprite)

	# Some static methods for compatibility with original FP API
	@staticmethod
	def create_rect(width, height, color=0xFFFFFF, alpha=1):
		shape = RectangleShape(width, height, color, alpha)
		return shape

	@staticmethod
	def create_circle(radius, color=0xFFFFFF, alpha=1):
		shape = CircleShape(radius, color, alpha)
		return shape

	# Transform functions
	def _set_angle(self, value):
		self.sprite.rotation = value
	angle = property(lambda self: self.sprite.rotation, _set_angle)

	def _set_scale_x(self, value):
		self._scale_x = value
		self.sprite.scale = (value*self._scale, self.sprite.scale[1])
	scale_x = property(lambda self: self.sprite.scale[0], _set_scale_x)

	def _set_scale_y(self, value):
		self.scale_y = value
		self.sprite.scale = (self.sprite.scale[0], value*self._scale)
	scale_y = property(lambda self: self.sprite.scale[1], _set_scale_y)

	def _set_scale(self, value):
		self._scale = value
		self.sprite.scale = (self._scale_x*value, self._scale_y*value)
	scale = property(lambda self: self._scale, _set_scale)

	def _set_origin_x(self, value):
		self.sprite.origin = (value, self.sprite.origin[1])
	origin_x = property(lambda self: self.sprite.origin[0], _set_origin_x)

	def _set_origin_y(self, value):
		self.sprite.origin = (self.sprite.origin[0], value)
	origin_y = property(lambda self: self.sprite.origin[1], _set_origin_y)

	def center_origin(self):
		tr = self.sprite.get_texture_rect()
		self.sprite.origin = (tr.width/2, tr.height/2)

	def _set_smooth(self, value):
		self.sprite.texture.smooth = value
	smooth = property(lambda self: self.sprite.texture.smooth, _set_smooth)

	# Color Tinting, etc
	def _set_alpha(self, value):
		value = min(1, max(0, value))
		color = self.sprite.color
		color.a = value*255
		self.sprite.color = color
	alpha = property(lambda self: self.sprite.color.a/255, _set_alpha)

	def _set_color(self, value):
		color = hex2color(value)
		color.a = self.sprite.color.a
		self.sprite.color = color
	color = property(lambda self: color2hex(self.sprite.color), _set_color)

	# Size information
	width = property(lambda self:self.sprite.get_texture_rect().width)
	height = property(lambda self:self.sprite.get_texture_rect().height)
	scaled_width = property(lambda self:self.sprite.get_texture_rect().width*self._scale_x*self._scale)
	scaled_height = property(lambda self:self.sprite.get_texture_rect().height*self._scale_y*self._scale)
	def _get_clip_rect(self):
		 tr = self.sprite.get_texture_rect()
		 return Rectangle(tr.left, tr.top, tr.width, tr.height)
	clip_rect = property(_get_clip_rect)


class ShapeMixin(object):
	# Need to redefine color/alpha due to slightly different API (color -> fill_color)
	def _set_alpha(self, value):
		value = min(1, max(0, value))
		color = self.sprite.fill_color
		color.a = value*255
		self.sprite.fill_color = color
	alpha = property(lambda self: self.sprite.fill_color.a/255, _set_alpha)

	def _set_color(self, value):
		color = hex2color(value)
		color.a = self.sprite.fill_color.a
		self.sprite.fill_color = color
	color = property(lambda self: color2hex(self.sprite.fill_color), _set_color)


class RectangleShape(ShapeMixin, Image):
	def __init__(self, width, height, color=0xFFFFFF, alpha=1):
		super().__init__(None)
		# I know, it's not a sprite. Whatever.
		self.sprite = sfml.RectangleShape((width, height))
		self.color = color
		self.alpha = alpha


class CircleShape(ShapeMixin, Image):
	def __init__(self, radius, color=0xFFFFFF, alpha=1):
		super().__init__(None)
		self.sprite = sfml.CircleShape(radius)
		self.color = color
		self.alpha = alpha


class Spritemap(Image):
	def __init__(self, source, frame_width=0, frame_height=0, callback=None):
		# Importing here to prevent cyclic imports. Any better ideas?
		from .core import PP
		self.PP = PP

		# Public variables
		self.complete = True
		self.callback = callback
		self.rate = 1

		# Private variables
		self._anims = {}
		self._anim = None
		self._index = 0
		self._frame = 0
		self._timer = 0

		# Init
		self._rect = Rectangle(0, 0, frame_width, frame_height)
		super().__init__(source, self._rect)
		source = self.sprite.texture
		if not frame_width:
			_rect.width = source.width
		if not frame_height:
			_rect.height = source.height
		self._width = source.width
		self._height = source.height
		self._columns = math.ceil(self._width / self._rect.width)
		self._rows = math.ceil(self._height / self._rect.height)
		self._frame_count = self._columns * self._rows

		self.active = True

	def render(self, target, point, camera):
		self._rect.x = self._rect.width * (self._frame % self._columns)
		self._rect.y = self._rect.height * int(self._frame / self._columns)
		self.sprite.set_texture_rect(self._rect)

		super().render(target, point, camera)

	def update(self):
		if self._anim and not self.complete:
			time_add = self._anim._frame_rate * self.rate
			time_add *= self.PP.elapsed
			self._timer += time_add
			if self._timer >= 1:
				while self._timer >= 1:
					self._timer -= 1
					self._index += 1
					if self._index == self._anim._frame_count:
						if self._anim._loop:
							self._index = 0
							if self.callback:
								self.callback()
						else:
							self._index = self._anim._frame_count - 1
							self.complete = True
							if self.callback:
								self.callback()
							break
				if self._anim:
					self._frame = int(self._anim._frames[self._index])

	def add(self, name, frames, frame_rate=0, loop=True):
		for i in range(len(frames)):
			frames[i] %= self._frame_count
			if frames[i] < 0:
				frames[i] += self._frame_count
		anim = Anim(name, frames, frame_rate, loop)
		anim._parent = self
		self._anims[name] = anim
		return anim

	def play(self, name="", reset=False, frame=0):
		if not reset and self._anim and self._anim._name == name:
			return self._anim
		self._anim = self._anims[name]
		self._index = 0
		self._timer = 1
		self._frame = int(self._anim._frames[frame % self._anim._frame_count])
		self.complete = False
		return self._anim

	def get_frame(self, column=0, row=0):
		return (row % self._rows) * self._columns + (column % self._columns)

	def set_frame(self, column=0, row=0):
		self._anim = None
		frame = self.get_frame(column, row)
		if self._frame == frame: return
		self._frame = frame
		self._timer = 0

	def rand_frame(self):
		self.frame = random.randint(self._frame_count)

	def set_anim_frame(self, name, index):
		frames = self._anims[name]._frames
		self.index %= len(frames)
		if self.index < 0:
			self.index += len(frames)
		self.frame = frames[self.index]

	def _set_frame(self, value):
		self._anim = None
		value %= self._frame_count
		if value < 0:
			value = self._frame_count + value
		if self._frame == value:
			return
		self._frame = value
		self._timer = 0
	frame = property(lambda self: self._frame, _set_frame)

	def _set_index(self, value):
		if not self._anim:
			return
		value %= self._anim._frame_count
		if self._index == value:
			return
		self._index = value
		self._frame = int(self._anim._frames[self._index])
		self._timer = 0
	index = property(lambda self: self._index, _set_index)

	frame_count = property(lambda self: self._frame_count)
	columns = property(lambda self: self._columns)
	rows = property(lambda self: self._rows)
	current_anim = property(lambda self: self._anim._name if self._anim else "")


class Anim:
	def __init__(self, name, frames, frame_rate=0, loop=True):
		self._name = name
		self._frames = frames
		self._frame_rate = frame_rate
		self._loop = loop
		self._frame_count = len(frames)
		self._parent = None

	def play(self, reset=False):
		self._parent.play(self._name, reset)

	name = property(lambda self: self._name)
	frames = property(lambda self: self._frames)
	frame_rate = property(lambda self: self._frame_rate)
	frame_count = property(lambda self: self._frame_count)
	loop = property(lambda self: self._loop)


# Utility functions + Caching
def hex2color(_hex):
	b = _hex & 255
	g = (_hex >> 8) & 255 
	r = (_hex >> 16) & 255
	return sfml.Color(r, g, b)
def color2hex(color):
	return color.r*65536 + color.g*256 + color.b

image_cache = {}
def get_image(loc, cache):
	if isinstance(loc, str):
		loc = loc.encode()
	if loc in image_cache:
		return image_cache[loc]
	else:
		image = sfml.Image.load_from_file(loc)
		pixels = image.get_pixels()
		texture = sfml.Texture.load_from_image(image)
		t = (texture, pixels)
		if cache:
			image_cache[loc] = t
		return t
