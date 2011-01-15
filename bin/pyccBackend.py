#!/usr/bin/env python3
import sys
sys.path.append('.')
sys.path.append('./backend')
sys.path.append('./backend/plugins')
import backend
import backend.config
import backend.server
import importlib
import backend.plugins.Plugin
import hashlib

config=backend.config.PyCCBackendConfig()
backendID=config.getstr('network','id')
if backendID is None:
	backendID=hashlib.sha1("|".join(sys.path).encode('utf8'))
server=backend.server.PyCCBackendServer(backendID)

# loading backend plugins
plugins=config.getstr('loadplugins','plugins').strip().split(',')
for plugin in plugins:
		d=importlib.import_module('backend.plugins.{pluginname}'.format(pluginname=plugin))
		for elementName in dir(d):
				element=getattr(d,elementName)
				if element is type and issubclass(element, backend.plugins.general.Plugin):
					server.addPlugin(element)

# starting server
try:
		server.listen(config.getstr('network','bind'),config.getint('network','port'))
		server.listenforever()
finally:
		server.shutdown()
