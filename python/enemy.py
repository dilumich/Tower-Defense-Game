import pygame, sys
from pygame.locals import *
from collections import deque
import copy

#enemy class
class Enemy:
	def __init__(self, enemyType, health, speed, money, Map, ID, healthFac, moneyFac):
		self.speed = float(speed)
		self.health = int(float(health) * healthFac)
		self.image = pygame.image.load(enemyType + '.png')
		self.rect = self.image.get_rect()
		self.x = 40.0
		self.y = 40.0
		self.money = int(float(money) * moneyFac)
		self.enemyType = enemyType
		self.rect.topleft = (self.x, self.y)
		self.route = None
		self.ID = ID
		self.isReduceSpeed = False
		self.direction = 'e'
		self.flagInit = True
		self.findRoute(Map, self.flagInit)
		if self.route[1][0] == 0:
			self.direction = 's'
		self.flagInit = False

	#get the grid of enemy based on the coordinates
	def getGrid(self):
		gridx = int((self.x - 40) / 50)
		gridy = int((self.y - 40) / 40)
		return gridx, gridy


	#Find the shortest route by using the breadth-first seaching algorithm
	def findRoute(self, Map, flagInit):
		gridx, gridy = self.getGrid()
		nextx = gridx
		nexty = gridy
		if flagInit == False:
			if self.direction == 'n':
				nexty -= 1
			elif self.direction == 's':
				nexty += 1
			elif self.direction == 'e':
				nextx += 1
			elif self.direction == 'w':
				nextx -= 1
		dupMap = copy.deepcopy(Map)
		dupMap[nextx][nexty] = 'S'
		queue = deque()
		queue.append((nextx, nexty))
		route = deque()
		while len(queue) != 0:
			currx = queue[0][0]
			curry = queue[0][1]
			queue.popleft()
			if (currx == 14 and curry == 15) or (currx == 15 and curry == 14):
				prevx = currx
				prevy = curry
				dire = ' '
				route.appendleft((15, 15, ' '))
				if currx == 14:
					dire = 'e'
				else:
					dire = 's'
				while prevx != nextx or prevy != nexty:
					route.appendleft((prevx, prevy, dire))
					if dupMap[prevx][prevy] == 'e':
						prevx = prevx - 1
						dire = 'e'
					elif dupMap[prevx][prevy] == 's':
						prevy = prevy - 1
						dire = 's'
					elif dupMap[prevx][prevy] == 'n':
						prevy = prevy + 1
						dire = 'n'
					elif dupMap[prevx][prevy] == 'w':
						prevx = prevx + 1
						dire = 'w'
				route.appendleft((nextx, nexty, dire))
				if self.flagInit == False:
					route.appendleft((gridx, gridy, self.direction))
				self.route = route
				return

			if curry > 0 and dupMap[currx][curry - 1] == ' ':
				queue.append((currx, curry - 1))
				dupMap[currx][curry - 1] = 'n'
			if currx < 15 and dupMap[currx + 1][curry] == ' ':
				queue.append((currx + 1, curry))
				dupMap[currx + 1][curry] = 'e'
			if curry < 15 and dupMap[currx][curry + 1] == ' ':
				queue.append((currx, curry + 1))
				dupMap[currx][curry + 1] = 's'
			if currx > 0 and dupMap[currx - 1][curry] == ' ':
				queue.append((currx - 1, curry))
				dupMap[currx - 1][curry] = 'w'
		#if no path is find, cross the tower
		MAP = getInitialMap()
		self.findRoute(MAP, flagInit)


	#update the enemy's status, and change the directions when reaching 
	#next grid
	def update(self):
		if self.direction == 'n':
			self.y -= self.speed
		if self.direction == 's':
			self.y += self.speed
		if self.direction == 'w':
			self.x -= (self.speed * 1.25)
		if self.direction == 'e':
			self.x += (self.speed * 1.25)
		self.rect.topleft = (self.x, self.y)
		if self.x >= (40 + (50 * 15)) and self.y >= (40 + (40 * 15)):
			return True
		if ((self.x - 40) % 50 == 0) and ((self.y - 40) % 40 == 0):
			self.route.popleft()
			self.direction = self.route[0][2]
		return False

def getInitialMap():
	map = []
	for i in range(16):
		column = []
		for j in range(16):
			column.append(' ')
		map.append(column)
	return map