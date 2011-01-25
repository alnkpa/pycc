import Plugin
import connection

class EchoPlugin(Plugin.Plugin):
	'''This Plugin responds to the sender with received package'''
	registeredCommands="echo"
	priority=5

	def recvCommand(self, package):
		if package.type != connection.PyCCPackage.TYPE_REQUEST:
			return
		package.connection.sendResponse(package)
