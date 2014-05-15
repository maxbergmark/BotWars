from tkinter import *
import threading
import socket
import select
import random
import math
import time
import json
import uuid



def toDegrees(rad):
	return 180*rad/math.pi

def toRadians(deg):
	return math.pi*deg/180

def rotate(coordinate, angle):
	return [coordinate[0]*math.cos(toRadians(angle)) - coordinate[1]*math.sin(toRadians(angle)), coordinate[0]*math.sin(toRadians(angle)) + coordinate[1]*math.cos(toRadians(angle))]




class Ship:

	def __init__(self, root, playerID, playerColor, playerUUID = '', active = True):
		self.root = root
		self.playerID = playerID
		self.uuid = playerUUID
		self.playerColor = playerColor
		self.speed = 4
		self.angle = 0
		self.score = 0
		self.kills = 0
		self.fired = 0
		self.hit = 0
		self.alive = True
		self.active = active
		self.pos = [random.randint(0,self.root.width), random.randint(0,self.root.height)]
		self.size = 2
		self.bullets = []
		self.scans = []
		self.health = 200
		self.energy = 100
		self.boost = False
		self.shield = False
		self.boostFrame = 0
		self.lastHitFrame = 0
		self.deathFrame = 0


	def drawShip(self):
		corners = [rotate([self.size*-5, self.size*3], self.angle), rotate([self.size*5, self.size*0], self.angle), rotate([self.size*-5, self.size*-3], self.angle)]
		self.corners = [None for i in range(len(corners))]
		for corner in range(len(corners)):
			self.corners[corner] = self.root.canvas.create_line((self.pos[0] + corners[corner-1][0])/self.root.scale, (self.pos[1] + corners[corner-1][1])/self.root.scale, (self.pos[0] + corners[corner][0])/self.root.scale, (self.pos[1] + corners[corner][1])/self.root.scale, fill = self.playerColor, width = self.size/2)

	def drawBars(self):
		self.healthBar = [self.root.canvas.create_line((self.pos[0]-self.size*10)/self.root.scale, (self.pos[1]+self.size*8)/self.root.scale, (self.pos[0]+10*self.size*(-1+self.health/100))/self.root.scale, (self.pos[1]+self.size*8)/self.root.scale, fill = 'white', width = 2), self.root.canvas.create_line((self.pos[0]+10*self.size*(-1+self.health/100))/self.root.scale, (self.pos[1]+self.size*8)/self.root.scale, (self.pos[0]+self.size*10)/self.root.scale, (self.pos[1]+self.size*8)/self.root.scale, fill = 'red', width = 2)]
		self.energyBar = [self.root.canvas.create_line((self.pos[0]-self.size*10)/self.root.scale, (self.pos[1]+self.size*10)/self.root.scale, (self.pos[0]+10*self.size*(-1+self.energy/50))/self.root.scale, (self.pos[1]+self.size*10)/self.root.scale, fill = 'white', width = 2), self.root.canvas.create_line((self.pos[0]+10*self.size*(-1+self.energy/50))/self.root.scale, (self.pos[1]+self.size*10)/self.root.scale, (self.pos[0]+self.size*10)/self.root.scale, (self.pos[1]+self.size*10)/self.root.scale, fill = 'blue', width = 2)]

	def drawShield(self):
		self.shieldObject = self.root.canvas.create_oval((self.pos[0]-7*self.size)/self.root.scale, (self.pos[1]+7*self.size)/self.root.scale, (self.pos[0]+7*self.size)/self.root.scale, (self.pos[1]-7*self.size)/self.root.scale, outline = '')
		if self.shield:
			self.root.canvas.itemconfig(self.shieldObject, outline = 'green')

	def drawName(self):
		self.nameObject = self.root.canvas.create_text((self.pos[0])/self.root.scale, (self.pos[1]-6*self.size)/self.root.scale, text = self.playerID, fill = 'white', font = ('Courier', 8))

	def changeName(self, name):
		self.playerID = name

	def changeColor(self, color):
		self.playerColor = color


	def moveShip(self):
		if self.alive:
			self.pos = [(self.pos[0]+self.speed*math.cos(toRadians(self.angle))) % self.root.width, (self.pos[1]+self.speed*math.sin(toRadians(self.angle))) % self.root.height]
		for bullet in self.bullets:
			bullet.moveBullet()
			bullet.checkCollision()
		for scan in self.scans:
			scan.deleteScan()
		self.checkShield()
		self.endBoost()



	def drawMaster(self):
		for bullet in self.bullets:
			bullet.drawBullet()
		for scan in self.scans:
			scan.drawScan()
		if self.alive:
			self.drawShip()
			self.drawShield()
			self.drawBars()
			self.drawName()




	def setAngle(self, angle):
		if self.energy >= 10 and self.alive:
			self.angle = angle
			self.energy -= 10

	def activateShield(self):
		if self.energy >= 2 and self.alive:
			self.shield = True
			

	def checkShield(self):
		if self.energy < 2:
			self.shield = False
			self.disableShield()
		if self.shield:
			self.energy -= 2

	def disableShield(self):
		self.shield = False


	def startBoost(self):
		if self.energy >= 25 and self.alive:
			self.speed = 8
			self.boostFrame = self.root.frame
			self.boost = True
			self.energy -= 25

	def endBoost(self):
		if self.root.frame >= self.boostFrame+50 and self.boost:
			self.speed = 4
			self.boost = False

	def fireBullet(self):
		if self.energy >= 20 and self.alive:
			self.fired += 1
			self.bullets.append(Bullet(self.root, self, self.angle, self.pos, self.playerID))
			self.energy -= 20



	def scanShips(self):
		if self.energy >= 5 and self.alive:
			self.scans.append(Scan(self.root, self, self.pos, self.playerID))
			self.energy -= 5
			return self.scans[-1].checkShips()

	def destroyShip(self):
		self.alive = False
		self.deathFrame = self.root.frame

	def respawnShip(self):
		self.pos = [random.randint(0, self.root.width), random.randint(0, self.root.height)]
		self.health = 200
		self.alive = True
		self.score = max(0, self.score-200)


class Scan:

	def __init__(self, root, ship, pos, playerID):
		self.root = root
		self.ship = ship
		self.pos = pos
		self.playerID = playerID
		self.startFrame = self.root.frame
		self.scanSize = 150
		

	def checkShips(self):
		self.positions = [player.pos for player in self.root.players if player.alive]
		self.relativePos = [[pos[i]-self.pos[i] for i in range(2)] for pos in self.positions]
		self.inRangeRelative = []
		for pos in self.relativePos:
			if (pos[0]**2+pos[1]**2)**.5 <= self.scanSize and (pos[0]**2+pos[1]**2)**.5 > 0:
				self.inRangeRelative.append(pos)
		return self.inRangeRelative

	def drawScan(self):
		self.scanObject = self.root.canvas.create_oval((self.pos[0]-self.scanSize)/self.root.scale, (self.pos[1]+self.scanSize)/self.root.scale, (self.pos[0]+self.scanSize)/self.root.scale, (self.pos[1]-self.scanSize)/self.root.scale, outline = 'white')

	def deleteScan(self):
		if self.root.frame >= self.startFrame + 3:
			self.ship.scans.remove(self)



class Bullet:

	def __init__(self, root, ship, angle, pos, playerID):
		self.root = root

		self.ship = ship
		self.speed = 10
		self.pos = pos
		self.size = 2
		self.angle = angle
		self.playerID = playerID
		

	def drawBullet(self):
		self.bullet = self.root.canvas.create_rectangle([(self.pos[i]+[-self.size, self.size][i])/self.root.scale for i in range(2)], [(self.pos[i]+[self.size, -self.size][i])/self.root.scale for i in range(2)], fill = 'white')


	def moveBullet(self):
		self.pos = [(self.pos[0]+self.speed*math.cos(toRadians(self.angle))), (self.pos[1]+self.speed*math.sin(toRadians(self.angle)))]
		if self.pos[0] > self.root.width or self.pos[1] > self.root.width or min(self.pos) < 0:
			self.ship.bullets.remove(self)
		

	def checkCollision(self):
		for player in self.root.players:
			if ((self.pos[0]-player.pos[0])**2 + (self.pos[1]-player.pos[1])**2)**.5 < player.size*5 and self.ship.uuid != player.uuid and player.alive:
				if player.shield == False:
					player.lastHitFrame = self.root.frame
					player.health -= 80
					self.ship.score += 20
					self.ship.hit += 1
					#print(self.ship.playerID, self.ship.fired, self.ship.hit/self.ship.fired)
					if player.health <= 0:
						player.destroyShip()
						self.ship.score += 80
						self.ship.kills += 1
						#print(player.playerID, 'died a horrible death.', self.ship.playerID, 'is responsible.', self.ship.kills, self.ship.score)
				else:
					player.disableShield()
				if self in self.ship.bullets:
					self.ship.bullets.remove(self)





class Game:

	def __init__(self):

		self.players = []
		self.bots = []
		self.playerConns = {}
		self.playerNames = []
		self.frame = 0
		self.scoreString = ''

		self.width = 640*1
		self.height = 640*1
		self.scale = 1
		self.framerate = 1000
		
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.bind(('localhost', 50027))
		self.serverSocket.listen(5)

		self.serverList = [self.serverSocket]
		self.connList = {}




	def initGraphic(self):

		self.root = Tk()
		self.root.title('BotWars')
		self.canvas = Canvas(self.root, width = self.width/self.scale, height = self.height/self.scale, bg = 'black')
		self.canvas.pack()


	def updateFrame(self):


		self.canvas.delete("all")
		
		self.scoreBoard = self.canvas.create_text(5, 5, text = self.scoreString, anchor = 'nw', fill = 'white')
		self.frameBoard = self.canvas.create_text(5, self.height/self.scale, text = str(self.frame), anchor = 'sw', fill = 'white')

		for player in self.players:
			if player.active:
				player.drawMaster()

		self.canvas.after(1, self.updateFrame)




	def addPlayer(self, conn, name, color):
		playerUUID = str(uuid.uuid4())
		self.playerNames.append(name)
		self.playerConns[playerUUID] = Ship(self, name, color, playerUUID) 
		self.connList[conn] = playerUUID
		self.players.append(self.playerConns[playerUUID])
<<<<<<< HEAD
		print(name, 'joined the game. Their color is', color + '.')
=======
>>>>>>> 85d693d9f0ac0bd1815028d0f1ee25e6461673bc
		return {'status': True, 'result': playerUUID, 'frame': self.frame}




	def newFrame(self):

		self.scoreList = sorted(self.players, key = self.getPlayerScore, reverse = True)
		self.nameList = [str(player.playerID) + ': ' + str(player.score) for player in self.scoreList if player.active]
		self.scoreString = '\n'.join(self.nameList[:10])


		self.getMessages()

		for player in self.players:
			player.moveShip()
			if self.frame - player.lastHitFrame > 50:
				player.health = min(player.health+1, 200)
			player.energy = min(player.energy+1, 100)

		for bot in self.bots:
			if self.frame % (50*self.width//640) == 0:
				bot.setAngle(360*random.random())
			if self.frame % 50 == 0:
				bot.fireBullet()
				

		for player in self.players:
			if player.alive == False and self.frame > player.deathFrame+100 and player.active:
				player.respawnShip()

		#if sum(1 for player in self.players if player.alive) == 1:
		#	self.winGame()
		#else:
		self.frame += 1
		time.sleep(1/self.framerate)


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



	def getMessages(self):
		(rtr, rtw, ie) = select.select(self.serverList, [], [], 0)
		for element in rtr:
			if element == self.serverSocket:
				(conn, addr) = self.serverSocket.accept()

				#print('A player joined the game.')
				self.serverList.append(conn)

			else:
				try:
					data = element.recv(1024)
					if not data and element in self.serverList:
						self.serverList.remove(element)
						self.playerConns[self.connList[element]].active = False
						self.playerNames.remove(self.playerConns[self.connList[element]].playerID)
						print(self.playerConns[self.connList[element]].playerID, 'disconnected.')
					else:
						obj = json.loads(data.decode().split('\0')[0])
						if obj:
							element.send((json.dumps(self.processMessage(element, obj)) + '\0').encode())
				except:
					print('message processing error')


	def processMessage(self, conn, message):
		
		if 'name' in message and 'color' in message:
			if message['name'] not in self.playerNames:
				return self.addPlayer(conn, message['name'], message['color'])
			else:
				return {'status': False, 'result': '', 'frame': self.frame}

		elif 'UUID' in message:
			if message['UUID'] in self.connList.values():
				self.connList = {key: value for key, value in self.connList.items() if value is not message['UUID']}
				self.connList[conn] = message['UUID']
				self.playerConns[self.connList[conn]].active = True
				self.playerNames.append(self.playerConns[self.connList[conn]].playerID)
				print(self.playerConns[self.connList[conn]].playerID, 'reconnected.')
			else:
				return {'status': False, 'result': '', 'frame': self.frame}


		elif conn in self.connList:

			if 'command' in message and 'value' in message:
				if message['command'] == 'angle':
					self.playerConns[self.connList[conn]].setAngle(message['value'])

				elif message['command'] == 'shield':
					if message['value'] == True:
						self.playerConns[self.connList[conn]].activateShield()
					else:
						self.playerConns[self.connList[conn]].disableShield()


			elif 'command' in message:

				if message['command'] == 'scanShips':
<<<<<<< HEAD
					scanned = self.playerConns[self.connList[conn]].scanShips()
					return {'status': True, 'result': [{'x': ship[0], 'y': ship[1]} for ship in scanned], 'frame': self.frame}
=======
					return {'status': True, 'result': self.playerConns[self.connList[conn]].scanShips(), 'frame': self.frame}

>>>>>>> 85d693d9f0ac0bd1815028d0f1ee25e6461673bc
				elif message['command'] == 'boost':
					self.playerConns[self.connList[conn]].startBoost()
				elif message['command'] == 'fire':
					self.playerConns[self.connList[conn]].fireBullet()

				elif message['command'] == 'addBot':
					self.bots.append(Ship(self, 'BOT', '#a0a0a0'))
					self.players.append(self.bots[-1])
				elif message['command'] == 'getEnergy':
					return {'status': True, 'result': self.playerConns[self.connList[conn]].energy, 'frame': self.frame}
				elif message['command'] == 'getHealth':
					return {'status': True, 'result': self.playerConns[self.connList[conn]].health, 'frame': self.frame}
				elif message['command'] == 'getPosition':
					return {'status': True, 'result': {'x': self.playerConns[self.connList[conn]].pos[0], 'y': self.playerConns[self.connList[conn]].pos[1]}, 'frame': self.frame}
				elif message['command'] == 'getScore':
					return {'status': True, 'result': self.playerConns[self.connList[conn]].score, 'frame': self.frame}
				elif message['command'] == 'top10':
					unSorted = [[ship.playerID, ship.score] for ship in self.playerConns.values() if ship.active]
					sortedScore = sorted(unSorted, key = self.getSort, reverse = True)[:min(10, len(unSorted))]
					return {'status': True, 'result': sortedScore, 'frame': self.frame}

		else:
			return {'status': False, 'result': '', 'frame': self.frame}
		return {'status': True, 'result': '', 'frame': self.frame}


	def getSort(self, value):
		return value[1]


def serverStart(game):
	while True:
		game.newFrame()
		time.sleep(0)


def graphicStart(game):

	game.initGraphic()
	game.updateFrame()
	game.root.mainloop()



game = Game()
threading.Thread(target = graphicStart, args = [game]).start()
serverStart(game)
