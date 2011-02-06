import Plugin
import pickle

class ChatLogPlugin(Plugin.EasyPlugin):
	'''is used to temporarily log messages send and received'''
	
	
	def init(self):
		try:
			with open("chatlog", "rb") as logfile:
				# unpickles the logfile so that logs from former chats will be
				# saved to
				self.log = pickle.load(logfile)
		except:
			self.log = []

	def commandAU_logSendMessage(self, package, username):
		'''will log a send Message'''
		i = self.isUserLogged(username)
		try:
			if i:
				self.log[i].append("send "+package.data)
			else:
				self.log.append([username, "send "+package.data])
		except:
			self.log[0] = [username, "send "+package.data]

	def commandAU_logRecvMessage(self, package, username):
		'''will log a received Message'''
		i = self.isUserLogged(username)
		try:
			if i:
				self.log[i].append("recv "+package.data)
			else:
				self.log.append([username,  "recv "+package.data])
		except:
			self.log[0] = [username, "recv "+package.data]

	def commandAR_showLogFor(self, package, username):
		i = self.isUserLogged(username)
		try:
			if i:
				for message in self.log[i]:
					stringtoreturn += message + "\n"
				return stringtoreturn
			else:
				return None
		except:
				return None

	def isUserLogged(self, username):
		for i in range(0,len(self.log)):
			if self.log[i][0] == username:
				return i
		return False
		
	def shutdown(self):
		with open("chatlog", "wb") as logfile:
			pickle.dump(self.log, logfile, pickle.HIGHEST_PROTOCOL)
