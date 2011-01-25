import configparser
import os.path
import shutil
import hashlib
import datetime

class PyCCBackendConfig():
	''' wrapper class to deliver configurations to a storage
	    currently the settings are save in simple ini files'''
	defaultconfigfile = 'config/defaultserver.cfg'
	configfile = 'config/server.cfg'

	def __init__(self):
		self.config = configparser.ConfigParser() # ini-parser
		# no local config ? -> copy default config
		if not os.path.isfile(PyCCBackendConfig.configfile):
			shutil.copyfile(PyCCBackendConfig.defaultconfigfile,
				PyCCBackendConfig.configfile)
		# read config file
		self.config.read(PyCCBackendConfig.configfile)

	def getstr(self, section, value, default=None):
		'''  return a string config value'''
		return self.config.get(section,value)

	def getint(self,section,value,default=None):
		''' return int config value '''
		return self.config.getint(section,value)

	def getNodeId(self):
		''' return the backend node id'''
		try:
			return self.getstr('network','id')
		except configparser.NoOptionError: # no node id yet
			# generate node id
			backendID = hashlib.sha1("{0}\n{1}".format(datetime.datetime.now(),
				str(os.environ)).encode('utf8')).hexdigest()
			# save node id
			self.config.set('network','id',backendID)
			with open(PyCCBackendConfig.configfile,'w') as f:
				self.config.write(f)
			return backendID


class PyCCPluginConfig():
	''' plugin specific config
	    data are mapped to server configuration [PyCCBackendConfig]'''
	def __init__(self, backendConfig, pluginName):
		self._config = backendConfig
		self._pluginName = pluginName

	def getstr(self,value,section='',default=None):
		'''  return a string config value'''
		return self._config.getstr('Plugin:{0}{1}'.format(self._pluginName,section),value)

	def getint(self,section,value,default=None):
		''' return int config value '''
		return self._config.getint('Plugin:{0}{1}'.format(self._pluginName,section),value)
