'''frontend - backend communication

Frontend for communacation from GUI to backend

'''


import subprocess
import socket
import os
import time

try:
	# first try global import
	import pycc.backend.connection as connection
except:
	try:
		# second try local import from parent directory
		import backend.connection as connection
	except ImportError:
		import sys
		sys.path.append('..')
		try:
			# third try relative import from parent directory
			import backend.connection as connection
		finally:
			try:
				sys.path.remove('..')
			except ValueError:
				pass



class Frontend(object):
	'''The Frontend Class for GUI communication with the backend server

serverStartCommand
	the server start command in a list
serverPort
	the port we expect the server on
serverStartupTries
	int of how many times the server attemts to bind to its port
defaultSocketArguments
	default arguments for our socket
'''
	serverStartCommand= ['../bin/pyccBackend.py']
	serverPort= 6554
	serverStartupTries= 1000
	defaultSocketArguments= (socket.AF_INET, socket.SOCK_STREAM)
	
	def __init__(self):
		'''initialize the frontend class'''
		self.socket= None
		# connectionhandle (int) : function
		# command : function
		self.callbacks= {} 

		self.pipe= None

	def getNodeId(self):
		return 'frontend'

	def connect(self, addr, *args):
		'''connect to the server on a given address

connect(addr, socket.AF_INET, socket.SOCK_STREAM)
the optimal arguments are for the socket class
'''
		sock= socket.socket(*(args + self.defaultSocketArguments[len(args):]))
		sock.connect(addr)
		self.connection= connection.PyCCConnection(sock, self.getNodeId())
		self.update(responses= 1)
		self.socket= sock
		sock.setblocking(0)

	def sendRequest(self, package, callback= None):
		'''send a package to the server.

sendRequest(command)
sendRequest((command, data))
sendRequest(package)

callback is a function that accepts one argument - the response package
its class is of connection.PyCCPackage .



'''
		if type(package) is str:
			package= connection.PyCCPackage(command= package)
		elif type(package) is tuple:
			# command, data
			if type(package[0]) is not str:
				raise ValueError('first element of tuple must be of type str')
			if len(package) == 1:
				package= connection.PyCCPackage(command= package[0])
			else:
				if type(package[1]) is not bytes:
					raise ValueError('second element of tuple must be of type bytes')
				package= connection.PyCCPackage(command= package[0], data= package[1])
		elif not isinstance(package, connection.PyCCPackage):
			raise ValueError('package shoult be of type bytes, \
tuple of two bytes or connection.PyCCPackage')
		package.handle= self.connection.newRequest()
		self.connection.sendRequest(package)
		if callback is not None:
			if hasattr(callback, '__call__'):
				self.callbacks[package.handle]= callback
			else:
				raise ValueError('callback must be a function or None')
		return package.handle

	def addCallback(self, command, callback):
		'''register a callback for a given command

The callback function will be called with a packet as first and only argument.
'''
		if type(command) is not str:
			raise ValueError('command must be of type str not of type {0}'.format(type(command)))
		if not hasattr(callback, '__call__'):
			raise ValueError('callback must be callable like a function')
		self.callbacks[command]= callback

	def _handleCommand(self, packet):
		'''find and call the callback function for the given packet.'''
		for comm in self.callbacks:
			if type(comm) is str and packet.command.startswith(comm):
				return self.callback[comm](packet)
		

	def update(self, responses= -1):
		'''look for responses and execute the callback functions

This function should be called regularily.
use updateLoopTkinter or other updateLoop functions to make thi happen.

return wether the connection is alive
'''
		while responses:
			responses-= 1
			try:
				packages= self.connection.parseInput()
			except socket.error:
				break
			if packages is None:
				continue
			if packages is False:
				return False
			for package in packages:
				if package.type == package.TYPE_REQUEST:
					self._handleCommand(package)
					continue
				callback= self.callbacks.get(package.handle, None)
				if callback is None:
					continue
				if not callback(package):
					self.callbacks.pop(package.handle)
		return True
		
	def startBackend(self, command= None, timeout= 1):
		'''startBackend() starts a server if no server is reacheable

return value is True if a server could be started
otherwise False

timeout are seconds
'''
		if command is None:
			command= self.serverStartCommand
		port= self.serverPort
		if self.pipe is not None:
			self.pipe.terminate()
			self.pipe= None
		self.socket= None
		try:
			self.connect(('localhost', port))
		except socket.error:
			pass
		else:
			return True
		t= time.time() + timeout
		for i in range(self.serverStartupTries):
			if time.time() > t:
				break
			c= command[:]
			c.extend(['-port', str(port), '-searchPort', '0'])
			self.pipe= subprocess.Popen(c)
			while self.pipe.poll() is None:
				try:
					self.connect(('localhost', port))
					break
				except socket.error:
					# connection refused I assume?
					time.sleep(0.01)
					pass
				if t < time.time():
					break
			if self.socket is None:
				# not connected
				port+= 1
				try:
					self.pipe.terminate()
				except OSError:
					pass
				self.pipe= None
				continue
			else:
				break
		return self.pipe is not None
	startServer= startBackend

	def closeBackend(self):
		'''close the server started by this object'''
		if self.pipe is not None:
			try:
				self.pipe.terminate()
			except OSError:
				pass
	closeServer= closeBackend
		

	def updateLoopTkinter(self, widget, timeout= 1):
		'''this makes tkinter call update() every timeout miliseconds'''
		try:
			self.update()
		finally:
			widget.after(timeout, self.updateLoopTkinter, widget, timeout)


if __name__ == '__main__':
	import types
	if type(print) is not types.LambdaType:
		_print= print
		print= lambda *args:_print('#######################', *args)
	# get a frontend object
	f= Frontend()
 	# start a backend server and connect to it
	s= f.startBackend()
	if s:
		print ('The backend server could be started.')
	else:
		print ('Failed to start the backend server. exiting')
		exit(1)

	def respondToEcho(p):
		print ('echo responded')
		print ('\tcommand:', p.command)
		print ('\ttype:', p.type)
		if p.type == p.TYPE_REQUEST:
			print ('\t--- das war eine Anfrage! sollte ncht sein, da plugins antworten.')
		elif p.type == p.TYPE_RESPONSE:
			print ('\t--- echo antwortet!!')
			print ('\t--- wir verarbeiten die daten...')
			print ('\tdata:', p.data)
		elif p.type == p.TYPE_ERROR:
			print ('\tein fehler ist aufgetreten.. in data steht der code dafuer')
			print ('\tdata:', p.data)
		else:
			# never happens
			pass
		print ('\techo bearbeitet')
	print('sent request echo - awaiting response')
	f.sendRequest('echo', respondToEcho)
	print('-------------1----------------')
	time.sleep(1)
	print('-------------2----------------')
	f.update()
	print('-------------3----------------')
	f.sendRequest(('echo', b'testdaten sind bytes'), respondToEcho)
	print('-------------4----------------')
	time.sleep(0.5)
	f.update()
	print('-------------5----------------')
	while not input():
		# update blockiert nicht
		f.update()
	f.closeServer()
