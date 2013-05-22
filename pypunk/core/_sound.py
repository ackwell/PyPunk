
import sfml
from ._pp import PP

class Sfx(object):
	def __init__(self, source, complete=None, _type='', stream=False):
		self._type = _type
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

		# For panning, etc
		Sfx.setup_sound(self.source)
		Sfx.localize_sound(self.source)

	def play(self, vol=1, pan=0, stop_on_remove=False):
		if self.source.status != sfml.audio.SoundSource.STOPPED:
			...#self.stop()
		# Make sure sound isn't looping (might have been looping previously)
		self.source.loop = False
		# SFML volume is 0 -> 100
		vol = PP.clamp(vol, 0, 1)
		self.source.volume = vol * 100
		# SFML Panning is between -100 (left) and 100 (right)
		pan = PP.clamp(vol, -1, 1)
		Sfx.localize_sound(self.source, pan*100, 0)

		# Keep reference to sounds that should persist until they finish playing.
		if not stop_on_remove:
			Sfx._add_sfx_ref(self)

		self.source.play()

	def loop(self, vol=1, pan=0, stop_on_remove=True):
		self.play(vol, pan, stop_on_remove)
		self.source.loop = True


	listener_depth = 10
	base_att = 0
	base_min_dist = 100
	@classmethod
	def setup_listener(cls, min_dist=100, att=0, listener_depth=10):
		cls.listener_depth = listener_depth
		cls.base_att = att
		cls.base_min_dist = min_dist
		sfml.audio.Listener.set_direction((0, 0, -cls.listener_depth))

	@classmethod
	def localize_listener(cls, x=0, y=0):
		sfml.audio.Listener.set_position((x, y, cls.listener_depth))

	@classmethod
	def setup_sound(cls, sound):
		sound.min_distance = cls.base_min_dist
		sound.attenuation = cls.base_att

	@classmethod
	def localize_sound(cls, sound, x=0, y=0):
		sound.position = (x, y, 0)

	# Used to keep tabs on sounds that should play out before being removed
	sfx_refs = []
	@classmethod
	def _add_sfx_ref(cls, sfx):
		if sfx not in cls.sfx_refs:
			cls.sfx_refs.append(sfx)

	@classmethod
	def _check_sfx_refs(cls):
		cls.sfx_refs = [ref for ref in cls.sfx_refs if\
			(lambda ref: ref.source.status != sfml.audio.SoundSource.STOPPED)(ref)]

	sound_cache = {}
	@classmethod
	def get_sound(cls, loc, cache=True):
		if loc in cls.sound_cache:
			return cls.sound_cache[loc]
		sound = sfml.audio.SoundBuffer.from_file(loc)
		if cache:
			cls.sound_cache[loc] = sound
		return sound
