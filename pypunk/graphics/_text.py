from ._bitmap import Image

class Text(Image):
	# Class variables - assigned to new Text obects
	self.font = "default"
	self.size = 16
	self.align = "left"
	self.default_leading = 0
	self.word_wrap = False
	self.resizeable = True

	# Not including backwards compatibility. Deal with it.
	def __init__(self, text, x=0, y=0, **options):
		# Private variables
		self._width = 0
		self._height = 0
		self._text_width = 0
		self._text_height = 0
		self._text = ''
		self._rich_text = ''
		self._font = Text.font
		self._size = Text.size
		self._align = Text.align
		self._leading = Text.default_leading
		self._word_wrap = Text.word_wrap

		# Public variables
		self.resizeable = Text.resizeable

		width = 0
		height = 0
		if len(options):
			if 'font' in options: self._font = options['font']
			if 'size' in options: self._size = options['size']
			if 'align' in options: self._align = options['align']
			if 'word_wrap' in options: self._word_wrap = options['word_wrap']
			if 'resizeable' in options: self.resizeable = options['resizeable']
			if 'width' in options: self.width = options['width']
			if 'height' in options: self.height = options['height']

		# INCOMPLETE