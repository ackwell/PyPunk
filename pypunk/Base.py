from PySFML import sf
import Punk, Event, Audio

#Base class, handles window initiation, etc.
class Engine(object):
	def __init__(self, width=640, height=480, fps=30, title="PyPunk", bgColor=(100, 149, 237)):
		"""Creates new Engine instance
		Args:
		width: width of window
		height: height of window
		fps: maximum FPS
		title: window caption
		bgColor: tuple (r,g,b) of background color
		"""

		#Provide engine reference to punk
		Punk.Engine = self

		#Set initial settings
		self.width = width
		self.height = height
		self.fps = fps
		self.title = title
		self._bgColour = sf.Color(bgColor[0], bgColor[1], bgColor[2], 255)

		#Initiate the window
		self.App = sf.RenderWindow(sf.VideoMode(self.width, self.height, 32), self.title)
		self.App.SetFramerateLimit(self.fps)

		#Other variables and stuff
		self.World = None
		self.ForceSize = True

		#Register events
		Event.RegisterEvent(sf.Event.Closed, self.onClose)
		Event.RegisterEvent(sf.Event.Resized, self.onResize)

		print "PyPunk initiated..."
	
	@property
	def Input(self):
		"""Get reference to simple event system"""
		return self.App.GetInput()

	def set_bgColor(self, v):
		self._bgColour = sf.Color(v[0], v[1], v[2])
	def get_bgColor(self):
		"""Set the window backgrond color (r,g,b)"""
		return (self._bgColour.r, self._bgColour.g, self._bgColour.b)
	bgColor = property(get_bgColor, set_bgColor)
	
	#Start looping
	def Begin(self):
		"""Start the engine"""
		while self.App.IsOpened():
			self.UpdateVars()
			Event.Input.ClearVars()
			self.App.Clear(self._bgColour)
			Event.DispatchEvents(self.App)
			if self.World: self.World.update(self.App)
			self.App.Display()
			Audio.checkSounds()
			if self.World: self.World.endOfFrame()
	
	#Vars
	def UpdateVars(self):
		"""Internal - update various variables"""
		try:
			Punk.elapsed = self.App.GetFrameTime()
			Punk.FPS = 1.0/Punk.elapsed
		except ZeroDivisionError:
			pass
	
	def WorldChanged(self):
		"""Calls the wold's end function"""
		self.World.end()
	
	#Events
	def onClose(self, args):
		"""Called on window exit"""
		print "PyPunk exiting..."
		self.App.Close()
	
	def onResize(self, args):
		"""Called on window resize.
		If self.ForceSize is True, will automatically resize window to original dimensions"""
		if self.ForceSize:
			self.App.SetSize(self.width, self.height)
		else:
			self.width = args["Width"]
			self.height = args["Height"]

class World(object):
	def __init__(self):
		"""Creates new World object"""
		self._layerList = {}
		self._typeList = {}

		self._add = []
		self._remove = []
	
	def update(self, App):
		"""Called every frame. Updates Entities that have been added"""
		#Loop through layers highest->lowest
		for layer in sorted(self._layerList.iterkeys(), reverse=True):
			#Loop through objects on the layer
			for i in range(len(self._layerList[layer])):
				object = self._layerList[layer][i]
				if not object.paused:
					object.updateTweens()
					object.update()
				if object.visible:
					object.render(App)
					
	def add(self, toAdd):
		"""Add a new Entity to the world"""
		self._add.append(toAdd)
	
	def remove(self, toRemove):
		"""Remove a previously added entity from the world"""
		self._remove.append(toRemove)
	
	def endOfFrame(self):
		"""Internal - add/remove entities from the world"""
		#add entities
		for e in self._add:
			#General rendering, etc
			self.addLayer(e)
			e.world = self

			#add to typeList if they *have* a type
			if not e.type == "":
				self.addType(e)
			e.added()
		self._add = []

		#remove entities
		for e in self._remove:
			self.remLayer(e)
			if not e.type == "":
				self.remType(e)
			e.world = None
			e.removed()
		self._remove = []
	
	def addLayer(self, e):
		try: dummy = self._layerList[e.layer]
		except KeyError: self._layerList[e.layer] = []
		self._layerList[e.layer].append(e)
	def addType(self, e):
		try: dummy = self._typeList[e.type]
		except KeyError: self._typeList[e.type] = []
		self._typeList[e.type].append(e)
	def remLayer(self, e):
		self._layerList[e.layer].remove(e)
	def remType(self, e):
		if e.type:
			self._typeList[e.type].remove(e)
	
	def end(self):
		self._layerList = {}
		self._typeList = {}
		self._add = []
		self._remove = []


class Entity(object):
	def __init__(self, x=0, y=0, graphic = None):
		"""Creates new Entity object
		Args:
		x: Initial x position of entity
		y: Initial y position of entity"""
		#Positioning
		self.x = x
		self.y = y
		self._layer = 0

		#Collision
		self.width = 0
		self.height = 0
		self._type = ""
		self.collidable = True

		#Graphics
		self.graphic = graphic
		self.visible = True

		#Should be updated
		self.paused = False

		#Parent world
		self.world = None

		self.tweens = []

	
	def get_layer(self):
		"""Get/set the layer of the entity"""
		return self._layer
	def set_layer(self, value):
		#If has not been added to world yet
		if not self.world:
			self._layer = value
		#If it has, remove it, change var, readd to new position
		else:
			self.world.remLayer(self)
			self._layer = value
			self.world.addLayer(self)
	layer = property(get_layer, set_layer)
	
	def get_type(self):
		"""Get/set the type of the entity (for collisions)"""
		return self._type
	def set_type(self, value):
		if not self.world:
			self._type = value
		else:
			self.world.remType(self)
			self._type = value
			self.world.addType(self)
	type = property(get_type, set_type)
	
	#add a tween to update
	def addTween(self, tween):
		"""Add a tween to update"""
		self.tweens.append(tween)
		tween._parent = self
	
	def removeTween(self, tween):
		self.tweens.remove(tween)

	def updateTweens(self):
		for tween in self.tweens:
			tween.updateTween()
	
	def update(self): pass
	
	def added(self): pass

	def removed(self):pass
	
	def render(self, App):
		"""Render graphic"""
		if self.graphic and self.visible:
			self.graphic.render(App, (self.x, self.y))
	
	def collide(self, type, x, y):
		"""Check for collision
		Args:
		type: type to check against
		x: virtual x position to place this entity
		y: virtual y position to place this entity"""
		try:
			for e in self.world._typeList[type]:
				if e.collidable and not e == self:
					if self.x < e.x+e.width \
					and self.x+self.width > e.x \
					and self.y < e.y+e.height \
					and self.y+self.height > e.y:
						return e
		except KeyError: pass
		return None
