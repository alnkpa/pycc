import backend.plugins.Plugin

class ShutdownPlugin(backend.plugins.Plugin.Plugin):
		def command_shutdown(self,interface,message):
				print(message)
