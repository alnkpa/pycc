#!/usr/bin/env python3
# -*- encoding:utf8 -*-

import socket
import select
import backend.plugins
import backend.plugins.general

class PyCCBackendServer(object):

	def __init__(self):
		self.server = None
		self.serverAddr = None
		self.serverPort = None
		self.clients = []
		self.read = True

	def listen(self, addr, port):
		self.serverAddr = addr
		self.serverPort = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# searching first free port:
		while True:
			try:
				self.server.bind((self.serverAddr, self.serverPort))
				break
			except:
				self.serverPort+=1
		with open('.port','w') as portfile:
			portfile.write(str(self.serverPort))
		self.server.listen(1)

	def shutdown(self):
		for client in self.clients:
			client.close()
		self.server.close()

	def listenforever(self):
		while self.read:
			toReadConnections, toWritConnections, priorityConnectsions = select.select(
				[self.server] + self.clients, [], [])

			for sock in toReadConnections:
				if sock is self.server: # new connection
					client, addr = self.server.accept()
					self.clientConnectionOpened(client)
				else:
					message = sock.recv(1024).decode('utf8')
					if message:
						self.handleCommand(sock,message)
					else:
						self.clientConnectionClosed(sock)

	def clientConnectionOpened(self,clientSocket):
		self.clients.append(clientSocket)
		ip = clientSocket.getpeername()[0]
		print("+++ connection from %s" % ip)

	def clientConnectionClosed(self,clientSocket):
		ip = clientSocket.getpeername()[0]
		print("+++ connection to %s closed" % ip)
		clientSocket.close()
		self.clients.remove(clientSocket)

	def handleCommand(self,clientSocket,message):
		ip = clientSocket.getpeername()[0]
		print("[%s] %s" % (ip, message))
		if message.strip() == 'shutdown':
			self.read = False
