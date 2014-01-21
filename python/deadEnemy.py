import pygame, sys
from pygame.locals import *
from collections import deque
import copy

#dead enemy class
class DeadEnemy:
	#initalize the date elements
	def __init__(self, enemyType, x, y):
		self.deadImage = pygame.image.load(enemyType + '_die.png')
		self.rect = self.deadImage.get_rect()
		self.rect.topleft = (x, y)
		self.counter = 0

	#update the dead enemy status
	def update(self):
		self.counter += 1
		if self.counter == 20:
			return True
		return False