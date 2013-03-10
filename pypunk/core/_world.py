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
		self._layers = {}
		self._types = {}
		self._entity_names = {}

	# Called when the world is switched to
	def begin(self): pass

	# Called when the world is switched away from
	def end(self): pass

	# Called by Engine game loop. Updates contained entities.
	def update(self):
		for e in self._iter_entities():
			if e.active:
				if e._tween:
					e.update_tweens()
				e.update()
			if e._graphic and e._graphic.active:
				e._graphic.update()

	# Called by Engine game loop. Renders contained entities
	def render(self):
		for e in self._iter_entities():
			if e.visible:
				e.render()

	def _iter_entities(self):
		for layer in sorted(self._layers.keys(), reverse=True):
			for e in self._layers[layer]:
				yield e

	mouse_x = property(lambda self:PP.screen.mouse_x+self.camera.x)
	mouse_y = property(lambda self:PP.screen.mouse_y+self.camera.y)

	def add(self, e):
		self._add.append(e)
		return e

	def remove(self, e):
		self._remove.append(e)
		return e

	def remove_all(self):
		pass #TODO

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
			e.layer = 0
		e.active = False
		return self.add(e)

	# ADD_MASK

	def bring_to_front(self, e):
		if self.is_at_front(e):
			return False
		layer = self._layers[e.layer]
		layer.remove(e)
		layer.append(e)

	def send_to_back(self, e):
		if self.is_at_back(e):
			return False
		layer = self._layers[e.layer]
		layer.remove(e)
		layer.insert(0, e)

	def bring_forward(self, e):
		if self.is_at_front(e):
			return False
		layer = self._layers[e.layer]
		i = layer.index(e)
		layer.remove(e)
		layer.insert(i+1, e)

	def send_backward(self, e):
		if self.is_at_back(e):
			return False
		layer = self._layers[e.layer]
		i = layer.index(e)
		layer.remove(e)
		layer.insert(i-1, e)

	def is_at_front(self, e):
		if e._world != self:
			return False
		if self._layers[e.layer].index(e) == len(self._layers[e.layer])-1:
			return True
		return False

	def is_at_back(self, e):
		if e._world != self:
			return False
		if self._layers[e.layer].index(e) == 0:
			return True
		return False

	# COLLIDE FUNCTIONS

	# ENTITY FINDING FUNCTIONS

	def _update_lists(self):
		# Remove entities
		for e in self._remove:
			e.removed()
			e._world = None
			self._remove_layer(e)
			if e._type != '':
				self._remove_type(e)
			if e._name != '':
				self._unregister_name(e)
		self._remove = []

		# Add entities
		for e in self._add:
			# Add to the update/render whatsit
			self._add_layer(e)
			# If it has a type, add it to the typelist, likewise for name
			if e._type != '':
				self._add_type(e)
			if e._name != '':
				self._register_name(e)
			e._world = self
			e.added()
		self._add = []

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