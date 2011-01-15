''' GUI for PYCC with resizing elements '''

import tkinter as tk

class MainWindow(tk.Tk):

	def __init__(self):
		''' creating and packing elements of the GUI '''
		tk.Tk.__init__(self)
		self.title("PYCC")

		# chat selection
		self.fChatSelection = tk.Frame(self)
		self.fChatSelection.grid(row = 0, column = 0)

		# selection between contact list and preferences
		self.fMenue = tk.Frame(self)
		self.fMenue.grid(row = 0, column = 1)
		self.bContacts = tk.Button(self.fMenue, text = 'C', command = self.displayContacts)
		self.bContacts.pack(side = 'left')
		self.bPreferences = tk.Button(self.fMenue, text = 'P', command = self.displayPreferences)
		self.bPreferences.pack(side = 'left')

		# chat window
		self.fChatWindow = tk.Frame(self)	
		self.fChatWindow.grid(row = 1, column = 0, sticky = 'nswe')
		self.sChatWindow = tk.Scrollbar(self.fChatWindow)
		self.sChatWindow.pack(side = 'right', fill = 'y')	
		self.tChatWindow = tk.Text(self.fChatWindow, yscrollcommand = self.sChatWindow.set, height = 20)
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
		self.bSend = tk.Button(self, text = 'Send')
		self.bSend.grid(row = 3, column = 0, sticky = 'w')

		# define expanding rows and columns
		self.rowconfigure(1 , weight = 1)
		self.columnconfigure(0 , weight = 1)

	def displayPreferences(self):
		self.fContacts.grid_forget()
		self.fPreferences.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')

	def displayContacts(self):
		self.fPreferences.grid_forget()
		self.fContacts.grid(row = 1, column = 1, rowspan = 3, sticky = 'nswe')

# open window if not imported
if __name__ == '__main__':
	window = MainWindow()
	window.mainloop()


