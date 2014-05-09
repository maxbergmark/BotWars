from tkinter import *
import socket
import select
import random
import math
import time



def toDegrees(rad):
	return 180*rad/math.pi

def toRadians(deg):
	return math.pi*deg/180

def rotate(coordinate, angle):
	return [coordinate[0]*math.cos(toRadians(angle)) - coordinate[1]*math.sin(toRadians(angle)), coordinate[0]*math.sin(toRadians(angle)) + coordinate[1]*math.cos(toRadians(angle))]




class Ship:

	def __init__(self, master, root, playerID, playerColor):
		self.root = root
		self.canvas = master
		self.playerID = playerID
		self.playerColor = playerColor
		self.speed = 4
		self.angle = 0
		self.score = 0
		self.alive = True
		self.pos = [random.randint(0,int(self.canvas.cget('width'))), random.randint(0,int(self.canvas.cget('height')))]
		#self.pos = [100+100*playerID, 100]
		self.size = 2
		self.bullets = []
		self.scans = []
		self.health = 100
		self.energy = 100
		self.boost = False
		self.shield = False
		self.boostFrame = 0
		self.lastHitFrame = 0
		self.deathFrame = 0
		self.createShip()
		self.createBars()
		self.createShield()
		self.createName()

	def createShip(self):
		corners = [rotate([self.size*-5, self.size*3], self.angle), rotate([self.size*5, self.size*0], self.angle), rotate([self.size*-5, self.size*-3], self.angle)]
		self.corners = [None for i in range(len(corners))]
		for corner in range(len(corners)):
			self.corners[corner] = self.canvas.create_line(self.pos[0] + corners[corner-1][0], self.pos[1] + corners[corner-1][1], self.pos[0] + corners[corner][0], self.pos[1] + corners[corner][1], fill = self.playerColor, width = self.size/2)

	def createBars(self):
		healthCoords = [self.pos[0] - self.size*10, self.pos[1] - self.size*8, self.pos[0] + self.size*10, self.pos[1] - self.size*8]
		energyCoords = [self.pos[0] - self.size*10, self.pos[1] - self.size*10, self.pos[0] + self.size*10, self.pos[1] - self.size*10]
		self.healthBar = [self.canvas.create_line(healthCoords, fill = 'white', width = 2), self.canvas.create_line(healthCoords[2], healthCoords[1], healthCoords[2], healthCoords[3], fill = 'red', width = 2)]
		self.energyBar = [self.canvas.create_line(energyCoords, fill = 'white', width = 2), self.canvas.create_line(energyCoords[2], energyCoords[1], energyCoords[2], energyCoords[3], fill = 'blue', width = 2)]

	def createShield(self):
		self.shieldObject = self.canvas.create_oval(self.pos[0]-7*self.size, self.pos[1]+7*self.size, self.pos[0]+7*self.size, self.pos[1]-7*self.size, outline = '')

	def createName(self):
		self.nameObject = self.canvas.create_text(self.pos[0], self.pos[1]-6*self.size, text = self.playerID, fill = 'white', font = ('Courier', 8))

	def changeName(self, name):
		self.playerID = name
		self.canvas.itemconfig(self.nameObject, text = self.playerID)

	def changeColor(self, color):
		self.playerColor = color
		for corner in self.corners:
			self.canvas.itemconfig(corner, fill = self.playerColor) 


	def drawShip(self):
		corners = [rotate([self.size*-5, self.size*3], self.angle), rotate([self.size*5, self.size*0], self.angle), rotate([self.size*-5, self.size*-3], self.angle)]
		for corner in range(len(corners)):
			self.canvas.coords(self.corners[corner], self.pos[0] + corners[corner-1][0], self.pos[1] + corners[corner-1][1], self.pos[0] + corners[corner][0], self.pos[1] + corners[corner][1])


	def moveShip(self):
		if self.alive:
			self.pos = [(self.pos[0]+self.speed*math.cos(toRadians(self.angle))) % int(self.canvas.cget('width')), (self.pos[1]+self.speed*math.sin(toRadians(self.angle))) % int(self.canvas.cget('height'))]
		for bullet in self.bullets:
			bullet.moveBullet()
			bullet.checkCollision()
		for scan in self.scans:
			scan.deleteScan()
		self.checkShield()
		self.endBoost()
		self.drawShip()
		self.drawBars()
		self.drawShield()
		self.drawName()

	def drawBars(self):
		self.canvas.coords(self.healthBar[0], self.pos[0]-self.size*10, self.pos[1]+self.size*8, self.pos[0]+10*self.size*(-1+self.health/50), self.pos[1]+self.size*8)
		self.canvas.coords(self.healthBar[1], self.pos[0]+10*self.size*(-1+self.health/50), self.pos[1]+self.size*8, self.pos[0]+self.size*10, self.pos[1]+self.size*8)
		self.canvas.coords(self.energyBar[0], self.pos[0]-self.size*10, self.pos[1]+self.size*10, self.pos[0]+10*self.size*(-1+self.energy/50), self.pos[1]+self.size*10)
		self.canvas.coords(self.energyBar[1], self.pos[0]+10*self.size*(-1+self.energy/50), self.pos[1]+self.size*10, self.pos[0]+self.size*10, self.pos[1]+self.size*10)

	def drawShield(self):
		self.canvas.coords(self.shieldObject, self.pos[0]-7*self.size, self.pos[1]+7*self.size, self.pos[0]+7*self.size, self.pos[1]-7*self.size)

	def drawName(self):
		self.canvas.coords(self.nameObject, self.pos[0], self.pos[1]-6*self.size)


	def setAngle(self, angle):
		if self.energy >= 10 and self.alive:
			self.angle = angle
			self.energy -= 10

	def activateShield(self):
		if self.energy >= 2 and self.alive:
			self.shield = True
			self.canvas.itemconfig(self.shieldObject, outline = 'green')

	def checkShield(self):
		if self.energy < 2:
			self.shield = False
			self.disableShield()
		if self.shield:
			self.energy -= 2

	def disableShield(self):
		self.shield = False
		self.canvas.itemconfig(self.shieldObject, outline = '')


	def startBoost(self):
		if self.energy >= 30 and self.alive:
			self.speed = 8
			self.boostFrame = self.root.frame
			self.boost = True
			self.energy -= 30

	def endBoost(self):
		if self.root.frame >= self.boostFrame+50 and self.boost:
			self.speed = 4
			self.boost = False

	def fireBullet(self):
		if self.energy >= 20 and self.alive:
			self.bullets.append(Bullet(self.canvas, self.root, self, self.angle, self.pos, self.playerID))
			self.energy -= 20

	def scanShips(self):
		if self.energy >= 5 and self.alive:
			self.scans.append(Scan(self.canvas, self.root, self, self.pos, self.playerID))
			self.energy -= 5
			return self.scans[-1].checkShips()

	def destroyShip(self):
		self.alive = False
		self.deathFrame = self.root.frame
		for corner in self.corners:
			self.canvas.itemconfig(corner, fill = '')
		for i in range(2):
			self.canvas.itemconfig(self.healthBar[i], fill = '')
			self.canvas.itemconfig(self.energyBar[i], fill = '')
		self.canvas.itemconfig(self.shieldObject, outline = '')
		self.canvas.itemconfig(self.nameObject, fill = '')

	def respawnShip(self):
		self.pos = [random.randint(0, int(self.canvas.cget('width'))), random.randint(0, int(self.canvas.cget('height')))]
		self.drawShip()
		self.drawBars()
		self.drawShield()
		self.health = 100
		self.alive = True
		self.score = max(0, self.score-200)
		for corner in self.corners:
			self.canvas.itemconfig(corner, fill = self.playerColor)
		for i in range(2):
			self.canvas.itemconfig(self.healthBar[i], fill = ['white', 'red'][i])
			self.canvas.itemconfig(self.energyBar[i], fill = ['white', 'blue'][i])


class Scan:

	def __init__(self, master, root, ship, pos, playerID):
		self.canvas = master
		self.root = root
		self.ship = ship
		self.pos = pos
		self.playerID = playerID
		self.startFrame = self.root.frame
		self.scanSize = 150
		self.scanObject = self.canvas.create_oval(self.pos[0]-self.scanSize, self.pos[1]+self.scanSize, self.pos[0]+self.scanSize, self.pos[1]-self.scanSize, outline = 'white')

	def checkShips(self):
		self.positions = [player.pos for player in self.root.players if player.alive]
		self.relativePos = [[pos[i]-self.pos[i] for i in range(2)] for pos in self.positions]
		self.inRangeRelative = []
		for pos in self.relativePos:
			if (pos[0]**2+pos[1]**2)**.5 <= self.scanSize and (pos[0]**2+pos[1]**2)**.5 > 0:
				self.inRangeRelative.append(pos)
		return self.inRangeRelative

	def deleteScan(self):
		if self.root.frame >= self.startFrame + 3:
			self.ship.scans.remove(self)
			self.canvas.delete(self.scanObject)


class Bullet:

	def __init__(self, master, root, ship, angle, pos, playerID):
		self.root = root
		self.canvas = master
		self.ship = ship
		self.speed = 10
		self.pos = pos
		self.size = 2
		self.angle = angle
		self.playerID = playerID
		self.createBullet()

	def createBullet(self):
		self.bullet = self.canvas.create_rectangle([self.pos[i]+[-self.size, self.size][i] for i in range(2)], [self.pos[i]+[self.size, -self.size][i] for i in range(2)], fill = 'white')

	def drawBullet(self):
		corners = [self.pos[0]-self.size, self.pos[1]+self.size, self.pos[0]+self.size, self.pos[1]-self.size]
		self.canvas.coords(self.bullet, corners[0], corners[1], corners[2], corners[3])

	def moveBullet(self):
		self.pos = [(self.pos[0]+self.speed*math.cos(toRadians(self.angle))), (self.pos[1]+self.speed*math.sin(toRadians(self.angle)))]
		if self.pos[0] > int(self.canvas.cget('width')) or self.pos[1] > int(self.canvas.cget('height')) or min(self.pos) < 0:
			self.ship.bullets.remove(self)
			self.canvas.delete(self.bullet)
		self.drawBullet()

	def checkCollision(self):
		for player in self.root.players:
			if ((self.pos[0]-player.pos[0])**2 + (self.pos[1]-player.pos[1])**2)**.5 < player.size*5 and self.playerID != player.playerID and player.alive:
				if player.shield == False:
					player.lastHitFrame = self.root.frame
					player.health -= 40
					self.ship.score += 20
					if player.health <= 0:
						player.destroyShip()
						self.ship.score += 80
						print(player.playerID, 'died a horrible death.', self.ship.playerID, 'is responsible.')
				else:
					player.disableShield()
				if self in self.ship.bullets:
					self.ship.bullets.remove(self)
				self.canvas.delete(self.bullet)





class Game:

	def __init__(self, master):

		self.root = root
		self.canvas = Canvas(master, width = 640, height = 640, bg = 'black')
		self.canvas.config(cursor = 'target')
		self.canvas.pack()
		self.players = []
		self.bots = []
		self.playerConns = {}
		self.frame = 0
		self.scoreBoard = self.canvas.create_text(5, 5, text = '', anchor = 'nw', fill = 'white')
		self.frameBoard = self.canvas.create_text(5, int(self.canvas.cget('height')), text = '', anchor = 'sw', fill = 'white')
		
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.bind(('0.0.0.0', 50007))
		self.serverSocket.listen(5)

		self.serverList = [self.serverSocket]
		self.addressList = {}
		self.connList = {}


		self.newFrame()



	def addPlayer(self, conn, addr, name, color):
		self.playerConns[addr] = Ship(self.canvas, self, name, color) 
		self.connList[conn] = addr
		self.players.append(self.playerConns[addr])



	def getMessages(self):
		(rtr, rtw, ie) = select.select(self.serverList, [], [], 0)
		for element in rtr:
			if element == self.serverSocket:
				(conn, addr) = self.serverSocket.accept()
				if addr[0] in self.addressList:
					self.serverList.remove(self.addressList[addr[0]])
					print(addr, 'reconnected.')
					self.connList[conn] = addr[0]
				else:
					print(addr, 'joined the game.')
					self.addPlayer(conn, addr[0], '', 'white')

				self.serverList.append(conn)
				self.addressList[addr[0]] = conn
					


					
			else:
				try:
					data = element.recv(1024)
					if len(data.decode()) > 0:
						element.send(self.processMessage(element, self.connList[element], data.decode()).encode())
				except:
					pass


	def processMessage(self, conn, addr, message):
		if message.split()[0] == 'angle':
			try:
				self.playerConns[self.connList[conn]].setAngle(float(message.split()[1]))
			except:
				return 'not done'
		elif message == 'remove':
			self.playerConns[addr].destroyShip()
			self.players.remove(self.playerConns[addr])
			del self.playerConns[addr]

		elif message == 'respawn':
			if addr not in self.playerConns:
				self.addPlayer(conn, addr, '', 'white')

		elif message.split()[0] == 'setName':
			self.playerConns[self.connList[conn]].changeName(' '.join(message.split()[1:]))

		elif message.split()[0] == 'setColor':
			self.playerConns[self.connList[conn]].changeColor(message.split()[1])

		elif message == 'scanShips':
			return str(self.playerConns[self.connList[conn]].scanShips())
		elif message == 'boost':
			self.playerConns[self.connList[conn]].startBoost()

		elif message.split()[0] == 'shield':
			if message.split()[1] == 'on':
				self.playerConns[self.connList[conn]].activateShield()
			else:
				self.playerConns[self.connList[conn]].disableShield()

		elif message == 'fire':
			self.playerConns[self.connList[conn]].fireBullet()

		elif message == 'addBot':
			self.bots.append(Ship(self.canvas, self, 'BOT', '#a0a0a0'))
			self.players.append(self.bots[-1])
		elif message == 'getFrame':
			return str(self.frame)
		elif message == 'getEnergy':
			return str(self.playerConns[self.connList[conn]].energy)
		elif message == 'getHealth':
			return str(self.playerConns[self.connList[conn]].health)



		else:
			return 'error'
		return 'done'






	def newFrame(self):
		if self.root.winfo_width() > 200 and self.root.winfo_height() > 200:
			self.canvas.config(width = self.root.winfo_width()-4, height = self.root.winfo_height()-4)
			self.canvas.coords(self.frameBoard, 5, int(self.canvas.cget('height')))

		scoreList = sorted(self.players, key = self.getPlayerScore, reverse = True)
		nameList = [str(player.playerID) + ': ' + str(player.score) for player in scoreList]
		scoreString = '\n'.join(nameList[:10])
		self.canvas.itemconfig(self.scoreBoard, text = scoreString)
		self.canvas.itemconfig(self.frameBoard, text = str(self.frame))

		self.getMessages()

		for player in self.players:
			player.moveShip()
			if self.frame - player.lastHitFrame > 50:
				player.health = min(player.health+.5, 100)
			player.energy = min(player.energy+1, 100)

		for bot in self.bots:
			if self.frame % 20 == 0:
				bot.setAngle(360*random.random())

		for player in self.players:
			if player.alive == False and self.frame > player.deathFrame+100:
				player.respawnShip()


		#if sum(1 for player in self.players if player.alive) == 1:
		#	self.winGame()
		#else:
		self.frame += 1
		self.canvas.after(1, self.newFrame)

	def winGame(self):
		winner = [player.playerID if player.alive else '' for player in self.players]
		winner.sort()
		scoreList = sorted(self.players, key = self.getPlayerScore, reverse = True)
		print('\nGame Won By: ', winner[-1])
		print()
		for player in scoreList:
			print(player.playerID+': ', player.score)
		self.root.destroy()

	def getPlayerScore(self, player):
		return player.score


print()

root = Tk()
root.title('BotWars')
app = Game(root)
#root.iconify()
#root.update()
#root.deiconify()
root.mainloop()