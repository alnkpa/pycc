import Plugin
import connection

class EchoPlugin(Plugin.Plugin):
	registeredCommands="echo"
	priority=5

	def recvCommand(self, package):
		if package.type != connection.PyCCPackage.TYPE_REQUEST:
			return
		package.connection.sendResponse(package)
