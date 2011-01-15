class Plugin(object):
	'''This class defines all Plugins
	
	It defines some methods, that all plugins need and use
	Any plugin will be derived from this class'''
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
		if self.name is not None:
			self.PyCCManager.registerPlugin(self.registeredName, \
						self, self.priority)

	def shutdown(self):
		pass
