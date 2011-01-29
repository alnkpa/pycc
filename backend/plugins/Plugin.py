class Plugin(object):
	'''This class is the base of all Plugins
	
	It defines methods that all plugins need and use
	Every plugin will be derived from this class

PluginClass.registeredName 
	is the string all commands for the plugin start with.
PluginClass.priority 
	is the priority relative to other plugins.
	PluginClass.recvCommand is called first for Plugins with 
	higher priority.

	Warning: please do not overwrite __init__ use init instead
'''
	#names under which the plugins wants to be registered
	registeredCommands=None
	priority=0


	#any plugin will be bound to a PyCCManager at its initialisation
	def __init__(self, manager, backend, config):
		'''all Plugins are initialized with a manager class'''
		self.backend = backend
		self.manager = manager
		self.PyCCManager = manager
		self.config = config


	def init(self):
		'''this is called once to initialize the plugin'''
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

class EasyPlugin(Plugin): # fix: how can I tell the sender of the command that
							# an error occurred
	'''This class is an advanced Plugin class for easier plugins

	Every command<Flags>_* will used as a registered command;
		first argument is the package
	supported flags:
		A: parsed command attributes
			command data of package is split into command + args
			(spaces separated)
			new package.command is the 0. argument
			other args are used as python args
			if the argument count is wrong a error is send to
			the client.
		R: return data are send as response
			if the method return a string or binary data
			a response package with this data is send.
			(other attributes were not changed)
		U: data must be utf8
			the data have to be utf8 string, no binary data
			possible.
			the data is automatically converted to utf8
			a convert error is send as error to the client

	Warning: our recvCommand must not be replaced!
'''

	#any plugin will be bound to a PyCCManager at its initialisation
	def __init__(self, manager, backend, config):
		'''all Plugins are initialized with a manager class'''
		Plugin.__init__(self, manager, backend, config)
		self._simplePlugin_commands = {}

	#tell the register that you want be registered with it
	def registerInManager(self):
		'''register command in the manager

this method should not be overwritten'''
		if type(self) == EasyPlugin: # don't register yourself
			return

		for element in dir(self): # search methods
			if not element.startswith('command'): # command-method?
				continue
			command, name = element.split('_',1)
			command = list(command[7:]) # get attributes
			self.manager.registerPlugin(name, self, self.priority)
			self._simplePlugin_commands[name] = (element, command)


	#Any command send from the PyCCManager will be here
	def recvCommand(self, package):
		'''all commands for this plugin are passed to this function

package is of type backend.connection.PyCCPackage
'''
		for command in self._simplePlugin_commands:
			if package.command.startswith(command):
				call, flags =self._simplePlugin_commands[command]
				if 'U' in flags: # data must be unicode
					try:
						package.data = package.data.decode('utf8')
					except UnicodeError:
						package.data = 'data have to be utf8'
						package.connection.sendError(package)
				if 'A' in flags: # parse attributes
					callargs = [package]
					args = package.command.split(' ')
					package.command = args[0]
					callargs = [package] + args[1:]
					try:
						result=getattr(self,call)(*callargs)
					except TypeError: # wrong arguments
						package.data = 'wrong arguments'
						package.connection.sendError(package)
				else:
					result=getattr(self,call)(package)
				if 'R' in flags:
					if type(result) is str or type(result) is bytearray:
						package.data = result
						package.connection.sendResponse(package)
			break





class PyCCPluginToBackendInterface(object):
	''' interface between plugin and the backend (e.g. server)
		plugin could access this class with self.backend'''
	
	def __init__(self,manager,server):
		''' init interface'''
		self._manager = manager
		self._server = server

	def getNodeIdForUser(self):
		'''planned'''
		pass

	def openConnection(self, host, port=62533):
		'''connect to a specifical host (server or other chat client backend)'''
		self._server.openConnection(host,port)

	def getNodeConnections(self,nodeId):
		''' iterate over all connection to a special node
			if there is no connection to this node, a new connection
			is automatically established.'''
		for connection in self._server.getConnectionList(nodeId):
			yield connection

	def getNodeId(self):
		''' return node id of currrent backend'''
		return self._server.getNodeId()
