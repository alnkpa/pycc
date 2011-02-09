import Plugin
import lib.records
import os
import hashlib
import datetime

class UserPlugin (Plugin.EasyPlugin, lib.records.User):
	'''This is the class for information about the user

use it like this: 
command= "setUserAttr attribute"
data= b"value"

so the value of attribute is set to value

use command= "getUserAttr attribute" to get value of attribute

for plugin developer:
get instance of this Plugin via self.manager.searchPlugin('UserPlugin')
user this plugin as normal list (<UserPluginInstance>[attr] ...)
see lib/records.py: User for more information


'''

	def __init__(self, *args, **kargs):
		Plugin.EasyPlugin.__init__(self,*args,**kargs)
		# increase revision number automatically
		lib.records.User.__init__(self, autoincrement = True)

	def init(self):
		'''initialize the class'''
		for attribute in self.config.options():
			if attribute == 'revision':
				self.revision = int(self.config.get(attribute))
			elif attribute == 'userhash':
				self.userhash = self.config.get('userhash')
			else:
				self[attribute] = self.config.get(attribute)
		# check fo userhash
		if self.userhash is None:
			# generate node id
			self.userhash = hashlib.sha1("{0}\n{1}".format(datetime.datetime.now(),
				str(os.environ)).encode('utf8')).hexdigest()
			self.config.set('userhash', self.userhash)

	# MANGER USE ATTRIBUTES
	def commandUA_setUserAttr(self, package, attribute):
		'''  the user attribute "attribute" (param) to a new  value'''
		self[attribute]= package.data
		self.config.set(attribute, package.data)


	def commandRA_getUserAttr(self, package, attribute):
		''' return the user attribute "attribute" (param)'''
		try:
			return self[attribute]
		except KeyError:
			package.data = 'unknown attribute "{0}"'.format(attribute)
			package.connection.sendError(package)


	def commandR_getUserRevision(self, package):
		''' return user setting revision, getUserAttr revision also possible'''
		return self.revision


	def commandA_setUserRevision(self, package, revision):
		''' set revision of user data (use only if you know what you do)'''
		self.revision = int(revision)
		self.config.set('revision', self.revision)


	# MANGE USER STATE
	def commandUA_setUserState(self, package, state):
		'''  the user state to "state" (param); with data you could set the state message'''
		self.state = state
		if package.data is not None:
			self.statemessage = package.data

	def commandRA_getUserState(self, package):
		''' return the user state (first line state name then optional state message'''
		return "{0}\n{1}".format(self.state, self.statemessage)


	# GENERAL INFORMATION
	def commandRA_listUserAttrs(self, package):
		''' return the user attribute "attribute" (param)'''
		return "\n".join(self.attributeList())


	def commandR_userInfo(self, package):
		''' return all information about yourself'''
		return str(self)
