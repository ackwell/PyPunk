import os
import sfml
from ._bitmap import Image
from ..core import PyPunkError

# Note: SFML Text objects are a lot more limited than that found in flash.
# I'll likely try to expand this somewhat at a later point, but for now, it
# is restricted to SFML's native capabilities
class Text(Image):
	# Class variables - assigned to new Text obects
	FONT = os.path.dirname(os.path.abspath(__file__)) + "/04B_03__.TTF"
	SIZE = 16
	# ALIGN = "left"
	# DEFAULT_LEADING = 0
	# WORD_WRAP = False
	# RESIZEABLE = True

	# Not including backwards compatibility. Deal with it.
	def __init__(self, text, x=0, y=0, **options):
		# Private variables
		# self._width = 0
		# self._height = 0
		# self._rich_text = ''
		# self._align = Text.ALIGN
		# self._leading = Text.DEFAULT_LEADING
		# self._word_wrap = Text.WORD_WRAP
		# Public variables
		# self.resizeable = Text.RESIZEABLE

		text = sfml.graphics.Text(text, Text._get_font(Text.FONT), Text.SIZE)
		Image.__init__(self, text)

		for k, v in options.items():
			if not hasattr(self, k):
				raise PyPunkError('"' + k + '" is not a property of Text.')
			setattr(self, k, v)

		self.x = x
		self.y = y

	def _set_text(self, value):
		self.drawable.string = value
	text = property(lambda self: self.drawable.string, _set_text)

	# Font property needs to accept Font and str path, if str, get font from cache/whatever 
	def _set_font(self, value):
		if isinstance(value, str):
			value = Text._get_font(value)
		self.drawable.font = value
	font = property(lambda self: self.drawable.font, _set_font)

	def _set_size(self, value):
		self.drawable.character_size = value
	size = property(lambda self: self.drawable.character_size, _set_size)

	_font_cache = {}
	@classmethod
	def _get_font(cls, loc, cache=True):
		if loc in cls._font_cache:
			return cls._font_cache[loc]
		font = sfml.graphics.Font.from_file(loc)
		if cache:
			cls._font_cache[loc] = font
		return font
