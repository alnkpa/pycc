import Plugin
import pickle
import Broadcast
import time

class ChatLogPlugin(Plugin.EasyPlugin):
	'''is used to temporarily log messages send and received
	writes to "chatlog" if closed and reads from it if initialized
	
	implements the following methods:
		-	logSendMessage:	takes "username" as an argument and the message in
							package.data
							"username" should be the user, the message was send
							to
		-	logRecvMessage:	takes "username" as an argument and the message in
							package.data
							"username" should be the user, the message was received
							to'''
	
	
	def init(self):
		try:
			with open("chatlog", "rb") as logfile:
				# unpickles the logfile so that logs from former chats will be
				# saved too
				self.log = pickle.load(logfile)
		except (pickle.PickleError, EOFError, IOError):
			self.log = []

	def commandAU_logSendMessage(self, package, username):
		'''will log a send Message'''
		# get index of user in log
		i = self.isUserLogged(username)
		# if user is already logged
		if i is not None:
			# save the message in the regarding sublist
			self.log[i].append("send "+str(time.time())+" "+package.data)
		# if not
		else:
			# make a new sublist
			self.log.append([username, "send "+str(time.time())+" "+package.data])

	# for commands see above
	def commandAU_logRecvMessage(self, package, username):
		'''will log a received Message'''
		i = self.isUserLogged(username)
		if i is not None:
			self.log[i].append("recv "+str(time.time())+" "+package.data)
		else:
			self.log.append([username,  "recv "+str(time.time())+" "+package.data])

	def commandAR_showLogFor(self, package, username):
		'''returns an log for a specific user with newlines "\n" escaped
		use Broadcast.Broadcast.unescape to unescape the message
		any real newline indicates a new message'''
		i = self.isUserLogged(username)
		if i is not None:
			stringtoreturn = ""
			for message in self.log[i][1:]:
				stringtoreturn += Broadcast.Broadcast.escape(message) + "\n"
			return stringtoreturn
		else:
			return None

	def isUserLogged(self, username):
		for i in range(0,len(self.log)):
			if self.log[i][0] == username:
				return i
		return None
		
	def shutdown(self):
		with open("chatlog", "wb") as logfile:
			pickle.dump(self.log, logfile, pickle.HIGHEST_PROTOCOL)
