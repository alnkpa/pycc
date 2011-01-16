#!/usr/bin/env python3
import sys
sys.path.append('.')
sys.path.append('./backend')
sys.path.append('./backend/plugins')
import backend
import backend.connection
import socket
import time

try:
	socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	with open('.port') as file:
		port=int(file.readline().strip())
	socket.connect(('127.0.0.1', port))
	con=backend.connection.PyCCConnection(socket,'testBackend')

	run=True

	while run:
		try:
			data=con.parseInput()
			if type(data) is backend.connection.PyCCPackage:
				data.dump()

		except KeyboardInterrupt:
			command = input('PyCC: ')
			if command == 'quit':
				run = False
			else:
				con.sendRequest(backend.connection.PyCCPackage(handle=con.newRequest(),command=command))
				if command == 'shutdown':
					run = False

finally:
	try:
		con.close()
	except NameError:
		socket.close()
