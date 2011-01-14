import configparser

class PyCCBackendConfig():
		def __init__(self):
				self.config=configparser.ConfigParser()
				self.config.read('config/server.cfg')

		def getstr(self,section,value,default=None):
				return self.config.get(section,value)

		def getint(self,section,value,default=None):
				return self.config.getint(section,value)
