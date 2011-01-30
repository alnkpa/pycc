#!/usr/bin/env python3
# -*- encoding:utf8 -*-

import socket
import select
import backend.plugins
import backend.connection
import sys
import traceback

class PyCCBackendServer(object):
	''' main backend control class
	    this class manage to connection and the whole network communication
	    the plugin management is done by the PyCCBackendPluginManager'''

	def __init__(self, config):
		self._config = config # config backend class [PyCCBackendConfig]
		self._nodeId = config.getNodeId() # determine node id
		self._serverAddr = None # server bind address
		self._serverPort = None # server port
		self._connections = { # open network connections
			'tcpListen': [], # tcp listening
			'udpListen': [], # udp listening
			'clients': [], # connections to/from other clients/backends
			'broadcasts': [] # udp broadcast address
			}
		self._nodeAddresses = {} # map from node to network address
		self._read = True # continue network reading
		# start network plugin manager:
		self._plugins = backend.plugins.PyCCBackendPluginManager(self,config)

	def listen(self, addr, port):
		''' call for binding server to network interfaces
		    addr: bind address [udp+tcp]
		    port: bind port [udp+tcp]'''
		self._serverAddr = addr
		self._serverPort = port
		# setting up tcp socket
		tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpSocket.bind((self._serverAddr, self._serverPort))
		tcpSocket.listen(1)
		self._connections['tcpListen'].append(tcpSocket)
		# setting up upd socket
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
		# startup plugins
		self._plugins.startup()

	def shutdown(self):
		''' server shutdown; close network connection'''
		# give plugins the possibility the close network communication:
		self._plugins.shutdown()
		# close network connections
		for socktype in self._connections:
			for client in self._connections[socktype]:
				client.close()

	def listenforever(self):
		''' handle network communication endless'''
		while self._read: # should i read more?
			# wait for new data to read:
			toReadConnections, toWriteConnections, priorityConnectsions = select.select(
				self._connections['tcpListen'] + self._connections['udpListen']
				+ self._connections['broadcasts'] + self._connections['clients'], [], [])

			for sock in toReadConnections: # handle all sockets with new data
				try:
					if sock in self._connections['tcpListen']: # new connection
						client, addr = sock.accept()
						# setting up client connection
						self.clientConnectionOpened(client)
					else:
						# read new input:
						parsed = sock.parseInput()
						if parsed is False: # could not read
							self.clientConnectionClosed(sock)
						elif type(parsed) is backend.connection.PyCCPackage:
							# inform about new data
							ip = sock.getpeername()[0]
							print("[%s] %s" % (ip, parsed))
							# handle package via plugin manager
							if parsed.type == backend.connection.PyCCPackage.TYPE_REQUEST: #Request
								self.handleCommand(sock,parsed)
				except (backend.connection.ProtocolException, socket.error) as e:
					print("{0}: {1}".format(type(e).__name__,e),file=sys.stderr)
					traceback.print_tb(e.__traceback__)
					self.clientConnectionClosed(sock)
				except Exception as e:
					print("{0}: {1}".format(type(e).__name__,e),file=sys.stderr)
					traceback.print_tb(e.__traceback__)
					self._read = False
					print("SERVER SHUTDOWN")
					break

	def clientConnectionOpened(self, clientSocket):
		''' prepare a new connection from a client (frontend or other backend)'''
		# starting pycc communication about this network socket
		pyccConnection=backend.connection.PyCCConnection(clientSocket,self._nodeId,mode='server')
		self._connections['clients'].append(pyccConnection) # save connection
		self._plugins.clientConnectionOpened(clientSocket) # inform package about new connection
		# print information
		ip = pyccConnection.getpeername()[0]
		print("+++ connection from %s" % ip)

	def clientConnectionClosed(self,clientSocket):
		''' close connection to client'''
		if clientSocket in self._connections['clients']: # client connection?
			try:
				ip = clientSocket.getpeername()[0]
				print("+++ connection to %s closed" % ip)
				self._plugins.clientConnectionClosed(clientSocket)
				clientSocket.close()
			except socket.error: # error whil closing: ignore
				pass
			self._connections['clients'].remove(clientSocket)

	def handleCommand(self,clientSocket,conElement):
		if conElement.command.strip() == 'shutdown':
			self._read = False
		self._plugins.handleCommand(conElement)

	def status(self):
		# return message about internal state of class and connections'';
		message = 'Clients:\n'
		for connection in self._connections['clients']:
				message += str(connection)
				message += '\n'
		message += 'NodeAddresses:\n'
		for node in self._nodeAddresses:
				message += '{0}: {1}\n'.format(node,self._nodeAddresses[node])
		message += 'BroadcastAdrresses:\n'
		for connection in self._connections['broadcasts']:
				message += str(connection)
				message += '\n'
		return message

	def openConnection(self,host,port=True):
		''' open connection to other backend'''
		if port == True: # use default port?
			port = self._serverPort
		# new socket:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
		# build pycc connection over socket
		con = backend.connection.PyCCConnection(sock,self._nodeId)
		self._connections['clients'].append(con)
		return con

	def getConnectionList(self, node):
		''' return a list with all connection to a specific node
		    :broadcast for broadcast connections
		    :frontend for connection from frontends
		    :clients for all connections to connected frontends/other backends'''
		count = 0
		if node == ':broadcast': # broadcast connections
			for con in self._connections['broadcasts']:
				yield con
				count = -1
			return
		elif node == ':frontend': # connections to frontends
			for con in self._connections['clients']:
				if con.getpeername()[0] == '127.0.0.1':
						yield con
			return
		elif node == ':clients':
			for con in self._connections['clients']:
				yield con
			return
		else: # other (normal) node
			for con in self._connections['clients']:
				if con.partnerNodeId == node:
						count += 1
						yield con
		if count == 0: # have to open connection
			if node in self._nodeAddresses: # network address of node known?
				con = self.openConnection(self._nodeAddresses[node])
				if issubclass(type(con),backend.connection.PyCCConnection):
					yield con
				else:
					print("ERROR: could not connect to node {0}".format(node))

	def getNodeId(self):
		''' return node id of this backend'''
		return self._nodeId

	def addBroadcastAddress(self,address):
		''' add new broadcast address'''
		udpSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		udpSocket.connect((address, self._serverPort))
		self._connections['broadcasts'].append(backend.connection.PyCCConnection(udpSocket,self._nodeId,status='udp'))

	def nodeAnnounce(self, package):
		''' add new relation between network address and node'''
		self._nodeAddresses[package.connection.partnerNodeId] = package.connection._address[0]
