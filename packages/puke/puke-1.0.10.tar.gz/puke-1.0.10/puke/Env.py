import os

class Env:

	@staticmethod
	def get(name):
		return os.environ.get(name)