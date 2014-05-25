import random
import socket
import math
import json

#This simple bot connects to the server, creates a ship, and then changes angle and fires as often as it can. 
#This is only to give an example of how to connect and make a simple bot. You may use this code to start making your own bot.

def toDegrees(rad):
	return 180*rad/math.pi

class Bot:

	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(2)
		self.socket.connect(('fbergmark.se', 7027))
		#self.socket.connect(('localhost', 7007))
		self.socket.send(self.startUp('test', '#0000ff')) #Please change name and color to your own preference.
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
		temp = json.loads(self.socket.recv(4096).decode().split('\0')[0])
		#print(temp)
		if 'result' in temp:
			return temp['result']
		return False
	
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