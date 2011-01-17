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
    registeredCommands= ['broadcastState']
    def init(self):
        self.baddrs= []
        self.addBroadcastAdresses(self.loadBroadcasts())

    # load, save broadcasts 

    def loadBroadcasts(self):
        '''read all broadcast addresses from a file'''
        with open('.broadcasts', 'a+') as f:
            return self.str2broadcasts(f.read())

    @staticmethod
    def str2broadcasts(s):
        '''read a list of lists of broadcastadresses from a file'''
        r= []
        for l in s.split('\n'):
            addrs= l.split(';')
            r.extend(addrs)
        return r

    def saveBroadcasts(self, b):
        '''save all broadcast adresses to a file'''
        with open('.broadcasts', 'a') as f:
            f.write(self.broadcasts2str(b))

    @staticmethod
    def broadcasts2str(b):
        '''return a string representing the list of  list of broadcastadresses'''
        s+= ';'.join(b) + '\n'
        return s

    @staticmethod
    def escape(b):
        '''escape the bytes newline'''
        return b.translate({b'\\': b'\\\\', b'\n': b'\\n'})

    @staticmethod
    def unescape(b):
        '''revert the escapeing of the newline'''
        return b.translate({b'\\n': b'\n', b'\\\\': b'\\'})

    def broadcastState(self, packet):
        '''broadcast the state of this node'''
        user= self.manager.searchPlugin('User')
        name=  user['name']
        node=  self.PyCCManager.server.getNodeId()
        state= user.get('state', '')
        #
        packet.command= 'recvBroadcast'
        packet.type= packet.TYPE_REQUEST
        packet.handle+= 2
        broadcastAdresses= self.broadcasts2str(self.getBroadcastAdresses())
        broadcastAdresses.encode('UTF-8')
        packet.data= b'\n'.join([self.escape(name), \
                                 self.escape(node), \
                                 self.escape(state),
                                 self.escape(broadcastAdresses)])
        self.sendBroadcast(packet)

    def recvBroadcast(self, packet):
        '''recv a broadcast sent by broadcastState'''
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
        if pack.startswith('broadcastState'):
            # broadcast the state of this node
            self.sendBroadcast(pack)

    def sendBroadcast(self, packet):
        '''send a packet to all broadcast adresses'''
        for conn in self.PyCCManager.server.getConnectionList("broadcast"):
            conn.send(packet)
                
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
        self.PyCCManager.server.addBroadcastConnection(addr)


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

    p= Broadcast(X('c'))
    p.init()
    b= b'123456789\\n\n\\\n\\n\n\\n\n\n\n\n\\rbhsdrge\n\\nn\n\dn '
    print(b)
    print(p.escape(b))
    print(p.unescape(p.escape(b)))
    assert p.unescape(p.escape(b)) == b
