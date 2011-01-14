#!/usr/bin/env python3
import sys
sys.path.append('.')
import backend
import backend.config
import backend.server
import importlib
import backend.plugins.general

config=backend.config.PyCCBackendConfig()
server=backend.server.PyCCBackendServer()

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
