import configparser
import os.path
import shutil
import hashlib
import datetime

class PyCCBackendConfig():
	defaultconfigfile='config/defaultserver.cfg'
	configfile='config/server.cfg'

	def __init__(self):
		self.config=configparser.ConfigParser()
		if not os.path.isfile(PyCCBackendConfig.configfile):
			shutil.copyfile(PyCCBackendConfig.defaultconfigfile,
				PyCCBackendConfig.configfile)
		self.config.read(PyCCBackendConfig.configfile)

	def getstr(self,section,value,default=None):
			return self.config.get(section,value)

	def getint(self,section,value,default=None):
			return self.config.getint(section,value)

	def getNodeId(self):
		try:
			return self.getstr('network','id')
		except configparser.NoOptionError:
			backendID=hashlib.sha1("{0}\n{1}".format(datetime.datetime.now(),
				str(os.environ)).encode('utf8')).hexdigest()
			self.config.set('network','id',backendID)
			with open(PyCCBackendConfig.configfile,'w') as f:
				self.config.write(f)
			return backendID

class PyCCPluginConfig():

	def __init__(self,backendConfig, pluginName):
		self._config = backendConfig
		self._pluginName = pluginName

	def getstr(self,value,section='',default=None):
		return self._config.getstr('Plugin:{0}{1}'.format(self._pluginName,section),value)

	def getint(self,section,value,default=None):
		return self._config.getint('Plugin:{0}{1}'.format(self._pluginName,section),value)
