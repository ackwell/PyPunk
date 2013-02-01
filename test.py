from pypunk.core import Engine

# Engine can probably be done inline - no need for child class
class Main(Engine):
	def __init__(self):
		super().__init__(800, 600, 60, "PyPunk Test - FP Tutorial")
		print("PyPunk has started successfully!")
		# Add world
		self.begin()

if __name__ == '__main__':
	engine = Main()