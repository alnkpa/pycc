#!/usr/bin/env python3
import os
import os.path
os.chdir(os.path.realpath(os.path.join(os.path.split(__file__)[0],'..')))
import sys
sys.path.append('.')
sys.path.append('./backend')
sys.path.append('./backend/plugins')
import connection
import ui.console
import socket
import time
import queue
import threading

try:
	socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	if len(sys.argv)>1:
		host = sys.argv[1]
	else:
		host = '127.0.0.1'
	if len(sys.argv) > 2:
		port = int(sys.argv[2])
	else:
		with open('.port') as file:
			port=int(file.readline().strip())
	socket.connect((host, port))
	con=connection.PyCCConnection(socket,'console')
	socket.settimeout(0.1)

	inputQueue = queue.Queue()
	todoQueue = queue.Queue()
	notifyEvent = threading.Event()

	connectionThread = ui.console.networkThread(con, inputQueue, notifyEvent)
	connectionThread.start()

	logicThread = ui.console.logicThread(con, inputQueue, todoQueue, notifyEvent)
	logicThread.start()

	cmd = ui.console.pyccConsole(con, logicThread, todoQueue, notifyEvent, 'tab')
	cmd.cmdloop()


finally:
	try:
		connectionThread
		todoQueue.put(("stop",None))
		notifyEvent.set()
		logicThread.join()
	except NameError:
		pass
	try:
		socket.close()
		connectionThread.join()
	except NameError:
		pass
	print()
