#!/usr/bin/env python3
import os
import os.path
os.chdir(os.path.realpath(os.path.join(os.path.split(__file__)[0],'..')))
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
				print('$$$${type}{handle}:{command}'.format(type=data.type,
					handle=data.handle,command=data.command))
				try:
					print(data.data.decode('utf8'))
				except UnicodeError:
					print(data.data)

		except KeyboardInterrupt:
			command = input('PyCC: ')
			if command.endswith('\\'):
				data = input('>')
				while data.endswith('\\'):
					data += '\n' + input('>')
			else:
				data = None
			if command == 'quit':
				run = False
			else:
				con.sendRequest(backend.connection.PyCCPackage(handle=con.newRequest(),command=command,data=data))
				if command == 'shutdown':
					run = False

finally:
	try:
		con.close()
	except NameError:
		socket.close()
