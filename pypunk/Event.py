from PySFML import sf

#Link sf librarys for 'em
Key = sf.Key
Event = sf.Event

Register = {
sf.Event.Closed:[],
sf.Event.Resized:[],
sf.Event.LostFocus:[],
sf.Event.GainedFocus:[],
sf.Event.TextEntered:[],
sf.Event.KeyPressed:[],
sf.Event.KeyReleased:[],
sf.Event.MouseWheelMoved:[],
sf.Event.MouseButtonPressed:[],
sf.Event.MouseButtonReleased:[],
sf.Event.MouseMoved:[],
sf.Event.MouseEntered:[],
sf.Event.MouseLeft:[],
sf.Event.JoyButtonPressed:[],
sf.Event.JoyButtonReleased:[],
sf.Event.JoyMoved:[]
}

#Deregistered auomatically (i hope) when exists == False
def RegisterEvent(event, func):
	"""Register a new event function.
	Function should accept single dictionary argument"""
	Register[event].append(func)

def DeregisterEvent(event, func):
	"""Deregister a registered event"""
	Register[event].remove(func)

def DispatchEvents(App):
	e = sf.Event()
	while App.GetEvent(e):
		#Insert appropriate arguments
		args = {}
		if e.Type == sf.Event.Resized:
			args["Width"] = e.Size.Width
			args["Height"] = e.Size.Height
		elif e.Type == sf.Event.TextEntered:
			args["Unicode"] = e.Text.Unicode
		elif e.Type == sf.Event.KeyPressed or e.Type == sf.Event.KeyReleased:
			args["Code"] = e.Key.Code
			args["Alt"] = e.Key.Alt
			args["Control"] = e.Key.Control
			args["Shift"] = e.Key.Shift
		elif e.Type == sf.Event.MouseButtonPressed or e.Type == sf.Event.MouseButtonReleased:
			args["Button"] = e.MouseButton.Button
			args["X"] = e.MouseButton.X
			args["Y"] = e.MouseButton.Y
		elif e.Type == sf.Event.MouseMoved:
			args["X"] = e.MouseMove.X
			args["Y"] = e.MouseMove.Y
		elif e.Type == sf.Event.MouseWheelMoved:
			args["Delta"] = e.MouseWheel.Delta
		elif e.Type == sf.Event.JoyButtonPressed or e.Type == sf.Event.JoyButtonReleased:
			args["JoystickId"] = e.JoyButton.JoystickId
			args["Button"] = e.JoyButton.Button
		elif e.Type == sf.Event.JoyMoved:
			args["JoystickId"] = e.JoyMove.JoystickId
			args["Axis"] = e.JoyMove.Axis
			args["Position"] = e.JoyMove.Position
		
		r=Register[e.Type]
		for func in r:
			try: #If it is possible for it not to exist, check it
				if func.im_self.world:
					func(args)
				else:
					r.remove(func)
			except AttributeError: #Otherwise just call it
				func(args)
		

