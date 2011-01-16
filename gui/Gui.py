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
		#Username 
		self.userNamePreferences = tk.Text(self.fPreferences, height = 1, width = 22)
		self.userNamePreferences.insert(tk.END, self.prefs.username)
		self.userNamePreferences.pack()
		self.bOk = tk.Button(self.fPreferences, text = 'OK')
		self.bOk.pack()

		#Textcolor
		v = tk.IntVar()
		self.lColor =tk.Label(self.fPreferences, text = 'Textcolor:', height = 2)
		self.lColor.pack()
		self.rbRed = tk.Radiobutton(self.fPreferences, text = 'Red',variable = v,value = 1)
		self.rbRed.pack( anchor = tk.W )
		self.rbBlue = tk.Radiobutton(self.fPreferences, text = 'Blue',variable = v, value = 2)
		self.rbBlue.pack( anchor = tk.W )
		self.rbGreen = tk.Radiobutton(self.fPreferences, text = 'Green',variable = v, value = 3)
		self.rbGreen.pack( anchor = tk.W )
		self.rbBlack = tk.Radiobutton(self.fPreferences, text = 'Black',variable = v, value = 4)
		self.rbBlack.pack( anchor = tk.W )
		
		
 
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
		self.protocol('WM_DELETE_WINDOW', self.windowClosing)
		
		#frontend = Frontend()
		#list = self.frontend.sendRequest('getAccounts')	
		#print(list)
		
		self.frontend = Frontend.Frontend()
		started = self.frontend.startBackend()
		if not started:
			print('Fehler!!!!')
		else:
			self.frontend.updateLoopTkinter(self)
		
		self.frontend.sendRequest('getAccounts', self.gotAccounts)

	def windowClosing(self):
		self.frontend.closeBackend()
		self.quit()

	def gotAccounts(self, package):
		data = package.data.decode('utf-8')
		data = data.split(',')
		print(data)
		accounts = []
		for account in data:
			h = account.split(':')
			accounts.append(h[1])
		self.loadContacts(accounts)	

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
<<<<<<< HEAD
		
		
		
=======
				
>>>>>>> 84ca3b116c6e858bbd4067bab86270413e83fb8d
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
			button = 'self.b{0}'.format(name)
			cache = 'self.c{0}'.format(name)
			buttonFunc = lambda s = self, n = name: s.switchChat(n)
			exec('{0} = tk.Button(self.fChatSelection, text = name, command = buttonFunc)'.format(button))
			# style button, mark as selected button
			exec('{0}.config(relief = tk.SUNKEN)'.format(button))
			# set currently active button to pressed button
			exec("self.activeButton = {0}".format(button))
			exec('{0}.pack(side = \'left\')'.format(button))
			exec('{0} = [\'\',\'\']'.format(cache))

			self.openChats.append(name)
			self.curChat = name

	def switchChat(self,name):
		''' switch from on chat into another
		cache current chat, insert new chat content into windows		
		'''
		self.title('PYCC - {0}'.format(name))
		if self.curChat != '':
			self.cacheChat(self.curChat)
		self.clearChat()
		self.readCache(name)
		self.curChat = name
		self.activeButton.config(relief = tk.RAISED)
		exec('self.activeButton = self.b{0}'.format(name))
		exec('self.b{0}.config(relief = tk.SUNKEN)'.format(name))

	def closeChat(self):
		button = 'self.b{0}'.format(self.curChat)
		cache = 'self.c{0}'.format(self.curChat)
		exec('{0}.forget()'.format(button))
		exec('del({0})'.format(button))
		exec('del({0})'.format(cache))
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
		cache = 'self.c{0}'.format(name)		
		exec('{0}[0] = self.tChatWindow.get(\'1.0\',\'end\').strip()'.format(cache))
		exec('{0}[1] = self.tText.get(\'1.0\',\'end\').strip()'.format(cache))

	def readCache(self,name):
		''' insert content from cache list of name into tChatWindow and tText '''
		# tChatWindow is read-only -> has to made editable first
		self.tChatWindow.config(state = 'normal')
		cache = 'self.c{0}'.format(name)	
		exec('self.tChatWindow.insert(\'end\', {0}[0])'.format(cache))
		exec('self.tText.insert(\'end\', {0}[1])'.format(cache))
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
<<<<<<< HEAD
		print ('textdown')

	def changeColor(self):
		pass

	
=======
>>>>>>> 84ca3b116c6e858bbd4067bab86270413e83fb8d

# open window if not imported
if __name__ == '__main__':
	window = MainWindow()
	#window.loadContacts(['Eric', 'Stanley', 'Kyle', 'Kenny', 'Martin', 'Leo', 'Dennis', 'Kevin', 'George', 'Maria', 'Achmed'])
	#frontend = Frontend()
	#list = self.frontend.sendRequest('getAccounts')	
	#print(list)
	window.mainloop()
