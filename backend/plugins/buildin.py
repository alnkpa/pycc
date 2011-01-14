import backend.plugins.general

class ShutdownPlugin(backend.plugins.general.Plugin):
		def command_shutdown(self,interface,message):
				print(message)
