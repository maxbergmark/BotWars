import socket

class mySocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(1)


myDict = {'scanShips': '[[10, 20], [34, 46]]', 'angle': '345'}


test = mySocket()
test.connect('localhost', 50007)
test.sock.settimeout(.1)
print(test.sock.gettimeout())
check = False
#while True:
(conn, addr) = test.sock.accept()
print('connect from: ', addr)
while True:
	try:
		data = conn.recv(9)
		print(data.decode())
		if data.decode() == 'terminate':
			check = True
			break
		else:
			conn.send(str(len(myDict[data.decode()])).encode())
			conn.send(myDict[data.decode()].encode())
		
	except:
		break

#conn.close()
if check:
	print('break')
	#break