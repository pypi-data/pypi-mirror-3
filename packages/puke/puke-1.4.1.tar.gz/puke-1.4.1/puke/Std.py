
class Std:

	def __init__(self, out = '', err = ''):
		self.out = out
		self.err = err

	
	def set(self, out, err):
		self.out = out
		self.err = err

	def __repr__(self):
		return "Stdout : %s\n\nStdErr : %s\n" % (self.out, self.err)

	def __str__(self):
		return self.__repr__()