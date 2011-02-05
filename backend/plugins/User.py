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
		lib.records.User.__init__(self)

	def init(self):
		'''initialize the class'''
		for attribute in self.config.options():
			if attribute == 'revision':
				self.revision = int(self.config.get(attribute))
			else:
				self[attribute] = self.config.get(attribute)
		# check fo userhash
		if 'userhash' not in self:
			# generate node id
			self['userhash'] = hashlib.sha1("{0}\n{1}".format(datetime.datetime.now(),
				str(os.environ)).encode('utf8')).hexdigest()
			self.config.set('userhash', self.userhash)
		self.autoincrement = True # increase revision number automatically

	def commandUA_setUserAttr(self, packege, attribute):
		'''  the user attribute "attribute" (param) to a new  value'''
		self[attribute]= packege.data
		self.config.set(attribute, packege.data)
		self.config.set('revision', self.revision)


	def commandRA_getUserAttr(self, packege, attribute):
		''' return the user attribute "attribute" (param)'''
		return self[attribute]


	def commandA_setUserRevision(self, packege, revision):
		''' set revision of user data (use only if you know what you do)'''
		self.revision = int(revision)
		self.config.set('revision', self.revision)


	def commandRA_listUserAttrs(self, packege):
		''' return the user attribute "attribute" (param)'''
		return "\n".join(self.attributeList())


	def commandR_userInfo(self, packege):
		''' return all information about yourself'''
		return str(self)
