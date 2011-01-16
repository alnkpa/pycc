import Plugin
import connection

class ConnectionPlugin(Plugin.Plugin):
	'''The class implemented the network management and routing for pycc
	'''
	#names under which the plugins wants to be registered
	registeredCommands=['getnodeid','connectto','relay','status']
	priority=0

	#Any command send from the PyCCManager will be here
	def recvCommand(self, package):
		'''all commands for this plugin are passed to this function

con is of type backend.connection.PyCCPackage
'''
		if package.type != connection.PyCCPackage.TYPE_REQUEST:
			return
		if package.command == 'getnodeid':
			package.data=self.PyCCManager.server.nodeID
			package.connection.sendResponse(package)
		elif package.command == 'status':
			package.data=self.PyCCManager.server.status()
			package.connection.sendResponse(package)
		elif package.command.startswith('connectto'):
			args=package.command.split(' ')
			if len(args)==2:
				args.append(62533)
			if len(args)!=3:
				return None
			else:
				print(args)
				self.PyCCManager.server.openConnection(args[1],int(args[2]))
		elif package.command.startswith('relay'):
			args=package.command.split(' ')
			if len(args)!=2:
				return None
			else:
				for con in self.PyCCManager.server.getConnectionList(args[1]):
					con.send(package.data)
