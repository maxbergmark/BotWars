import ast
import socket
import math
import json

def toDegrees(rad):
	return 180*rad/math.pi

class Bot:

	def __init__(self):
		self.nearby = False
		self.fireFrame = 0
		self.lastTarget = None;
		self.lastScanFrame = 0

		self.fired = 0
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(2)
		self.socket.connect(('localhost', 50027))
		#'''
		self.socket.send(self.startUp('enemy', 'red'))
		self.UUID = self.readMessage()
		print(self.UUID)
		self.socket.send(self.makeMessage('angle', 90))
		self.readMessage()


		for i in range(0):
			self.socket.send(self.makeMessage('addBot'))
			self.socket.recv(4096).decode()
		#'''
		#self.socket.send(self.reconnect('2ff36714-387b-400b-9b4d-a19dc95eb6ab'))
		#self.socket.recv(4096).decode()

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
		self.firstScan = []
		self.lastScan = []
		self.socket.send(self.makeMessage('getEnergy'))
		self.energy = self.readMessage()
		if self.energy >= 80:
			self.socket.send(self.makeMessage('scanShips'))

			nearby = self.readMessage()
			if nearby:
				for ship in nearby:
					self.firstScan.append([(ship[0]**2+ship[1]**2)**.5, toDegrees(math.atan2(ship[1], ship[0])), ship[0], ship[1]])
				if self.firstScan != []:
					firstTarget = sorted(self.firstScan, key=self.getSort)[0]
				if nearby != []:
					self.socket.send(self.makeMessage('scanShips'))
					nearby = json.loads(self.socket.recv(4096).decode().split('\0')[0])['result']
					#nearby = ast.literal_eval(self.socket.recv(4096).decode())
					if nearby:
						for ship in nearby:
							self.lastScan.append([(ship[0]**2+ship[1]**2)**.5, toDegrees(math.atan2(ship[1], ship[0])), ship[0], ship[1]])
						if self.lastScan != []:
							lastTarget = sorted(self.lastScan, key=self.getSort)[0]
	
			if self.firstScan != [] and self.lastScan != []:
				angle = toDegrees(math.atan2(lastTarget[3]+.055*lastTarget[0]*(lastTarget[3]-firstTarget[3]), lastTarget[2]+.055*lastTarget[0]*(lastTarget[2]-firstTarget[2])))
				self.socket.send(self.makeMessage('angle', angle))
				self.socket.recv(4096).decode()
				for i in range(3):
					self.socket.send(self.makeMessage('fire'))
					self.socket.recv(4096).decode()
					self.fired += 1
					#print(self.fired)

			if len(self.firstScan) > 5 or len(self.lastScan) > 5:
				self.socket.send(self.makeMessage('shield', True))
			else:
				self.socket.send(self.makeMessage('shield', False))
			self.socket.recv(4096).decode()

	def getSort(self, item):
		return item[0]



myBot = Bot()

while True:
	myBot.playSelf()