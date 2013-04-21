from ._entity import Entity
from ._tweening import Tweener
from ._pp import PP
from ..geom import Point

class World(Tweener):
	def __init__(self):
		super().__init__()
		
		# Public variables
		self.visible = True
		self.camera = Point()

		# Private variables
		# Adding/removal
		self._add = []
		self._remove = []
		# Layers/types
		self._entity_names = {}
		# Update info
		self._update_first = None
		self._count = 0
		# Render info
		self._render_first = {}
		self._render_last = {}
		self._layer_list = []
		self._layer_count = {}
		self._layer_sort = False
		self._class_count = {}
		self._type_first = {}
		self._type_count = {}


	# Called when the world is switched to
	def begin(self): pass

	# Called when the world is switched away from
	def end(self): pass

	# Called by Engine game loop. Updates contained entities.
	def update(self):
		e = self._update_first
		while e:
			if e.active:
				if e._tween:
					e.update_tweens()
				e.update()
			if e._graphic and e._graphic.active:
				e._graphic.update()
			e = e._update_next

	# Called by Engine game loop. Renders contained entities
	def render(self):
		for i in self._layer_list:
			e = self._render_last[i]
			while e:
				if e.visible:
					e.render()
				e = e._render_prev

	mouse_x = property(lambda self:PP.screen.mouse_x+self.camera.x)
	mouse_y = property(lambda self:PP.screen.mouse_y+self.camera.y)

	def add(self, e):
		self._add.append(e)
		return e

	def remove(self, e):
		self._remove.append(e)
		return e

	def remove_all(self):
		e = self._update_first
		while e:
			self._remove.append(e)
			e = e._update_next

	def add_list(self, *entities):
		if entities[0] is list:
			for e in entities[0]:
				self.add(e)
			return
		for e in entities:
			self.add(e)

	def remove_list(self, *entities):
		if entities[0] is list:
			for e in entities[0]:
				self.remove(e)
			return
		for e in entities:
			self.remove(e)

	def add_graphic(self, graphic, layer=0, x=0, y=0):
		e = Entity(x, y, graphic)
		if layer != 0:
			e.layer = layer
		e.active = False
		return self.add(e)

	# ADD_MASK

	def bring_to_front(self, e):
		if e._world != self or not e._render_prev:
			return False
		# Pull from list
		e._render_prev._render_next  = e._render_next
		if e._render_next:
			e._render_next._render_prev = e._render_prev
		else:
			self._render_last[e._layer] = e._render_prev
		# Place at start
		e._render_next = self._render_first[e._layer]
		e._render_next._render_prev = e
		self._render_first[e._layer] = e
		e._render_prev = None
		return True

	def send_to_back(self, e):
		if e._world != self or not e._render_next:
			return False
		e._render_next._render_prev = e._render_prev
		if e._render_prev:
			e._render_prev._render_next = e._render_next
		else:
			self._render_first[e._layer] = e._render_next
		e._render_prev = self._render_last[e._layer]
		e._render_prev._render_next = e
		self._render_last[e._layer] = e
		e._render_next = None
		return True

	def bring_forward(self, e):
		if e._world != self or not e._render_prev:
			return False
		e._render_prev._render_next = e._render_next
		if e._render_next:
			e._render_next._render_prev = e._render_prev
		else:
			self._render_last[e._layer] = e._render_prev
		e._render_next = e._render_prev
		e._render_prev = e._render_prev._render_prev
		e._render_next._render_prev = e
		if e._render_prev:
			e._render_prev._render_next = e
		else:
			self._render_first[e._layer] = e
		return True

	def send_backwards(self, e):
		if e._world != self or not e._render_next:
			return False
		e._render_next._render_prev = e._render_prev
		if e._render_prev:
			e._render_prev._render_next = e._render_next
		else:
			self._render_first[e._layer] = e._render_next
			e._render_prev = e._render_next
			e._render_next = e._render_next._render_next
			e._render_prev._render_next = e
			if e._render_next:
				e._render_next._render_prev = e
			else:
				self._render_last[e._layer] = e
			return True

	def is_at_front(self, e):
		return e._render_prev == None

	def is_at_back(self, e):
		return e._render_next == None

	# COLLIDE FUNCTIONS

	count = property(lambda self: self._count)

	def type_count(self, t):
		return self._type_count[t]

	def class_count(self, c):
		return self._class_count[c]

	def layer_count(self, l):
		return self._layer_count[l]

	first = property(lambda self: self._update_first)

	layers = property(lambda self: len(self._layer_list))

	def type_first(self, t):
		if not self._update_first:
			return None
		return self._type_first[t]

	def class_first(self, c):
		if not self._update_first:
			return None
		e = self._update_first
		while e:
			if isinstance(e, c):
				return e
			e = e._update_next
		return None

	def layer_first(self, l):
		if not self._update_first:
			return None
		return self._render_first[l]

	def layer_last(self, l):
		if not self._update_first:
			return None
		return self._render_last[l]

	def _get_farthest(self):
		if not self._update_first:
			return None
		return self._render_last[self._layer_list[-1]]
	farthest = property(_get_farthest)

	def _get_nearest(self):
		if not self._update_first:
			return None
		return self._render_last[self._layer_list[0]]
	nearest = property(_get_nearest)

	def _get_layer_farthest(self):
		if not self._update_first:
			return None
		return self._layer_list[-1]
	layer_farthest = property(_get_layer_farthest)

	def _get_layer_nearest(self):
		if not self._update_first:
			return None
		return self._layer_list[0]
	layer_nearest = property(_get_layer_nearest)

	def _get_unique_types(self):
		return len(self._type_count)
	unique_types = property(_get_unique_types)

	def get_type(self, t, into):
		e = self._type_first[t]
		while e:
			into.append(e)
			e = e._type_next

	def get_class(self, c, into):
		e = self._update_first
		while e:
			if isinstance(e, c):
				into.append(e)
			e = e._update_next

	def get_layer(self, l, into):
		e = self._render_last[l]
		while e:
			into.append(e)
			e = e._render_prev

	def get_all(self, into):
		e = self._update_first
		while e:
			into.append(e)
			e = e._update_next

	def get_instance(self, name):
		return self._entity_names[name]

	def _update_lists(self):
		for e in self._remove:
			if not e._world:
				if e in self._add:
					self._add.remove(e)
				continue
			if e._world != self:
				continue
			e.removed()
			e._world = None
			self._remove_update(e)
			self._remove_render(e)
			if e._type:
				self._remove_type(e)
			if e._name:
				self._unregister_name(e)
			if e.auto_clear and e._tween:
				e.clear_tweens()
		self._remove = []

		for e in self._add:
			if e._world:
				continue
			self._add_update(e)
			self._add_render(e)
			if e._type:
				self._add_type(e)
			if e._name:
				self._register_name(e)
			e._world = self
			e.added()
		self._add = []

		# Recycle entities here if ever I implement that

		# Sort layer list
		if self._layer_sort:
			if len(self._layer_list) > 1:
				self._layer_list.sort()
			self._layer_sort = False

	def _add_update(self, e):
		if self._update_first:
			self._update_first._update_prev = e
			e._update_next = self._update_first
		else:
			e._update_next = None
		e._update_prev = None
		self._update_first = e
		self._count += 1
		if e._class not in self._class_count:
			self._class_count[e._class] = 0
		self._class_count[e._class] += 1

	def _remove_update(self, e):
		if self._update_first == e:
			self._update_first = e._update_next
		if e._update_next:
			e._update_next._update_prev = e._update_prev
		if e._update_prev:
			e._update_prev._update_next = e._update_next
		e._update_next = e._update_prev = None
		self._count -= 1
		self._class_count[e._class] -= 1

	def _add_render(self, e):
		if e._layer in self._render_first:
			f = self._render_first[e._layer]
			e._render_next = f
			f._render_prev = e
			self._layer_count[e._layer] += 1
		else:
			self._render_last[e._layer] = e
			self._layer_list.append(e._layer)
			self._layer_sort = True
			e._render_next = None
			self._layer_count[e._layer] = 1
		self._render_first[e._layer] = e
		e._render_prev = None

	def _remove_render(self, e):
		if e._render_next:
			e._render_next._render_prev = e._render_prev
		else:
			self._render_last[e._layer] = e._render_prev
		if e._render_prev:
			e._render_prev._render_next = e._render_next
		else:
			self._render_first[e._layer] = e._render_next
			if not e._render_next:
				self._layer_list.remove(e._layer)
				self._layer_sort = True
		self._layer_count[e._layer] -= 1
		e._render_next = e._render_prev = None

	def _add_type(self, e):
		if e._type in self._type_first and self._type_first[e._type] is not None:
			self._type_first[e._type]._type_prev = e
			e._type_next = self._type_first[e._type]
			self._type_count[e._type] += 1
		else:
			e._type_next = None
			self._type_count[e._type] = 1
		e._type_prev = None
		self._type_first[e._type] = e

	def _remove_type(self, e):
		if self._type_first[e._type] == e:
			self._type_first[e._type] = e._type_next
		if e._type_next:
			e._type_next._type_prev = e._type_prev
		if e._type_prev:
			e._type_prev._type_next = e._type_next
		e._type_next = e._type_prev = None
		self._type_count[e._type] -= 1

	def _register_name(self, e):
		self._entity_names[e._name] = e

	def _unregister_name(self, e):
		if self._entity_names[e._name] == e:
			del self._entity_names[e._name]
