import Plugin

class ChatLogPlugin(Plugin.EasyPlugin):
	'''is used to temporarily log messages send and received'''
	
	
	def init(self):
		log = []
#		# search for the running contactPlugin
#		contactPlugin = self.PyCCManager.searchPlugin("ContactPlugin")
#		accounts = contactPlugin.commandR_getAccounts("spamAndEggs").split(",")
#		# 
#		for i in range(0,len(accounts)):
#			accounts[i] = [accounts[i].split(":")[0]]

	def commandAU_logSendMessage(self, package, username):
		'''will log a send Message'''
		i = self.isUserLogged(username)
		try:
			if i:
				log[i].append("send "+package.data)
			else:
				log.append([username,  "send "+package.data])
		except:
			log[0] = [username, "send "+package.data]

	def commandAU_logRecvMessage(self, package, username):
		'''will log a received Message'''
		i = self.isUserLogged(username)
		try:
			if i:
				log[i].append("recv "+package.data)
			else:
				log.append([username,  "recv "+package.data])
		except:
			log[0] = [username, "recv "+package.data]

	def commandAR_showLogFor(self, package, username):
		i = self.isUserLogged(username)
		try:
			if i:
				return log[i]
			else:
				return None
		except:
				return None

	def isUserLogged(self, username):
		for i in range(0,len(log)):
			if log[i][0] == username:
				return i
		return False
