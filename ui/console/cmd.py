import cmd
import connection

class pyccConsole(cmd.Cmd):

	debug=True

	prompt = '> '

	def __init__(self, backendConnection, logicThread, todoQueue, notifyEvent, *args, **kargs):
		cmd.Cmd.__init__(self,*args,**kargs)
		self.backendConnection = backendConnection
		self.logicThread = logicThread
		self.todoQueue = todoQueue
		self.notifyEvent = notifyEvent

	def completenames(self, text, *ignored):
		''' add blank to commands for faster completion'''
		return [complete + ' ' for complete in cmd.Cmd.completenames(self, text, *ignored)]

	def do_status(self, args):
		''' list information about open connections and other backend information'''
		self.todoQueue.put(('status', None))
		self.notifyEvent.set()
		self.logicThread.syncRequestEvent.clear()
		if not self.logicThread.syncRequestEvent.wait(1):
			print('request timed out')


	def do_connectTo(self, args):
		''' open connection to pycc (relay) server'''
		self.todoQueue.put(('connectTo', args))
		self.notifyEvent.set()
		self.logicThread.syncRequestEvent.clear()
		if not self.logicThread.syncRequestEvent.wait(1):
			print('request timed out')


	def do_shutdown(self, args):
		''' shutdown pycc backend and exit console'''
		self.todoQueue.put(('shutdown', None))
		self.notifyEvent.set()
		if not self.logicThread.syncRequestEvent.wait(1):
			print('request timed out')
		return True

	def emptyline(self):
		pass

	def do_EOF(self, line):
		''' close console'''
		return True


	def do_list(self, args):
		''' sends message to other chat user'''
		self.todoQueue.put(('list', None))
		self.notifyEvent.set()
		self.logicThread.syncRequestEvent.clear()
		if not self.logicThread.syncRequestEvent.wait(0.2):
			print('request timed out')


	def do_sendMessage(self, args):
		''' sends message to other chat user'''
		args = args.split(' ')
		if len(args) == 1: # no message
			message = ''
			readMore = True
			while readMore:
				newMessage = input('|')
				if newMessage:
					if newMessage[-1] == '\\':
						message += newMessage[0:-1] + '\n'
					else:
						message += newMessage + '\n'
				else:
					readMore = False
		else:
			message = " ".join(args[1:])
		self.todoQueue.put(('sendMessage', args[0], message[0:-1]))
		self.notifyEvent.set()
		self.logicThread.syncRequestEvent.clear()
		if not self.logicThread.syncRequestEvent.wait(0.2):
			print('request timed out')

	def complete_sendMessage(self, text, line, start_index, end_index):
		try:
			self.logicThread.accountLock.acquire()
			if text:
				return [
					useraccount + ' ' for useraccount in self.logicThread.accounts
					if useraccount.startswith(text)
				]
			else:
				return list(self.logicThread.accounts.keys())
		finally:
			self.logicThread.accountLock.release()
