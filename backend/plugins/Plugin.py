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
	def __init__(self, PyCCManager):
		'''all Plugins are initialized with a manager class'''
		self.PyCCManager = PyCCManager

	#This method sends a command to the PyCCManager
	def sendCommand(self, command, data):
		'''send a command to the PyCCManager - not yet ready for use'''
		self.PyCCManager.send(command, data)

	#Any command send from the PyCCManager will be here
	def recvCommand(self, con):
		'''all commands for this plugin are passed to this function

con is of type backend.connection.PyCCPackage
'''
		pass

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
		else:
			raise ValueError('invalid value for attribute registeredCommands {0}'.format(comm))

	def startup(self):
		pass

	def shutdown(self):
		'''this method shuts down the Plugin

It is called after all commands are handled.
The Plugin will not be used afterwards.
'''
		pass
