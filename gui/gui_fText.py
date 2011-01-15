import Tkinter as tk

#Fenster:
root = tk.Tk()

#Frame - Textfeld:
fText = tk.Frame(root)
fText.pack(fill = tk.BOTH, expand = 1)

#Textfeld:
text = tk.Text(fText)
v = "hallo"
text.insert(tk.END, v)
text.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

#Eingabe_Scrollbar:
scrollbar = tk.Scrollbar(text)
scrollbar.config(orient = tk.VERTICAL, jump = 0, command = text.yview)
scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

#senden-Button:
send_Button = tk.Button(fText, text="Senden")
send_Button.pack(side = tk.RIGHT)
text.insert(tk.END, v)
text.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
root.mainloop()
