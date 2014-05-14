import ast
import socket
import math

def toDegrees(rad):
	return 180*rad/math.pi

class Bot:

	def __init__(self):
		self.nearby = False
		self.fireFrame = 0
		self.lastTarget = None;
		self.lastScanFrame = 0
		self.firstScan = False
		self.lastScan = False
		self.willFire = False
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(1)
		self.socket.connect(('localhost', 50027))
		self.socket.send('setName Max Bergmark'.encode())
		self.socket.recv(1024).decode()
		self.socket.send('setColor green'.encode())
		self.socket.recv(1024).decode()
		for i in range(10):
			self.socket.send('addBot'.encode())
			self.socket.recv(1024).decode()

	def playSelf(self):
		#self.socket.send('getFrame'.encode())
		#self.frame = int(self.socket.recv(1024).decode())
		self.socket.send('getEnergy'.encode())
		self.energy = int(self.socket.recv(1024).decode())

		if self.energy >= 70 or self.firstScan:
			self.socket.send('scanShips'.encode())
			nearby = ast.literal_eval(self.socket.recv(1024).decode())
			if nearby != [] and self.firstScan:
				self.firstScan = False
				self.lastScan = True
			elif nearby != []:
				self.firstScan = True
			else:
				self.firstScan = False
				self.lastScan = False

			if nearby:
				self.nearby = True
				self.shipInfo = []
				for ship in nearby:
					self.shipInfo.append([(ship[0]**2+ship[1]**2)**.5, toDegrees(math.atan2(ship[1], ship[0])), ship[0], ship[1]])
				closeTarget = sorted(self.shipInfo, key=self.getSort)[0]

				if len(self.shipInfo) > 30:
					self.socket.send('shield on'.encode())
				else:
					self.socket.send('shield off'.encode())
				self.socket.recv(1024).decode()
				if self.lastTarget and self.lastScan:
					angle = toDegrees(math.atan2(closeTarget[3]+.05*closeTarget[0]*(closeTarget[3]-self.lastTarget[3]), closeTarget[2]+.05*closeTarget[0]*(closeTarget[2]-self.lastTarget[2])))
					self.socket.send(('angle ' + str(angle)).encode())
					self.socket.recv(1024).decode()
					self.fireFrame = self.frame+1
					self.willFire = True

			else:
				closeTarget = None
				self.nearby = False

			self.lastTarget = closeTarget
		else:
			self.firstScan = False

		if self.willFire:
			for i in range(3):
				self.socket.send('fire'.encode())
				self.socket.recv(1024).decode()
			self.firstScan = False
			self.lastScan = False
			self.willFire = False

				

	def getSort(self, item):
		return item[0]



myBot = Bot()

while True:
	myBot.playSelf()
	myBot.socket.send('getFrame'.encode())
	myBot.frame = int(myBot.socket.recv(1024).decode())
	#print(myBot.frame)