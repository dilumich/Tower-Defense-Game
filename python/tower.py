import pygame, sys
from pygame.locals import *
from enemy import *
from cannonball import *
from deadEnemy import *
import copy
import math

#tower class
class Tower:
	#initalize the data elements
	def __init__(self, shootingRange, cost, damage, shootingSpeed,\
	 cannonSpeed, x, y, towerType):
		self.shootingRange = shootingRange
		self.shootingSpeed = shootingSpeed
		self.cost = cost
		self.damage = damage
		self.cannonSpeed = cannonSpeed
		self.x = (x * 50) + 40
		self.y = (y * 40) + 40
		self.cannonBall = None
		self.coolTimeFlag = False
		self.cannonImage = None
		self.isBubbleTower = False
		self.flagShooting = False
		self.coolTimeCounter = 0
		self.target = None
		if towerType == 0:
			self.cannonImage = pygame.image.load('cannonBall_1.png')
			self.isBubbleTower = True
		elif towerType == 1:
			self.cannonImage = pygame.image.load('cannonBall_2.png')
		elif towerType == 2:
			self.cannonImage = None

	#shoot enemy if any enemy is within the shooting range and set cool time flag
	def shoot(self, enemyAll):
		if self.coolTimeFlag == False:
			for enemy in enemyAll:
				distance = ((enemy.x - self.x) ** 2) + ((enemy.y - self.y) ** 2)
				if distance <= (self.shootingRange ** 2):
					self.coolTimeFlag = True
					self.cannonBall = CannonBall(self.cannonSpeed, self.x, self.y,\
				 	enemy.x + 10, enemy.y + 20, math.sqrt(distance))
					self.flagShooting = True
					self.target = enemy.ID
					break
		return
	#update the cannonball status and destroy the corrsponding cannonball obejct 
	#when the cannonbal hits the enemy, then update the game stutus and unset
	#cool time flag 
	def update(self, enemyAll, deadEnemy, gameState):
		if self.cannonImage == None:
			return
		self.shoot(enemyAll)
		if self.coolTimeFlag == True:
			self.coolTimeCounter += (1.0 / self.shootingSpeed)
			if self.coolTimeCounter >= 40:
				self.coolTimeCounter = 0
				if self.cannonBall == None:
					self.coolTimeFlag = False
		if self.flagShooting == True:
			flagHit = self.cannonBall.update()
			if flagHit == True:
				for i in range(len(enemyAll)):
					if enemyAll[i].ID == self.target:
						if self.isBubbleTower and enemyAll[i].isReduceSpeed == False:
							enemyAll[i].isReduceSpeed = True
							enemyAll[i].speed /= 2
						enemyAll[i].health -= self.damage
						if enemyAll[i].health < 0:
							deadNew = DeadEnemy(enemyAll[i].enemyType,\
							 enemyAll[i].x, enemyAll[i].y)
							deadEnemy.append(deadNew)
							gameState[0] += enemyAll[i].money
							gameState[4] += enemyAll[i].money
							gameState[2] += 1
							enemyAll.pop(i)
						break
				self.cannonBall = None
				self.target = None
				self.flagShooting = False
			else:
				rect = self.cannonImage.get_rect()
				rect.topleft = (self.cannonBall.currPointX, self.cannonBall.currPointY)
				return rect
		return None

