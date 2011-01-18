#!/usr/bin/env python3
# -*- encoding:utf8 -*-

import socket
import select
import backend.plugins
import backend.connection
import sys
import traceback

class PyCCBackendServer(object):

	def __init__(self, config):
		self._config = config
		self._nodeId = config.getNodeId()
		self._server = None
		self._serverAddr = None
		self._serverPort = None
		self._connections = {
			'tcpListen': [],
			'udpListen': [],
			'clients': [],
			'broadcasts': []
			}
		self._nodeAddresses = {}
		self._read = True
		self._plugins = backend.plugins.PyCCBackendPluginManager(self,config)

	def listen(self, addr, port):
		self._serverAddr = addr
		self._serverPort = port
		# setting up tcp socket
		tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpSocket.bind((self._serverAddr, self._serverPort))
		tcpSocket.listen(1)
		# setting up upd socket
		self._connections['tcpListen'].append(tcpSocket)
		udpSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		udpSocket.bind((self._serverAddr, self._serverPort))
		pyccConnection=backend.connection.PyCCConnection(udpSocket,self._nodeId,status='udp',mode='server')
		self._connections['udpListen'].append(pyccConnection)
		# save used port
		with open('.port','w') as portfile:
			portfile.write(str(self._serverPort))
		print(self._serverAddr, self._serverPort)
		self._plugins.startup()

	def shutdown(self):
		self._plugins.shutdown()
		for socktype in self._connections:
			for client in self._connections[socktype]:
				client.close()

	def listenforever(self):
		while self._read:
			toReadConnections, toWriteConnections, priorityConnectsions = select.select(
				self._connections['tcpListen'] + self._connections['udpListen']
				+ self._connections['broadcasts'] + self._connections['clients'], [], [])

			for sock in toReadConnections:
				try:
					if sock in self._connections['tcpListen']: # new connection
						client, addr = sock.accept()
						self.clientConnectionOpened(client)
					else:
						parsed=sock.parseInput()
						if parsed is False :
							self.clientConnectionClosed(sock)
						elif type(parsed) is backend.connection.PyCCPackage:
							ip = sock.getpeername()[0]
							print("[%s] %s" % (ip, parsed))
							if parsed.type == backend.connection.PyCCPackage.TYPE_REQUEST: #Request
								self.handleCommand(sock,parsed)
				except (backend.connection.ProtocolException,socket.error) as e:
					print("{0}: {1}".format(type(e).__name__,e),file=sys.stderr)
					traceback.print_tb(e.__traceback__)
					self.clientConnectionClosed(sock)

	def clientConnectionOpened(self,clientSocket):
		pyccConnection=backend.connection.PyCCConnection(clientSocket,self._nodeId,mode='server')
		self._connections['clients'].append(pyccConnection)
		self._plugins.clientConnectionOpened(clientSocket)
		ip = pyccConnection.getpeername()[0]
		print("+++ connection from %s" % ip)

	def clientConnectionClosed(self,clientSocket):
		try:
			ip = clientSocket.getpeername()[0]
			print("+++ connection to %s closed" % ip)
			self._plugins.clientConnectionClosed(clientSocket)
			clientSocket.close()
		except socket.error:
			pass
		finally:
			try:
				self._connections['clients'].remove(clientSocket)
			except ValueError:
				self._connections['broadcast'].remove(clientSocket)

	def handleCommand(self,clientSocket,conElement):
		if conElement.command.strip() == 'shutdown':
			self._read = False
		self._plugins.handleCommand(conElement)

	def status(self):
		message='Clients:\n'
		for connection in self._connections['clients']:
				message+=str(connection)
				message+='\n'
		message+='NodeAddresses:\n'
		for node in self._nodeAddresses:
				message+='{0}: {1}\n'.format(node,self._nodeAddresses[node])
		message+='BroadcastAdrresses:\n'
		for connection in self._connections['broadcasts']:
				message+=str(connection)
				message+='\n'
		return message

	def openConnection(self,host,port=True):
		if port == True:
			port = self._serverPort
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
		con=backend.connection.PyCCConnection(sock,self._nodeId)
		self._connections['clients'].append(con)
		return con

	def getConnectionList(self, node):
		count=0
		if node == ':broadcast':
			for con in self._connections['broadcasts']:
				print('yield broadcast con')
				yield con
				cound = -1
		else:
			for con in self._connections['clients']:
				if con.partnerNodeId==node:
						count+=1
						yield con
		if count==0:
			if node in self._nodeAddresses:
				con=self.openConnection(self._nodeAddresses[node])
				if issubclass(type(con),backend.connection.PyCCConnection):
					yield con
				else:
					print("ERROR: could not connect to node {0}".format(node))

	def getNodeId(self):
		return self._nodeId

	def addBroadcastAddress(self,address):
		udpSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		udpSocket.connect((address, self._serverPort))
		self._connections['broadcasts'].append(backend.connection.PyCCConnection(udpSocket,self._nodeId,status='udp'))

	def nodeAnnounce(self, package):
		self._nodeAddresses[package.connection.partnerNodeId] = package.connection._address[0]
