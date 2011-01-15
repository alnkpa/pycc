import Plugin

class ContactPlugin(Plugin):
	''' Manages all the Contacts '''
	def __init__
		'''initially get all '''
		self.contacts = []
		f = open(".contacts")
		for line in f.readlines()
			contacts.append((line.strip().split(":")[0],line.strip().split(":")[1]))		

	def recvcommand(self,package)	
		''' Processes the given Command'''
		if package.command=="addAccount":
			self.addAccount(data):
		elif package.command=="deleteAccount":
			self.deleteAccount(data):
		elif package.command=="getAccount"
			self.getAccountName(package.data,package):
		elif package.command="getAccounts":
			self.getAccounts(package)
	
	def addAccount(self,data):
		'''Adds a new contact to the contact storage'''
		accountHash, accountName = data.split(":")		
		contacts.append[(accountHash,accountName)]
		
	def deleteAccount(self,data):
		'''Deletes a specific account by Name'''		
		contacts.remove((data, returnAccountHash(data)))
		
	def getAccountName(self,accountHash):
		'''Get a specific accountName'''
		for contact in contacts:
			if contact[0]==accountHash:
				package.data = contact[1]				
				sendcommand(package)	

	def getAccountHash(self,accountName):
		'''Get a specific accontHash'''
		for contact in contacts:
			if contact[1]==accountName:
				package.data = contact[0]				
				sendcommand(package)

	def returnAccountHash(self,accountName):
		'''Get a specific accontHash'''
		for contact in contacts:
			if contact[1]==accountName:
				return contact[0]

	def getAccounts(package)
		'''Get all of the accounts, comma seperated accountHash:accountName pairs are returned'''		
		string=""		
		for contact in contacts:
			string=string+contact[0],contact[1]
		package.data=string
		sendcommand(package)
