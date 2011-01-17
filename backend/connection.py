import socket

class ProtocolException(Exception):
	def __init__(self, type, message):
		self.type = type
		self.message = message
	def __str__(self):
		return "ProtocolException: {0} - {1}".format(self.type,self.message)

class PyCCPackage(object):
	""" record class
	    this class is used to transfer and save information about request, 
	    response and error messages of the PyCC protocol

	    connection: connection to client [PyCCConnection]
	    type: message type (request, response, error) [str:A,O,E]
	    handle: message identifier - nesessary to assign responses to requests [?]
	    command: command (handle by plugins) [str]
	    data: data of message [bytearray]"""
	TYPE_REQUEST='A'
	TYPE_RESPONSE='O'
	TYPE_ERROR='E'

	def __init__(self,connection=None,type=None,handle=None,command=None,data=None):
		self.connection=connection
		self.type=type
		self.handle=handle
		self.command=command
		self.data=data

	def __str__(self):
		return 'PyCCP:{0}{1}:{2}|{3}'.format(self.type,
			self.handle,self.command,self.data)

	def dump(self):
		print( 'PyCCP:\nType:{0}\\\nHandle:{1}\\\nCommand:{2}\\\nData:\n{3}\\'.format(self.type,
			self.handle,self.command,self.data))


class PyCCConnection(object):
	version='0.1'

	def __init__(self, socket, nodeid, mode = 'client', status = 'new'):
		""" create a new PyCC-Connection over the socket socket (server or client mode)
		    socket: tcp-connection instance
		    mode: client or server (e.g. helpful for protocol init)"""
		self._socket = socket
		self._nodeid = nodeid
		self.partnerNodeId = None
		self._address = None
		self._mode = mode
		self._status = status
		self._boundary = None
		if self._mode == 'server' and self._status != 'udp':
			self._nextComHandle = 0
			self.sendstr('PyCC|{version}|{nodeid}\n'.format(version=PyCCConnection.version,nodeid=self._nodeid))
			self._status='init'
		else:
			self._nextComHandle = 1
		self._buffer=bytearray()
		self._callbacks={}
		self._heloUdpPorts = []

	def _parseMessageStart(self):
		self._element = PyCCPackage(connection=self)
		self._boundary = None
		# Extract MessageType:
		if self._buffer[0]==bytearray(b'A')[0]:
			self._element.type=PyCCPackage.TYPE_REQUEST
		elif self._buffer[0]==bytearray(b'O')[0]:
			self._element.type=PyCCPackage.TYPE_RESPONSE
		elif self._buffer[0]==bytearray(b'E')[0]:
			self._element.type=PyCCPackage.TYPE_ERROR
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
		try:
			while (self._buffer[posEndLine]!=bytearray(b'\n')[0]):
				posEndLine+=1
		except IndexError:
			return None
		posEndBoundary=posEndHandle+1
		try:
			while (self._buffer[posEndBoundary]!=bytearray(b',')[0]):
				posEndBoundary+=1
		except IndexError:
			self._boundary=False
			self._element.command=self._buffer[posEndHandle+1:posEndLine].decode('utf8').rstrip()
			return True
		else: # no boundary
			self._boundary=self._buffer[posEndHandle+1:posEndBoundary]
			self._element.command=self._buffer[posEndBoundary+1:posEndLine].decode('utf8').rstrip()
			return posEndLine

	def parseInput(self):
		""" parse new unread data in the socket
		    return recieved connection packages
		    Return:
		      False: connection closed
		      None: new new packages
		      PyCCPackage: new package
		    """

		newData, self._address = self._socket.recvfrom(8192)
		if not newData:
			return False
		if self._status == 'new':
			try:
				tmp=newData.decode('utf8').split("|")
				if len(tmp)!=3 or tmp[0]!='PyCC':
					raise ProtocolException(6,'wrong protocol (header)')
				self.partnerNodeId=tmp[2].strip()
				if self._mode != 'udp':
					self.sendstr('PyCC|{version}|{nodeid}\n'.format(version=PyCCConnection.version,nodeid=self._nodeid))
				self._status='open'
				newData=newData[newData.find(bytearray(b'\n'))+1:]
				if len(newData)==0:
					return None
			except UnicodeError:
				raise ProtocolException(6,'wrong protocol (header)')
		elif self._status == 'init':
			tmp=newData.decode('utf8').split("|")
			if len(tmp)!=3:
				raise ProtocolException(3,'unknown init')
			self.partnerNodeId=tmp[2].strip()
			if tmp[1].find(',')>-1:
				self.sendstr('OK. {0}\n'.format(tmp[1].split(',')[-1]))
			self._status = 'open'
			newData=newData[newData.find(bytearray(b'\n'))+1:]
			if len(newData)==0:
				return None
		elif self._status == 'udp' and self._address[1] not in self._heloUdpPorts:
			lineEndPos=newData.find(bytearray(b'\n'))
			if lineEndPos>-1:
				tmp=newData[0:lineEndPos].decode('utf8').split("|")
			else:
				tmp=newData.decode('utf8').split("|")
			if len(tmp)!=3 or tmp[0]!='PyCC':
				raise ProtocolException(6,'wrong protocol (header)')
			else:
				self._heloUdpPorts.append(self._address[1])
			self.partnerNodeId=tmp[2].strip()
			newData=newData[lineEndPos+1:]
			if len(newData)==0:
				return None

		self._buffer += newData
		result=self._parseMessageStart()
		if result == False: # not all data received
			return
		elif result is True: # no boundary set -> one line
			self._element.data = None
			self._buffer = self._buffer=bytearray()
			self._boundary = None
			return self._getNewPackage(self._element)
		elif type(result) is int:
			pos = self._buffer.find(self._boundary,result)
			if pos == -1: # boundry not yet recieved
				return None
			else:
				self._element.data = self._buffer[result+1:pos]
				#FixMe:
				# Idea: self._buffer = self._buffer[pos+len(self._boundary)+1:]
				# Problem: ending \r\n
				self._buffer = self._buffer[pos+len(self._boundary)+1:]
				if self._buffer.startswith(bytearray(b'\r')):
						self._buffer = self._buffer[1:]
				if self._buffer.startswith(bytearray(b'\n')):
						self._buffer = self._buffer[1:]
				#self._buffer = bytearray()
				self._boundary = None
				return self._getNewPackage(self._element)

	def _getNewPackage(self,package):
		if ( package.type == PyCCPackage.TYPE_RESPONSE or \
			package.type == PyCCPackage.TYPE_RESPONSE) \
			and package.handle in self._callbacks:
				callbackData = self._callbacks[package.handle]
				if callbackData[0](package,callbackData[1]) is True:
					del self._callbacks[package.handle]
				return None
		else:
			return package

	def newRequest(self):
		""" build handle for a new reqeust"""
		self._nextComHandle+=2
		return self._nextComHandle-2

	def sendPackage(self,package):
		if self._status == 'udp' and self._mode == 'server':
			return True
		if package.data is None:
			boundary=''
			data=b''
		else:
			boundary='EOF,'
			if type(package.data) is str:
				data=package.data.encode('utf8')
			else:
				data=package.data
			data+=b'EOF\n'
		message='{type}{comHandle}:{endBoundary}{command}\n'\
			.format(type=package.type,comHandle=package.handle,
			endBoundary=boundary,command=package.command).encode('utf8')
		message+=data
		if self._status == 'udp':
			self.sendstr('PyCC|{version}|{node}\n'.format(version=PyCCConnection.version,node = self._nodeid))
		self.send(message)

	def sendRequest(self, package, callback = None, callbackExtraArg = None):
		'''send new request to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type=PyCCPackage.TYPE_REQUEST
		if package.handle is None:
			package.handle = self.newRequest()
		if callback is not None:
			if hasattr(callback, '__call__'):
				self._callbacks[package.handle] = (callback,callbackExtraArg)
			else:
				raise ValueError('callback must be a function or None')
		self.sendPackage(package)
		return package.handle

	def sendResponse(self, package):
		'''send new response to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type=PyCCPackage.TYPE_RESPONSE
		self.sendPackage(package)

	def sendError(self, package):
		'''send error to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type=PyCCPackage.TYPE_ERROR
		self.sendPackage(package)


	def send(self,data):
		'''send all data to the recipient'''
		return self._socket.sendall(data)

	def sendstr(self,data):
		'''send all data to the recipient'''
		return self._socket.sendall(data.encode('utf8'))

	def recv(self, bufsize= 8192):
		'''receive up to 8192 bytes of data'''
		# fix: need a handler for invalid packages
		data=self._socket.recv(bufsize).decode('utf8')
		if self._status == 'new':
			self.sendstr('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			self._status = 'init'

	def fileno(self):
		''' file handle for select.select'''
		return self._socket.fileno()

	def getpeername(self):
		if self._status == 'udp': # and self._mode == 'client':
			return self._address
		else:
			return self._socket.getpeername()

	def close(self, *args):
		'''shut down the socket connection 

optimal argument is
socket.SHUT_RD = 0
socket.SHUT_RDWR = 2
socket.SHUT_WR = 1
'''
		return self._socket.close(*args)

	def __str__(self):
		info=self.getpeername()
		if info is None or len(info) != 2:
			info = ('', '')
		return '{0}:{1}@{2} -- nodeId:{3}'.format(info[0],info[1],self._status,self.partnerNodeId)
