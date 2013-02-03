import sfml

# Expose the Keyboard, Event and Mouse classes to the PyPunk API
Key = sfml.Keyboard
Event = sfml.Event
Mouse = sfml.Mouse


# Singleton factory class so I can have property classmethods and such
class Singleton(object):
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls._instance


class _input(Singleton):
	def __init__(cls):
		# Public 
		cls.last_key = None

		cls.mouse_wheel = False
		cls.mouse_x = 0
		cls.mouse_y = 0

		# Private
		cls._key_register = {}
		cls._key_groups = {}

		cls._mouse_register = {}
		cls._mouse_wheel_delta = 0

	# Called by the Engine to set up initial event bindings
	def _bind_events(cls):
		EventManager.register_event(Event.KEY_PRESSED, cls._on_key_pressed)
		EventManager.register_event(Event.KEY_RELEASED, cls._on_key_released)
		EventManager.register_event(Event.MOUSE_MOVED, cls._on_mouse_move)
		EventManager.register_event(Event.MOUSE_BUTTON_PRESSED, cls._on_mouse_pressed)
		EventManager.register_event(Event.MOUSE_BUTTON_RELEASED, cls._on_mouse_released)
		EventManager.register_event(Event.MOUSE_WHEEL_MOVED, cls._on_mouse_wheel)

	# Input define, etc
	def define(cls, name, *keys):
		if len(keys) == 1 and isinstance(keys[0], list):
			cls._key_groups[name] = keys[0]
		else:
			cls._key_groups[name] = keys

	def keys(cls, name):
		return cls._key_groups[name]

	# Check functions
	def _check_key_register(cls, _input, action):
		if isinstance(_input, str):
			if _input not in cls._key_groups:
				return False
			for k in cls._key_groups[_input]:
				if _input in cls._key_register:
					if cls._key_register[_input][action]:
						return True
			return False
		if _input in cls._key_register:
			return cls._key_register[_input][action]
		return False

	def check(cls, _input):
		return cls._check_key_register(_input, 'down')

	def pressed(cls, _input):
		return cls._check_key_register(_input, 'pressed')

	def released(cls, _input):
		return cls._check_key_register(_input, 'released')

	# Mouse functions
	def mouse_down(cls, button=Mouse.LEFT):
		if button in cls._mouse_register:
			return cls._mouse_register[button]['down']
		return False

	def mouse_up(cls, button=Mouse.LEFT):
		if button in cls._mouse_register:
			return cls._mouse_register[button]['up']
		return False

	def mouse_pressed(cls, button=Mouse.LEFT):
		if button in cls._mouse_register:
			return cls._mouse_register[button]['pressed']
		return False

	def mouse_released(cls, button=Mouse.LEFT):
		if button in cls._mouse_register:
			return cls._mouse_register[button]['released']
		return False

	def _get_mouse_wheel_delta(cls):
		# This seems mighty weird to me but whatever
		if cls.mouse_wheel:
			cls.mouse_wheel = False
			return cls._mouse_wheel_delta
		return 0
	mouse_wheel_delta = property(_get_mouse_wheel_delta)

	# Clear the Pressed/Released state of the variables
	def _clear_states(cls):
		for key in cls._key_register.values():
			key['pressed'] = key['released'] = False

		for button in cls._mouse_register.values():
			button['pressed'] = button['released'] = False

	# Private callback functions
	def _on_key_pressed(cls, event):
		# Make sure there's an registry entry
		if event.code not in cls._key_register:
			cls._key_register[event.code] = {'pressed':False, 'released':False, 'down':False}
		# Check that it's not down already, set pressed and down to True
		key = cls._key_register[event.code]
		if not key['down']:
			key['down'] = key['pressed'] = True
			# set the last_key
			cls.last_key = event.code

	def _on_key_released(cls, event):
		if event.code not in cls._key_register:
			cls._key_register[event.code] = {'pressed':False, 'released':False, 'down':False}
		key = cls._key_register[event.code]
		if key['down']:
			key['down'] = False
			key['released'] = True

	def _on_mouse_move(cls, event):
		cls.mouse_x = event.x
		cls.mouse_y = event.y

	def _on_mouse_pressed(cls, event):
		if event.button not in cls._mouse_register:
			cls._mouse_register[event.button] = {'up':False,'down':False,'pressed':False,'released':False}
		button = cls._mouse_register[event.button]
		if not button['down']:
			button['down'] = button['pressed'] = True
			button['up'] = False

	def _on_mouse_released(cls, event):
		if event.button not in cls._mouse_register:
			cls._mouse_register[event.button] = {'up':False,'down':False,'pressed':False,'released':False}
		button = cls._mouse_register[event.button]
		if button['down']:
			button['up'] = button['released'] = True
			button['down'] = False

	def _on_mouse_wheel(cls, event):
		cls.mouse_wheel = True
		cls._mouse_wheel_delta = event.delta
Input = _input()


class _event_manager(Singleton):
	def __init__(cls):
		cls.event_register = {}

	# Register a callback function to an event
	def register_event(cls, event, callback):
		if event not in cls.event_register:
			cls.event_register[event] = []
		cls.event_register[event].append(callback)

	# Will probably need a dereg function at some point

	# Dispatch all waiting events for specified screen object
	def dispatch_events(cls, screen):
		for event in screen.iter_events():
			# Check if the event is in the register, if it is, execute callbacks
			if event.type in cls.event_register:
				for callback in cls.event_register[event.type]:
					callback(event)
					# According to my old code, might have to do some fancy stuff
					# here to dereg stuff
EventManager = _event_manager()