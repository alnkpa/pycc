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
	registeredName=None
	priority=0
	
	#any plugin will be bound to a PyCCManager at its initialisation
	def __init__(self, PyCCManager):
		self.PyCCManager = PyCCManager

	#This class sends a command to the PyCCManager
	def sendCommand(self, command, data):
		self.PyCCManager.send(command, data)

	#Any command send from the PyCCManager will be here
	def recvCommand(self, con):
		pass

	#tell the register that you want be registered with it
	def registerInManager(self):
		name= self.registeredName
		if name is not None:
			self.PyCCManager.registerPlugin(name, self,\
							self.priority)

	def startup(self):
		pass

	def shutdown(self):
		pass
