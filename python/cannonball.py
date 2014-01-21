import pygame, sys
from pygame.locals import *

#cannon ball class
class CannonBall:
	#initialize the date elements 
	def __init__(self, speed, x1, y1, x2, y2, dist):
		self.speed = speed
		self.currPointX = (float)(x1 + 20)
		self.currPointY = (float)(y1 + 10)
		self.distance = dist
		self.lenCovered = 0
		if dist == 0:
			dist == 1
		self.speedX = float((x2 - x1) * speed) / dist
		self.speedY = float((y2 - y1) * speed) / dist
		self.flagEnd = False

	#update cannon ball's status
	def update(self):
		self.lenCovered += self.speed
		self.currPointX += self.speedX
		self.currPointY += self.speedY
		if self.lenCovered > self.distance:
			return True