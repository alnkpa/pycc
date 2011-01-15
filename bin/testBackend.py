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
	con=backend.connection.PyCCConnection(socket)

	for i in range(4):
		input=con.parseInput()
		if type(input) is backend.connection.PyCCPackage:
			input.dump()
		else:
			print(input)
		if i < 4:
			time.sleep(1)
			con.sendRequest(backend.connection.PyCCPackage(handle=con.newRequest(),command='echo',data='tmp test'))
finally:
	try:
		con.close()
	except NameError:
		socket.close()
