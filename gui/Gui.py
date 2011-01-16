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
