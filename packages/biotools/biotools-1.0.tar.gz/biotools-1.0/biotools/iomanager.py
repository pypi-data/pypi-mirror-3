class IOManager(object):
	def __init__(self, methods=None):
		self.methods   = methods or {}
		self.protected = set(self.methods.keys())

		nil = lambda *x: None
		self.default = {'rhook': nil, 'read':  nil,
		                'whook': nil, 'write': nil}

	def __contains__(self, key):
		return key in self.methods

	def __getitem__(self, key):
		return self.methods.get(key, self.default)

	def get(self, key, default=None):
		try: return self.methods[key]
		except: return default or self.default

	def __setitem__(self, key, value):
		if key not in self.protected:
			self.methods[key] = value
		return value

	def __iter__(self):
		return iter(self.methods)
