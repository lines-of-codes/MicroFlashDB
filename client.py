import socket
from timeit import timeit
from MFDBresponsecode import Response

HOST = '127.0.0.1'
PORT = 9000
BUFFERSIZE = 1024

def connect(query):
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
            print("UNEXPECTED ERROR: Invalid Keyword.")
        elif msgparts[1] == str(Response.noKeyMatches):
            print("UNEXPECTED ERROR: No key matches in the requested table.")
    else: print(msg.decode('utf-8'))

connect("SET TABLE new_table TYPE highly-used")
# connect("SET 1 IN new_table TO testing")
# connect("SET TABLE TO second_table")
# connect("GET 7 IN userstable")
# functimer = timeit(lambda: connect("GET 7 IN userstable"), number=1)
# print(functimer)
# connect("GET 7 IN users")