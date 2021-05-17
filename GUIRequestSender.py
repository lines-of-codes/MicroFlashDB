import tkinter as tk
from tkinter import simpledialog
import socket
from MFDBresponsecode import Response

msg = tk.Tk()
msg.withdraw()

HOST = simpledialog.askstring("Server IP", "Please input target Server IP.", initialvalue='127.0.0.1')
PORT = simpledialog.askinteger("Port Number", "Please insert server port number.", initialvalue=9000)
BUFFERSIZE = simpledialog.askinteger("Buffersize", "Please insert the acceptable max return lenght.", initialvalue=1024)

mw = tk.Tk()
mw.title("MicroFlashDB Request Sender")

lstbx = tk.Listbox(mw, width=100)
text = tk.Text(mw, height=2, selectbackground="yellow", selectforeground="black", undo=True)

def connect(query):
    text.delete('1.0', 'end')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # sock.send("SET 20 IN users TO :(".encode("utf-8"))
    # msg = sock.recv(BUFFERSIZE)
    sock.send(query.encode('utf-8'))
    msg = sock.recv(BUFFERSIZE)
    msgparts = msg.decode()
    msgparts = msgparts.split()
    if msgparts[0] == 'ERROR':
        if msgparts[1] == str(Response.invalidKeyword):
            try:
                lstbx.insert(tk.END, f"UNEXPECTED ERROR: Invalid Keyword. {msgparts[2]}")
            except IndexError:
                lstbx.insert(tk.END, "UNEXPECTED ERROR: Invalid Keyword.")
        elif msgparts[1] == str(Response.noKeyMatches):
            try:
                lstbx.insert(tk.END, f"UNEXPECTED ERROR: No key matches in the requested table. {msgparts[2]}")
            except IndexError:
                lstbx.insert(tk.END, "UNEXPECTED ERROR: No key matches in the requested table.")
        elif msgparts[1] == str(Response.noTableMatches):
            try:
                lstbx.insert(tk.END, f"UNEXPECTED ERROR: No table matches. {msgparts[2]}")
            except IndexError:
                lstbx.insert(tk.END, "UNEXPECTED ERROR: No table matches.")
        else:
            lstbx.insert(tk.END, f"UNKNOWN ERROR: {msgparts[1]}")
    else: lstbx.insert(tk.END, msg.decode('utf-8'))
    # lstbx.insert(tk.END, msg.decode('utf-8'))

sendBtn = tk.Button(mw, text="Send", command=lambda: connect(text.get('1.0', 'end')))

lstbx.pack(pady=10, fill=tk.X)
text.pack(side=tk.LEFT)
sendBtn.pack(side=tk.RIGHT)

mw.mainloop()