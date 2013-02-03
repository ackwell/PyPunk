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

		# get the pixels in case I need them down the road (pixel perfect, etc)
		texture, self.pixels = get_image(source, cache)
		self.sprite = sfml.Sprite(texture)

		# Set the cliprect if it's been passed
		if clip_rect:
			self.sprite.set_texture_rect(clip_rect)

	def render(self, target, point, camera):
		self._point.x = point.x + self.x - self.origin_x - camera.x * self.scroll_x
		self._point.y = point.y + self.y - self.origin_y - camera.y * self.scroll_y

		# position the sprite
		self.sprite.position = (self._point.x, self._point.y)

		# Draw eet
		target.draw(self.sprite)

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
