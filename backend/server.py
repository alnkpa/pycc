#!/usr/bin/env python3
# -*- encoding:utf8 -*-

import socket
import select
import backend.plugins
import backend.connection

class PyCCBackendServer(object):

	def __init__(self):
		self.server = None
		self.serverAddr = None
		self.serverPort = None
		self.clients = []
		self.read = True
		self.plugins = backend.plugins.PyCCBackendPluginManager(self)

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
		self.plugins.startup()

	def shutdown(self):
		self.plugins.shutdown()
		for client in self.clients:
			client.close()
		self.server.close()

	def listenforever(self):
		while self.read:
			toReadConnections, toWriteConnections, priorityConnectsions = select.select(
				[self.server] + self.clients, [], [])

			for sock in toReadConnections:
				try:
					if sock is self.server: # new connection
						client, addr = self.server.accept()
						self.clientConnectionOpened(client)
					else:
						parsed=sock.parseInput()
						if parsed is False :
							self.clientConnectionClosed(sock)
						elif type(parsed) is backend.connection.PyCCConnectionElement:
							if parsed.type == backend.connection.PyCCConnectionElement.TYPE_REQUEST: #Request
								self.handleCommand(sock,parsed)
				except backend.connection.ProtocolException as e:
					print("{0}: {1}".format(type(e),e))
					self.clientConnectionClosed(sock)
				except socket.error as e:
					print("{0}: {1}".format(type(e),e))
					self.clientConnectionClosed(sock)

	def clientConnectionOpened(self,clientSocket):
		pyccConnection=backend.connection.PyCCConnection(clientSocket,mode='server')
		self.clients.append(pyccConnection)
		self.plugins.clientConnectionOpened(clientSocket)
		ip = pyccConnection.getpeername()[0]
		print("+++ connection from %s" % ip)

	def clientConnectionClosed(self,clientSocket):
		ip = clientSocket.getpeername()[0]
		print("+++ connection to %s closed" % ip)
		self.plugins.clientConnectionClosed(clientSocket)
		clientSocket.close()
		self.clients.remove(clientSocket)

	def handleCommand(self,clientSocket,conElement):
		ip = clientSocket.getpeername()[0]
		print("[%s] %s" % (ip, conElement))
		if conElement.command.strip() == 'shutdown':
			self.read = False
		self.plugins.handleCommand(clientSocket,conElement) # FixMe
		
	def registerPlugin(self,plugin):
		self.plugins.registerPlugin(plugin)
