''' GUI for PYCC '''

import tkinter as tk
import Frontend, Preferences

class MainWindow(tk.Tk):

	def __init__(self):
		''' creating and packing elements of the GUI '''
		tk.Tk.__init__(self)
		self.title("PYCC")
		self.openChats = []
		self.curChat = ''
		
		# initiate preferences
		self.Preferences = Preferences.Preferences('preferences.cfg')
		self.username = self.Preferences.prefs['username']
		self.textcolor = self.Preferences.prefs['textcolor']
		
		# chat selection
		self.fChatSelection = tk.Frame(self)
		self.fChatSelection.grid(row = 0, column = 0, sticky = 'w')
		# set current selected button to None
		self.activeButton = None

		# selection between contact list and preferences
		self.fMenue = tk.Frame(self)
		self.fMenue.grid(row = 0, column = 1)
		self.bContacts = tk.Button(self.fMenue, text = 'Contacts', command = self.displayContacts, width = 6, fg = self.textcolor)
		self.bContacts.config(relief = tk.SUNKEN)
		self.bContacts.pack(side = 'left')
		self.bPreferences = tk.Button(self.fMenue, text = 'Prefs', command = self.displayPreferences, width = 6, fg = self.textcolor)
		self.bPreferences.pack(side = 'left')

		# chat window
		self.fChatWindow = tk.Frame(self)	
		self.fChatWindow.grid(row = 1, column = 0, sticky = 'nswe')
		self.sChatWindow = tk.Scrollbar(self.fChatWindow)
		self.sChatWindow.pack(side = 'right', fill = 'y')
		# read-only; switch back to state = 'normal' to insert text	
		self.tChatWindow = tk.Text(self.fChatWindow, yscrollcommand = self.sChatWindow.set, height = 20, state = 'disabled', fg = self.textcolor)
		self.tChatWindow.pack(side = 'left', fill = 'both', expand = True)
		self.sChatWindow.config(command = self.tChatWindow.yview)

		# input window
		self.fText = tk.Frame(self)	
		self.fText.grid(row = 2, column = 0, sticky = 'nswe')
		self.sText = tk.Scrollbar(self.fText)
		self.sText.pack(side = 'right', fill = 'y')	
		self.tText = tk.Text(self.fText, yscrollcommand = self.sText.set, height = 4, state = 'disabled', fg = self.textcolor)
		self.tText.pack(side = 'left', fill = 'x', expand = True)
		self.sText.config(command = self.tText.yview)

		# preferences
		self.fPreferences = tk.Frame(self)
		self.sPreferences = tk.Scrollbar(self.fPreferences)
		self.sPreferences.pack(side = 'right', fill='y')
		# username
		self.fUserName = tk.Frame(self.fPreferences)
		self.fUserName.pack(padx = 10, pady = 10, anchor = 'w')				
		self.lUserName = tk.Label(self.fUserName, text = 'Username:', fg = self.textcolor)
		self.lUserName.pack(anchor = 'w', pady = 5)
		self.eUserName = tk.Entry(self.fUserName, width = 15, fg = self.textcolor)
		self.eUserName.insert('end', self.username)
		self.eUserName.pack(anchor = 'w')
		# textcolor
		self.tc = tk.StringVar()
		self.fColors = tk.Frame(self.fPreferences)
		self.fColors.pack(padx = 10, anchor = 'w')
		self.fColors2 = tk.Frame(self.fPreferences)
		self.fColors2.pack(padx = 10, anchor = 'w')
		self.lColors = tk.Label(self.fColors, text = 'Textcolor:', fg = self.textcolor)
		self.lColors.pack(anchor = 'w', pady = 5)
		self.rbBlack = tk.Radiobutton(self.fColors, width = 3, variable = self.tc, value = '#000000', indicatoron = 0, activebackground = '#000000',selectcolor = '#000000', bg = '#444444')		
		self.rbBlack.pack(side = 'left')
		self.rbRed = tk.Radiobutton(self.fColors, width = 3, variable = self.tc, value = '#FF0000', indicatoron = 0, activebackground = '#FF0000',selectcolor = '#FF0000', bg = '#DD4444')
		self.rbRed.pack(side = 'left')
		self.rbBlue = tk.Radiobutton(self.fColors, width = 3, variable = self.tc, value = '#0000FF', indicatoron = 0, activebackground = '#0000FF',selectcolor = '#0000FF', bg = '#4444BB')
		self.rbBlue.pack(side = 'left')
		self.rbGreen = tk.Radiobutton(self.fColors, width = 3, variable = self.tc, value = '#00FF00', indicatoron = 0, activebackground = '#00FF00',selectcolor = '#00FF00', bg = '#44DD44')
		self.rbGreen.pack(side = 'left')
		self.rbWhite = tk.Radiobutton(self.fColors2, width = 3, variable = self.tc, value = '#FFFFFF', indicatoron = 0, activebackground = '#FFFFFF',selectcolor = '#FFFFFF', bg = '#EEEEEE')
		self.rbWhite.pack(side = 'left')
		self.rbYellow = tk.Radiobutton(self.fColors2, width = 3, variable = self.tc, value = '#FFFF00', indicatoron = 0, activebackground = '#FFFF00',selectcolor = '#FFFF00', bg = '#DDDD44')
		self.rbYellow.pack(side = 'left')
		self.rbViolet = tk.Radiobutton(self.fColors2, width = 3, variable = self.tc, value = '#FF00FF', indicatoron = 0, activebackground = '#FF00FF',selectcolor = '#FF00FF', bg = '#DD44DD')
		self.rbViolet.pack(side = 'left')
		self.rbTurquoise = tk.Radiobutton(self.fColors2, width = 3, variable = self.tc, value = '#00FFFF', indicatoron = 0, activebackground = '#00FFFF',selectcolor = '#00FFFF', bg = '#44DDDD')
		self.rbTurquoise.pack(side = 'left')

		self.bSave = tk.Button(self.fPreferences, text = 'Save', width = 8, command = self.savePrefs, fg = self.textcolor)
		self.bSave.pack(padx = 10, pady = 20, anchor = 'w')
 
		# contact list
		self.fContacts = tk.Frame(self)	
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')
		self.sContacts = tk.Scrollbar(self.fContacts)
		self.sContacts.pack(side = 'right', fill = 'y')	
		self.lContacts = tk.Listbox(self.fContacts, yscrollcommand = self.sContacts.set, fg = self.textcolor)
		self.lContacts.pack(side = 'left', fill = 'y')
		self.sContacts.config(command = self.lContacts.yview)
		
		# chat buttons
		self.fChatButtons = tk.Frame(self)
		self.fChatButtons.grid(row = 3, column = 0, sticky = 'w')
			
		self.bSend = tk.Button(self.fChatButtons, text = 'Send', command = self.sendMessage, width = 10, state = 'disabled', fg = self.textcolor)
		self.bSend.pack(side = 'left')		
		self.bCloseChat = tk.Button(self.fChatButtons, text = 'Close Chat', command = self.closeChat, width = 10, state = 'disabled', fg = self.textcolor)
		self.bCloseChat.pack(side = 'left')

		# define expanding rows and columns
		self.rowconfigure(1, weight = 1)
		self.columnconfigure(0, weight = 1)
		self.columnconfigure(1, minsize = 177)

		# define events
		self.lContacts.bind('<Double-ButtonPress-1>', self.startChat)
		self.tText.bind('<KeyRelease-Return>', self.sendMessage)
		self.tText.bind('<Shift-KeyRelease-Return>', self.newline)
		self.protocol('WM_DELETE_WINDOW', self.windowClosing)
		
		self.frontend = Frontend.Frontend()
		started = self.frontend.startBackend()
		if not started:
			print('Fehler!!!!')
		else:
			self.frontend.updateLoopTkinter(self)
		
		# add callback to be raised when new message is received
		self.frontend.addCallback('newMessage', self.gotNewMessage)	
		
		#load contact list from pycc/.contacts
		self.frontend.sendRequest('getAccounts', self.gotAccounts)

	def windowClosing(self):
		'''called, when user wants to end program'''
		self.frontend.closeBackend()
		self.destroy()

	def gotAccounts(self, package):
		'''raised, when account-list was returned from frontend'''
		data = package.data.decode('utf-8')
		data = data.split(',')
		accounts = []
		for account in data:
			h = account.split(':')
			accounts.append(h[1])
		self.loadContacts(accounts)
	
	def gotNewMessage(self, package):
		'''Called when new message'''
		#currently not implemented
		pass	

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
			self.showMessage(message,self.username)
			print(self.messageSent)
			self.frontend.sendRequest(('sendMessage', (self.curChat + ':' + message).encode('utf-8'), self.messageSent))
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
			exec('{0} = tk.Button(self.fChatSelection, text = name, command = buttonFunc, fg = self.textcolor)'.format(button))
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

	def savePrefs(self):
		self.username = self.eUserName.get()
		self.textcolor = self.tc.get()
		self.Preferences.setPreferences(self.username, self.textcolor)
		self.refreshWidgets()

	def refreshWidgets(self):
		self.bContacts.config(fg = self.textcolor)
		self.bPreferences.config(fg = self.textcolor)
		self.tChatWindow.config(fg = self.textcolor)
		self.tText.config(fg = self.textcolor)
		self.lUserName.config(fg = self.textcolor)
		self.eUserName.config(fg = self.textcolor)
		self.lColors.config(fg = self.textcolor)
		self.lContacts.config(fg = self.textcolor)
		self.bSend.config(fg = self.textcolor)
		self.bCloseChat.config(fg = self.textcolor)
		for name in self.openChats:
			exec('self.b{0}.config(fg = self.textcolor)'.format(name))
		


# open window if not imported
if __name__ == '__main__':
	window = MainWindow()
	#window.loadContacts(['Eric', 'Stanley', 'Kyle', 'Kenny', 'Martin', 'Leo', 'Dennis', 'Kevin', 'George', 'Maria', 'Achmed'])
	#frontend = Frontend()
	#list = self.frontend.sendRequest('getAccounts')	
	#print(list)
	window.mainloop()
