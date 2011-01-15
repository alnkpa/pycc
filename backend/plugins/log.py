import Plugin

class LogPlugin(Plugin.Plugin):
	registeredName=""
	priority=5

	def startup(self):
	    self.file=open('logs/backend.log','a')

	def shutdown(self):
		self.file.close()

	def recvCommand(self, conElement):
		self.file.write("{0}\n".format(str(conElement)))
		self.file.flush()
		return 'continue'
