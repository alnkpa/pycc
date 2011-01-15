'''frontend - backend communication

Frontend for communacation from GUI to backend

'''


import subprocess
import socket
import os
import time

try:
    import pycc.backend.connection as connection
except:
    import sys
    sys.path.append('..')
    try:
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
    int of how many times the server attemts to connect
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
        self.callbacks= {} # connectionhandle (int) : function
        self.pipe= None

    def connect(self, addr, *args):
        '''connect to the server on a given address

connect(addr, socket.AF_INET, socket.SOCK_STREAM)
the optimal arguments are for the socket class
'''
        sock= socket.socket(*(args + self.defaultSocketArguments[len(args):]))
        sock.connect(addr)
        sock.setblocking(0)
        self.connection= connection.PyCCConnection(sock)
        self.socket= sock

    def sendRequest(self, package, callback= None):
        '''send a package to the server.

sendRequest(command)
sendRequest((command, data))
sendRequest(package)

callback is a function that accepts one argument - the response package
its class is of connection.PyCCPackage .



'''
        if type(package) is bytes:
            package= connection.PyCCPackage(command= package)
        elif type(package) is tuple:
            # command, data
            package= connection.PyCCPackage(command= package[0], \
                                            data= package[1])
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

    def update(self):
        '''look for responses and execute the callback functions

This function should be called regularily.
use updateLoopTkinter or other updateLoop functions to make thi happen.

return wether the connection is alive
'''
        while 1:
            try:
                package= self.connection.parseInput()
            except socket.error:
                break
            if package is None:
                continue
            if package is False:
                return False
            print ('update:package', package)
            callback= self.callbacks.get(package.handle, None)
            if callback is None:
                continue
            if not callback(package):
                self.callbacks.pop(package.handle)
        return True
        
    def updateLoopTkinter(self, widget, timeout= 1):
        '''this makes tkinter call update() every timeout miliseconds'''
        try:
            self.update()
        finally:
            widget.after(timeout, self.startTkinterUpdateLoop, widget, timeout)

    def startServer(self, command= None, timeout= 1):
        '''startServer() starts a server if no server is reacheable

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
        print(1)
        for i in range(self.serverStartupTries):
            if time.time() > t:
                break
            c= command[:]
            c.extend(['-port', str(port), '-searchPort', '0'])
            self.pipe= subprocess.Popen(c)
            print('poll:', self.pipe.poll())
            while self.pipe.poll() is None:
                print ('try connect')
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
                print('not connected')
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

    def closeServer(self):
        '''close the server started by this object'''
        if self.pipe is not None:
            try:
                self.pipe.terminate()
            except OSError:
                pass
        
if __name__ == '__main__':
    f= Frontend()
    s= f.startServer()
    print ('started:', s)
    if s:
        pass
    input()
    f.closeServer()
