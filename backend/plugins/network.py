import Plugin
import connection


# fix: document this module

class ConnectionPlugin(Plugin.EasyPlugin):
	'''The class implemented the network management and routing for pycc
	'''
	def init(self):
		self.server = self.manager.server

	def commandR_getNodeId(self, package):
		''' return the node id of the current backend'''
		return self.server.getNodeId()

	def commandR_status(self, package):
		'''reply with the status of the server'''
		return self.server.status()

	def commandA_connectTo(self, package, host, port=62533):
		''''''
		if self.backend.openConnection(host,int(port)):
			# fix: what do true und false mean?
			return True
		else:
			return False

	def commandA_relay(self, package, node): # command with argument parsing
		args=package.command.split(' ')
		if len(args)!=2:
			return None
		else:
			for con in self.backend.getNodeConnections(args[1]):
				data = package.data.decode('utf8').split('\n')
				newPackage = connection.PyCCPackage()
				newPackage.command = data[0]
				newPackage.data = "\n".join(data[1:])
				con.sendRequest(newPackage,callback = self.handleResponse,
					callbackExtraArg = package)

	def handleResponse(self, newPackage, orgPackage = None):
		newPackage.handle = orgPackage.handle
		newPackage.command = orgPackage.command
		orgPackage.connection.sendPackage(newPackage)
		return None
