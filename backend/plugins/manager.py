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

	def clientConnectionOpened(self,client):
		''' method is called directly after a new connection to the server was opened
		    client: client connection (PyCCConnection)'''
		pass

	def clientConnectionClosed(self,client):
		''' method is called directly after a client connection has been closed
		    client: client connection (PyCCConnection)'''
		pass

	def handleCommand(self,client,comHandle,command,data):
		''' method is called for handle a command request
		    clientSocket: client connection (PyCCConnection)
		    comHandle: identifier of the corresponding request
		    command: command name
		    data: message of command'''
		pass
