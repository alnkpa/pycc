'''Manages all the contacts'''

import Plugin

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
						- can be called by any package from anywhere in the 
							moment
		getAccounts		- returns all Accounts of the user
						- does not need anything
						- can be called by any package from anywhere in the 
							moment'''

	def init(self):
		'''initially get all'''
		self.contacts = []
		f = open(".contacts")
		append = self.contacts.append
		for line in f.readlines():
			if line != "\n":
				append((line.strip().split(":")[0],line.strip().split(":")[1]))		

	def commandA_addAccount(self, package, command, argument):
		'''Adds a new contact to the contact storage
		Takes an argument with the form name:nodeId'''
		argument = argument.decode("utf-8")
		accountName, nodeId = argument.split(":")		
		self.contacts.append((accountName, nodeId))
		
	def commandA_deleteAccount(self, command, name):
		'''Deletes a specific account by Name'''		
		try:		
			self.contacts.remove((name, self.returnNodeId(name)))
		except ValueError:
			pass

	def commandR_getAccounts(self, package):
		'''Get all of the accounts, comma seperated accountName:accountNodeId pairs are returned'''		
		string=""		
		for contact in self.contacts:
			string=string+contact[0]+":"+contact[1]+","
		return string

	def returnNodeId(self, name):
		for contact in self.contacts:
			if contact[0] == name:
				return contact[1]
		raise ValueError

	def returnUserName(self,  nodeId):
		for contact in self.contacts:
			if contact[1] == nodeId:
				return contact[0]
		raise ValueError

	def shutdown(self):
		f=open(".contacts","w")
		for contact in self.contacts:
			f.write(contact[0]+":"+contact[1]+"\n")
