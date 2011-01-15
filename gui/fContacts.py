#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import tkinter
#from tkinter import *

root = tkinter.Tk()
#initializing the frame for the contact-list
fContacts = tkinter.Frame(root)

#scrollbar for contact-list
contactsScrollbar = tkinter.Scrollbar(fContacts)
#creating list-box for contact-list with binding to contactsScrollbar
contacts = tkinter.Listbox(fContacts, yscrollcommand = contactsScrollbar)
#add contactsScrollbar to the right side of the frame and stretch vertical
contactsScrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)

contacts.pack(fill = tkinter.Y)
fContacts.pack(side = tkinter.LEFT)


contacts.insert(tkinter.END, "Kirstin")
contacts.insert(tkinter.END, "Aileen")
contacts.insert(tkinter.END, "Joseph")
contacts.insert(tkinter.END, "Anita")
contacts.insert(tkinter.END, "Stefan")
root.mainloop()

