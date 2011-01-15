class Plugin(object):
	'''This class defines all Plugins
	
	It defines some methods, that all plugins need and use
	Any plugin will be derived from this class'''
	#names under which the plugins wants to be registered
	registeredName=[]
	priority=0
	
	#any plugin will be bound to a backend at its initialisation
	def __init__(self, backend):
		self.backend = backend

	#This class sends a command to the backend
	def sendCommand(self, data):
		self.backend.send(data)

	#Any command send from the backend will be here
	def recvCommand(self, data):
		pass

	#tell the register that you want be registered with it
	def registerInBackend(self):
		for name in self.registeredName:
			self.backend.registerPlugin(name, self, self.priority)
