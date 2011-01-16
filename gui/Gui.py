''' GUI for PYCC with resizing elements '''

import tkinter as tk
import Frontend
import Preferences

class MainWindow(tk.Tk):

	def __init__(self):
		''' creating and packing elements of the GUI '''
		tk.Tk.__init__(self)
		self.title("PYCC")
		self.openChats = []
		self.curChat = ''
		
		self.prefs = Preferences.Preferences('preferences.cfg')
		
		# chat selection
		self.fChatSelection = tk.Frame(self)
		self.fChatSelection.grid(row = 0, column = 0, sticky = 'w')
		# set current selected button to None
		self.activeButton = None

		# selection between contact list and preferences
		self.fMenue = tk.Frame(self)
		self.fMenue.grid(row = 0, column = 1)
		self.bContacts = tk.Button(self.fMenue, text = 'Contacts', command = self.displayContacts, width = 6)
		self.bContacts.config(relief = tk.SUNKEN)
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
		self.tText = tk.Text(self.fText, yscrollcommand = self.sText.set, height = 4, state = 'disabled')
		self.tText.pack(side = 'left', fill = 'x', expand = True)
		self.sText.config(command = self.tText.yview)

		# preferences
		self.fPreferences = tk.Frame(self)
		self.fPreferences.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.sPreferences = tk.Scrollbar(self.fPreferences)
		self.sPreferences.pack(side = 'right', fill='y')
		self.luserPreferences = tk.Label(self.fPreferences, text = 'Username:')
		self.luserPreferences.pack()
		self.userNamePreferences = tk.Text(self.fPreferences, height = 1, width = 22)
		self.userNamePreferences.insert(tk.END, self.prefs.username)
		self.userNamePreferences.pack()
		self.bOk = tk.Button(self.fPreferences, text = 'OK')
		self.bOk.pack()
	
		# contact list
		self.fContacts = tk.Frame(self)	
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.sContacts = tk.Scrollbar(self.fContacts)
		self.sContacts.pack(side = 'right', fill = 'y')	
		self.lContacts = tk.Listbox(self.fContacts, yscrollcommand = self.sContacts.set)
		self.lContacts.pack(side = 'left', fill = 'y')
		self.sContacts.config(command = self.lContacts.yview)
		
		# chat buttons
		self.fChatButtons = tk.Frame(self)
		self.fChatButtons.grid(row = 3, column = 0, sticky = 'w')
			
		self.bSend = tk.Button(self.fChatButtons, text = 'Send', command = self.sendMessage, width = 10, state = 'disabled')
		self.bSend.pack(side = 'left')		
		self.bCloseChat = tk.Button(self.fChatButtons, text = 'Close Chat', command = self.closeChat, width = 10, state = 'disabled')
		self.bCloseChat.pack(side = 'left')

		# define expanding rows and columns
		self.rowconfigure(1 , weight = 1)
		self.columnconfigure(0 , weight = 1)

		# define events
		self.lContacts.bind('<Double-ButtonPress-1>', self.startChat)
		self.tText.bind('<KeyRelease-Return>', self.sendMessage)
		self.tText.bind('<Shift-KeyRelease-Return>', self.newline)
		
		self.frontend = Frontend.Frontend()
		started = self.frontend.startBackend()
		if not started:
			print('Fehler!!!!')
		else:
			self.frontend.updateLoopTkinter(self)

	def displayPreferences(self):
		''' hide contanct list and show preferences instead '''
		self.fContacts.grid_forget()
		self.fPreferences.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.bPreferences.config (relief = tk.SUNKEN)	
		self.bContacts.config (relief = tk.RAISED)

	def displayContacts(self):
		''' hide preferences and show contact list instead '''
		self.fPreferences.grid_forget()
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.bContacts.config (relief = tk.SUNKEN)
		self.bPreferences.config (relief = tk.RAISED)

	def showMessage(self,message,user):
		''' print message slightly formated in the chat window '''
		self.tChatWindow.config(state = 'normal')
		if self.tChatWindow.get('1.0','end').strip() != '':
			self.tChatWindow.insert('end','\n\n')	
		self.tChatWindow.insert('end','~ {0}:\n{1}'.format(user,message))
		self.tChatWindow.config(state = 'disabled')
		self.textDown()
				
	def sendMessage(self, *event):
		''' delete message from input window and show it in the chat window '''
		
		if self.tText.get('1.0','end').strip() != '':
			message = self.tText.get('1.0','end').strip()
			self.showMessage(message,'Me')
			self.frontend.sendRequest(('sendMessage', message.encode('UTF-8'), self.messageSent))
			self.tText.delete('1.0','end')
				
	def messageSent(self, package):
		if package.type == package.TYPE_RESPONSE:
			pass
		elif package.type == package.TYPE_ERROR:
			print('error', package.data)

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
		# set currently activeButton's style back to standard
		if(self.activeButton != None):
			self.activeButton.config(relief = tk.RAISED)
		# get contact's name from index
		index = int(self.lContacts.curselection()[0])
		name = self.lContacts.get(index)
		# if chat with contact already exists, switch method
		if name in self.openChats:
			self.switchChat(name)
		else:
			self.title('PYCC - ' + name)
			if self.openChats == []:
				self.tText.config(state = 'normal')
				self.bSend.config(state = 'normal')
				self.bCloseChat.config(state = 'normal')
			# cache current chat, clear windows
			if self.curChat != '':
				self.cacheChat(self.curChat)
				self.clearChat()
			# dynamically create button and cache name from contact's name with exec
			button = 'self.b' + name
			cache = 'self.c' + name
			buttonFunc = lambda s = self, n = name: s.switchChat(n)
			exec(button + '= tk.Button(self.fChatSelection, text = name, command = buttonFunc)')
			# style button, mark as selected button
			exec(button + '.config(relief = tk.SUNKEN)')
			# set currently active button to pressed button
			exec("self.activeButton = " + button)
			exec(button + '.pack(side = \'left\')')
			exec(cache + '= [\'\',\'\']')


			
			self.openChats.append(name)
			self.curChat = name

	def switchChat(self,name):
		''' switch from on chat into another
		cache current chat, insert new chat content into windows		
		'''
		self.title('PYCC - ' + name)
		if self.curChat != '':
			self.cacheChat(self.curChat)
		self.clearChat()
		self.readCache(name)
		self.curChat = name
		self.activeButton.config(relief = tk.RAISED)
		exec('self.activeButton = self.b' + name)
		exec('self.b' + name + '.config(relief = tk.SUNKEN)')

	def closeChat(self):
		button = 'self.b' + self.curChat
		cache = 'self.c' + self.curChat
		exec(button + '.forget()')
		exec('del(' + button + ')')
		exec('del(' + cache + ')')
		i = self.openChats.index(self.curChat)
		self.openChats.pop(i)
		self.curChat = ''
		if len(self.openChats) != 0:
			self.switchChat(self.openChats[i-1])
		else:			
			self.clearChat()			
			self.tText.config(state = 'disabled')
			self.bSend.config(state = 'disabled')
			self.bCloseChat.config(state = 'disabled')

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
		
	def newline(self, event):
		line = self.tText.index('insert').split('.')[0]
		self.tText.mark_set('insert',line + '.0')
		
	def textDown(self):
		self.tChatWindow.see(tk.END)
		self.tText.see(tk.END)

	

# open window if not imported
if __name__ == '__main__':
	window = MainWindow()
	window.loadContacts(['Eric', 'Stanley', 'Kyle', 'Kenny', 'Martin', 'Leo', 'Dennis', 'Kevin', 'George', 'Maria', 'Achmed'])
	window.mainloop()
