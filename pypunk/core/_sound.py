
import sfml
from ._pp import PP

class Sfx(object):
	def __init__(self, source, complete=None, _type='', stream=False):
		self._type = _type
		self.complete = complete

		# Used to store unchanged vol/pan
		self._vol = 100
		self._pan = 0

		self.source = None
		# Passed a path to the file
		if isinstance(source, str):
			if stream:
				raise NotImplementedError() # create a streming buffer with sfml.Music
			else:
				buf = Sfx._get_sound(source)
				self.source = sfml.audio.Sound(buf)
		else:
			self.source = source

		# For panning, etc
		Sfx.setup_sound(self.source)
		Sfx.localize_sound(self.source)

	def play(self, vol=1, pan=0, stop_on_remove=False):
		if not self._is_stopped:
			self.stop()
		# Make sure sound isn't looping (might have been looping previously)
		self.source.loop = False
		self.volume = vol
		self.pan = pan

		# Keep reference to sounds that should persist until they finish playing.
		if not stop_on_remove:
			Sfx._add_sfx_ref(self)

		self._add_playing()
		self.source.play()

	def loop(self, vol=1, pan=0, stop_on_remove=True):
		self.play(vol, pan, stop_on_remove)
		self.source.loop = True

	def stop(self, force=False):
		if self._is_stopped:
			return False
		self._remove_playing()
		if force:
			self.source.stop()
		else:
			self.source.pause()
		return True

	def resume(self):
		self.source.play()
		self._add_playing()

	def _add_playing(self):
		if self._type not in Sfx._type_playing:
			Sfx._type_playing[self._type] = []
		Sfx._type_playing[self._type].append(self)

	def _remove_playing(self):
		if self._type in Sfx._type_playing and self in Sfx._type_playing[self._type]:
			Sfx._type_playing[self._type].remove(self)

	def _set_volume(self, vol):
		self._vol = vol = max(0, vol)
		filtered_vol = vol * Sfx.get_volume(self._type)
		filtered_vol = PP.clamp(filtered_vol, 0, 1) # Only clamp temporary value
		# SFML volume is 0 -> 100
		self.source.volume = filtered_vol * 100
	volume = property(lambda self: self._vol, _set_volume)

	def _set_pan(self, pan):
		self._pan = pan = PP.clamp(pan, -1, 1)
		filtered_pan = pan + Sfx.get_pan(self._type)
		filtered_pan = PP.clamp(filtered_pan, -1, 1)
		# SFML Panning is between -100 (left) and 100 (right)
		Sfx.localize_sound(self.source, pan*100, 0)
	pan = property(lambda self: self._pan, _set_pan )

	def _set_type(self, _type):
		if self._type == _type:
			return
		self._remove_playing()
		self._type = _type
		self._add_playing()
		# Recalculate vol/pan
		self.volume = self.volume
		self.pan = self.pan

	playing = property(lambda self: not self._is_stopped)

	position = property(lambda self: self.source.playing_offset.seconds)

	# Length - don't think SFML supports this...

	_type_transforms = {}
	_type_playing = {}
	@classmethod
	def get_pan(cls, _type):
		if _type not in cls._type_transforms:
			return 0
		return cls._type_transforms[_type]['pan']

	@classmethod
	def get_volume(cls, _type):
		if _type not in cls._type_transforms:
			return 1
		return cls._type_transforms[_type]['volume']

	@classmethod
	def set_pan(cls, _type, pan):
		if _type not in cls._type_transforms:
			cls._type_transforms[_type] = {'pan':0, 'volume':1}
		cls._type_transforms[_type]['pan'] = PP.clamp(pan, -1, 1)
		for sfx in cls._type_playing[_type]:
			sfx.pan = sfx.pan

	@classmethod
	def set_volume(cls, _type, vol):
		if _type not in cls._type_transforms:
			cls._type_transforms[_type] = {'pan':0, 'volume':1}
		cls._type_transforms[_type]['vol'] = max(0, vol)
		for sfx in cls._type_playing[_type]:
			sfx.volume = sfx.volume

	def _is_stopped(self):
		return self.source.status == sfml.audio.SoundSource.STOPPED

	_listener_depth = 10
	_base_att = 0
	_base_min_dist = 100
	@classmethod
	def setup_listener(cls, min_dist=100, att=0, listener_depth=10):
		cls._listener_depth = listener_depth
		cls._base_att = att
		cls._base_min_dist = min_dist
		sfml.audio.Listener.set_direction((0, 0, -cls._listener_depth))

	@classmethod
	def localize_listener(cls, x=0, y=0):
		sfml.audio.Listener.set_position((x, y, cls._listener_depth))

	@classmethod
	def setup_sound(cls, sound):
		sound.min_distance = cls._base_min_dist
		sound.attenuation = cls._base_att

	@classmethod
	def localize_sound(cls, sound, x=0, y=0):
		sound.position = (x, y, 0)

	# Used to keep tabs on sounds that should play out before being removed
	_sfx_refs = []
	@classmethod
	def _add_sfx_ref(cls, sfx):
		if sfx not in cls._sfx_refs:
			cls._sfx_refs.append(sfx)

	@classmethod
	def _check_sfx_refs(cls):
		cls._sfx_refs = [ref for ref in cls._sfx_refs if\
			(lambda ref: ref.source.status != sfml.audio.SoundSource.STOPPED)(ref)]

	_sound_cache = {}
	@classmethod
	def _get_sound(cls, loc, cache=True):
		if loc in cls._sound_cache:
			return cls._sound_cache[loc]
		sound = sfml.audio.SoundBuffer.from_file(loc)
		if cache:
			cls._sound_cache[loc] = sound
		return sound
