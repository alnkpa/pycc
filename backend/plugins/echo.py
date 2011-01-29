import Plugin
import connection

class EchoPlugin(Plugin.EasyPlugin):
	'''This Plugin responds to the sender with received package'''

	def command_echo(self, package):
		''' echo the package '''
		package.connection.sendResponse(package)

	def command_echoToFrontend(self, package):
		''' echo this package to the frondends'''
		for connection in self.backend.getNodeConnections(":frontend"):
			connection.sendResponse(package)
