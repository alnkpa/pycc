import backend.plugins.Plugin

# fix: comment this module

class ShutdownPlugin(backend.plugins.Plugin.Plugin):
		def command_shutdown(self,interface,message):
				print(message)
