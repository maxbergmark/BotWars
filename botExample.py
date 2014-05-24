import random
import socket
import math
import json

def toDegrees(rad):
	return 180*rad/math.pi

class Bot:

	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(2)
		#self.socket.connect(('213.103.216.250', 7027))
		self.socket.connect(('localhost', 7007))
		self.socket.send(self.startUp('test', '#0000ff'))
		self.UUID = self.readMessage()
		print(self.UUID)

	def startUp(self, name, color):
		return (json.dumps({'name': name, 'color': color}) + '\0').encode()

	def reconnect(self, UUID):
		return (json.dumps({'UUID': UUID}) + '\0').encode()

	def makeMessage(self, message, value = None):
		if value == None:
			return (json.dumps({'command': message}) + '\0').encode()
		return (json.dumps({'command': message, 'value': value}) + '\0').encode()

	def readMessage(self):
		return json.loads(self.socket.recv(4096).decode().split('\0')[0])['result']

	def playSelf(self):
		self.socket.send(self.makeMessage('getEnergy'))
		self.energy = self.readMessage()
		if self.energy >= 50:
			self.socket.send(self.makeMessage('angle', 360*random.random()))
			self.readMessage()
			self.socket.send(self.makeMessage('fire'))
			self.readMessage()



myBot = Bot()

while True:
	myBot.playSelf()