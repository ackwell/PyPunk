import math
import sfml

# Expose the Keyboard, Event and Mouse classes to the PyPunk API
Key = sfml.window.Keyboard
Event = sfml.window.Event
Mouse = sfml.window.Mouse


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
				if k in cls._key_register:
					if cls._key_register[k][action]:
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


# Easing functions - using a singleton to save myself typing @staticmethod for errything
class _ease(Singleton):
	def __init__(cls):
		cls.PI = math.pi
		cls.PI2 = math.pi / 2
		cls.B1 = 1 / 2.75
		cls.B2 = 2 / 2.75
		cls.B3 = 1.5 / 2.75
		cls.B4 = 2.5 / 2.75
		cls.B5 = 2.25 / 2.75
		cls.B6 = 2.625 / 2.75

	# QUAD #
	def quad_in(cls, t): return t**2
	def quad_out(cls, t): return -t*(t-2)
	def quad_in_out(cls, t): t2=t-1; return t**2*2 if t<=0.5 else 1-t2**2*2

	# CUBIC #
	def cube_in(cls, t): return t**3
	def cube_out(cls, t): t-=1; return 1+t**3
	def cube_in_out(cls, t): t2=t-1; return t**3*4 if t<=0.5 else 1+t2**3*4

	# QUART #
	def quart_in(cls, t): return t**4
	def quart_out(cls, t): t-=1; return 1-t**4
	def quart_in_out(cls, t): t2=t*2-2; return t**4*8 if t<=0.5 else (1-t2**4)/2+0.5

	# QUINT #
	def quint_in(cls, t): return t**5
	def quint_out(cls, t): t=-1; return t**5+1
	def quint_in_out(cls, t): t*=2; t2=t-2; return (t**5)/2 if t<1 else (t2**5+2)/2

	# SINE #
	def sine_in(cls, t): return -math.cos(cls.PI2*t)+1
	def sine_out(cls, t): return math.sin(cls.PI2*t)
	def sine_in_out(cls, t): return -math.cos(cls.PI*t)/2+0.5

	# BOUNCE #
	def bounce_in(cls, t):
		t=1-t
		if t<cls.B1: return 1-7.5625*t**2;
		if t<cls.B2: return 1-(7.5625*(t-cls.B3)*(t-cls.B3)+0.75)
		if t<cls.B4: return 1-(7.5625*(t-cls.B5)*(t-cls.B5)+0.9375)
		return 1-(7.5625*(t-cls.B6)*(t-cls.B6)+0.984375)
	def bounce_out(cls, t):
		if t<cls.B1: return 7.5625*t**2;
		if t<cls.B2: return 7.5625*(t-cls.B3)*(t-cls.B3)+0.75
		if t<cls.B4: return 7.5625*(t-cls.B5)*(t-cls.B5)+0.9375
		return 7.5625*(t-cls.B6)*(t-cls.B6)+0.984375
	def bounce_in_out(cls, t):
		if t<0.5:
			t=1-t*2
			if t<cls.B1: return (1-7.5625*t**2)/2
			if t<cls.B2: return (1-(7.5625*(t-cls.B3)*(t-cls.B3)+0.75))/2
			if t<cls.B4: return (1-(7.5625*(t-cls.B5)*(t-cls.B5)+0.9375))/2
			return (1-(7.5625*(t-cls.B6)*(t-cls.B6)+0.984375))/2
		t=t*2-1
		if t<cls.B1: return (7.5625*t**2)/2+0.5
		if t<cls.B2: return (7.5625*(t-cls.B3)*(t-cls.B3)+0.75)/2+0.5
		if t<cls.B4: return (7.5625*(t-cls.B5)*(t-cls.B5)+0.9375)/2+0.5
		return (7.5625*(t-cls.B6)*(t-cls.B6)+0.984375)/2+0.5

	# CIRCLE #
	def circ_in(cls, t): return -(math.sqrt(1-t*t)-1)
	def circ_out(cls, t): return math.sqrt(1-(t-1)*(t-1))
	def circ_in_out(cls, t): return (math.sqrt(1-t*t*4)-1)/-2 if t<=0.5 else (math.sqrt(1-(t*2-2)*(t*2-2))+1)/2

	# EXPONENTIAL #
	def expo_in(cls, t): return math.pow(2, 10*(t-1))
	def expo_out(cls, t): return -math.pow(2, -10*t)+1
	def expo_in_out(cls, t): return math.pow(2, 10*(t*2-1))/2 if t<0.5 else (-math.pow(2, -10*(t*2-1))+2)/2

	# BACK #
	def back_in(cls, t): return t**2*(2.70158*t-1.70158)
	def back_out(cls, t): t-=1; return 1-t**2*(-2.70158*t-1.70158)
	def back_in_out(cls, t):
		t*=2;
		if t<1: return t**2*(2.70158*t-1.70158)/2
		t-=2; return (1-t**2*(-2.70158*t-1.70158))/2+0.5
Ease = _ease()