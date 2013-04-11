from ._entity import Entity
from ._tweening import Tweener
from ._pp import PP
from ..geom import Point

# Might be worth using original next/prev based update and render order... dunno

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
		# self._layers = {}
		# self._types = {}
		self._entity_names = {}
		# Update info
		self._update_first = None
		# Render info
		self._render_first = {}
		self._render_last = {}
		self._layer_list = []
		# self._layer_count = []
		self._layer_sort = False
		# self._class_count = {}
		# self._type_first = {}
		# self._type_count = {}


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

	# def _iter_entities(self):
	# 	for layer in sorted(self._layers.keys(), reverse=True):
	# 		for e in self._layers[layer]:
	# 			yield e

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

	# ENTITY FINDING FUNCTIONS

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
			if len(_layer_list) > 1:
				self._layer_list.sort()
			self._layer_sort = False

	def _add_layer(self, e):
		if e.layer not in self._layers:
			self._layers[e.layer] = []
		self._layers[e.layer].append(e) 

	def _add_type(self, e):
		if e.type not in self._types:
			self._types[e.type] = []
		self._types[e.type].append(e)

	def _register_name(self, e):
		self._entity_names[e._name] = e

	def _remove_layer(self, e):
		# Possibly need to catch error? (according to old code)
		self._layers[e.layer].remove(e)

	def _remove_type(self, e):
		if e.type:
			self._types[e.type].remove(e)

	def _unregister_name(self, e):
		if e._name in self._entity_names and self._entity_names[e._name] == e:
			del self._entity_names[e._name]