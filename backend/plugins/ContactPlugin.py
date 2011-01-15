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

	def recvcommand(self,package):
		''' Processes the given Command'''
		if package.command=="addAccount":
			self.addAccount(data)
		elif package.command=="deleteAccount":
			self.deleteAccount(data)
		elif package.command=="getAccountName":
			self.getAccountName(package.data,package)
		elif	package.command=="getAccountHash":
			self.getAccountHash(package.data,package)
		elif package.command=="getAccounts":
			self.getAccounts(package)
	
	def addAccount(self,data):
		'''Adds a new contact to the contact storage'''		
		accountHash, accountName = data.split(":")		
		contacts.append((accountHash,accountName))
		
	def deleteAccount(self,data):
		'''Deletes a specific account by Name'''		
		try:		
			self.contacts.remove((data, returnAccountHash(data)))
		except ValueError:			
			pass

	def getAccountName(self,accountHash):
		'''Get a specific accountName'''
		for contact in self.contacts:
			if contact[0]==accountHash:
				package.data = contact[1]				
				sendcommand(package) 	#fixthat	

	def getAccountHash(self,accountName):
		'''Get a specific accontHash'''
		for contact in contacts:
			if contact[1]==accountName:
				package.data = contact[0]				
				sendcommand(package)	#fixthat

	def returnAccountHash(self,accountName):
		'''Get a specific accontHash'''
		for contact in contacts:
			if contact[1]==accountName:
				return contact[0]

	def getAccounts(package):
		'''Get all of the accounts, comma seperated accountHash:accountName pairs are returned'''		
		string=""		
		for contact in self.contacts:
			string=string+contact[0]+":"+contact[1]
		package.data=string
		sendcommand(package)

	def shutdown(self):
		f=open(".contacts","w")
		for contact in self.contacts:		
			f.write(contact[0]+":"+contact[1])
