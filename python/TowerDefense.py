# Tower Defense
# By Di Lu dilu@umich.edu
# All rights reserved 
# Any distribution or usage are prohibited unless permission is provided

import random, pygame, sys, copy
from pygame.locals import *
from deadEnemy import *
from enemy import *
from tower import *

FPS = 40 #frames per second, the speed rate of the prgram
WINDOWWIDTH = 1150 #window's width in pixel
WINDOWHEIGHT = 800 #window's height in pixel

GRIDSIZE = 16 #grid size of the map, eg. map will be 16 * 16, when GRIDSIZE = 16

TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 45

TOWERCONSTRUCTIONTIME = 1

#color configurations
BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

#game state settings 
INITMONEY = 1000
INITTIME = 0
INITENEMY = 0
INITSCORE = 0
TIMECOUNTER = 0

#enemies Settings 
#Name        Name      Health    Speed  Money Drop
HORNGIRL = ('horngirl',  100,      1,      50)
PINKGIRL = ('pinkgirl',  200,      2,     100)
CATGIRL  = ('catgirl',   300,      1,     150)
BOY      = ('boy',       500,      1,     200)
PRINCESS = ('princess',  1000,   0.5,     250)

#towers Settings
#Name 		   Range 	Cost 	Damage 	ShootingSpeed CannonSpeed
BUBBLETOWER = (100,     200,     20,         1,           20)
SOLIDTOWER  = (100,     400,     50,       0.5,           20)
BLOCKTOWER  = (  0,     50,       0,         0,            0)


#main function definations
def main():
	#set glocal variables to ficilitate other functions to use them
	global DISPLAYSURF, FPSCLOCK, ALLIMAGE, FLOOR, ENEBASE, OURBASE, \
		bubbleImage, solidImage, blockImage, pauseImage, helpImage, \
		enemyAll, ENEMYTYPE, enemyHealthFactor, enemyMoneyDropFactor,\
		BASICFONT

	#create game state object, including money, time ellipsed, enemies
	#defeated, and time counter
	gameStateObj = [INITMONEY, INITTIME, INITENEMY, TIMECOUNTER, INITSCORE]

	#initialize the pygame settings 
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

	#set captions and fonts
	pygame.display.set_caption('Tower Defense')
	BASICFONT = pygame.font.Font('freesansbold.ttf', 22)
	IMFOFONT = pygame.font.SysFont('comicsansms', 32)

	#load images from graphics files
	FLOOR = pygame.image.load('floor.png')
	ENEBASE = pygame.image.load('enemyBase.png')
	OURBASE = pygame.image.load('base.png')
	bubbleImage = pygame.image.load('barbican_1.png')
	solidImage = pygame.image.load('barbican_2.png')
	blockImage = pygame.image.load('rock.png')
	pauseImage = pygame.image.load('pause.png')
	helpImage = pygame.image.load('help.png')

	#all tower types
	ENEMYTYPE = [HORNGIRL, PINKGIRL, CATGIRL, BOY, PRINCESS]

	#all enemy types
	TOWERTYPE = [BUBBLETOWER, SOLIDTOWER, BLOCKTOWER]

	#enemy health and money droped settings 
	enemyHealthFactor = 1.0
	enemyMoneyDropFactor = 1.0

	#load sounds from sound filesf
	soundCannotPlace = pygame.mixer.Sound('coolTime.wav')
	flagCannotPlace = False

	#initialize the game map
	MAP = initialMap()

	#data structions for towers, enemies, and dead enemies
	towerAll  = []
	enemyAll  = []
	deadEnemy = []

	enemyCounter = 0

	#initialize mouse coordinations and corresponding flags
	mousex = 0
	mousey = 0
	mouseClicked = False
	towerSelected = None
	towerType = None

	#initialize the tower construction cool time counter and flag
	COOLTIMECOUNTER = 0
	FLAGCOUNTER = False

	startScreen()

	#main game loop, never return, program exits by system function exit()
	while True:
		#draw borad map, all towers, enemies, and dead enemies
		drawBoard()
		drawTower(MAP)
		drawDeadEnemy(deadEnemy)
		for ene in enemyAll:
			gameOver = ene.update()
			if gameOver == True:
				gameover()
			DISPLAYSURF.blit(ene.image, ene.rect)
		for tow in towerAll:
			temp = tow.update(enemyAll, deadEnemy, gameStateObj)
			if temp != None:
				DISPLAYSURF.blit(tow.cannonImage, temp)


		#event handling loop
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == MOUSEMOTION:
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouseClicked = True
			elif event.type == KEYDOWN:
				if event.key == K_1:
					halt()
				elif event.key == K_9:
					gameStateObj[0] += 100
				elif event.key == K_UP:
					enemyHealthFactor += 0.1
					enemyMoneyDropFactor -= 0.1
				elif event.key == K_DOWN:
					enemyHealthFactor -= 0.1
					enemyMoneyDropFactor += 0.1
				
		gridx, gridy = getGridAtPixel(mousex, mousey)

		if gridx != None and gridy != None:
			#the mouse is currently over a grid
			if towerSelected != None:
				towerRect = towerSelected.get_rect()
				towerRect.topleft = ((gridx * 50 + 40), (gridy * 40 + 40))
				DISPLAYSURF.blit(towerSelected, towerRect)
				if mouseClicked == True:
					#set prohibited area fro tower construction based on enemies locations
					for ene in enemyAll:
						currGridx, currGridy = ene.getGrid()
						if currGridx == gridx and currGridy == gridy:
							flagCannotPlace = True
							break
						if ene.direction == 'n' and currGridx == gridx\
						 and currGridy == (gridy + 1):
							flagCannotPlace = True
							break
						if ene.direction == 's' and currGridx == gridx\
						 and currGridy == (gridy - 1):
							flagCannotPlace = True
							break
						if ene.direction == 'w' and currGridx == (gridx + 1)\
						 and currGridy == gridy:
							flagCannotPlace = True
							break
						if ene.direction == 'e' and currGridx == (gridx - 1)\
						 and currGridy == gridy:
							flagCannotPlace = True
							break
					if flagCannotPlace == True:
						soundCannotPlace.play()
						#set flag indicating tower cannot be constructed here
						flagCannotPlace = False 
					elif FLAGCOUNTER == False:
						#construct tower and update the grid map and tower data structure
						#set the cool time counter, and update all enemies routes
						Type = int(towerType) - 1
						if TOWERTYPE[Type][1] <= gameStateObj[0]:
							gameStateObj[0] -= TOWERTYPE[Type][1]
							MAP[gridx][gridy] = towerType
							towerNew = Tower(TOWERTYPE[Type][0], TOWERTYPE[Type][1], \
								TOWERTYPE[Type][2], TOWERTYPE[Type][3], TOWERTYPE[Type][4], \
								gridx, gridy, Type)
							towerAll.append(towerNew)
							towerSelected = None
							towerType = None
							FLAGCOUNTER = True
							for ene in enemyAll:
								ene.findRoute(MAP, False)
					else:
						#play sound indicating tower cannot be placed here
						soundCannotPlace.play()
		#select tower if mouse clicked 
		elif mouseClicked == True:
			towerSelected, towerType = SelectedTower(mousex, mousey)

		#set money display surface
		moneySurf = BASICFONT.render('Money: %d' % gameStateObj[0], 1, TEXTCOLOR)
		moneyRect = moneySurf.get_rect()
		moneyRect.topleft = (880, 100)
		DISPLAYSURF.blit(moneySurf, moneyRect)

		#set time display surface
		timeSurf = BASICFONT.render('Time: %d' % gameStateObj[1], 1, TEXTCOLOR)
		timeRect = timeSurf.get_rect()
		timeRect.topleft = (880, 140)
		DISPLAYSURF.blit(timeSurf, timeRect)

		#set enemy defeated display surface
		enemySurf = BASICFONT.render('Enemy defeated: %d' % gameStateObj[2], 1, TEXTCOLOR)
		enemyRect = enemySurf.get_rect()
		enemyRect.topleft = (880, 180)
		DISPLAYSURF.blit(enemySurf, enemyRect)

		#set score display surface
		scoreSurf = BASICFONT.render('Score: %d' % gameStateObj[4], 1, TEXTCOLOR)
		scoreRect = scoreSurf.get_rect()
		scoreRect.topleft = (880, 220)
		DISPLAYSURF.blit(scoreSurf, scoreRect)

		#set mouseClicked flag False for reusage
		mouseClicked = False

		#display promote on the main display surface when tower is cooled down
		#and update the corresponding counter and flag
		if FLAGCOUNTER == True:
			constrSurf = IMFOFONT.render('Cool Time: Tower Constructing', 1, TEXTCOLOR)
			constrRect = constrSurf.get_rect()
			constrRect.topleft = (220, 340)
			DISPLAYSURF.blit(constrSurf, constrRect)
			COOLTIMECOUNTER += 1
			if COOLTIMECOUNTER == TOWERCONSTRUCTIONTIME * FPS:
				COOLTIMECOUNTER = 0
				FLAGCOUNTER = False

		#update the game status 
		enemyCounter = gameStateUpdate(gameStateObj, enemyCounter, MAP)

		#draw all main display updates to the monitor
		pygame.display.update()

		#increase the health and money droped of enemies over the time
		enemyHealthFactor += 0.001
		enemyMoneyDropFactor += 0.0001

		#wait for a clock tick
		FPSCLOCK.tick(FPS)

#display the start image and start the game when a key is pressed
def startScreen():
	title = pygame.image.load('tower_title.png')
	titleRect = title.get_rect()
	titleRect.centerx = 600
	titleRect.centery = 400
	DISPLAYSURF.fill(BGCOLOR)
	DISPLAYSURF.blit(title, titleRect)

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				return

	pygame.display.update()
	FPSCLOCK.tick()

#initialize the map
def initialMap():
	map = []
	for i in range(GRIDSIZE):
		column = []
		for j in range(GRIDSIZE):
			column.append(' ')
		map.append(column)
	return map

#draw the board and auxiliary settings
def drawBoard():
	DISPLAYSURF.fill(BGCOLOR)
	floory = 40
	for i in range(GRIDSIZE):
		floorx = 40
		for j in range (GRIDSIZE):
			DISPLAYSURF.blit(FLOOR, (floorx, floory))
			floorx += 50
		floory += 40
	DISPLAYSURF.blit(ENEBASE, (40, 40))
	DISPLAYSURF.blit(OURBASE, (790, 640))
	DISPLAYSURF.blit(bubbleImage, (880, 260))
	DISPLAYSURF.blit(solidImage, (960, 260))
	DISPLAYSURF.blit(blockImage, (1040, 260))
	DISPLAYSURF.blit(pauseImage, (910, 380))
	DISPLAYSURF.blit(helpImage, (910, 450))

#select tower according to the position of mouse
def SelectedTower(mousex, mousey):
	if mousex >= 880 and mousex <=930 and mousey >=270 and mousey <= 340:
		return pygame.image.load('barbican_1.png'), '1'
	elif mousex >= 960 and mousex <= 1010 and mousey >=270 and mousey <= 340:
		return pygame.image.load('barbican_2.png'), '2'
	elif mousex >= 1040 and mousex <= 1090 and mousey >= 270 and mousey <= 340:
		return pygame.image.load('rock.png'), '3'
	elif mousex >= 910 and mousex <= 1060 and mousey >= 380 and mousey <= 430:
		halt()
		return None, None
	elif mousex >= 910 and mousex <= 1060 and mousey >= 450 and mousey <= 500:
		help()
		return None, None
	else:
		return None, None

#return the coordinates of the grid given the position of mouse
def getGridAtPixel(mousex, mousey):
	gridx = (mousex - 40) / 50
	gridy = (mousey - 60) / 40
	if gridx >= 0 and gridx <= 15 and gridy >= 0 and gridy <= 15:
		return gridx, gridy
	else:
		return None, None

#draw towers in the map
def drawTower(MAP):
	for i in range(GRIDSIZE):
		for j in range(GRIDSIZE):
			if MAP[i][j] == '1':
				rect = bubbleImage.get_rect()
				rect.topleft = ((i * 50 + 40), (j * 40 + 40))
				DISPLAYSURF.blit(bubbleImage, rect)
			elif MAP[i][j] == '2':
				rect = solidImage.get_rect()
				rect.topleft = ((i * 50 + 40), (j * 40 + 40))
				DISPLAYSURF.blit(solidImage, rect)
			elif MAP[i][j] == '3':
				rect = blockImage.get_rect()
				rect.topleft = ((i * 50 + 40), (j * 40 + 40))
				DISPLAYSURF.blit(blockImage, rect)

#draw the image of dead enemies
#and erase the enemy from the list when time is up
def drawDeadEnemy(deadEnemy):
	i = 0
	while i < len(deadEnemy):
		Flag = deadEnemy[i].update()
		if Flag == False:
			DISPLAYSURF.blit(deadEnemy[i].deadImage, deadEnemy[i].rect)
			i += 1
		else:
			deadEnemy.pop(i)

#generate enemies according to pre-defined pattern
def gameStateUpdate(gameStateObj, enemyCounter, MAP):
	gameStateObj[3] += 1
	if gameStateObj[3] % FPS == 0:
		enemyCounter += 1
		temp = gameStateObj[1] % 5
		enemyNew = Enemy(ENEMYTYPE[temp][0], ENEMYTYPE[temp][1],\
		 ENEMYTYPE[temp][2], ENEMYTYPE[temp][3], MAP, enemyCounter,\
		 enemyHealthFactor, enemyMoneyDropFactor)
		enemyAll.append(enemyNew)
		gameStateObj[0] += 10
		gameStateObj[1] += 1
		gameStateObj[4] += 5
	return enemyCounter

def terminate():
	pygame.quit()
	sys.exit()

#display pause image, and resume when a key is presses
def halt():
	haltImage = pygame.image.load('tower_paused.png')
	titleRect = haltImage.get_rect()
	titleRect.centerx = 560
	titleRect.centery = 400
	DISPLAYSURF.fill(BGCOLOR)
	DISPLAYSURF.blit(haltImage, titleRect)

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				return

	pygame.display.update()
	FPSCLOCK.tick()

#displya gameover image, and exit when a key is pressed
def gameover():
	gameOverImage = pygame.image.load('gameover.png')
	titleRect = gameOverImage.get_rect()
	titleRect.centerx = 560
	titleRect.centery = 400
	DISPLAYSURF.fill(BGCOLOR)
	DISPLAYSURF.blit(gameOverImage, titleRect)

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				terminate()

	pygame.display.update()
	FPSCLOCK.tick()

#display help image, and resume when a key is pressed
def help():
	helpImage = pygame.image.load('helpInstr.png')
	titleRect = helpImage.get_rect()
	titleRect.centerx = 570
	titleRect.centery = 400
	DISPLAYSURF.fill(BGCOLOR)
	DISPLAYSURF.blit(helpImage, titleRect)

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				return

	pygame.display.update()
	FPSCLOCK.tick()



if __name__ == '__main__':
	main()

