import Plugin

class User (Plugin.Plugin):
	'''This is the class for information about users

use it like this: 
command= "user attribute"
data= b"value"

so the value of attribute is set to value


'''
	registeredCommands= ['user']
	def init(self):
		'''initialize the class'''
		self.attributes= {} # 'str' : bytes


	def recvCommand(self, packet):
		attr= packet.command.split(' ')[1]
		self[attr]= packet.data

	def __getitem__(self, item):
		'''get searchPlugin('User')[key]'''
		return self.attributes[item]
		
	def __setitem__(self, item, value):
		'''set searchPlugin('User')[key] = value'''
		self.attributes[item]= value

	def get(self, *args):
		'''get(value, [defaultValue])

Try to get the value for key from the plugin.
If this fails defaultValue is returned.
defaultValue defaults to None.
'''
		return self.attributes.get(*args)
