class PyCCBackendPluginManager(object):
	''' class for manage the backend plugins
	    it connects the backend with the plugins'''

	def __init__(self,server):
		self.server=server

	def startup(self):
		''' method is called directly after the server has started up'''
		pass

	def shutdown(self):
		''' method is called directly before the server will stuting down'''
		pass

	def clientConnectionOpened(self,clientSocket):
		''' method is called directly after a new connection to the server was opened
		    clientSocket: client connection (PyCCConnection)'''
		pass

	def clientConnectionClosed(self,clientSocket):
		''' method is called directly after a client connection has been closed
		    clientSocket: client connection (PyCCConnection)'''
		pass

	def handleCommand(self,clientSocket,comHandle,command,message):
		''' method is called for handle a command request
		    clientSocket: client connection (PyCCConnection)
		    comHandle: identifier of the corresponding request
		    command: command name
		    message: message of command'''
		pass
