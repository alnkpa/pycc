import socket

class ProtocolException(Exception):
	pass

class PyCCConnection(object):
	version='0.1'

	def __init__(self, socket, mode='client'):
		self.socket = socket
		self.mode = mode
		self.status = 'new'
		if self.mode == 'server':
			self.nextComHandle = 0
			self.send('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			self.status='init'
		else:
			self.nextComHandle = 1

	def send(self,data):
		'''send all data to the recipient'''
		return self.socket.sendall(bytes(data,encoding='utf8'))

	def fileno(self):
		''' file handle for select.select'''
		return self.socket.fileno()

	def getpeername(self):
		return self.socket.getpeername()

	def close(self, *args):
		'''shut down the socket connection 

optimal argument is
socket.SHUT_RD = 0
socket.SHUT_RDWR = 2
socket.SHUT_WR = 1
'''
		return self.socket.close(*args)

	def parseInput(self):
		message=self.socket.recv(1024).decode('utf8')
		if not message:
			return False
		if self.status == 'new':
			if not message.startswith('PyCC'):
				raise ProtocolException
			self.send('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
		elif self.status == 'init':
			tmp=message.split("|")
			if len(tmp)!=3:
				raise ProtocolException
			self.send('OK. {0}\n'.format(tmp[1]))
			self.status = 'open'
		else:
			pos=message.find(':')
			if pos<2:
				raise ProtocolException
			messageType=message[0]
			comHandle=message[1:pos]
			messageData=message[pos+1:]
			return (messageType,comHandle,messageData)
		return True

	def newRequest(self):
		self.nextComHandle+=2
		return self.nextComHandle-2

	def sendRequest(self, comHandle, data):
		self.send('A{comHandle}:{data}'.format(comHandle).format(data))

	def sendResponse(self, comHandle, data):
		self.send('O{comHandle}:{data}'.format(comHandle).format(data))

	def sendError(self, comHandle, message):
		self.send('E{comHandle}:{data}'.format(comHandle).format(data))

	def recv(self, bufsize= 8192):
		'''receive up to 8192 bytes of data'''
		# fix: need a handler for invalid packages
		return self.socket.recv(bufsize).decode('utf8')

