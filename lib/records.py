class User(object):
	'''This is the record class for a chat user
general members:
  revision: int; revision number of user attributes
		this is use to check fast wheather user settings have changed
  autoincrement: bool; automatacally increment revision number when setting a user attribute
  userhash: str; unique identifer of the user
  state: str; name of chat state (offline, online, away ...)
  statemessage: str|None; user specific text message for current state

(optional) attributes:
node: str; node id of this user
username: str; username
firstname: str; firstname of user
surname: str; surname of user
...
'''

	def __init__(self, autoincrement=False, userhash = None, state = 'offline', revision = 0, **kargs):
		'''initialize the class'''
		self.autoincrement = autoincrement
		object.__setattr__(self,'_attributes',kargs) # 'str' : str/bytes
		self.userhash = userhash
		self.revision = revision
		if type(state) is tuple: # state and staemessage given
			self.state, self.statemessage = state
		else: # only state given
			self.state = state
			self.statemessage = None

	def __getitem__(self, item):
		'''get attr via <UserInstance>[item]'''
		if item == 'userhash':
			return self.userhash
		elif item == 'revision':
			return revision
		elif item == 'state':
			return self.state
		elif item == 'statemessage':
			return self.statemessage
		else: # general attribute
			return self._attributes[item]

	def __getattr__(self, item):
		'''get attr via <UserInstance>.item'''
		if item in self._attributes:
			return self._attributes[item]
		else:
			raise AttributeError('user {0} has no attribute {1}'.format('',item))

	def __setitem__(self, item, value):
		'''get attr via <UserInstnace>[item] = value'''
		# handle userhash, state and statemessage separat
		if item == 'userhash':
			self.userhash = value
		elif item == 'state':
			self.state = value
		elif item == 'statemessage':
			self.statemessage = value
		else:
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

	def __str__(self):
		result  = '{0}@r{1}'.format(self.userhash,self.revision)
		result += '\nstate:\n\t{0}\nstatemessage:\n\t{1}'.format(self.state.replace('\n','\n\t'),
			str(self.statemessage).replace('\n','\n\t'))
		for option in self._attributes:
			try:
				result+='\n{0}:\n\t{1}'.format(option,
					str(self._attributes[option]).replace('\n','\t\n'))
			except UnicodeError:
				continue
		return result
