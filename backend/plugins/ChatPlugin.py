import Plugin
import ContactPlugin

class ChatPlugin(Plugin.EasyPlugin):
	'''is used to send messages to other users
		use sendMessage to send a message to a specified user
		use recvMessage to send a message to the user of this plugin
		'''

	def commandAU_sendMessage(self, package, name):
		'''A command called when a message should be send to a user
			command is structured like the following: "sendMessage <username>"
			message to be send should be in package.data
			'''
		# package.data should be the message
		message = package.data
		try:
			# search for the running contactPlugin
			contactPlugin = self.PyCCManager.searchPlugin("ContactPlugin")
			chatLogPlugin = self.PyCCManager.searchPlugin("ChatLogPlugin")
			try:
				# search for the relevant nodeId
				accountNodeId = contactPlugin.returnNodeId(name)
				chatLogPlugin.commandAU_logSendMessage(package,  name)
				# change the command so the other backend will know it belongs to it
				package.command = "recvMessage"
				# send the message to every connection belonging to the nodeId
				for connection in self.backend.getNodeConnections(accountNodeId):
					connection.sendRequest(package)
			# just some error handling
			except ValueError:
				package.type = "E"
				package.data = "No such accountname"
				package.connection.sendError(package)
		except KeyError:
			package.type = "E"
			package.data = "relevant Plugins not found"
			package.connection.sendError(package)
	
	def command_recvMessage(self, package):
		'''A command called when a new message arrives
			message to be received is in package.data
			'''
		nodeId = package.connection.partnerNodeId
		try:
			# search for the running contactPlugin
			contactPlugin = self.PyCCManager.searchPlugin("ContactPlugin")
			chatLogPlugin = self.PyCCManager.searchPlugin("ChatLogPlugin")
			try:
				# search for the relevant username
				accountName = contactPlugin.returnUserName(nodeId)
				chatLogPlugin.commandAU_logRecvMessage(package, accountName)
				# forward message to every frontend
				for connection in self.backend.getNodeConnections(":frontend"):
					package.command = "newMessage " + accountName
					connection.sendRequest(package)
			# error handling
			except ValueError:
				package.type = "E"
				package.data = "No such nodeId"
				package.connection.sendError(package)
		except KeyError:
			package.type = "E"
			package.data = "ContactPlugin not found"
			package.connection.sendError(package)
