import threading
import connection
import socket

class networkThread(threading.Thread):

	def __init__(self, pyccConnection, inputQueue, notifyEvent):
		threading.Thread.__init__(self)
		self.pyccConnection = pyccConnection
		self.inputQueue = inputQueue
		self.notifyEvent = notifyEvent

	def run(self):
		''' main loop of theard'''
		run = True
		while run:
			try:
				data = self.pyccConnection.parseInput()
			except socket.timeout:
				continue
			except socket.error:
				run = False
				continue
			if data is False: # connection closed
				self.run = False

			if type(data) is not list: # no new packages
				continue
			for package in data:
				if type(package) is not connection.PyCCPackage:
					continue
				# send package to logicThread
				self.inputQueue.put(package)
			self.notifyEvent.set() # new data for logicThread


class logicThread(threading.Thread):

	def __init__(self, pyccConnection, inputQueue, todoQueue, notifyEvent):
		threading.Thread.__init__(self)
		self.pyccConnection = pyccConnection
		self.inputQueue = inputQueue
		self.todoQueue = todoQueue
		self.notifyEvent = notifyEvent
		self.syncRequestEvent = threading.Event()
		self.callbacks = {}
		self.accounts = {}
		self.accountLock = threading.Lock()

	def run(self):
		''' main loop of thread'''
		work = True
		self.requestAccountList()
		while work and self.notifyEvent.wait(): # wait for new input packages or console request
			while not self.inputQueue.empty(): # handle all packages from net
				package = self.inputQueue.get()
				if package.handle in self.callbacks:
					self.callbacks[package.handle](package)
					continue
				print('$$$${type}{handle}:{command}'.format(type=package.type,
					handle=package.handle,command=package.command))
				try:
					print(package.data.decode('utf8'))
				except AttributeError:
					pass
				except UnicodeError:
					print(package.data)

			while not self.todoQueue.empty(): # handle data from cmd
				newData = self.todoQueue.get()
				if 'stop' in (newData,newData[0]):
					work = False
					break
				if newData[0] == 'status':
					self.sendStatus()
					continue
				if newData[0] == 'connectTo':
					self.connectTo(newData[1])
					continue
				if newData[0] == 'shutdown':
					self.shutdown()
					continue
				if newData[0] == 'sendMessage':
					self.sendMessage(newData[1], newData[2])
					continue
				if newData[0] == 'list':
					self.sendList()
					continue
			self.notifyEvent.clear() # all task done

	def sendPackage(self, package, callback=None):
		''' send a package to backend - support for callback methods'''
		if callback is not None:
			self.callbacks[package.handle]=callback
		self.pyccConnection.sendPackage(package)

	def newRequest(self):
		''' return new PyCCPackage (type is request)'''
		package = connection.PyCCPackage()
		package.type = package.TYPE_REQUEST
		package.handle = self.pyccConnection.newRequest()
		return package

	def sendStatus(self):
		''' send status command to backend'''
		package = self.newRequest()
		package.command = 'status'
		self.sendPackage(package, self.recvStatus)

	def recvStatus(self, package):
		''' get status response'''
		print(package.data.decode('utf8'))
		self.syncRequestEvent.set()

	def connectTo(self, args):
		''' send connetTo to backend'''
		package = self.newRequest()
		package.command = 'connectTo {0}'.format(args)
		self.sendPackage(package)
		self.syncRequestEvent.set()

	def shutdown(self):
		''' send shutdown to backend'''
		package = self.newRequest()
		package.command = 'shutdown'
		self.sendPackage(package)
		self.syncRequestEvent.set()

	def requestAccountList(self):
		''' ask backend for list of all accounts'''
		package = self.newRequest()
		package.command = 'getAccounts'
		self.sendPackage(package, self.getAccountList)

	def getAccountList(self, package):
		''' get response for account list request'''
		try:
			self.accountLock.acquire()
			self.accounts = {user.split(":")[0]: user.split(":")[1] for user in  package.data.decode('utf8').split(",") }
			self.accountLock.release()
		except:
			print("error")

	def sendMessage(self, user, message):
		''' send message to other user'''
		package = self.newRequest()
		package.command = 'sendMessage {0}'.format(user)
		package.data = message
		self.sendPackage(package, self.recvStatus)
		self.syncRequestEvent.set()

	def sendList(self):
		''' send listContactStates to backend'''
		package = self.newRequest()
		package.command = 'listContactStates'
		self.sendPackage(package, self.recvList)

	def recvList(self, package):
		''' get listContactStates response'''
		print(package.data.decode('utf8'))
		self.syncRequestEvent.set()
