
import sfml

class Sfx(object):
	def __init__(self, source, complete=None, t='', stream=False):
		self._type = t
		self.complete = complete

		self.source = None
		# Passed a path to the file
		if isinstance(source, str):
			if stream:
				raise NotImplementedError() # create a streming buffer with sfml.Music
			else:
				buf = Sfx.get_sound(source)
				self.source = sfml.audio.Sound(buf)
		else:
			self.source = source

		# Set minimum distance and attenuation for panning.
		# I'm sure people can fiddle with these themselves if they absolutely must.
		self.source.min_distance = 100
		self.source.attenuation = 0

	def play(self, vol=1, pan=0):
		if self.source.status != sfml.audio.SoundSource.STOPPED:
			self.stop()
		
		# Panning is between -100 (left) and 100 (right)

	# Allow user to reposition the listener
	@staticmethod
	def move_listener(x, y, z):
		sfml.audio.Listener.set_position((x, y, z))

	sound_cache = {}
	@classmethod
	def get_sound(cls, loc, cache=True):
		if loc in cls.sound_cache:
			return cls.sound_cache[loc]
		sound = sfml.audio.SoundBuffer.from_file(loc)
		if cache:
			cls.sound_cache[loc] = sound
		return sound
