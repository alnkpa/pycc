import Plugin

class ContactPlugin(Plugin.Plugin):
	''' Manages all the Contacts '''
	registeredCommands = ["addAccount","deleteAccount","getAccountName","getAccountHash","getAccounts"]	
	def __init__(self,PyCCManager):
		'''initially get all '''
		Plugin.Plugin.__init__(self,PyCCManager)
		self.contacts = []
		f = open(".contacts")
		append = self.contacts.append
		for line in f.readlines():
			append((line.strip().split(":")[0],line.strip().split(":")[1]))		

	def recvCommand(self,package):
		''' Processes the given Command'''
		command = package.command
		arg = package.data
		if command == "addAccount":
			self.addAccount(arg)
		elif command == "deleteAccount":
			self.deleteAccount(arg)
		elif command == "getAccountName":
			self.getAccountName(arg,package)
		elif command == "getAccountHash":
			self.getAccountHash(arg,package)
		elif command == "getAccounts":
			self.getAccounts(package)
	
	def addAccount(self,data):
		'''Adds a new contact to the contact storage
		Takes an argument with the form Hash:Name'''		
		accountHash, accountName = data.split(":")		
		self.contacts.append((accountHash,accountName))
		
	def deleteAccount(self,data):
		'''Deletes a specific account by Name'''		
		try:		
			self.contacts.remove((data, returnAccountHash(data)))
		except ValueError:			
			pass

	def getAccountName(self,accountHash,package):
		'''Get a specific accountName'''
		for contact in self.contacts:
			if contact[0]==accountHash:
				package.data = contact[1]				
				package.connection.sendResponse(package)	

	def getAccountHash(self, accountName, package):
		'''Get a specific accountHash'''
		for contact in self.contacts:
			if contact[1]==accountName:
				package.data = contact[0]				
				print("eior")
				package.connection.sendResponse(package)	#fixthat

	def returnAccountHash(self,accountName):
		'''Get a specific accountHash'''
		for contact in contacts:
			if contact[1]==accountName:
				return contact[0]
		raise KeyError

	def getAccounts(self,package):
		'''Get all of the accounts, comma seperated accountHash:accountName pairs are returned'''		
		string=""		
		for contact in self.contacts:
			string=string+contact[0]+":"+contact[1]+","
		package.data=string[:-1]
		package.connection.sendResponse(package)

	def shutdown(self):
		f=open(".contacts","w")
		for contact in self.contacts:		
			f.write(contact[0]+":"+contact[1]+"\n")
