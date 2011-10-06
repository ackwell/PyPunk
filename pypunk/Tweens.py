from PySFML import sf
import Punk

#maybe make an exists var so tweens can be removed?

class Timer:
	def __init__(self):
		"""Create new simple timer"""
		self.running = False
		self.value = 0
	
	#Not actually a tween but meh
	def updateTween(self):
		if self.running:
			self.value += Punk.elapsed
	
	#Start counting
	def start(self):
		self.running = True

	#Stop counting, reset
	def stop(self):
		self.running = False
		self.value = 0
	
	#Stop counting, stay at current value
	def pause(self):
		self.running = False

	#Continue counting, reset value
	def reset(self):
		self.value = 0