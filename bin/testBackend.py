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

	for i in range(4):
		#con.sendRequest(backend.connection.PyCCPackage(handle=con.newRequest(),command='echo'))
		input=con.parseInput()
		if type(input) is backend.connection.PyCCPackage:
			input.dump()
		else:
			print(input)
		if i < 3:
			time.sleep(1)
			con.sendRequest(backend.connection.PyCCPackage(handle=con.newRequest(),command='echo'))
finally:
	try:
		con.close()
	except NameError:
		socket.close()
