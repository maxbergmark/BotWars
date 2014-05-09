import random
import socket
import time



bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bot.settimeout(.1)
bot.connect(('localhost', 50007))
bot.send('setName Max Bergmark'.encode())
bot.recv(1024).decode()
bot.send('setColor green'.encode())
bot.recv(1024).decode()


while True:
	#bot.send(('angle ' + str(random.randint(0,359))).encode())
	#bot.recv(1024)
	#bot.send('boost'.encode())
	#bot.recv(1024)
	time.sleep(1)