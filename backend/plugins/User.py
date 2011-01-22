import Plugin

class User (Plugin.Plugin):
    '''This is the class for information about users

use it like this: 
command= "user attribute"
data= b"value"

so the value of attribute is set to value


'''
    registeredCommands= ['user']
    def init(self):
        '''initialize the class'''
        self.attributes= {} # 'str' : bytes


    def recvCommand(self, packet):
        attr= packet.command.split(' ')[1]
        self[attr]= packet.data

    def __getitem__(self, item):
        return self.attributes[item]
        
    def __setitem__(self, item, value):
        self.attributes[item]= value

    def get(self, *args):
        return self.attributes.get(*args)
