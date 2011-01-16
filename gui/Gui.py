<<<<<<< HEAD
import tkinter as tk

class MainWindow(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)

		self.title('PYCC')



# menue frame
		self.fMenue = fMenue = tk.Frame(root)

		bContacts = tk.Button(fMenue, text = "C", command = displayContacts)
		bContacts.pack(side = tk.LEFT)
		bPreferences = tk.Button(fMenue, text = "P", command = displayPreferences)
		bPreferences.pack(side = tk.RIGHT)

		fMenue.grid(row = 0, column = 1)

# preferences frame
		self.fPreferences = fPreferences = tk.Frame(root)
		lPref = tk.Label(fPreferences, text = "Einstellungen")
		lPref.pack()

# contact list frame
		self.fContacts = fContacts = tk.Frame(root)
		fContactsScrollbar = tk.Scrollbar(fContacts)
		fContactsScrollbar.pack(side = tk.RIGHT, fill = tk.Y)

		fContactlist = tk.Listbox(fContacts, height= 27, yscrollcommand = fContactsScrollbar.set)
		fContactsList.pack(side = tk.LEFT, fill = tk.BOTH)
		fContactsScrollbar.config(command = fContactsList.yview)

		fContacts.grid(row = 1, column = 1, rowspan = 3)

# chat selection frame
		self.fChatSelection = fChatSelection = tk.Frame(root)
=======
''' GUI for PYCC with resizing elements '''
>>>>>>> 4c48e724d76f39f1e36fac04dc81fd1b9deb3b47

import tkinter as tk

<<<<<<< HEAD

# chat window frame
		self.fChatWindow = fChatWindow = tk.Frame(root)
		fChatWindowScrollbar = tk.Scrollbar(fChatWindow)
		fChatWindowScrollbar.pack(side = tk.RIGHT, fill = tk.Y)
		fChatWindowText = tk.Text(fChatWindow, yscrollcommand = fChatWindowScrollbar.set)
		fChatWindowText.pack(side = tk.LEFT, fill = tk.BOTH)
		fChatWindowScrollbar.config(command = fChatWindowText.yview)
		fChatWindow.grid(row = 1, column = 0)

# chat entry frame
		self.fText = fText = tk.Frame(root)

		fTextScrollbar = tk.Scrollbar(fText)
		fTextText = tk.Text(fText, yscrollcommand = fTextScrollbar.set, height = 4, width = 72)
		fTextText.pack(side = tk.LEFT, fill = tk.BOTH)
		fTextScrollbar.config(command = fTextText.yview)
		
		bSend = tk.Button(fText, text = "Send", command = send)
		bSend.pack(side = tk.RIGHT, fill = tk.Y)
		fTextScrollbar.pack(side = tk.RIGHT, fill = tk.Y)

		fText.grid(row = 2, column = 0)

# functions
	def displayContacts(self, a=0):
		print("Display Contacts")
	
	def displayPreferences(self, a=0):
		print("Display Preferences")
	
	def send(self, a=0):
		print("Send a message")

#Methoden:
def empfange(msg, addr):
	pass

def sende(msg, addr):
	print(msg)

def add_contact(addr):

def remove_contact(addr):

def 



	root = tk.Tk()
	root.title("PYCC")

	root.mainloop()

## send button
#bSend = tk.Button(root, text = "Send", command = send)
#bSend.grid(row = 3, column = 0)
=======
class MainWindow(tk.Tk):

	def __init__(self):
		''' creating and packing elements of the GUI '''
		tk.Tk.__init__(self)
		self.title("PYCC")
		self.openChats = []
		self.curChat = ''

		# chat selection
		self.fChatSelection = tk.Frame(self)
		self.fChatSelection.grid(row = 0, column = 0, sticky = 'w')

		# selection between contact list and preferences
		self.fMenue = tk.Frame(self)
		self.fMenue.grid(row = 0, column = 1)
		self.bContacts = tk.Button(self.fMenue, text = 'Contacts', command = self.displayContacts, width = 6)
		self.bContacts.pack(side = 'left')
		self.bPreferences = tk.Button(self.fMenue, text = 'Prefs', command = self.displayPreferences, width = 6)
		self.bPreferences.pack(side = 'left')

		# chat window
		self.fChatWindow = tk.Frame(self)	
		self.fChatWindow.grid(row = 1, column = 0, sticky = 'nswe')
		self.sChatWindow = tk.Scrollbar(self.fChatWindow)
		self.sChatWindow.pack(side = 'right', fill = 'y')
		# read-only; switch back to state = 'normal' to insert text	
		self.tChatWindow = tk.Text(self.fChatWindow, yscrollcommand = self.sChatWindow.set, height = 20, state = 'disabled')
		self.tChatWindow.pack(side = 'left', fill = 'both', expand = True)
		self.sChatWindow.config(command = self.tChatWindow.yview)

		# input window
		self.fText = tk.Frame(self)	
		self.fText.grid(row = 2, column = 0, sticky = 'nswe')
		self.sText = tk.Scrollbar(self.fText)
		self.sText.pack(side = 'right', fill = 'y')	
		self.tText = tk.Text(self.fText, yscrollcommand = self.sText.set, height = 4)
		self.tText.pack(side = 'left', fill = 'x', expand = True)
		self.sText.config(command = self.tText.yview)

		# contact list
		self.fContacts = tk.Frame(self)	
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.sContacts = tk.Scrollbar(self.fContacts)
		self.sContacts.pack(side = 'right', fill = 'y')	
		self.lContacts = tk.Listbox(self.fContacts, yscrollcommand = self.sContacts.set)
		self.lContacts.pack(side = 'left', fill = 'y')
		self.sContacts.config(command = self.lContacts.yview)
		
		# preferences
		self.fPreferences = tk.Frame(self)
		self.lPreferences = tk.Label(self.fPreferences, text = 'Preferences')
		self.lPreferences.pack()
		
		# send button
		self.bSend = tk.Button(self, text = 'Send', command = self.sendMessage, width = 10)
		self.bSend.grid(row = 3, column = 0, sticky = 'w')

		# define expanding rows and columns
		self.rowconfigure(1 , weight = 1)
		self.columnconfigure(0 , weight = 1)

		# define events
		self.lContacts.bind('<Double-ButtonPress-1>', self.startChat)
		self.tText.bind('<KeyPress-Return>', self.sendMessage)

	def displayPreferences(self):
		''' hide contanct list and show preferences instead '''
		self.fContacts.grid_forget()
		self.fPreferences.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')

	def displayContacts(self):
		''' hide preferences and show contact list instead '''
		self.fPreferences.grid_forget()
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')

	def showMessage(self,message,user):
		''' print message slightly formated in the chat window '''
		self.tChatWindow.config(state = 'normal')
		self.tChatWindow.insert('end','~ {0}:\n{1}\n\n'.format(user,message))
		self.tChatWindow.config(state = 'disabled')

	def sendMessage(self, *event):
		''' delete message from input window and show it in the chat window '''
		if self.tText.get('1.0','end').strip() != '':
			message = self.tText.get('1.0','end').strip()
			self.showMessage(message,'Me')
			self.tText.delete('1.0','end')

	def loadContacts(self, contacts):
		''' fill contact list or add contact
		parameter contacts has to be an iterable instance of nicknames
		'''
		for contact in contacts:
			self.lContacts.insert('end',contact)

	def startChat(self, event):
		''' event: doubleclick on contact list
		save current chat in cache
		create new button in fChatSelection, create new cache for chat
		'''	
		# get contact's name from index
		index = int(self.lContacts.curselection()[0])
		name = self.lContacts.get(index)
		# if chat with contact already exists, switch method
		if name in self.openChats:
			self.switchChat(name)
		else:
			self.title('PYCC - ' + name)
			# cache current chat, clear windows
			if self.curChat != '':
				self.cacheChat(self.curChat)
				self.clearChat()
			# dynamically create button and cache name from contact's name with exec
			button = 'self.b' + name
			cache = 'self.c' + name
			buttonFunc = lambda s = self, n = name: s.switchChat(n)
			exec(button + '= tk.Button(self.fChatSelection, text = name, command = buttonFunc)')
			exec(button + '.pack(side = \'left\')')
			exec(cache + '= [\'\',\'\']')
			
			self.openChats.append(name)
			self.curChat = name

	def switchChat(self,name):
		''' switch from on chat into another
		cache current chat, insert new chat content into windows		
		'''
		self.title('PYCC - ' + name)
		self.cacheChat(self.curChat)
		self.clearChat()
		self.readCache(name)
		self.openChats.append(name)
		self.curChat = name
		
	def cacheChat(self,name):
		''' save content of tChatWindow and tText in cache list of name '''
		cache = 'self.c' + name		
		exec(cache + '[0] = self.tChatWindow.get(\'1.0\',\'end\').strip()')
		exec(cache + '[1] = self.tText.get(\'1.0\',\'end\').strip()')

	def readCache(self,name):
		''' insert content from cache list of name into tChatWindow and tText '''
		# tChatWindow is read-only -> has to made editable first
		self.tChatWindow.config(state = 'normal')
		cache = 'self.c' + name	
		exec('self.tChatWindow.insert(\'end\', ' +cache + '[0])')
		exec('self.tText.insert(\'end\', ' + cache + '[1])')
		self.tChatWindow.config(state = 'disable')

	def clearChat(self):
		''' remove all content from tChatWindow and tTest '''
		self.tChatWindow.config(state = 'normal')
		self.tChatWindow.delete('1.0','end')
		self.tText.delete('1.0','end')
		self.tChatWindow.config(state = 'disable')
		

# open window if not imported
if __name__ == '__main__':
	window = MainWindow()
	window.loadContacts(['Eric', 'Stanley', 'Kyle', 'Kenny'])
	window.mainloop()
>>>>>>> 4c48e724d76f39f1e36fac04dc81fd1b9deb3b47
