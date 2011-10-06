from PySFML import sf

class Sfx(sf.Sound):
	def __init__(self, loc):
		"""New sfx object
		loc: loaction of sound file"""
		sf.Sound.__init__(self)
		self.SetBuffer(GetSound(loc))

class Music(sf.Music):
	def __init__(self, loc):
		"""New music object
		loc: location of music file"""
		sf.Music.__init__(self)
		self.OpenFromFile(loc)
	
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