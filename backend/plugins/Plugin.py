class Plugin(object):
	registeredName=[]
	priority=0
	def __init__(self, backend):
		self.backend = backend

	def sendCommand(self, data):
		self.backend.send(data)

	def recvCommand(self, data):
		pass

	def registerInBackend(self):
		for name in self.registeredName:
			self.backend.registerPlugin(name, self, self.priority)
