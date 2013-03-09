from .utils import Input, Key

class Console(object):
	def __init__(self):
		Input.define('_ARROWS', Key.RIGHT, Key.LEFT, Key.DOWN, Key.UP)