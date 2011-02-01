import configparser
import os.path
import shutil
import hashlib
import datetime

class PyCCBackendConfig():
	''' wrapper class to deliver configurations to a storage
	    currently the settings are save in simple ini files
	    see configparser modul documentation for more info'''
	defaultconfigfile = 'config/defaultserver.cfg'
	configfile = 'config/server.cfg'

	def __init__(self):
		''' read configuration from hard disk'''
		self.config = configparser.ConfigParser() # ini-parser
		# no local config ? -> copy default config
		if not os.path.isfile(PyCCBackendConfig.configfile):
			shutil.copyfile(PyCCBackendConfig.defaultconfigfile,
				PyCCBackendConfig.configfile)
		# read config file
		self.config.read(PyCCBackendConfig.configfile)

	def saveToDisk(self):
		''' save configuration to hard disk'''
		with open(PyCCBackendConfig.configfile,'w') as f:
			self.config.write(f)

	def get(self, section, option):
		'''  return a config value'''
		return self.config.get(section, option)

	def set(self, section, option, value):
		''' set a config value'''
		if not self.config.has_section(section):
			self.config.add_section(section)
		self.config.set(section, option, value)
		self.saveToDisk()

	def getstr(self, section, option):
		'''  return a string config value'''
		return self.config.get(section,option)

	def getint(self,section,option):
		''' return int config value '''
		return self.config.getint(section,option)

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
			self.saveToDisk()
			return backendID

	def sections(self):
		''' return a list with all available sections'''
		try:
			return self.config.sections()
		except configparser.NoSectionError:
			return []

	def options(self, section):
		''' return a list with all available option names of a specific section'''
		try:
			return self.config.options(section)
		except configparser.NoSectionError: # section does not yet exists
			return []

class PyCCPluginConfig():
	''' plugin specific config
	    data are mapped to server configuration [PyCCBackendConfig]'''

	__slots__ = ('_config', '_pluginName', '_sectionPrefix')

	def __init__(self, backendConfig, pluginName):
		self._config = backendConfig
		self._pluginName = pluginName
		self._sectionPrefix = 'Plugin:{0}'.format(self._pluginName)

	def get(self, option, section=None):
		'''  return a string config value'''
		return self.getstr(option, section)

	def getstr(self, option, section=None):
		'''  return a string config value'''
		if section is None:
			return self._config.getstr(self._sectionPrefix, option)
		else:
			return self._config.getstr(self._sectionPrefix + '-' + section, option)

	def getint(self, option, section=None):
		''' return int config value '''
		if section is None:
			return self._config.getint(self._sectionPrefix, option)
		else:
			return self._config.getint(self._sectionPrefix + '-' + section, option)

	def set(self, option, value, section=None):
		''' set a config value'''
		if section is None:
			return self._config.set(self._sectionPrefix, option, value)
		else:
			return self._config.set(self._sectionPrefix + '-' + section, option, value)

	def sections(self):
		''' return a list with all available sections'''
		sections = []
		for section in self._config.sections():
			if section.startswith(self._sectionPrefix):
				sections.append(section[len(self._sectionPrefix)+1:])
		return sections

	def options(self, section=None):
		''' return a list with all available option names of a specific section'''
		if section is None:
			return self._config.options(self._sectionPrefix)
		else:
			return self._config.options(self._sectionPrefix + '-' + section)
