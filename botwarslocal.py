from tkinter import *
import math
import random
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

	def drawBars(self):
		self.canvas.coords(self.healthBar[0], self.pos[0]-self.size*10, self.pos[1]+self.size*8, self.pos[0]+10*self.size*(-1+self.health/50), self.pos[1]+self.size*8)
		self.canvas.coords(self.healthBar[1], self.pos[0]+10*self.size*(-1+self.health/50), self.pos[1]+self.size*8, self.pos[0]+self.size*10, self.pos[1]+self.size*8)
		self.canvas.coords(self.energyBar[0], self.pos[0]-self.size*10, self.pos[1]+self.size*10, self.pos[0]+10*self.size*(-1+self.energy/50), self.pos[1]+self.size*10)
		self.canvas.coords(self.energyBar[1], self.pos[0]+10*self.size*(-1+self.energy/50), self.pos[1]+self.size*10, self.pos[0]+self.size*10, self.pos[1]+self.size*10)

	def drawShield(self):
		self.canvas.coords(self.shieldObject, self.pos[0]-7*self.size, self.pos[1]+7*self.size, self.pos[0]+7*self.size, self.pos[1]-7*self.size)


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
				if self in self.ship.bullets:
					self.ship.bullets.remove(self)
				self.canvas.delete(self.bullet)





class Game:

	def __init__(self, master, players):

		self.root = root
		self.canvas = Canvas(master, width = 640, height = 640, bg = 'black')
		self.canvas.config(cursor = 'target')
		self.canvas.pack()
		#colors = ['white', 'green', 'blue', 'red', 'yellow', 'pink', 'purple']
		colors = ['white', 'green']
		self.playerNames = ['Max']
		self.playerNames.extend(['CPU' + str(i) for i in range(1, players)])
		self.players = [Ship(self.canvas, self, self.playerNames[i], colors[i == 0]) for i in range(players)]
		self.bot = Bot(self.canvas, self, self.players[0])
		self.frame = 0
		self.scoreBoard = self.canvas.create_text(5, 5, text = '', anchor = 'nw', fill = 'white')
		self.frameBoard = self.canvas.create_text(5, int(self.canvas.cget('height')), text = '', anchor = 'sw', fill = 'white')
		

		self.newFrame()





	def newFrame(self):
		if self.root.winfo_width() > 200 and self.root.winfo_height() > 200:
			self.canvas.config(width = self.root.winfo_width()-4, height = self.root.winfo_height()-4)
			self.canvas.coords(self.frameBoard, 5, int(self.canvas.cget('height')))

		scoreList = sorted(self.players, key = self.getPlayerScore, reverse = True)
		nameList = [str(player.playerID) + ': ' + str(player.score) for player in scoreList]
		scoreString = '\n'.join(nameList[:10])
		self.canvas.itemconfig(self.scoreBoard, text = scoreString)
		self.canvas.itemconfig(self.frameBoard, text = str(self.frame))

		for player in self.players:
			player.moveShip()
			if self.frame - player.lastHitFrame > 50:
				player.health = min(player.health+.5, 100)
			player.energy = min(player.energy+1, 100)

		for player in self.players:
			if player.alive == False and self.frame > player.deathFrame+100:
				player.respawnShip()

			if player.playerID == 'Max':
				self.bot.playSelf(player)

			else:
				if self.frame % 23 == 0:
					player.fireBullet()
				
				if self.frame % 40 == 0:
					player.setAngle(random.randint(0,359))
				
				#if self.frame % 50 == 0:
				#	player.scanShips()
				if self.frame % 100 == 0:
					player.activateShield()
				if self.frame % 100 == 0:
					player.disableShield()
				if self.frame % 300 == 0:
					player.startBoost()
			
			

		if sum(1 for player in self.players if player.alive) == 1:
			self.winGame()
		else:
			self.frame += 1
			#if self.frame % 1 == 0:
			#	self.canvas.update_idletasks()
			self.canvas.after(30, self.newFrame)

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


class Bot:

	def __init__(self, master, root, player):
		self.canvas = master
		self.root = root
		self.player = player
		self.nearby = False
		self.fireFrame = 0
		self.lastTarget = None;
		self.lastScanFrame = 0

	def playSelf(self, player):
		if self.nearby:
			update = 1
		else:
			update = 25
		if self.root.frame % update == 0 and player.energy >= 45 or self.root.frame == self.lastScanFrame+1:
			nearby = player.scanShips()
			if self.root.frame != self.lastScanFrame+1:
				self.lastScanFrame = self.root.frame
			if nearby:
				self.nearby = True
				self.shipInfo = []
				for ship in nearby:
					self.shipInfo.append([(ship[0]**2+ship[1]**2)**.5, toDegrees(math.atan2(ship[1], ship[0])), ship[0], ship[1]])
				closeTarget = sorted(self.shipInfo, key=self.getSort)[0]

				if len(self.shipInfo) > 30:
					player.activateShield()
				else:
					player.disableShield()

				if self.lastTarget and self.root.frame == self.lastScanFrame+1:
					player.setAngle(toDegrees(math.atan2(closeTarget[3]+.05*closeTarget[0]*(closeTarget[3]-self.lastTarget[3]), closeTarget[2]+.05*closeTarget[0]*(closeTarget[2]-self.lastTarget[2]))))
					self.fireFrame = self.root.frame+1

			else:
				closeTarget = None
				self.nearby = False

			self.lastTarget = closeTarget

		if self.root.frame == self.fireFrame:
			player.fireBullet()

				

	def getSort(self, item):
		return item[0]


print()

root = Tk()
root.title('BotWars')
app = Game(root, 10)
#root.iconify()
#root.update()
#root.deiconify()
root.mainloop()