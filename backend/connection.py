import socket

class ProtocolException(Exception):
	''' Exception for pycc communication error
	    This error will be raised, if the pycc protocol is not correctly used
	    by the communication partner'''
	ERNO_NO_COMMAND_HANDLE = 2
	ERNO_INVALID_COMMAND_HANDLE = 3
	ERNO_WRONG_PROTOCOL_HEADER = 6

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
	    type: message type [str:A,O,E]
	        request - TYPE_REQUEST
	        response - TYPE_RESPONSE
	        error - TYPE_ERROR
	    handle: message identifier - 
	        nesessary to assign responses to requests
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
		print( 'PyCCP:\nType:{0}\\\nHandle:{1}\\\nCommand:{2}\\\nData:\n{3}\\'\
			.format(self.type,self.handle,self.command,self.data))


class PyCCConnection(object):
	""" PyCC Network communication
	    wrapper class for the pycc protocol. the transfer pycc messages to/from an underlining
	    socket.
	    Attributes:
		- partnerNodeId: str; node it of communication partner
	"""
	version='0.1' # protocol version

	def __init__(self, socket, nodeid, mode = 'client', status = 'new'):
		""" create a new PyCC-Connection over the socket socket (server or client mode)
		    socket: tcp-connection instance
		    mode: client or server (e.g. helpful for protocol init)"""
		self._socket = socket # underlining socket.socket for network communication
		self._nodeid = nodeid # node id of this backend
		self.partnerNodeId = None # node id of communication partner
		self._address = None # partner address in udp connections
		self._mode = mode # communication modus ('client', 'server')
		self._status = status # communication status ('new', 'init', 'open', 'udp')
		self._boundary = None # message end string (for messages with data part)
		if self._mode == 'server' and self._status != 'udp': # if tcp server
			self._nextComHandle = 0
			# send server info to client:
			self.sendstr('PyCC|{version}|{nodeid}\n'.format(version=PyCCConnection.version, nodeid=self._nodeid))
			self._status='init' # communication initizalised, response of partner nesessary
		else: # client or upd
			self._nextComHandle = 1 # use odd command handles
		self._buffer = bytearray() # buffer, for messages with are recieved over more socket read calls
		self._callbacks = {} # list of callbacks for message responses and errors
		self._heloUdpPorts = [] # list of udp port which had send an helo

	def _parseMessageStart(self):
		''' this method parsed the _buffer attribute for a complete message
		    Return values:
			- None: no message header end found
			- True: message without data found
			- int: message with boundary found - number is position of header end'''
		self._element = PyCCPackage(connection=self) # prepare PyCCPackage for next mesasge
		self._boundary = None # no boundary known
		if self._status == 'udp' and self._buffer.startswith(b'PyCC|'): # Receive Header in UDP-Connection
			# remove pycc header (first line)
			self._buffer = self._buffer[self._buffer.find(bytearray(b'\n'))+1:]
			if len(self._buffer) == 0: # no more data, parsing finished
				return None
		# Extract MessageType:
		if self._buffer[0] == bytearray(b'A')[0]: # request message
			self._element.type = PyCCPackage.TYPE_REQUEST
		elif self._buffer[0] == bytearray(b'O')[0]: # response message
			self._element.type = PyCCPackage.TYPE_RESPONSE
		elif self._buffer[0] == bytearray(b'E')[0]: # error message
			self._element.type = PyCCPackage.TYPE_ERROR
		else: # there are no more message types
			raise ProtocolException(ProtocolException.ERNO_UNKNOWN_MESSAGE_TYPE,
				'unknown message type\n{0}'.format(self._buffer))
		# Extract ComHandle:
		posEndHandle = 1
		while posEndHandle < len(self._buffer) and self._buffer[posEndHandle] != bytearray(b':')[0]:
			posEndHandle += 1
		if posEndHandle >= len(self._buffer): # no end handle char found
			raise ProtocolException(ProtocolException.ERNO_NO_COMMAND_HANDLE,
				'no comHandle')
		try:
			self._element.handle = int(self._buffer[1:posEndHandle])
		except ValueError: # handle was no integer
			raise ProtocolException(
				ProtocolException.ERNO_INVALID_COMMAND_HANDLE,
				'invalid comHandle')
		# Extract endline
		posEndLine = posEndHandle + 1
		try:
			while (self._buffer[posEndLine] != bytearray(b'\n')[0]):
				posEndLine += 1
		except IndexError: # no end line found -> message end not yet recieved
			return None
		# Searching for boundary delimiter
		posEndBoundary = posEndHandle + 1
		try:
			while (self._buffer[posEndBoundary] != bytearray(b',')[0]):
				posEndBoundary += 1
		except IndexError: # no boundary found
			self._boundary = False
			self._element.command = self._buffer[posEndHandle+1:posEndLine]\
				.decode('utf8').rstrip() # command is full line after handle
			return True
		else: # boundary found
			self._boundary = self._buffer[posEndHandle+1:posEndBoundary]
			self._element.command = self._buffer[posEndBoundary+1:posEndLine]\
				.decode('utf8').rstrip() # comand starts after boundary
			return posEndLine # searching for boundary end nesessary

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
		if self._status == 'new': # communication is not yet established (client mode)
			try: # server had to be send helo
				tmp=newData.decode('utf8').split("|") # part header
				if len(tmp)!=3 or tmp[0]!='PyCC': # no pycc protocol
					raise ProtocolException(6,'wrong protocol (header)')
				self.partnerNodeId = tmp[2].strip() # node id of server
				if self._mode != 'udp': # if tcp connection, answer -> finish handshace
					self.sendstr('PyCC|{version}|{nodeid}\n'.format(version=PyCCConnection.version,nodeid=self._nodeid))
				self._status = 'open' # connection is succesfully opend
				# remove header from data:
				newData = newData[newData.find(bytearray(b'\n'))+1:]
				if len(newData) == 0: # no more data available
					return None
			except UnicodeError: # header was no utf8
				raise ProtocolException(ProtocolException.ERNO_WRONG_PROTOCOL_HEADER,
					'wrong protocol (header)')
		elif self._status == 'init': # server mode, client response nesessary
			try:
				tmp = newData.decode('utf8').split("|") # header have to be utf8
				if len(tmp) != 3:
					raise ProtocolException(3,'unknown init')
				self.partnerNodeId = tmp[2].strip() # extract client node id
				if tmp[1].find(',') >- 1: # more than on protocol version possible
					self.sendstr('OK. {0}\n'.format(tmp[1].split(',')[-1]))
				self._status = 'open' # connection established
				# remove header from data:
				newData = newData[newData.find(bytearray(b'\n'))+1:]
				if len(newData)==0: # no more data available
					return None
			except UnicodeError: # header was no utf8
				raise ProtocolException(ProtocolException.ERNO_WRONG_PROTOCOL_HEADER,
					'wrong protocol (header)')
		elif self._status == 'udp' and self._address[1] not in self._heloUdpPorts:
			lineEndPos = newData.find(bytearray(b'\n'))
			if lineEndPos >- 1:
				tmp = newData[0:lineEndPos].decode('utf8').split("|")
			else:
				tmp = newData.decode('utf8').split("|")
			if len(tmp) !=3 or tmp[0] != 'PyCC':
				raise ProtocolException(6,'wrong protocol (header)')
			else:
				self._heloUdpPorts.append(self._address[1])
			self.partnerNodeId=tmp[2].strip()
			newData=newData[lineEndPos+1:]
			if len(newData)==0:
				return None

		self._buffer += newData # append now data to buffer
		result = self._parseMessageStart() # search for message header
		if result == False or result is None: # not all data received
			return
		elif result is True: # no boundary set -> one line
			self._element.data = None # no data
			self._buffer = self._buffer = bytearray() # message read
			self._boundary = None # no boundary known (of next package)
			return self._getNewPackage(self._element) # result recieved package
		elif type(result) is int: # package with boundary found
			pos = self._buffer.find(self._boundary,result) # search for boundary
			if pos == -1: # boundary not yet recieved
				return None # no new package there
			else: # boundary found
				self._element.data = self._buffer[result+1:pos] # extract data
				self._buffer = self._buffer[pos+len(self._boundary)+1:]
				if self._buffer.startswith(bytearray(b'\r')):
					self._buffer = self._buffer[1:]
				if self._buffer.startswith(bytearray(b'\n')):
					self._buffer = self._buffer[1:]
				self._boundary = None # no boundary known (of next package)
				return self._getNewPackage(self._element) # return new package

	def _getNewPackage(self,package):
		''' all recieved packages are transfered throught this method
		    callbacks for package is searched and called
		    packages with callback are then removed
		    Return values: see parseInput'''
		if ( package.type == PyCCPackage.TYPE_RESPONSE or \
			package.type == PyCCPackage.TYPE_RESPONSE) \
			and package.handle in self._callbacks:
				callbackData = self._callbacks[package.handle]
				# remove callback if callback return True:
				if callbackData[0](package,callbackData[1]) is True:
					del self._callbacks[package.handle]
				return None # package was handled
		else: # no callback
			return package

	def newRequest(self):
		""" build handle for a new reqeust"""
		self._nextComHandle += 2
		return self._nextComHandle-2

	# fix: needs to be commented
	def sendPackage(self,package):
		# send package (all types possible)
		if self._status == 'udp' and self._mode == 'server': # could not send in udp server mode
			return True
		if package.data is None: # oneline package
			boundary=''
			data=b''
		else: # calculate boundary
			# FixME
			boundary = 'EOF,'
			if type(package.data) is str: # auto convert to binary data
				data = package.data.encode('utf8')
			else:
				data = package.data
			data += b'EOF\n'
		message='{type}{comHandle}:{endBoundary}{command}\n'\
			.format(type=package.type,comHandle=package.handle,
			endBoundary=boundary,command=package.command).encode('utf8')
		message += data # append data to package
		if self._status == 'udp': # send header in udp mode
			self.sendstr('PyCC|{version}|{node}\n'.format(version=PyCCConnection.version,node = self._nodeid))
		self.send(message) # send binary array via socket

	def sendRequest(self, package, callback = None, callbackExtraArg = None):
		'''send new request to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type = PyCCPackage.TYPE_REQUEST # force message type
		if package.handle is None: # handle not yet set
			package.handle = self.newRequest()
		if callback is not None: # callback requested
			if hasattr(callback, '__call__'): # valid callback?
				self._callbacks[package.handle] = (callback,callbackExtraArg)
			else:
				raise ValueError('callback must be a function or None')
		self.sendPackage(package)
		return package.handle # return handle of package

	def sendResponse(self, package):
		'''send new response to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type = PyCCPackage.TYPE_RESPONSE # force mesasge type
		self.sendPackage(package)

	def sendError(self, package):
		'''send error to connection partner
		package: data to send (not all data uses e.g. type) [PyCCPackage]'''
		package.type = PyCCPackage.TYPE_ERROR # force message type
		self.sendPackage(package)


	def send(self,data):
		'''send all data to the recipient'''
		return self._socket.sendall(data)

	def sendstr(self,data):
		'''send full string to the recipient'''
		return self._socket.sendall(data.encode('utf8'))

	def recv(self, bufsize= 8192):
		'''receive up to 8192 bytes of data'''
		data = self._socket.recv(bufsize).decode('utf8')
		if self._status == 'new':
			self.sendstr('PyCC|{version}|PyCC-Node\n'.format(version=PyCCConnection.version))
			self._status = 'init'

	def fileno(self):
		''' file handle for select.select'''
		return self._socket.fileno()

	def getpeername(self):
		if self._status == 'udp': # and self._mode == 'client':
			return self._address # cached address from last package
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
		''' return core information about this connection'''
		info = self.getpeername()
		if info is None or len(info) != 2:
			info = ('', '')
		return '{0}:{1}@{2} -- nodeId:{3}'.format(info[0],info[1],self._status,self.partnerNodeId)
