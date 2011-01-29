import Plugin

class User (Plugin.EasyPlugin):
	'''This is the class for information about users

use it like this: 
command= "setUserAttr attribute"
data= b"value"

so the value of attribute is set to value


'''
	def init(self):
		'''initialize the class'''
		self.attributes= {} # 'str' : bytes


	def commandA_setUserAttr(self, packet, attribute):
		'''  the user attribute "attribute" (param) to a new  value'''
		self[attribute]= packet.data


	def commandRA_getUserAttr(self, packet, attribute):
		''' return the user attribute "attribute" (param)'''
		return self.attributes[attribute]

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
