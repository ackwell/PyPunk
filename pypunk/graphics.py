import sfml
from .geom import Point


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
		
		# Public Variables
		self.angle = 0
		self.scale = 1
		self.scale_x = 1
		self.scale_y = 1
		self.origin_x = 0
		self.origin_y = 0
		self.smooth = False

		# get the pixels in case I need them down the road (pixel perfect, etc)
		texture, self.pixels = get_image(source, cache)
		self.sprite = sfml.Sprite(texture)

	def render(self, target, point, camera):
		self._point.x = point.x + self.x - self.origin_x - camera.x * self.scroll_x
		self._point.y = point.y + self.y - self.origin_y - camera.y * self.scroll_y

		# position the sprite
		self.sprite.position = (self._point.x, self._point.y)

		# Draw eet
		target.draw(self.sprite)

	# NEEDS TRANSFORMATION STUFF HERE


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
