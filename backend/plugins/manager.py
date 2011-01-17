#!/usr/bin/env python3
'''Plugin loader module

'''
import sys
import os
import traceback

import Plugin

try:
	import config
except ImportError:
	sys.path.append('..')
	try:
		import config
	finally:
		try:
			sys.path.remove('..')
		except ValueError:
			pass

#PLUGIN_BASE_MODULE_NAME is the Plugin module of which all Plugins inherit
PLUGIN_BASE_MODULE_NAME = 'Plugin'
PLUGIN_BASE_CLASS_NAME = 'Plugin'

CONTINUE= 'continue'

def getPluginClasses():
	'''load and return a list of all Plugin derivates in the local modules'''
	# the module name   "package.package. ... .name"	so only show the packages
	package = '.'.join(__name__.split('.')[:-1])
	# directory of this file
	dirPath = os.path.dirname(__file__) 
	if not dirPath:
		dirPath= '.'
	if package:
		# might be nonlocal import, from another Plugin
		# 'package.package.'
		package += '.'
	# get the plugin class
	pluginModuleName = package + PLUGIN_BASE_MODULE_NAME
	# enable simple import in Plugins as possible during tests
	sys.path.append(dirPath)
	try:
		module = __import__(pluginModuleName)
		Plugin = getattr(module, PLUGIN_BASE_CLASS_NAME)
		assert isinstance(Plugin, type), "the Plugin base class should be a class"
		# fileList of the local directory
		fileList= os.listdir(dirPath)
		# load the plugins in order
		fileList.sort()
		# list of the Plugin classes - classes derived from Plugin
		pluginClasses= []
		for pModuleFile in fileList:
			# split .py or .pyc from file name
			modName, ext= os.path.splitext(pModuleFile)
			if modName.startswith('_') or ext not in(".py",".pyw"):
				# do not load _modules
				continue
			try:
				# try importing
				module= __import__(package+modName)
			except ImportError:
				continue
			attributes = dir(module)
			# search for Plugin classes
			for attr in attributes:
				if attr.startswith('_'):
					# variables starting with _ shall not be considered
					continue
				try:
					cls= getattr(module, attr)
				except AttributeError:
					# should not occour
					continue
				# 1. find classes
				# 2. issubclass only on classes -> find Plugin derivates
				# 3. assure we do not load plugins twice
				if isinstance(cls, type) and \
				   issubclass(cls, Plugin) and\
				   cls not in pluginClasses:
					pluginClasses.append(cls)
	finally:
		try:
			sys.path.remove(dirPath)
		except ValueError:
			# already removed
			pass
	return pluginClasses
	
class PyCCBackendPluginManager(object):
	''' class for manage the backend plugins
		it connects the backend with the plugins'''

	def __init__(self, server, config):
		self.server=server
		self.config=config
		self.plugins = [] # (command, plugin, priority)

	def loadPlugins(self):
		'''this method loads all Plugins from the directory'''
		self.plugins = []
		PClasses=getPluginClasses()
		for pluginClass in PClasses:
			try:
				p=pluginClass(self,
					Plugin.PyCCPluginToBackendInterface(self,self.server),
					config.PyCCPluginConfig(self.config,pluginClass.__name__))
				p.init()
				p.registerInManager()
			except Exception as e:
				traceback.print_exception(*sys.exc_info())
				print('Could not load plugin {0}:\n{1}: {2}'.format(pluginClass.__name__,type(e).__name__,str(e)),file=sys.stderr)


	def registerPlugin(self, command, plugin, priority):
		'''register a plugin under a given command with a priority

plugins with higher pliority get the packets first
'''
		self.plugins.append((command, plugin, priority))
		self.plugins.sort(key=lambda t: t[2])

	def startup(self):
		''' method is called directly after the server has started up'''
		self.loadPlugins()
		for plu in self.plugins:
			plu[1].startup()
			
	def searchPlugin(self, name):
		'''search for the plugin with the class name <name>'''
		for plu in self.plugins:
			if type(plu[1]).__name__ == name:
				return plu[1]
		raise KeyError

	def shutdown(self):
		''' method is called directly before the server will stuting down'''
		for plu in self.plugins:
			plu[1].shutdown()

	def clientConnectionOpened(self,client):
		''' method is called directly after a new connection to the server was opened
			client: client connection (PyCCConnection)'''
		pass

	def clientConnectionClosed(self,client):
		''' method is called directly after a client connection has been closed
			client: client connection (PyCCConnection)'''
		pass

	def handleCommand(self, conPackage):
		''' method is called for handleing a command request
			conPackage: connection element (PyCCPackage)'''
		for plugin in self.plugins:
			if conPackage.command.startswith(plugin[0]):
				v= plugin[1].recvCommand(conPackage)
				if v != CONTINUE:
					break

	def getCommandList(self):
		'''for debug return a list of command, plugin'''
		return [(p[0], p[1].__name__) for p in self.plugins]

__all__ = ['getPluginClasses', 'PyCCBackendPluginManager', 'CONTINUE']

if __name__ == '__main__':
	# test module

	# test getPluginClasses
	print ('-' * 50)
	print('test getPlugins')
	print(getPluginClasses())
	s= ''
	for p in getPluginClasses():
		if p.registeredCommands:
			if type(p.registeredCommands) is str:
				s+= p.__name__ + '\n\n* '  + p.registeredCommands + '\n\n'
			else:
				s+= p.__name__ + '\n'
				for c in p.registeredCommands:
					s+= '\n* '  + c
				s+= '\n\n'
	print('commands:')
	print (s)

