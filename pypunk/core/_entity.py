from ._pp import PP
from ._tweening import Tweener

class Entity(Tweener):
	def __init__(self, x=0, y=0, graphic=None, mask=None):
		super().__init__()

		# Public variables
		self.visible = True
		self.collidable = True
		self.x = x
		self.y = y
		self.width = 0
		self.height = 0
		self.origin_x = 0
		self.origin_y = 0
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
		self._mask = None
		self._graphic = None
		self._point = PP.point
		self._camera = PP.point2

		if graphic:
			self.graphic = graphic
		if mask:
			self.mask = mask
		#self.HITBOX.assign_to(self)

	def added(self): pass

	def removed(self): pass

	def update(self): pass

	def render(self):
		if self._graphic and self._graphic.visible:
			if self._graphic.relative:
				self._point.x = self.x
				self._point.y = self.y
			else:
				self._point.x = self._point.y = 0
			self._camera.x = self._world.camera.x if self._world else PP.camera.x
			self._camera.y = self._world.camera.y if self._world else PP.camera.y
			self._graphic.render(self.render_target if self.render_target else PP.screen, self._point, self._camera)

	# COLLISION FUNCTIONS

	# onCamera

	world = property(lambda self:self._world)

	left = property(lambda self:self.x-origin_x)
	right = property(lambda self:self.left+self.width)
	top = property(lambda self:self.y-self.origin_y)
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
	# Bad code, i know. SOWEEEE (using 'type' as a variable)
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

	# SET HITBOX, ETC

	def center_origin(self):
		self.origin_x = width/2
		self.origin_y = height/2

	# DISTANCE FUNCTIONS

	def __str__(self):
		return self._class

	# MOVE FUNCTIONS

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