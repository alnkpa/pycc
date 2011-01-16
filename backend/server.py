#!/usr/bin/env python3
# -*- encoding:utf8 -*-

import socket
import select
import backend.plugins
import backend.connection

class PyCCBackendServer(object):

	def __init__(self,id):
		self._nodeId=id
		self._server = None
		self._serverAddr = None
		self._serverPort = None
		self._connections = {
			'tcpListen':[],
			'udpListen':[],
			'clients':[],
			'broadcasts':[]
			}
		self._read = True
		self._plugins = backend.plugins.PyCCBackendPluginManager(self)

	def listen(self, addr, port):
		self._serverAddr = addr
		self._serverPort = port
		# setting up tcp socket
		tcpSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
					print("{0}: {1}".format(type(e),e))
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
			self._connections['clients'].remove(clientSocket)

	def handleCommand(self,clientSocket,conElement):
		if conElement.command.strip() == 'shutdown':
			self._read = False
		self._plugins.handleCommand(conElement)

	def status(self):
		message=''
		for connection in self._connections['clients']:
				message+=str(connection)
				message+='\n'
		return message

	def openConnection(self,host,port=62533):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
		con=backend.connection.PyCCConnection(sock,self._nodeId)
		self._connections['clients'].append(con)

	def getConnectionList(self, node):
		count=0
		for con in self._connections['clients']:
				if con.partnerNodeId==node:
						count+=1
						yield con
		if count==0:
			# fix: open connection
			pass

	def getNodeId(self):
		return self._nodeId

	def addBroadcastAddress(self,address):
		udpSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udpSocket.connect((self.address, self._serverPort))
		self._connections['broadcasts'].append(backend.connection.PyCCConnection(udpSocket,self._nodeId,status='udp'))
