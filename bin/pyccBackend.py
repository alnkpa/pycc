#!/usr/bin/env python3
import sys
sys.path.append('.')
sys.path.append('./backend')
sys.path.append('./backend/plugins')
sys.path.append('..')
sys.path.append('../backend')
sys.path.append('../backend/plugins')

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

# default value
port = config.getint('network','port')
network= config.getstr('network','bind')
searchPort= True

# loading arguments
argIndex= 1
while argIndex < len(sys.argv):
	arg= sys.argv[argIndex]
	argIndex+= 1
	if arg == '-searchPort':
		# 1, 0
		searchPort= int(sys.argv[argIndex])
		argIndex+= 1
	if arg == '-network':
		# string
		searchPort= sys.argv[argIndex]
		argIndex+= 1
	if arg == '-port':
		# string
		searchPort= int(sys.argv[argIndex])
		argIndex+= 1

# starting server
try:
		while searchPort:
			try:
				server.listen(network,port)
				break
			except:
				port+=1
		else:
			server.listen(network,port)
		
		server.listenforever()
finally:
		server.shutdown()
