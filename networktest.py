import socket
import time

class mySocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))


test = mySocket()
test.connect('localhost', 50007)
while True:
	text = str(input('Input: '))
	test.sock.send(text.encode())
	data = test.sock.recv(1024)

	#test.sock.close()
	print(data.decode())