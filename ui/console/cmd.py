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
