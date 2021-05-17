import socket
from MFDBresponsecode import Response
import basicdataencryptor as decoder

class InvalidKeyword(Exception):
    pass

class NoMatchesKey(Exception):
    pass

class UnknownError(Exception):
    pass

class ClientBaseClass:
    def __init__(self, host, port, password=None, isEncrypted=False, eShiftedUp=3, buffersize=512):
        self.host = host
        self.port = port
        self.password = password
        self.isEncrypted = isEncrypted
        self.eShiftedUp = eShiftedUp
        self.BUFFERSIZE = buffersize
    
    def connect(self, query, returnAsBoolean=False, socketAddressFamily=socket.AF_INET, socketKind=socket.SOCK_STREAM)
        sock = socket.socket(socketAddressFamily, socketKind)
        sock.connect((self.host, self.port))
        # sock.send("SET 20 IN users TO :(".encode("utf-8"))
        # msg = sock.recv(BUFFERSIZE)
        if self.password == None:
            sock.send(query.encode('utf-8'))
        else:
            if self.isEncrypted:
                sock.send("elinf " + decoder.encrypt(self.password) + " " + query)
            else:
                sock.send("linf " + self.password + " " + query)
        msg = sock.recv(self.BUFFERSIZE)
        msgparts = msg.decode()
        msgparts = msgparts.split()
        if msgparts[0] == 'ERROR':
            if msgparts[1] == str(Response.invalidKeyword):
                if returnAsBoolean: return False
                else: raise InvalidKeyword
            elif msgparts[1] == str(Response.noKeyMatches):
                if returnAsBoolean: return False
                else: raise NoMatchesKey
            else:
                if returnAsBoolean: return False
                else: raise UnknownError(f"Server returned unknown error. Consider update this Client Library. (Error: {msgparts[1:]})")
        elif msgparts[0] == 'SUCCESS':
            return True
        else: return decoder.decrypt(msgparts[0], self.eShiftedUp)