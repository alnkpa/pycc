import Plugin
import ContactPlugin

class ChatPlugin(Plugin.EasyPlugin):
	'''is used to send messages to other users
		use sendMessage to send a message to a specified user
		use recvMessage to send a message to the user of this plugin
		'''

	def commandAU_sendMessage(self, package, command, argument):
		name = argument
		message = package.data
		try:
			contactPlugin = self.PyCCManager.searchPlugin("ContactPlugin")
			try:
				accountNodeId = contactPlugin.returnNodeId(name)
				package.command = "recvMessage"
				for connection in self.backend.getNodeConnections(accountNodeId):
					connecticon.sendRequest(package)
			except ValueError:
				package.type = "E"
				package.data = "No such accountname"
				package.connection.sendErrors(package)
		except KeyError:
			package.type = "E"
			package.data = "ContactPlugin not found"
			package.connection.sendErrors(package)
	
	def command_recvMessage(self, package):
		nodeId = package.connection.partnerNodeId
		try:
			contactPlugin = self.PyCCManager.searchPlugin("ContactPlugin")
			try:
				accountName = contactPlugin.returnUserName(nodeId)
			except ValueError:
				package.type = "E"
				package.data = "No such nodeId"
				package.connection.sendErrors(package)
		except KeyError:
			package.type = "E"
			package.data = "ContactPlugin not found"
			package.connection.sendErrors(package)
		for connection in self.backend.getNodeConnections(":frontend"):
			package.command = "newMessage " + accountName
			connection.sendRequest(package)