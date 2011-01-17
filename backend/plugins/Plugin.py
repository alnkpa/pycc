class Plugin(object):
	'''This class is tge base of all Plugins
	
	It defines methods that all plugins need and use
	Every plugin will be derived from this class

PluginClass.registerdName 
	is the string all commands for the plugin start with.
PluginClass.priority 
	is the priority relative to other plugins.
	PluginClass.recvCommand is called first for Plugins with 
	higher priority.
'''
	#names under which the plugins wants to be registered
	registeredCommands=None
	priority=0


	#any plugin will be bound to a PyCCManager at its initialisation
	def __init__(self, manager, backend, config):
		'''all Plugins are initialized with a manager class'''
		self.backend = backend
		self.PyCCManager = manager
		self.config = config


	def init(self):
		'''this is called once after the plugin is initialized'''
		pass


	#This method sends a command to the PyCCManager
	def sendCommand(self, command, data):
		'''send a command to the PyCCManager - not yet ready for use'''
		self.PyCCManager.send(command, data)

	#Any command send from the PyCCManager will be here
	def recvCommand(self, con):
		'''all commands for this plugin are passed to this function

con is of type backend.connection.PyCCPackage
'''
		raise NotImplementedError('if you see this you forgot to implement \
recvComment(self, con) in your Plugin.')

	#tell the register that you want be registered with it
	def registerInManager(self):
		'''register this Plugin in the manager

this method should not be overwritten'''
		comm= self.registeredCommands
		if type(comm) is str:
			self.PyCCManager.registerPlugin(comm, self,\
							self.priority)
		elif hasattr(comm, '__iter__'):
			reg = self.PyCCManager.registerPlugin
			for comm in comm:
				reg(comm, self, self.priority)
		elif comm is None:
			pass		
		else:
			raise ValueError('invalid value for attribute registeredCommands {0}'.format(comm))

	def startup(self):
		'''this is called for each command registered
when the manager starts up'''
		pass

	def shutdown(self):
		'''this method shuts down the Plugin

It is called after all commands are handled.
The Plugin will not be used afterwards.
'''
		pass


class PyCCPluginToBackendInterface(object):
	
	def __init__(self,manager,server):
		self._manager = manager
		self._server = server

	def getNodeIdForUser(self):
		pass

	def getNodeConnections(self,nodeId):
		for connection in self._server.getConnectionList(nodeId):
			yield connection

	def getNodeId(self):
		return self._server.getNodeId()
