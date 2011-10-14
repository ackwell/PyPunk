from PySFML import sf
from Punk import *
import math

#Reference to colour
Color = sf.Color

class Graphic(object):
	def __init__(self):
		# if the graphic should render
		self.visible = True

		# offset
		self.x = 0
		self.y = 0

		# If the graphic should render at its position relative to its parent Entity's position.
		self.relative = True

		#Origin of image
		self.originX = 0
		self.originY = 0

		#Scrollfactor
		self.scrollX = 1
		self.scrollY = 1

		# Graphic information
		self._assign = None		# private
		self._scroll = True		# private
		self._point = Point()	# private
		self._alpha = 1.0		# private

	def render(self, App, point=Point(), camera=Punk.camera):
		"""Render the image to App"""
		offsetx = int(self.x - self.originX - camera.x * self.scrollX)
		offsety = int(self.y - self.originY - camera.y * self.scrollY)
		if self.relative: offsetx += point.x; offsety += point.y
		self.SetPosition(offsetx, offsety)

		if self.visible: App.Draw(self)

	@property
	def assign(self):
		return self._assign
	@assign.setter
	def assign(self, value):
		self._assign = value
	
	def set_alpha(self, value):
		if value > 1: value = 1
		self._alpha = value
		self.SetColor(sf.Color(255, 255, 255, int(value*255)))
	alpha = property(lambda self: self._alpha, set_alpha)

class Image(Graphic, sf.Sprite):
	def __init__(self, loc, rect=None):
		"""Create new Image
		Args:
		loc: location of image"""
		Graphic.__init__(self)
		if type(loc) == str: self.img = GetImage(loc)
		elif type(loc) == sf.Image: self.img = loc
		else: raise TypeError("Please pass the path to an image or a sf.Image instance")
		sf.Sprite.__init__(self, self.img)

		if rect:
			self.SetSubRect(sf.IntRect(rect.x, rect.y, rect.x+rect.width, rect.y+rect.height))

		#None of \/THESE\/ do anything right now. Will be added later

		# Rotation of the image, in degrees.
		self.angle = 0

		# Scale of the image, affects both x and y scale.
		self.scale = 1

		# X scale of the image.
		self.scaleX = 1

		# Y scale of the image.
		self.scaleY = 1

		# X origin of the image, determines transformation point.
		self.originX = 0

		# Y origin of the image, determines transformation point.
		self.originY = 0






class Spritemap(Image):
	def __init__(self, loc, frameWidth=0, frameHeight=0, callback=None):
		Graphic.__init__(self)

		self.complete = True
		self.callback = None
		self.rate = 1

		self._rect = Rectangle(0, 0, frameWidth, frameHeight)

		Image.__init__(self, loc, self._rect)

		self._width = self.GetImage().GetWidth()
		self._height = self.GetImage().GetHeight()
		if not frameWidth: self._rect.width = self._width
		if not frameHeight: self._rect.height = self._height
		self._columns = self._width / self._rect.width
		self._rows = self._height / self._rect.height
		self._frameCount = self._columns * self._rows
		self.callback = callback
		
		self._timer = 0
		self._anims = {}
		self._anim = None

		self._frame = 0
		self._index = 0

	def render(self, App, point=Point(), camera=Punk.camera):
		if self._anim and not self.complete:
			self._timer += (self._anim["frameRate"] * Punk.elapsed) * self.rate
			if self._timer >= 1:
				while self._timer >= 1:
					self._timer -= 1
					self._index += 1
					if self._index == len(self._anim["frames"]):
						if self._anim["loop"]:
							self._index = 0
							if self.callback: self.callback()
						else:
							self._index = len(self._anim["frames"])-1
							self.complete = True
							if self.callback: self.callback()
							break
				if self._anim: self._frame = self._anim["frames"][self._index]
		self._rect.x = int((self._frame % self._columns) * self._rect.width)
		self._rect.y = int(math.ceil(self._frame / self._columns) * self._rect.height)
		self.SetSubRect(sf.IntRect(self._rect.x, self._rect.y, self._rect.x+self._rect.width, self._rect.y+self._rect.height))

		Image.render(self, App, point, camera)
	
	def add(self, name, frames, frameRate=0, loop=True):
		try: dummy = self._anims[name]
		except KeyError:
			self._anims[name] = {"name":name, "frames":frames, "frameRate":frameRate, "loop":loop}
			return
		raise TypeError("Cannot have multiple animations with the same name")
	
	def play(self, name="", reset=False, frame=0):
		if not reset and self._anim and self._anim["name"] == name: return self._anim
		try: self._anim = self._anims[name]
		except TypeError: self._anim = None
		if not self._anim:
			self._frame = self._index = 0
			self.complete = True
			return None
		self._index = 0
		self._timer = 0
		self._frame = int(self._anim["frames"][frame % len(self._anim["frames"])])
		self.complete = False
		return self._anim
	
	def getFrame(self, column=0, row=0):
		return (row % self._rows) * self._columns + (column % self._columns)
	
	def setFrame(self, colum=0, row=0):
		self._anim = None
		frame = (row % _rows) * _columns + (column % _columns)
		if self._frame == frame: return
		self._frame = frame
		self._timer = 0

	def randFrame(self):
		self._frame = math.randint(self._frameCount)
	
	def setAnimFrame(self, name, index):
		frames = self._anims[name]["frames"]
		index %= len(frames)
		if index < 0: index += len(frames)
		self._frame = frames[index]

	def set_frame(self, value):
		self._anim = False
		value %= self._frameCount
		if value < 0: value += self._frameCount
		if self._frame == value: return
		self._frame = value
		self._timer = 0
	frame = property(lambda self: self._frame, set_frame)

	def set_index(self, value):
		if not self._anim: return
		value %= len(self._anim["frames"])
		if self._index == value: return;
		self._index = value
		self._frame = self._anim["frames"][self._index]
		self._timer = 0
	index = property(lambda self: self._index if self._anim else 0, set_index)

	frameCount = property(lambda self: self._frameCount)
	columns = property(lambda self: self._columns)
	rows = property(lambda self: self._rows)
	currentAnim = property(lambda self: self._anim["name"] if self._anim else "")

		





class Tilemap(Graphic, sf.Sprite):
	def __init__(self, loc, width, height, tileWidth, tileHeight):
		Graphic.__init__(self)

		if type(loc) == str: self.img = GetImage(loc)
		elif type(loc) == sf.Image: self.img = loc
		else: raise TypeError("Please pass the path to an image or a sf.Image instance")
		sf.Sprite.__init__(self, self.img)

		self._width = width
		self._height = height
		self._columns = int(math.ceil(width / tileWidth))
		self._rows = int(math.ceil(height / tileHeight))
		self._tileCols = self.GetImage().GetWidth() / tileWidth
		self._tileRows = self.GetImage().GetHeight() / tileHeight
		self._tile = Rectangle(0, 0, tileWidth, tileHeight)

		#-1 == do not draw
		self._map = [[-1 for j in range(self._rows)] for i in range(self._columns)]
	
	def setTile(self, column, row, index):
		self._map[column][row] = index
	
	def clearTile(self, column, row):
		self.setTile(column, row, -1)
	
	def getTile(self, column, row):
		return self._map[column][row]
	
	def setRect(self, column, row, width=1, height=1, index=0):
		for cl in range(column, column+width):
			for rw in range(row, row+height):
				self._map[cl][rw] = index
	
	def clearRect(self, column, row, width=1, height=1):
		self.setRect(column, row, height, width, -1)

	def render(self, App, point=Point(), camera=Punk.camera):
		if not self.visible: return
		for col in range(len(self._map)):
			for row in range(len(self._map[col])):
				tile = self._map[col][row]
				if not tile == -1:
					self._tile.x = int((tile % self._tileCols) * self._tile.width)
					self._tile.y = int(math.ceil(tile / self._tileCols) * self._tile.height)
					#print self._tile.x, self._tile.y
					self.SetSubRect(sf.IntRect(self._tile.x, self._tile.y, self._tile.x+self._tile.width, self._tile.y+self._tile.height))

					offsetx = int(self.x + col*self._tile.width - self.originX - camera.x * self.scrollX)
					offsety = int(self.y + row*self._tile.height - self.originY - camera.y * self.scrollY)
					if self.relative: offsetx += point.x; offsety += point.y
					self.SetPosition(offsetx, offsety)

					App.Draw(self)

class Shape(Graphic, sf.Shape):
	def __init__(self):
		"""Create a shape"""
		Graphic.__init__(self)
		sf.Shape.__init__(self)
	
	def createRect(self, width, height, colour):
		"""Predefined rectangle shape"""
		self.AddPoint(0, 0, colour)
		self.AddPoint(width, 0, colour)
		self.AddPoint(width, height, colour)
		self.AddPoint(0, height, colour)

class Text(Graphic, sf.String):
	def __init__(self, loc, text="", size=16):
		"""Create text graphic
		Args:
		loc: location of font
		text: text to display
		size: font size"""
		Graphic.__init__(self)

		self.fnt = GetFont(loc, size)

		sf.String.__init__(self)
		self.SetText(text)
		self.SetFont(self.fnt)
		self.SetSize(size)
	
	def set_color(self, value):
		self.SetColor(sf.Color(value[0], value[1], value[2]))
	def get_color(self):
		"""Get/Set the color of the text"""
		clr = self.GetColor()
		return (clr.r, clr.g, clr.b)
	color = property(get_color, set_color)

	def set_text(self, value): self.SetText(value)
	text = property(lambda self: self.GetText(), set_text)

	def set_size(self, value): self.SetSize(value)
	size = property(lambda self: self.GetSize(), set_size)

class Graphiclist(object):
	def __init__(self, *args):
		"""List of graphics to render"""
		self.list = args
	
	def add(self, toAdd):
		self.list.append(toAdd)
	def remove(self, toRem):
		self.list.remove(toRem)
	
	def render(self, App, point=Point(), camera=Punk.camera):
		for obj in self.list:
			obj.render(App, point, camera)

#Caches
imageCache = {}
def GetImage(loc):
	try: #Will only run if already loaded
		return imageCache[loc]
	except KeyError:
		Image = sf.Image()
		Image.SetSmooth(False)
		if not Image.LoadFromFile(loc):
			return None
		imageCache[loc] = Image
		return Image

fontCache = {}
def GetFont(loc, size):
	try:
		fnt = fontCache[loc]
		old_size = fnt.GetCharacterSize()
		if size < old_size:
			return fnt
	except KeyError: pass
	Font = sf.Font()
	if not Font.LoadFromFile(loc, size):
		return None
	fontCache[loc] = Font
	return Font
