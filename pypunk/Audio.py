from PySFML import sf

class Sfx(sf.Sound):
	def __init__(self, loc):
		"""New sfx object
		loc: loaction of sound file"""
		sf.Sound.__init__(self)
		self.SetBuffer(GetSound(loc))
		sfxList.append(self)

class Music(sf.Music):
	def __init__(self, loc):
		"""New music object
		loc: location of music file"""
		sf.Music.__init__(self)
		self.OpenFromFile(loc)

#This is just used to make sure sounds finish playing before being GC'D
sfxList = []
def checkSounds():
	for sfx in sfxList:
		try:
			if not sfx.im_self.world and sfx.GetStatus() == 0:
				sfxList.remove(sfx)
		except AttributeError: pass
	
soundCache = {}
def GetSound(loc):
	try:
		return soundCache[loc]
	except KeyError:
		snd = sf.SoundBuffer()
		if not snd.LoadFromFile(loc):
			return None
		soundCache[loc] = snd
		return snd