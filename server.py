import socket
import threading
from traceback import print_exc
import orjson
from MFDBresponsecode import Response
import basicdataencryptor as encryptor
from random import randint
from string import ascii_letters, digits

global isRunning
isRunning = True

def run():
	global instanceCode
	letters_digits = ascii_letters + digits
	instanceCode = letters_digits[randint(0, 61)]
	instanceCode += letters_digits[randint(0, 61)]
	instanceCode += letters_digits[randint(0, 61)]
	instanceCode += letters_digits[randint(0, 61)]
	instanceCode += letters_digits[randint(0, 61)]
	print(" / MicroFlashDB - Server 1.0.0 BETA /")

	print("Instance code: " + instanceCode)

	print("Loading databases...")
	
	conffile = open(".mfdbconfig", "r")
	confdict = orjson.loads(conffile.read())
	mdbfile = open(confdict['dbfile'], "r")
	conffile.close()

	# Create HighlyAccessedTable
	hatstore = {}
	fcont = mdbfile.read()
	if fcont:
		try:
			hatstore = orjson.loads(fcont)['hatstore']
		except KeyError:
			hatstore = {}
	else: hatstore = {}
			# Table | KEY:VALUE data Inside Table
	
	try:
		hatstore = hatstore['hatstore']
	except KeyError:
		pass
	del fcont
	mdbfile.close()

	HOST = confdict['serveraddress']
	PORT = confdict['serverport']
	QUERY_BUFFERSIZE = confdict['maxquerybytes']

	if confdict['iptype'] == 'IPv4':
		SOCKETFAMILY = socket.AF_INET
	else:
		SOCKETFAMILY = socket.AF_INET6

	server = socket.socket(SOCKETFAMILY, socket.SOCK_STREAM)
	server.bind((HOST, PORT))

	server.listen()

	# Handling Requests
	def handle(client):
		# Parse & Execute message
		def checkrequest(messageparts, originalmessageparts):
			if messageparts[0] == 'get':
				if messageparts[1] == 'table':
					try:
						retmsg = orjson.dumps(hatstore[messageparts[2]])
						client.send(retmsg.encode('utf-8'))
					except KeyError:
						try:
							retmsg = orjson.dumps(ntstore[messageparts[2]])
							client.send(retmsg.encode('utf-8'))
						except KeyError:
							client.send(f"ERROR {Response.noTableMatches}")
				try:
					if confdict['encryptdata']:
						omsg = hatstore[messageparts[3]][messageparts[1]]
						msg = ""
						if isinstance(omsg, list):
							for i in omsg:
								msg += i + " "
							msg = msg[:-1]
						else: msg = omsg
						del omsg
						client.send(encryptor.encrypt(msg, confdict['encryptionsettings']['shiftedup']).encode('utf-8'))
						del msg
					else:
						omsg = hatstore[messageparts[3]][messageparts[1]]
						msg = ""
						if isinstance(omsg, list):
							for i in omsg:
								msg += i + " "
							msg = msg[:-1]
						else: msg = omsg
						del omsg
						client.send(msg.encode('utf-8'))
						del msg
				except KeyError:
					try:
						dbf = open(confdict['dbfile'], "r")
						fcont = dbf.read()
						fcont = orjson.loads(fcont)
						dbf.close()
						omsg = fcont['ntstore'][messageparts[3]][messageparts[1]]
						msg = ""
						for i in omsg:
							msg += i + " "
						msg = msg[:-1]
						client.send(msg.encode("utf-8"))
						del fcont
						del dbf
						del omsg
						del msg
					except KeyError:
						client.send(f"ERROR {Response.noKeyMatches}".encode('utf-8'))
				except Exception as e:
					client.send(f"ERROR {e}")
			elif messageparts[0] == 'set':
				if messageparts[1] == 'tablename' or messageparts[1] == 'table':
					# SET TABLE table_name TYPE normal
					try:
						if messageparts[4] == 'normal':
							dbf = open(confdict['dbfile'], "r")
							fcont = dbf.read()
							fcont = orjson.loads(fcont)
							fcont['ntstore'][messageparts[2]] = {}
							fcont = orjson.dumps(fcont)
							dbf.close()
							dbf = open(confdict['dbfile'], "w")
							dbf.write(fcont.decode('utf-8'))
							dbf.close()
							del fcont
							del dbf
						elif messageparts[4] == 'hat':
							hatstore[messageparts[2]] = {}
						else:
							client.send(f"ERROR {Response.invalidKeyword} INVALID TYPE".encode('utf-8'))
							return
					except IndexError:
						client.send(f"ERROR {Response.invalidKeyword} TYPE NOT SPECIFIED".encode('utf-8'))
					client.send("SUCCESS".encode('utf-8'))
					if messageparts[4] == 'normal':
						dbf = open(confdict['dbfile'], "r")
						fcont = dbf.read()
						fcont = orjson.loads(fcont)
						fcont['ntstore'][messageparts[2]] = {}
						fcont = orjson.dumps(fcont)
						dbf.close()
						dbf = open(confdict['dbfile'], "w")
						dbf.write(fcont.decode('utf-8'))
						dbf.close()
						del fcont
						del dbf
				else:
					# SET key IN table TO value extended
					try:
						hatstore[messageparts[3]][messageparts[1]] = originalmessageparts[5:]
					except KeyError:
						try:
							dbf = open(confdict['dbfile'], "r")
							fcont = dbf.read()
							fcont = orjson.loads(fcont)
							fcont['ntstore'][messageparts[3]][messageparts[1]] = originalmessageparts[5:]
							fcont = orjson.dumps(fcont)
							dbf.close()
							dbf = open(confdict['dbfile'], "w")
							dbf.write(fcont.decode('utf-8'))
							dbf.close()
							del dbf
							del fcont
						except KeyError:
							client.send(f"ERROR {Response.noTableMatches}".encode('utf-8'))
							return
					client.send("SUCCESS".encode('utf-8'))
			elif messageparts[0] == 'delete':
				if messageparts[1] == 'table':
					try:
						del hatstore[messageparts[2]]
					except KeyError:
						client.send(f"ERROR {Response.noKeyMatches}".encode('utf-8'))
						return
					client.send("SUCCESS".encode('utf-8'))
				else:
					del hatstore[messageparts[3]][messageparts[1]]
					client.send("SUCCESS".encode('utf-8'))
			elif messageparts[0] == 'save':
				if messageparts[1] == 'hat':
					try:
						dbf = open(confdict['dbfile'], "r")
						fcont = dbf.read()
						fcont = orjson.loads(fcont)
						fcont['hatstore'] = hatstore
						fcont = orjson.dumps(fcont)
						fcont = fcont.decode('utf-8')
						dbf.close()
						dbf = open(confdict['dbfile'], "w")
						dbf.write(fcont.decode('utf-8'))
						dbf.close()
					except Exception as e:
						client.send(f"ERROR {e}".encode('utf-8'))
						return
					client.send("SUCCESS".encode('utf-8'))
				elif messageparts[1] == 'normal':
					client.send("SUCCESS".encode('utf-8'))
				else:
					client.send(f"ERROR {Response.invalidKeyword}")
			elif messageparts[0] == 'shutdown':
				if originalmessageparts[1] == instanceCode:
					global isRunning
					isRunning = False
					client.send("SUCCESS".encode('utf-8'))
				else:
					client.send(f"ERROR {Response.invalidInstanceCode}".encode("utf-8"))
			elif messageparts[0] == 'authorlogtable':
				print(hatstore)
				client.send("SUCCESS".encode('utf-8'))
			else:
				client.send(f"ERROR {Response.invalidKeyword}".encode("utf-8"))
		message = client.recv(confdict['maxquerybytes'])
		messageparts = message.decode('utf-8')
		lmessageparts = messageparts.lower()
		if messageparts.endswith("\n"):
			messageparts = messageparts[:-1]
		if lmessageparts.endswith("\n"):
			lmessageparts = lmessageparts[:-1]
		messageparts = messageparts.split(" ")
		lmessageparts = lmessageparts.split(" ")
		if confdict['isProtected']:
			def checkpassword(messageparts):
				fullpassword = ""
				checkfirst = False
				reachend = False
				for i in messageparts:
					if i.startswith('"') and not checkfirst:
						fullpassword += i
						checkfirst = True
						continue
					if checkfirst:
						if i.endswith('"') and not reachend:
							reachend = True
							fullpassword += i
							continue
						if not reachend:
							fullpassword += i

				if not fullpassword.endswith('"'):
					breakloop = False
					while not breakloop:
						message = client.recv(128)
						message = message.decode('utf-8')
						if message.endswith('"'):
							fullpassword += message
							breakloop = True
							continue
						else:
							fullpassword += message
				fullpassword = fullpassword[1:-1]
				if fullpassword == confdict['connpasswd']:
					return True
				else:
					return False

			if messageparts[0] == 'linf':
				if checkpassword(messageparts[1]):
					checkrequest(lmessageparts[2:], messageparts[2:])
			elif messageparts[0] == 'elinf':
				if checkpassword(encryptor.decrypt(messageparts[1], confdict['encryptionsettings']['shiftedup'])):
					checkrequest(lmessageparts[2:], messageparts[2:])
		else:
			checkrequest(lmessageparts, messageparts)

	# Recieve
	def recieve():
		try:
			global isRunning
			while isRunning:
				client, address = server.accept()
				print(f"Connection recieved from {address}")

				thread = threading.Thread(target=handle, args=(client,), daemon=True)
				thread.start()
		except KeyboardInterrupt:
			raise SystemExit
		except Exception:
			print_exc()
			raise SystemExit

	print("Server running...")
	recieve()

if __name__ == '__main__':
	run()