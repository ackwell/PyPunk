from PySFML import sf
from Punk import *
import Event, Audio

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
		# global game properties
		Punk.width = width
		Punk.height = height

		# global game objects
		Punk.engine = self
		Punk._world = World()

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
			if Punk._world: 
				Punk._world.update()
				Punk._world.render()
			self.App.Display()
			Audio.checkSounds()
			if Punk._world: Punk._world.endOfFrame()
	
	#Vars
	def UpdateVars(self):
		"""Internal - update various variables"""
		try:
			Punk.elapsed = self.App.GetFrameTime()
			Punk.FPS = 1.0/Punk.elapsed
		except ZeroDivisionError:
			pass
	
	def WorldChanged(self):
		"""Calls the world's end function"""
		Punk.world.end()
	
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

		self.active = True
		self.visible = True
	
	def update(self):
		"""Called every frame. Updates Entities that have been added"""
		#Loop through layers highest->lowest
		for layer in sorted(self._layerList.iterkeys(), reverse=True):
			#Loop through objects on the layer
			for i in range(len(self._layerList[layer])):
				obj = self._layerList[layer][i]
				if obj.active and self.active:
					obj.updateTweens()
					obj.update()
	def render(self):
	 	for layer in sorted(self._layerList.iterkeys(), reverse=True):
			for i in range(len(self._layerList[layer])):
				obj = self._layerList[layer][i]
				if obj.visible and self.visible:
					obj.render()
					
	def add(self, toAdd):
		"""Add a new Entity to the world"""
		self._add.append(toAdd)
	
	def remove(self, toRemove):
		"""Remove a previously added entity from the world"""
		self._remove.append(toRemove)
	
	def removeAll(self):
		self._layerList = {}
		self._typeList = {}
		self._add = []
	
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
		try: self._layerList[e.layer].remove(e)
		except ValueError: print "Could not remove "+str(e)+" from layerList ("+str(self._layerList)+")"
	def remType(self, e):
		if e.type:
			self._typeList[e.type].remove(e)
	
	#Collisions
	def collidePoint(self, type, pX, pY):
		try:
			for e in self._typeList[type]:
				if e.collidePoint(e.x, e.y, pX, pY): return e
		except KeyError: pass
		return None

	def collideLine(self, type, fromX, fromY, toX, toY, precision=1, p=None):
		if precision < 1: precision = 1
		if Punk.distance(fromX, fromY, toX, toY) < precision:
			if p:
				if fromX == toX and fromY == toY:
					p.x = toX; p.y = toY
					return self.collidePoint(type, toX, toY)
				return self.collideLine(type, fromX, fromY, toX, toY, 1, p)
			else: return self.collidePoint(type, fromX, toY)
		xDelta = math.fabs(toX-fromX)
		yDelta = math.fabs(toY-fromY)
		xSign = precision if toX>fromX else -precision
		ySign = precision if toY>fromY else -precision
		x = fromX
		y = fromY
		if xDelta>yDelta:
			ySign*=yDelta/xDelta
			if xSign>0:
				while x<toX:
					e = self.collidePoint(type, x, y)
					if e:
						if not p: return e
						if precision < 2:
							p.x=x-xSign;p.y=y-ySign
							return e
						return self.collideLine(type, x-xSign, y-ySign, toX, toY, 1, p)
					x+=xSign;y+=ySign
			else:
				while x>toX:
					e=self.collidePoint(type, x, y)
					if e:
						if not p: return e
						if precision < 2:
							p.x=x-xSign;p.y=y-ySign
							return e
						return self.collideLine(type, x-xSign, y-ySign, toX, toY, 1, p)
					x+=xSign;y+=ySign
		else:
			xSign*=xDelta/yDelta
			if ySign>0:
				while y<toY:
					e = self.collidePoint(type, x, y)
					if e:
						if not p: return e
						if precision < 2:
							p.x=x-xSign;p.y=y-ySign
							return e
						return self.collideLine(type, x-xSign, y-ySign, toX, toY, 1, p)
					x+=xSign;y+=ySign
			else:
				while y>toY:
					e=self.collidePoint(type, x, y)
					if e:
						if not p: return e
						if precision < 2:
							p.x=x-xSign;p.y=y-ySign
							return e
						return self.collideLine(type, x-xSign, y-ySign, toX, toY, 1, p)
					x+=xSign;y+=ySign
		if precision>1:
			if not p: return self.collidePoint(type, toX, toY)
			if self.collidePoint(type, toX, toY):
				return self.collideLine(type, x-xSign, y-ySign, toX, toY, 1, p)
		if p:
			p.x=toX;p.y=toY
		return None
		
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
		self.originX = 0
		self.originY = 0
		self._type = ""
		self.collidable = True

		#Graphics
		self.graphic = graphic
		self.visible = True

		#Should be updated
		self.active = True

		#Parent world
		self.world = None

		self.tweens = []

	def set_layer(self, value):
		#If has not been added to world yet
		if not self.world:
			self._layer = value
		#If it has, remove it, change var, readd to new position
		else:
			self.world.remLayer(self)
			self._layer = value
			self.world.addLayer(self)
	layer = property(lambda self: self._layer, set_layer)
	
	def set_type(self, value):
		if not self.world:
			self._type = value
		else:
			self.world.remType(self)
			self._type = value
			self.world.addType(self)
	type = property(lambda self: self._type, set_type)
	
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
	
	def render(self):
		"""Render graphic"""
		if self.graphic and self.visible:
			self.graphic.render(Punk.buffer, Point(self.x, self.y), Punk.camera)
	
	def collide(self, type, x, y):
		"""Check for collision
		Args:
		type: type to check against
		x: virtual x position to place this entity
		y: virtual y position to place this entity"""
		_x = self.x; _y = self.y
		self.x = x; self.y = y
		try:
			for e in self.world._typeList[type]:
				ent = self.checkCol(e)
				if ent:
					self.x = _x; self.y = _y
					return ent
		except KeyError: pass
		self.x = _x; self.y = _y
		return None
	
	def collideWith(self, e, x, y):
		_x = self.x; _y = self.y
		self.x = x; self.y = y
		ent = self.checkCol(e)
		if ent:
			self.x = _x; self.y = _y
			return ent
		return None
	
	def checkCol(self, e):
		if e.collidable and not e == self:
			if self.x - self.originX + self.width > e.x - e.originX \
			and self.y - self.originY + self.height > e.y - e.originY \
			and self.x - self.originX < e.x - e.originX + e.width \
			and self.y - self.originY < e.y - e.originY + e.height:
				return e
		return None
	
	def collidePoint(self, x, y, pX, pY):
		if pX>=x-self.originX and pY>=y-self.originY\
		and pX<x-self.originX+self.width and pY<y-self.originY+self.height:
			return True
		return False
	
	def setHitbox(self, width=0, height=0, originX=0, originY=0):
		self.width = width
		self.height = height
		self.originX = originX
		self.originY = originY
