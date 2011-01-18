'''This Plugin distributes the information about this node.

a broadcast includes
state (Status)
username
nodeId





'''


import sys
import socket
import Plugin


sys.path.append('..')
try:
	import connection
except ImportError:
	try:
		import backend.connection as connection
	except ImportError:
		import backend.connection as connection

class Broadcast(Plugin.Plugin):
	'''


'''
	port = 62533
	registeredCommands= ['broadcastState','recvBroadcast']
	def init(self):
		self.server = self.manager.server
		self.baddrs= []
		self.addBroadcastAdresses(self.loadBroadcasts())

	# load, save broadcasts 

	def loadBroadcasts(self):
		'''read all broadcast addresses from a file'''
		with open('.broadcasts', 'r') as f:
			return self.str2broadcasts(f.read())

	def str2broadcasts(self, s):
		'''read a list of lists of broadcastadresses from a file'''
		r= []
		for l in s.split('\n'):
			addrs= l.split(';')
			for addr in addrs:
				if self.isValidAddress(addr):
					r.append(addr)
		return r

	@staticmethod
	def isValidAddress(addr):
		'''=> bool wether the given address is a valid'''
		if not addr:
			return False
		for b in addr:
			if b in '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_:.':
				pass
			else:
				return False
		return True

	def saveBroadcasts(self, b):
		'''save all broadcast adresses to a file'''
		with open('.broadcasts', 'a') as f:
			f.write(self.broadcasts2str(b))

	@staticmethod
	def broadcasts2str(b):
		'''return a string representing the list of  list of broadcastadresses'''
		s= ';'.join(b) + '\n'
		return s

	@staticmethod
	def escape(b):
		'''escape the bytes newline'''
		if type(b) is str:
			return b.translate({'\\': '\\\\', '\n': '\\n'})
		b2= b''
		for b in b:
			if b == b'\n':
				b2+= b'\\n'
			elif b == '\\':
				b2+= b'\\\\'
			else:
				b2+= bytes((b,))
		return b2

	@staticmethod
	def unescape(b):
		'''revert the escapeing of the newline'''
		if type(b) is str:
			return b.translate({b'\\n': b'\n', b'\\\\': b'\\'})
		b2= last= b''
		for b in b:
			if b == b'\\':
				if last == b'\\':
					last= b''
					b2+= b'\\'
			elif b == 'n':
				if last == b'\\':
					b2+= b'\n'
			else:
				b2+= bytes((b,))
			last = b
		return b2


	def broadcastState(self, packet):
		'''broadcast the state of this node'''
		user= getattr(self, 'user', None)
		if user is None:
			user= self.manager.searchPlugin('User')
		name=  user.get('name', '')
		node=  self.backend.getNodeId()
		state= user.get('state', '')
		#
		packet.command= 'recvBroadcast'
		packet.type= packet.TYPE_REQUEST
		packet.handle+= 2
		broadcastAdresses= self.broadcasts2str(self.getBroadcastAdresses())
		packet.data= '\n'.join([self.escape(name), \
								 self.escape(node), \
								 self.escape(state),
								 self.escape(broadcastAdresses)])
		self.sendBroadcast(packet)

	def recvBroadcast(self, packet):
		'''recv a broadcast sent by broadcastState'''
		self.server.nodeAnnounce(packet) # inform server about node address
		l= packet.data.split(b'\n')
		# user name
		if len(l) >= 1:
			name= self.unescape(l[0])
		else:
			return
		# node id
		if len(l) >= 2:
			node= self.unescape(l[1]).decode('UTF-8')
		else:
			return
		# state
		if len(l) >= 3:
			state= self.unescape(l[2])
			# fix: what happes if recved state?
		else:
			state= b''
		# broadcast addresses
		if len(l) >= 4:
			ba= self.unescape(l[3]).decode('UTF-8')
			# decode the addresses
			ba= self.str2broadcasts(ba)
			self.addBroadcastAdresses(ba)
		else:
			state= b''
		# fix: save the tuple of name and node

	def getBroadcastAdresses(self):
		'''return the list of known broadcast addresses'''
		# [['255.255.255.255', '172.16.59.255', '172.16.23.255']]
		return self.baddrs

	def recvCommand(self, pack):
		'''recv a command'''
		if pack.command.startswith('broadcastState'):
			# broadcast the state of this node
			self.broadcastState(pack)
			#self.sendBroadcast(pack)
		elif pack.command.startswith('recvBroadcast'):
			# broadcast the state of this node
			self.recvBroadcast(pack)
			#self.sendBroadcast(pack)

	def sendBroadcast(self, packet):
		'''send a packet to all broadcast adresses'''
		for conn in self.backend.getNodeConnections(":broadcast"):
			conn.sendRequest(packet)

	def addBroadcastAdresses(self, l):
		'''add the broadcastadresses we do not know
and add them also as connection'''
		l2= self.getBroadcastAdresses()
		for a in set(l):
			if a not in l2:
				# fix: right function name?
				self.addServerBroadcastConnection(a)
				# if no error: append
				self.baddrs.append(a)

	def addServerBroadcastConnection(self, addr):
		'''add a server broadcast connection to the given address'''
		self.server.addBroadcastAddress(addr)


if __name__ == '__main__':
	class X:
		def __init__(self, name):
			self.name= name
		def __getattribute__(self, attr):
			name= object.__getattribute__(self, 'name')
			print('getting', name, '.', attr)
			return X(name + '.' + attr)
		def __call__(self, *args, **kw):
			name= object.__getattribute__(self, 'name')
			print('calling', name, args, kw)

	p= Broadcast(X('a'),X('b'),X('c'))
	p.init()
	b= b'123456789\\n\n\\\n\\n\n\\n\n\n\n\n\\rbhsdrge\n\\nn\n\dn '
	print(b)
	print(p.escape(b))
	print(p.unescape(p.escape(b)))
	assert p.unescape(p.escape(b)) == b
