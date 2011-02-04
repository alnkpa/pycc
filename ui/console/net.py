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
		run = True
		while run:
			try:
				data = self.pyccConnection.parseInput()
			except socket.timeout:
				continue
			except socket.error:
				run = False
				continue
			if data is False:
				self.run = False
			
			if type(data) is not list:
				continue
			for package in data:
				if type(package) is not connection.PyCCPackage:
					continue
				self.inputQueue.put(package)
			self.notifyEvent.set()


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
		work = True
		self.requestAccountList()
		while work and self.notifyEvent.wait(): # wait for new input packages or console request
			while not self.inputQueue.empty():
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

			while not self.todoQueue.empty():
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
			self.notifyEvent.clear()

	def sendPackage(self, package, callback=None):
		if callback is not None:
			self.callbacks[package.handle]=callback
		self.pyccConnection.sendPackage(package)

	def newRequest(self):
		package = connection.PyCCPackage()
		package.type = package.TYPE_REQUEST
		package.handle = self.pyccConnection.newRequest()
		return package

	def sendStatus(self):
		package = self.newRequest()
		package.command = 'status'
		self.sendPackage(package, self.recvStatus)

	def recvStatus(self, package):
		print(package.data.decode('utf8'))
		self.syncRequestEvent.set()

	def connectTo(self, args):
		package = self.newRequest()
		package.command = 'connectTo {0}'.format(args)
		self.sendPackage(package)
		self.syncRequestEvent.set()

	def shutdown(self):
		package = self.newRequest()
		package.command = 'shutdown'
		self.sendPackage(package)
		self.syncRequestEvent.set()

	def requestAccountList(self):
		package = self.newRequest()
		package.command = 'getAccounts'
		self.sendPackage(package, self.getAccountList)

	def getAccountList(self, package):
		try:
			self.accountLock.acquire()
			self.accounts = {user.split(":")[0]: user.split(":")[1] for user in  package.data.decode('utf8').split(",") }
			self.accountLock.release()
		except:
			print("error")

	def sendMessage(self, user, message):
		package = self.newRequest()
		package.command = 'sendMessage {0}'.format(user)
		package.data = message
		self.sendPackage(package, self.recvStatus)
		self.syncRequestEvent.set()
