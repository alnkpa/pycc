class User(object):
	'''This is the record class for a chat user
supported attributes:
userhash: str; user identifier
revision: int; revision number of all attributes
nodes: list of str; list of nodes of this user
username: str; username
'''

	def __init__(self, autoincrement=False, revision = 0, **kargs):
		'''initialize the class'''
		self.autoincrement = autoincrement
		object.__setattr__(self,'_attributes',kargs) # 'str' : str/bytes
		self.revision = revision

	def __getitem__(self, item):
		'''get attr via <UserInstnace>[item]'''
		return self._attributes[item]

	def __getattr__(self, item):
		'''get attr via <UserInstnace>.item'''
		if item in self._attributes:
			return self._attributes[item]
		else:
			raise AttributeError('user {0} has no attribute {1}'.format('',item))

	def __setitem__(self, item, value):
		'''get attr via <UserInstnace>[item] = value'''
		if self.autoincrement:
			self.revision += 1
		self._attributes[item]= value

	def __contains__(self, item):
		'''test wheather an attributes exists (for <element> in <UserInstnace>)'''
		return item in self._attributes

	def get(self, *args):
		'''get(value, [defaultValue])

Try to get the value for key from the plugin.
If this fails defaultValue is returned.
defaultValue defaults to None.
'''
		return self._attributes.get(*args)

	def attributeList(self):
		''' return a list of all attributes of this user'''
		return self._attributes.keys()
