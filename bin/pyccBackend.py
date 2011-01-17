#!/usr/bin/env python3
# fixing working directory
import os
import os.path
os.chdir(os.path.realpath(os.path.join(os.path.split(__file__)[0],'..')))
# fixing include path
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
import socket

config=backend.config.PyCCBackendConfig()
server=backend.server.PyCCBackendServer(config)

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
		port= int(sys.argv[argIndex])
		argIndex+= 1

# starting server
try:
		while searchPort:
			try:
				server.listen(network,port)
				break
			except socket.error as e:
				# [Errno 98] Address already in use
				if e.args[0] == 98:
					port+=1
				else:
					raise
		else:
			server.listen(network,port)
		
		server.listenforever()
finally:
		server.shutdown()
