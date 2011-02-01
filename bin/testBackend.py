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
	if len(sys.argv)>1:
		host = sys.argv[1]
	else:
		host = '127.0.0.1'
	if len(sys.argv) > 2:
		port = int(sys.argv[2])
	else:
		with open('.port') as file:
			port=int(file.readline().strip())
	socket.connect((host, port))
	con=backend.connection.PyCCConnection(socket,'testBackend')

	run=True

	while run:
		try:
			data=con.parseInput()
			if type(data) is not list:
				continue
			for package in data:
				if type(package) is not backend.connection.PyCCPackage:
					continue
				print('$$$${type}{handle}:{command}'.format(type=package.type,
					handle=package.handle,command=package.command))
				try:
					print(package.data.decode('utf8'))
				except AttributeError:
					pass
				except UnicodeError:
					print(package.data)

		except KeyboardInterrupt:
			command = input('PyCC: ')
			if command.endswith('\\'):
				command = command[0:len(command)-1]
				more=True
				data = ''
				while more:
					newData=input('>')
					if newData.endswith('\\'):
						data += newData[0:len(newData)-1]
						more = True
					else:
						data += newData
						more = False
					data += '\n'
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
