import socket

class ProtocolException(Exception):
	def __init__(self, type, message):
		self.type = type
		self.message = message
	def __str__(self):
		return "ProtocolException: {0} - {1}".format(self.type,self.message)

class PyCCConnectionElement(object):
	TYPE_REQUEST='A'
	TYPE_REPONSE='O'
	TYPE_ERROR='E'

	def __init__(self,connection=None,type=None,handle=None,command=None,data=None):
		self.connection=connection
		self.type=type
		self.handle=handle
		self.command=command
		self.data=data

	def __str__(self):
		return 'PyCCCE:{0}{1}:{2}\n{3}'.format(self.type,
			self.handle,self.command,self.data)


class PyCCConnection(object):
	version='0.1'

	def __init__(self, socket, mode='client'):
		self._socket = socket
		self._mode = mode
		self._status = 'new'
		self._boundary = None
		if self._mode == 'server':
			self._nextComHandle = 0
			self.send('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			self._status='init'
		else:
			self._nextComHandle = 1
		self._buffer=bytearray()

	def _parseMessageStart(self):
		self._element = PyCCConnectionElement(connection=self)
		self._boundary = None
		# Extract MessageType:
		if self._buffer[0]==bytearray(b'A')[0]:
			self._element.type=PyCCConnectionElement.TYPE_REQUEST
		elif self._buffer[0]==bytearray(b'O')[0]:
			self._element.type=PyCCConnectionElement.TYPE_REQUEST
		elif self._buffer[0]==bytearray(b'E')[0]:
			self._element.type=PyCCConnectionElement.TYPE_REQUEST
		else:
			raise ProtocolException(1,'unknown message type')
		# Extract ComHandle:
		posEndHandle=1
		while posEndHandle<len(self._buffer) and self._buffer[posEndHandle]!=bytearray(b':')[0]:
			posEndHandle+=1
		if posEndHandle>=len(self._buffer):
			raise ProtocolException(2,'no comHandle')
		try:
			self._element.handle=int(self._buffer[1:posEndHandle])
		except ValueError:
			raise ProtocolException(3,'invalid comHandle')
		# Extract endline
		posEndLine=posEndHandle+1
		while posEndLine<len(self._buffer) and (self._buffer[posEndLine]!=bytearray(b'\n')[0]):
			posEndLine+=1
		if posEndLine>=len(self._buffer):
			return False
		tmp=self._buffer[posEndHandle+1:posEndLine].decode('utf8').split(',')
		if len(tmp)==2:
			self._boundary=tmp[0]
			self._element.command=tmp[1]
			return True
		else: # no boundary
			self._boundary=False
			self._element.command=tmp[0]
			return True
		return posEndLine


	def parseInput(self):
		newData=self._socket.recv(8192)
		if not newData:
			return False
		if self._status == 'new':
			if not newData.startswith('PyCC'):
				raise ProtocolException
			self.send('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			return None
		elif self._status == 'init':
			tmp=newData.decode('utf8').split("|")
			if len(tmp)!=3:
				raise ProtocolException(3,'unknown init')
			self.send('OK. {0}\n'.format(tmp[1]))
			self._status = 'open'
			return None

		self._buffer += newData
		if self._boundary == None:
			result=self._parseMessageStart()
			if result == False: # not all data received
				print('more data needed')
				return
			elif result is True: # no boundary set -> one line
				self._element.data = self._buffer[result:]
				self._buffer = self._buffer=bytearray()
				self._boundary = None
				return self._element
			elif result is int:
				pos = self._buffer[result:].find(self.boundary)
				if pos == -1: # boundry not yet recieved
					return False
				else:
					self._element.data = self._buffer[result:pos]
					self._buffer = self._buffer[pos+len(self.boundary)]
					self._boundary = None
		return self._element

	def newRequest(self):
		self._nextComHandle+=2
		return self._nextComHandle-2

	def sendRequest(self, comHandle, command, data=None):
		'''send new request to connection partner
		comHandle: identifier of request (for responces)
		command: command name
		data: binary or utf8 data for transfer
		endBoundary: binary-code for request end mark;  True for auto setting'''
		message='A{comHandle}:{endBoundary},{command}\n'\
			.format(comHandle).format(data).encode('utf8')
		if data is str:
			message+=data.encode('utf8')
		else:
			message+=data
		self.send(message)

	def sendResponse(self, comHandle, command, data=None):
		'''send new response to connection partner
		comHandle: identifier of the corresponding request
		command: command name
		data: binary or utf8 data for transfer
		endBoundary: binary-code for request end mark;  True for auto setting'''
		message='O{comHandle}:{endBoundary},{command}\n'\
			.format(comHandle).format(data).encode('utf8')
		if data is str:
			message+=data.encode('utf8')
		else:
			message+=data
		self.send(message)

	def sendError(self, comHandle, message):
		self.send('E{comHandle}:{data}'.format(comHandle).format(data))



	def send(self,data):
		'''send all data to the recipient'''
		return self._socket.sendall(bytes(data,encoding='utf8'))

	def recv(self, bufsize= 8192):
		'''receive up to 8192 bytes of data'''
		# fix: need a handler for invalid packages
		data=self.socket.recv(bufsize).decode('utf8')
		if self.status == 'new':
			self.send('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			self.status = 'init'

	def fileno(self):
		''' file handle for select.select'''
		return self._socket.fileno()

	def getpeername(self):
		return self._socket.getpeername()

	def close(self, *args):
		'''shut down the socket connection 

optimal argument is
socket.SHUT_RD = 0
socket.SHUT_RDWR = 2
socket.SHUT_WR = 1
'''
		return self._socket.close(*args)
