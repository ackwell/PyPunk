from PySFML import sf

class Sfx(sf.Sound):
	def __init__(self, loc):
		"""New sfx object
		loc: loaction of sound file"""
		sf.Sound.__init__(self)
		self.SetBuffer(GetSound(loc))
		
	def __del__(self):
		if not self.GetStatus() == 0:
			try: sfxList.append(self)
			except AttributeError: pass

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
			if sfx.GetStatus() == 0:
				sfxList.remove(sfx)
		except AttributeError: print "bet i'll see this"
	
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