import sfml

# Expose the Keyboard and Event classes to the PyPunk API
Key = sfml.Keyboard
Event = sfml.Event


# Singleton factory class so I can have property classmethods and such
class Singleton(object):
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls._instance


class _input(Singleton):
	key_register = {}

	# Called by the Engine to set up initial event bindings
	#@classmethod
	def _bind_events(cls):
		EventManager.register_event(Event.KEY_PRESSED, cls._on_key_pressed)
		EventManager.register_event(Event.KEY_RELEASED, cls._on_key_released)

	# Private callback functions
	#@classmethod
	def _on_key_pressed(cls, event):
		# Make sure there's an registry entry
		if event.code not in cls.key_register:
			cls.key_register[event.code] = {'pressed':False, 'released':False, 'down':False}
		# Check that it's not down already, set pressed and down to True
		key = cls.key_register[event.code]
		if not key['down']:
			key['down'] = key['pressed'] = True

	#@classmethod
	def _on_key_released(cls, event):
		if event.code not in cls.key_register:
			cls.key_register[event.code] = {'pressed':False, 'released':False, 'down':False}
		key = cls.key_register[event.code]
		if key['down']:
			key['down'] = False
			key['released'] = True

	# Clear the Pressed/Released state of the variables
	#@classmethod
	def _clear_key_states(cls):
		for key in cls.key_register.values():
			key['pressed'] = key['released'] = False
Input = _input()


class _event_manager(Singleton):
	event_register = {}

	# Register a callback function to an event
	#@classmethod
	def register_event(cls, event, callback):
		if event not in cls.event_register:
			cls.event_register[event] = []
		cls.event_register[event].append(callback)

	# Will probably need a dereg function at some point

	# Dispatch all waiting events for specified screen object
	#@classmethod
	def dispatch_events(cls, screen):
		for event in screen.iter_events():
			# Check if the event is in the register, if it is, execute callbacks
			if event.type in cls.event_register:
				for callback in cls.event_register[event.type]:
					callback(event)
					# According to my old code, might have to do some fancy stuff
					# here to dereg stuff
EventManager = _event_manager()