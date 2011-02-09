'''Manages all the contacts'''

import Plugin
import records

class ContactPlugin(Plugin.EasyPlugin):
	'''Manages all the Contacts

		With this plugin you may read and change all the accounts given in
		self.contacts

		self.contacts is a list containing tuples whose first items are the
			AccountName and second nodeId

		addAccount		- needs AccountName and nodeId seperated by a
							colon in package.data
						- adds the given account to a temporary list
						- can be called by any package from anywhere in the
							moment
		deleteAccount	- needs an AccountName to be deleted
						- can be called by any package from anywhere at the
							moment
		getAccounts		- returns all Accounts of the user
						- does not need anything
						- can be called by any package from anywhere in the
							moment'''

	def init(self):
		'''initially get all'''
		self.contacts = {}
		for contacthash in self.config.sections(): # iterate about all saved contacts
			contact = records.User(userhash = contacthash)
			for option in self.config.options(contacthash):
				if option == 'revision':
					contact.revision = int(self.config.get(option, section = contacthash))
				else:
					contact[option] = self.config.get(option, section = contacthash)
			self.contacts[contacthash] = contact

	def startup(self):
		'''load user plugin (not possible in init because the ContactPlugin is maybe
		   loaded before the UserPlugin'''
		try:
			self.user = self.manager.searchPlugin('UserPlugin')
		except KeyError: # no UserPlugin found
			self.user = None

	def saveContact(self, contact):
		''' save to data of one contact to the plugin config'''
		userhash = contact.userhash # get userhash
		for attribute in contact.attributeList(): # save every attribute
			self.config.set(attribute, contact[attribute], section = userhash)
		# save revision extra because revision is not a user attribute
		self.config.set('revision', contact.revision, section = userhash)


	def commandA_addAccount(self, package, argument):
		'''Adds a new contact to the contact storage
		Takes an argument with the form name:nodeId
		FixMe: should be improved'''
		accountName, nodeId = argument.split(":")
		contact = records.User(username=accountName, nodes=[nodeId])
		self.saveContact(contact)
		self.contacts[contact] = contact

	def commandA_deleteAccount(self, command, name):
		'''Deletes a specific account by Name
		   FixMe: not working anymore'''
		try:
			self.contacts.remove((name, self.returnNodeId(name)))
		except ValueError:
			pass

	def commandR_getAccounts(self, package):
		'''Get all of the accounts, comma seperated accountName:accountNodeId pairs are returned'''
		string=""
		for contact in self.contacts:
			string=string+self.contacts[contact].username+":"+self.contacts[contact].userhash+","
		return string[:-1] # remove last ,

	def commandR_listAccounts(self, package):
		'''list all avaibable attributes about all known user'''
		string=""
		for contact in self.contacts:
			string += str(self.contacts[contact])+"\n\n"
		return string[:-2] # remove last \n\n

	def commandR_listContactStates(self, package):
		''' return a list with username and state of all contacts'''
		result = ''
		for account in self.contacts:
			result += '{username}: {state}\n'.format(
				username=self.contacts[account].get('username',\
				self.contacts[account].userhash), state = self.contacts[account].state)
		return result[:-1]


	def command_accountList(self,  package):
		print(self.contacts)



	def commandA_announceYourself(self, package):
		''' inform all clients about the current user attributes'''
		if self.user is None: # have we user attribtes set and UserPlugin avaibable?
			return
		for con in self.backend.getNodeConnections(":clients"): # infor all! clients
			con.sendRequest(self.backend.newPackage(
				command = 'announceUser {0} {1}'.format(self.user['userhash'],
				self.user.revision)))

	def commandA_announceUser(self, package, userhash, revision):
		''' other backend inform us about its new/current user settings'''
		if userhash.strip() == self.user.userhash.strip(): # get yourself
			return
		revision = int(revision) # revision have to be an integer
		if userhash in self.contacts:
			self.contacts[userhash]['node'] = package.connection.partnerNodeId
		if userhash in self.contacts and self.contacts[userhash].revision >= revision:
			return # no new information
		# fetch a list of all user attributes of the other backend:
		package.connection.sendRequest(self.backend.newPackage(command = 'listUserAttrs'),
			callback = self.receiveUserList, callbackExtraArg = (userhash, revision))

	def receiveUserList(self, package, userhashRevision):
		''' callback for the result of the list of all user attributes of the other backend'''
		userhash, revision = userhashRevision # split extra callback arguments
		if userhash not in self.contacts: # new contact
			self.contacts[userhash] = records.User(userhash = userhash, revision = revision)
		else: # existing contact -> update revision
			self.contacts[userhash].revision = revision
		# ask for every attribute:
		for attr in package.data.decode('utf-8').strip().split('\n'):
			package.connection.sendRequest(self.backend.newPackage(
				command = 'getUserAttr {0}'.format(attr)),
				callback = self.receiveUserAttr, callbackExtraArg = (userhash, attr))
		return True # callback done -> should be deleted

	def receiveUserAttr(self, package, userhashAttr):
		''' callback for the user attribute request to an other backend'''
		userhash, attr = userhashAttr # split extra callback arguments
		self.contacts[userhash][attr] = package.data.decode('utf-8') # get new value
		self.saveContact(self.contacts[userhash]) # save changed contact
		return True # callback done -> should be deleted



	def returnNodeId(self, name):
		for contact in self.contacts:
			if self.contacts[contact].username == name:
				return self.contacts[contact].node
		raise ValueError

	def returnUserName(self,  nodeId):
		for contact in self.contacts:
			if self.contacts[contact].node == nodeId:
				return self.contacts[contact].username
		raise ValueError
