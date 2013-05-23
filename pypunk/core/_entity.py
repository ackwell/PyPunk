from ._pp import PP
from ._tweening import Tweener

class Entity(Tweener):
	"""
	Main game Entity class, updated by World.

	:param x: X position to place the Entity.
	:param y: Y position to place the Entity.
	:param graphic: Graphic to assign to the Entity.
	:param mask:    Mask to assign to the Entity.
	"""
	def __init__(self, x=0, y=0, graphic=None, mask=None):
		"""
		If you override this, make sure you call ``super().__init__()``
		to ensure the Entity instance is instanciated correctly.
		"""
		super().__init__()

		# Public variables
		#: If the Entity should render. Default: ``True``
		self.visible = True
		#: If the Entity should respond to collision checks. Default: ``True``
		self.collidable = True
		#: X position of the Entity in the World.
		self.x = x
		#: Y position of the Entity in the World.
		self.y = y
		#: Width of the Entity's hitbox.
		self.width = 0
		#: Height of the Entity's hitbox.
		self.height = 0
		#: X origin of the Entity's hitbox.
		self.origin_x = 0
		#: Y origin of the Entity's hitbox.
		self.origin_y = 0
		#: The Screen target to draw the entity onto. Leave as None
		#: to render to the current window.
		self.render_target = None

		# Private variables
		self._class = self.__class__.__name__
		self._world = None
		self._type = ''
		self._name = ''
		self._layer = 0
		self._update_prev = None
		self._update_next = None
		self._render_prev = None
		self._render_next = None
		self._type_prev = None
		self._type_next = None
		self.HITBOX = None
		self._mask = None
		self._x = 0
		self._y = 0
		self._move_x = 0
		self._move_y = 0
		self._graphic = None
		self._point = PP.point
		self._camera = PP.point2

		if graphic:
			self.graphic = graphic
		if mask:
			self.mask = mask
		#self.HITBOX.assign_to(self)

	def added(self):
		"""Override this, called when the Entity is added to a World."""
		pass

	def removed(self):
		"""Override this, called when the Entity is removed from a World."""
		pass

	def update(self):
		"""Override this, called as part of the frame update loop."""
		pass

	def render(self):
		"""
		Renders the Entity. If you override this for special behaviour,
		remember to call ``super().render()`` to render the Entity's graphic.
		"""
		if self._graphic and self._graphic.visible:
			if self._graphic.relative:
				self._point.x = self.x
				self._point.y = self.y
			else:
				self._point.x = self._point.y = 0
			self._camera.x = self._world.camera.x if self._world else PP.camera.x
			self._camera.y = self._world.camera.y if self._world else PP.camera.y
			self._graphic.render(self.render_target if self.render_target else PP.screen, self._point, self._camera)

	def collide(self, t, x, y):
		"""
		Checks for a collision against an Entity type.

		:param type: The Entity type to check against.
		:param x:    Virtual x position to place this Entity.
		:param y:    Virtual y position to place this Entity.
		:return:     The first Entity collided with, or ``None`` if no collision.
		"""
		if not self._world:
			return None

		if t not in self._world._type_first:
			return None
		e = self._world._type_first[t]

		while e:
			if self.collide_with(e, x, y):
				return e
			e = e._type_next
		return None

	def collide_types(self, types, x, y):
		"""
		Checks for collision against multiple Entity types.

		:param types: A list of Entity types to check against.
		:param x:     Virtual x position to place this entity.
		:param y:     Virtual y position to place this entity.
		:return:      The first Entity collided with, or ``None`` if no collision.
		"""
		if not self._world:
			return None

		if isinstance(types, str):
			return self.collide(types, x, y)
		else:
			for t in types:
				e = collide(t, x, y)
				if e:
					return e

		return None

	def collide_with(self, e, x, y):
		"""
		Checks if this Entity collides with a specific Entity.

		:param e: The Entity to collide against.
		:param x: Virtual x position to place this entity.
		:param y: Virtual y position to place this entity.
		:return:  The Entity ``e`` if they overlap, else ``None``.
		"""
		# Not altogether sure why this is needed, keeping in in case magic
		self._x, self._y = self.x, self.y
		self.x, self.y = x, y

		if e.collidable and e != self \
		and x - self.origin_x + self.width > e.x - e.origin_x \
		and y - self.origin_y + self.height > e.y - e.origin_y \
		and x - self.origin_x < e.x - e.origin_x + e.width \
		and y - self.origin_y < e.y - self.origin_y + e.height:
			if not self._mask:
				if not e._mask or e._mask.collide(self.HITBOX):
					self.x, self.y = self._x, self._y
					return e
				self.x, self.y = self._x, self._y
				return None
			if self._mask.collide(e._mask if e._mask else e.HITBOX):
				self.x, self.y = self._x, self._y
				return e
		self.x, self.y = self._x, self._y
		return None

	def collide_rect(self, x, y, r_x, r_y, r_width, r_height):
		"""
		Checks if this Entity overlaps the specified rectangle.

		:param x:   Virtual x position to place this Entity.
		:param y:   Virtual y position to place this Entity.
		:param r_x: X position of the rectangle.
		:param r_y: Y position of the Rectangle.
		:param r_width:  Height of the rectangle.
		:param r_height: Width of the Rectangle.
		"""
		if x - self.origin_x + self.width >= r_x and y - self.origin_y >= r_y \
		and x - self.origin_x <= r_x + r_width and y - self.origin_y <= r_y + r_height:
			if not self._mask:
				return True
			self._x, self._y = self.x, self.y
			self.x, self.y = x, y
			PP.entity.x = r_x
			PP.entity.y = r_y
			PP.entity.width = r_width
			PP.entity.height = r_height
			if (self._mask.collide(PP.entity.HITBOX)):
				self.x, self.y = self._x, self._y
				return True
			self.x, self.y = self._x, self._y
		return False

	def collide_point(self, x, y, p_x, p_y):
		"""
		Checks if this Entity overlaps the specified position.

		:param x:   Virtual x position to place this Entity.
		:param y:   Virtual y position to place this Entity.
		:param p_x: X position of the rectangle.
		:param p_y: Y position of the Rectangle.
		"""
		if p_x >= x - self.origin_x and p_y >= y - self.origin_y \
		and p_x < x - self.origin_x + self.width and p_y < y - self.origin_y + self.height:
			if not self._mask:
				return True
			self._x, self._y = self.x, self.y
			self.x, self.y = x, y
			PP.entity.x = p_x
			PP.entity.y = p_y
			PP.entity.width = 1
			PP.entity.height = 1
			if (self._mask.collide(PP.entity.HITBOX)):
				self.x, self.y = self._x, self._y
				return True
			self.x, self.y = self._x, self._y
		return False

	"""
	.. todo::

	   # collide_into
	   # collide_types_into
	   # onCamera
	"""

	#: Read only. The World object this Entity has been added to.
	world = property(lambda self:self._world)
	#MISSING SOME PROPERTIES IN HERE.
	#: Read only. The leftmost position of the Entity's hitbox.
	left = property(lambda self:self.x-origin_x)
	#: Read only. The rightmost position of the Entity's hitbox.
	right = property(lambda self:self.left+self.width)
	#: Read only. The topmost position of the Entity's hitbox.
	top = property(lambda self:self.y-self.origin_y)
	#: Read only. The topmost position of the Entity's hitbox.
	bottom = property(lambda self:self.top+self.height)
	center_x = property(lambda self:self.left+self.width/2)
	center_y = property(lambda self:self.top+self.height/2)

	def _set_layer(self, value):
		if self._layer == value:
			return
		if not self._world:
			self._layer = value
			return
		self._world._remove_layer(self)
		self._layer = value
		self._world._add_layer(self)
	layer = property(lambda self:self._layer, _set_layer)

	def _set_type(self, value):
		if self.type == value:
			return
		if not self._world:
			self._type = value
			return
		if self._type:
			self._world._remove_type(self)
		self._type = value
		if self._type:
			self._world._add_type(self)
	# Not supposed to use type as a variable, I know. Deal with it.
	type = property(lambda self:self._type, _set_type)

	def _set_graphic(self, g):
		if self._graphic == g:
			return
		self._graphic = g
		if g and g.assign != None:
			g.assign()
	graphic = property(lambda self:self._graphic, _set_graphic)

	def add_graphic(g):
		raise NotImplementedError()

	def set_hitbox(self, width=0, height=0, origin_x=0, origin_y = 0):
		self.width = width
		self.height = height
		self.origin_x = origin_x
		self.origin_y = origin_y

	def set_hitbox_to(self, o):
		if hasattr(o, 'width'):
			self.width = o.width
		if hasattr(o, 'height'):
			self.height = o.height
		if hasattr(o, 'origin_x'):
			self.origin_x = o.origin_x
		elif hasattr(o, 'x'):
			self.origin_x = -o.x
		if hasattr(o, 'origin_y'):
			self.origin_y = o.origin_y
		elif hasattr(o, 'y'):
			self.origin_y = -o.y

	def set_origin(self, x=0, y=0):
		self.origin_x = x
		self.origin_y = y

	def center_origin(self):
		self.origin_x = width/2
		self.origin_y = height/2

	# distance_from

	# distance_to_point

	# distance_to_rect

	def __str__(self):
		return self._class

	# move_by

	# move_to

	# move_towards

	# move_collide_x

	# move_collide_y

	def clamp_horizontal(self, left, right, padding=0):
		if self.x - self.origin_x < left + padding:
			self.x = left + self.origin_x + padding
		if self.x - self.origin_x + self.width > right - padding:
			self.x = right - self.width + self.origin_x - padding

	def clamp_vertical(self, top, bottom, padding=0):
		if self.y - self.origin_y < top + padding:
			self.y = top + self.origin_y + padding
		if self.y - self.origin_y + self.height > bottom - padding:
			self.y = bottom - self.height + self.origin_x - padding

	def _set_name(self, value):
		if self._name == value:
			return
		if self._name and self._world:
			self._world._unregister_name(self)
		self._name = value
		if self._name and self._world:
			self._world._register_name(self)
	name = property(lambda self: self._name, _set_name)

	def get_class(self):
		return self._class