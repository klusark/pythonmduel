#/usr/bin/env python
"""
Mduel
"""
import time
time.clock()
#Import Modules
import pygame, cPickle, PixelPerfect, socket, ConfigParser, math, select
#from socket import socket
from os import path
from re import findall
from random import randint
from zlib import compress, decompress
from pygame.locals import *
#function to create our resources

def loadImage(name, rect, colorkey=None):
	fullname = path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	image = image.convert()
	image = pygame.transform.scale(image,(image.get_width()*2,image.get_height()*2))
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	if rect == 0:
		return image
	else:
		return image, image.get_rect()
	
#classes for our game objects
class Player(pygame.sprite.Sprite):
	"""The Payer class"""
	def __init__(self, x, y, platform):
		"""Initializes Player class"""
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.frames = {}
		self.loadImages()
		self.rect.inflate_ip(-10, 0)
		self.image = self.stand
		self.rect.move_ip(x,y)
		self.feetRect = pygame.Rect(x+5, y+41, 38, 7)
		self.platform = platform
		self.xMove = 0
		self.yMove = 0
		self.lastkey = 0
		self.current = 0
		self.crouching = 0
		self.running = 0
		self.dir = 0
		self.crouchdown = 0
		self.crouchup = 0
		self.fallingforwards = 0
		self.fallingback = 0
		self.rolling = 0
		self.gravity = 1
		self.maxVol = 6
		self.inAir = 0
		self.jumpfwd = 0
		self.noKeys = 0
		self.name = "Unset"
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
		
	def loadAnm(self,name,num):
		self.frames[name]=[]
		for i in range(num):
			image = loadImage(name+str(i)+".png", 0, -1)
			self.frames[name].append(image)
			
	def loadImages(self):
		"""loads images"""
		self.loadAnm("run", 4)
		self.loadAnm("jumpfwd", 3)
		self.loadAnm("fallforwards", 2)
		self.loadAnm("fallback", 2)
		self.loadAnm("crouch", 2)
		self.loadAnm("roll", 4)
		self.fall = loadImage('fall.png', 0, -1)
		self.stand, self.rect = loadImage('stand.png', 1, -1)
		
	def setKeys(self, right = K_RIGHT, left = K_LEFT, down = K_DOWN, up = K_UP):
		"""setKeys(right key, left key, crouch key)
		Sets the keys for the player object"""
		self.keys = {}
		self.keys["right"] = right
		self.keys["left"] = left
		self.keys["down"] = down
		self.keys["up"] = up
		
	def MoveKeyDown(self, key):
		"""Event fuction for when any keys bound to the current player object are hit"""
		if not self.inAir:
			if not self.crouching:
				if key == self.keys["right"]:
					self.xMove = 6
					self.dir = 0
					self.running = 1
				elif key == self.keys["left"]:
					self.xMove = -6
					self.dir = 1
					self.running = 1
			if not self.running:
				if key == self.keys["down"]:
					self.crouchdown = 1
					self.crouching = 1
					self.current = 0
				if key == self.keys["up"]:
					print "upjump"
			elif self.running:
				if key == self.keys["down"]:
					self.rolling = 1
					self.current = 0
					if key == self.keys["right"]:
						self.xMove = 8
					elif key == self.keys["left"]:
						self.xMove = -8
				elif key == self.keys["up"]:
					if key == self.keys["right"]:
						self.xMove = 10
					elif key == self.keys["left"]:
						self.xMove = -10
					self.yMove = -6
					self.jumpfwd = 1
					self.inAir = 1
					self.current = 0
					#self.running = 0
					#print "jump fwd"

		if not self.lastkey:
			self.lastkey = key

	def MoveKeyUp(self, key):
		"""Event fuction for when any keys bound to the current player object are let go of"""
		if not self.noKeys:
			if key == self.lastkey:
				if key == self.keys["down"]:
					self.crouchup = 1
					self.crouchdown = 0
				self.lastkey = 0
				self.xMove = 0
				self.running = 0
				#self.crouching = 0
				self.current = 0

	def update(self):
		if self.fallingforwards:
			if self.current == len(self.frames["fallforwards"]) -1:
				self.current = 0
				self.fallingforwards = 0
				self.xMove = 0
			else:
				self.current += 1
			self.image = self.frames["fallforwards"][self.current]
		elif self.fallingback:
			if self.current == len(self.frames["fallback"]) -1:
				self.current = 0
				self.fallingback = 0
				self.noKeys = 0
				#self.xMove = 0
			else:
				self.current += 1
			self.image = self.frames["fallback"][self.current]
		elif self.crouching:
			self.image = self.frames["crouch"][self.current]
			if self.current == len(self.frames["crouch"]) -1:
				self.current = len(self.frames["crouch"]) -1
			elif self.crouchdown:
				self.current += 1
			if self.crouchup:
				self.crouchup = 0
				self.current -= 1
				self.crouching = 0
		elif self.rolling:
			self.image = self.frames["roll"][self.current]
			if self.current == len(self.frames["roll"]) -1:
				self.rolling = 0
				self.crouching = 1
				self.current = 0
				self.crouchdown = 1
				self.xMove = 0
				self.lastkey=self.keys["down"]
			else:
				self.current += 1
		elif self.jumpfwd:
			self.image = self.frames["jumpfwd"][self.current]
			if self.current == len(self.frames["jumpfwd"]) -1:
				self.jumpfwd = 0
				self.current = 0
			else:
				self.current += 1
		elif self.running:
			self.image = self.frames["run"][self.current]
			if self.current == len(self.frames["run"]) -1:
				self.current = 0
			else:
				self.current += 1
		elif self.inAir:
			self.image = self.fall
		else:
			self.crouchup = 0
			self.crouchdown = 0
			self.image = self.stand
		if self.dir==1:
			self.image = pygame.transform.flip(self.image, 1, 0)
		#if self.yMove < self.maxVol:
		#	self.yMove += self.gravity
		
		move = self.feetRect.move(0, self.yMove)
		
		if move.collidelist(self.platform) == -1:
			self.rect.move_ip(0, self.yMove)
			self.feetRect.move_ip(0, self.yMove)
		else:
			self.inAir = 0
			for i in range(self.gravity+1, 0, -1):
				move = self.feetRect.move(0, i)
				
				if move.collidelist(self.platform) == -1:
					self.rect.move_ip(0, i)
					self.feetRect.move_ip(0, i)
		self.rect.move_ip(self.xMove,0)
		self.feetRect.move_ip(self.xMove,0)

	def collide(self, dir, speed):
		"""Acts on collitions"""
		#if self.xMove == -6 or self.xMove == 6 and speed == -6 or speed == 6:
		#	if self.xMove == -6:
		#		self.xMove = 6
		#	else:
		#		self.xMove = -6
		#	self.fallingback = 1
		#	self.running = 0
		#	self.current = 0
		#	self.noKeys = 1
			#self.xMove = 6
		#else:
		#	self.fallingforwards = 0
			
		#print otherdir, speed
		return
	
class Platform(pygame.sprite.Sprite):
	"""Platform Sprite"""
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = loadImage('platform.png', 1, -1)
		self.rect.move_ip(x, y)
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
		self.rectTop = pygame.Rect(x, y, 14, 1)

class Mallow(pygame.sprite.Sprite):
	"""Mallow Sprite"""
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = loadImage('mallow.png', 1)
		self.rect.move_ip(x, y)

class MallowAnm(pygame.sprite.Sprite):
	"""MallowAnm Sprite"""
	def __init__(self,x,y,frame):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.rect = pygame.Rect(0, 0, 16, 8)
		self.rect.move_ip(x, y)
		self.frames = {}
		self.loadAnm("mallow", 4)
		self.current = frame
	
	def loadAnm(self,name,num):
		self.frames[name]=[]
		for i in range(num):
			image = loadImage(name+str(i)+".png", 0, -1)
			self.frames[name].append(image)

	def update(self):
		if self.current == len(self.frames["mallow"])-1:
			self.current = 0
		else:
			self.current += 1
		self.image = self.frames["mallow"][self.current]

class Bubble(pygame.sprite.Sprite):
	"""MallowAnm Sprite"""
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.rect = pygame.Rect(0, 0, 16, 16)
		self.rect.move_ip(x, y)
		self.frames = {}
		self.loadAnm("bubble", 3)
		self.current = 0
		#load weapon images
		self.weapons = {}
		self.weapons["gun"] = loadImage('gun.png', 0, -1)
		self.weapons["hook"] = loadImage('hook.png', 0, -1)
		self.weapons["x"] = loadImage('x.png', 0, -1)
		self.weapons["parachute"] = loadImage('parachute.png', 0, -1)
		self.weapons["nuke"] = loadImage('nuke.png', 0, -1)
		self.weapons["boot"] = loadImage('boot.png', 0, -1)
		self.weapons["death"] = loadImage('death.png', 0, -1)
		self.weapons["invis"] = loadImage('invis.png', 0, -1)
		self.weapons["10000v"] = loadImage('10000v.png', 0, -1)
		self.weapons["mine"] = loadImage('mine.png', 0, -1)
		self.currentWeapon = self.weapons.keys()[randint(0,9)]
		self.vector = (40,10)
		
	def loadAnm(self,name,num):
		self.frames[name]=[]
		for i in range(num):
			image = loadImage(name+str(i)+".png", 0, -1)
			self.frames[name].append(image)

	def update(self):
		if self.current == len(self.frames["bubble"])-1:
			self.current = 0
		else:
			self.current += 1
		self.image = self.frames["bubble"][self.current]
		self.image.blit(self.weapons[self.currentWeapon], (0, 0))
		
		newpos = self.calcnewpos(self.rect,self.vector)
		self.rect = newpos

	def calcnewpos(self,rect,vector):
		(angle,z) = vector
		(dx,dy) = (z*math.cos(angle),z*math.sin(angle))
		return rect.move(dx,dy)
class Rope(pygame.sprite.Sprite):
	"""The rope"""
	def __init__(self,x,y,len):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = loadImage('rope.png', 1)
		self.rect.move_ip(x, y)
		self.image = pygame.transform.scale(self.image,(1,16*len))

class Main():
	def __init__(self):
		"""Init function for the main class. Sets up everything."""
		
	#Initialize Everything
		#pygame.init()
		pygame.font.init()
		pygame.display.init()
		self.screen = pygame.display.set_mode((640, 400))
		pygame.display.set_caption('Mduel')
	#Menu
		self. introimage = loadImage("intro.png",0)
	#Create The Backgound
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((0, 0, 0))

	#Display The Background
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
		
	#Font
		self.font = pygame.font.Font("data/marshmallowDuel.ttf", 28)
		self.font2 = pygame.font.Font("data/marshmallowDuel.ttf", 20)
	#Prepare Game Objects
		self.clock = pygame.time.Clock()
		self.platform = self.generateBricks()
		self.groundGroup = pygame.sprite.Group()
		self.groundGroup.add(self.platform)
		self.platfromRects = []
		for i in self.platform:
			self.platfromRects.append(i.rectTop)
		self.player1 = Player(39, 288, self.platfromRects)
		#self.player1 = Player(0, 0, self.platfromRects)
		self.player1.setKeys(K_d, K_a, K_s, K_w)
		self.player2 = Player(457, 288, self.platfromRects)
		self.player2.dir = 1
		self.player2.setKeys()
		self.rope = self.generateRopes()
		self.mallow = []
		for i in range(22):
			self.mallow.append(Mallow(i*(15*2),400-(15*2)))
		#mallows = MallowAnm()
		self.mallows = []
		frame = 0
		for i in range(20):
			if frame == 4:
				frame = 0
			self.mallows.append(MallowAnm(i*(16*2),400-16-30,frame))
			frame +=1
		self.bubble1 = Bubble(50, 50)
		self.bubble2 = Bubble(50, 50)
		self.allsprites = pygame.sprite.RenderPlain((self.player1, self.player2, self.platform, self.mallows, self.mallow, self.rope, self.bubble1))
		self.playerGroup = pygame.sprite.Group()
		self.playerGroup.add(self.player1, self.player2)
		
	#Odds and ends
		self.menu = 1
		self.playing = 0
		self.page = 0
		self.bind = 0
		self.connect = 0
		self.bound = 0
		self.connected = 0
		self.selected =  -2
		self.getnewkey = 0
		self.menuItems = [""]*3#number of main menu items
		self.keyItems = {}
		self.quit = 0
	#players
		self.playerfile = open("players","r")
		self.players = []
		self.playerinfo = []
		self.playerlist = self.playerfile.readlines()
		for i in range(6):
			self.players.append("".join(findall("[a-zA-Z]+", self.playerlist[i])))
			self.playerinfo.append(findall("[-0-9]+", self.playerlist[i]))
		self.player1.name = self.players[0]
		self.player2.name = self.players[1]
		
	#settings
		self.settings = ConfigParser.RawConfigParser()
		self.settings.readfp(open('settings'))
		self.port = self.settings.getint('net','port')

		self.sideLeft = pygame.Rect(0, 0, 0, 640)
		self.sideRight = pygame.Rect(400, 0, 0, 640)
		self.sideTop = pygame.Rect(400, 0, 0, 640)
		self.sideBottom = pygame.Rect(400, 0, 0, 640)
		print time.clock()

	def mainloop(self):
		"""The games main loop"""
		while 1:
			self.clock.tick(10)
			if self.playing:
				self.inGameEvents()
				self.allsprites.update()
				if len(PixelPerfect.spritecollide_pp(self.player1, self.playerGroup, 0)) == 2:
					self.player1.collide(self.player2.dir, self.player2.xMove)
					self.player2.collide(self.player1.dir, self.player1.xMove)
				#Draw Everything
				self.screen.blit(self.background, (0, 0))
				self.allsprites.draw(self.screen)
				pygame.display.flip()
			if self.menu:
				self.inMenuEvents()
				self.drawPage()
				self.screen.blit(self.background, (0, 0))
				pygame.display.flip()
			if self.bind:
				if not self.bound:
					self.binds()
					self.bound = 1
				read, write, err = select.select([self.conn], [self.conn], [])
				if len(read):
					self.player2 = self.depickelForRecving(self.conn.recv(512), self.player2)
				if len(write):
					self.conn.send(self.pickelForSending(self.player1))
			if self.connect:
				if not self.connected:
					if self.connects():
						self.connected=1
					#if self.s:
					else:
						self.connect=0
						continue
				read, write, err = select.select([self.s], [self.s], [])
				if len(read):
					self.player1 = self.depickelForRecving(self.s.recv(512), self.player1)
				if len(write):
					self.s.send(self.pickelForSending(self.player2))
					
			if self.quit:
				return

	def drawPage(self):
		"""Pages are 0: shows intro image 1: main menu 2: view fighters 3: set controls 9: displays who is playing when game is starting 10: get game started"""
		if self.page is 0:
			self.background.blit(self.introimage, (0, 0))
		elif self.page is 1:
			if self.selected == -1:
				self.selected = 2
			if self.selected == 3:
				self.selected = 0
			if not self.drawMenuItem("Begin Game",		0, 50, 9):
				return
			if not self.drawMenuItem("View Fighters",	1, 70, 2):
				return
			if not self.drawMenuItem("Set Controls",	2, 90, 3):
				return
		elif self.page is 2:
			for i in range(len(self.players)):
				if self.players[i] == self.player1.name:
					self.colour = (176, 0, 0)
				elif self.players[i] == self.player2.name:
					self.colour = (0, 48, 192)
				else:
					self.colour = (164, 64, 164)
				
				y=144+18*(i+1)
				self.text = self.font2.render(self.players[i], 0, self.colour)
				self.background.blit(self.text, (0, y))
				
				self.text = self.font2.render(self.playerinfo[i][0], 0, self.colour)
				self.background.blit(self.text, (150, y))
				
				self.text = self.font2.render(self.playerinfo[i][1], 0, self.colour)
				self.background.blit(self.text, (250, y))
				
				self.text = self.font2.render(self.playerinfo[i][2], 0, self.colour)
				self.background.blit(self.text, (300, y))
				
				self.text = self.font2.render(self.playerinfo[i][3], 0, self.colour)
				self.background.blit(self.text, (400, y))
				
				self.text = self.font2.render(self.playerinfo[i][4], 0, self.colour)
				self.background.blit(self.text, (500, y))
				
			self.text = self.font.render("Name", 0, (255, 255, 255))
			self.background.blit(self.text, (0,140))
			self.text = self.font.render("Rank", 0, (255, 255, 255))
			self.background.blit(self.text, (150,140))
			self.text = self.font.render("W", 0, (255, 255, 255))
			self.background.blit(self.text, (250,140))
			self.text = self.font.render("L", 0, (255, 255, 255))
			self.background.blit(self.text, (300,140))
			self.text = self.font.render("S", 0, (255, 255, 255))
			self.background.blit(self.text, (400,140))
			self.text = self.font.render("FIDS", 0, (255, 255, 255))
			self.background.blit(self.text, (500,140))
		elif self.page is 3:
			self.posinfo={}
			self.posinfo["p1"]=self.player1
			self.posinfo["p2"]=self.player2
			self.posinfo["x1"]=50
			self.posinfo["x2"]=450
			self.posinfo["colour1"]=(176, 0, 0)
			self.posinfo["colour2"]=(0, 48, 192)
			for i in range(1,3):
				stri = str(i)

				self.text = self.font.render("Player "+str(i), 0, self.posinfo["colour"+stri])
				self.background.blit(self.text, (self.posinfo["x"+stri],25))
				
				self.setNewKey("Right", "right", stri, 50)
				self.setNewKey("Left", "left", stri, 75)
				self.setNewKey("Crouch", "down", stri, 100)
				self.setNewKey("Jump", "up", stri, 125)

		elif self.page is 9:
			self.text = self.font.render(self.player1.name+" vs. "+self.player2.name, 0, (164, 64, 164))
			self.pos = self.text.get_rect(center=(self.background.get_width()/2,self.background.get_height()/2))
			self.background.blit(self.text, self.pos)
		elif self.page is 10:
			self.playing = 1
			self.menu = 0
			self.background.fill((0, 0, 0))

	def generateBricks(self):
		"""platform generator"""
		platform = []
		for i in range(51):
			if (i<3):
				platform.append(Platform((i*16+24)*2, (192-32+8)*2))
			elif (i<6):
				platform.append(Platform((256-24-((i-3)*16))*2, (192-32+8)*2))
			elif (i>47):
				platform.append(Platform((256-16-8-((i-47)*16))*2, (192-32+8+4*-32)*2))
			elif (i>44):
				platform.append(Platform(((i-45)*16+16+16+8)*2, (192-32+8+4*-32)*2))
			else:
				j = i-6;
				col = j%13;
				row = j/13;
				if (randint(0,10) < 7):
					platform.append(Platform(((col+1)*16+16)*2, (192-32+8+((row+1)*-32))*2))
		return platform

	def generateRopes(self):
		"""Rope generator"""
		rope = []
		rope.append(Rope(56*2, 3*2, 9*2))
		rope.append(Rope((256-56)*2, 3*2, 9*2))
		return rope

	def inGameEvents(self):
		"""Handle Input Events"""
		for event in pygame.event.get():
			if event.type == QUIT:
				self.quit = 1
			elif event.type == KEYDOWN:
				if event.key in self.player1.keys.values():
					self.player1.MoveKeyDown(event.key)
				if event.key in self.player2.keys.values():
					self.player2.MoveKeyDown(event.key)
				if event.key == K_b:
					self.bind = 1
				if event.key == K_c:
					self.connect = 1
			elif event.type == KEYUP:
				if event.key in self.player1.keys.values():
					self.player1.MoveKeyUp(event.key)
				if event.key in self.player2.keys.values():
					self.player2.MoveKeyUp(event.key)

	def inMenuEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.quit = 1
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				self.page = 1
				self.background.fill((0, 0, 0))
			elif event.type == KEYDOWN:
				if self.page is 0:
					if event.key is K_SPACE:
						self.page = 1
						self.background.fill((0, 0, 0))
				if self.page is 1:
					if event.key == K_DOWN:
						if self.selected == -2:
							self.selected = 2
						self.selected +=1
					if event.key == K_UP:
						if self.selected == -2:
							self.selected = 0
						self.selected -=1

					if event.key == K_RETURN:
						if self.selected == 0:
							self.page=9
							self.background.fill((0, 0, 0))
						elif self.selected == 1:
							self.page = 2
							self.background.fill((0, 0, 0))
						elif self.selected == 2:
							self.page = 3
							self.background.fill((0, 0, 0))
				if self.page is 3:
					if self.getnewkey:
						self.posinfo["p"+self.getnewkey[1]].keys[self.getnewkey[0]] = event.key
						self.getnewkey = 0
						self.background.fill((0, 0, 0))
				if self.page is 9:
					if event.key == K_SPACE:
						self.page = 10
					
	def drawMenuItem(self, text, selectId, y, page):
		if self.selected == selectId:
			self.menucolour = (176, 0, 0)
		else:
			self.menucolour = (255,255,255)
		text = self.font.render(text, 0, self.menucolour)
		self.menuItems[selectId] = text.get_rect(center=(self.background.get_width()/2, y))
		self.background.blit(text, self.menuItems[selectId])
		
		if self.menuItems[selectId].collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
			self.page = page
			self.background.fill((0, 0, 0))
			return 0
		return 1
		
	def setNewKey(self, name, key, i, y):
		self.text = self.font.render(name+": "+pygame.key.name(self.posinfo["p"+i].keys[key]), 0, self.posinfo["colour"+i])
		self.keyItems["textpos"+i] = self.text.get_rect(x=self.posinfo["x"+i],y=y)
		self.background.blit(self.text, self.keyItems["textpos"+i])
		if self.keyItems["textpos"+i].collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
			self.text = self.font.render("Press new "+name+" key: ", 0, (255,255,255))
			self.pos = self.text.get_rect(centerx=self.background.get_width()/2,y=350)
			self.background.blit(self.text, self.pos)
			self.getnewkey = (key, i)
			
	def connects(self):
		"""Connects to the server"""
		self.HOST = '127.0.0.1'	# The remote host
		self.s = socket.socket()
		try:
			self.s.connect((self.HOST, self.port))
		except socket.error, msg:
			print msg[1]
			return 0
		return 1

	def binds(self):
		"""Makes the curret player wait for a connection from another player"""
		self.HOST = ''
		self.s = socket.socket()
		self.s.bind((self.HOST, self.port))
		self.s.listen(1)
		self.conn, self.addr = self.s.accept()
		print 'Connected by', self.addr


	def pickelForSending(self, player):
		"""Gets the infermation in the player objet ready for sending"""
		info = {}
		info["xMove"] =  player.xMove
		info["yMove"] =  player.yMove
		info["current"] =  player.current
		info["running"] =  player.running
		info["dir"] =  player.dir
		dump = cPickle.dumps(info)
		return compress(dump)
		
	def depickelForRecving(self, info, player):
		"""inserts infermation from other client"""
		info = decompress(info)
		info = cPickle.loads(info)
		if "xMove" in info:
			player.xMove = info["xMove"]
		if "yMove" in info:
			player.yMove = info["yMove"]
		if "current" in info:
			player.current = info["current"]
		if "running" in info:
			player.running = info["running"]
		if "dir" in info:
			player.dir = info["dir"]
		"""for value in info:
			player.value = info[value]
			print player.value, player.xMove, value""" #does not work yet. want to make it work. may use dicts for info storage in player
		return player
	
if __name__ == '__main__':
	main = Main()
	try:
		main.mainloop()
	except KeyboardInterrupt:
		print "Keyboard Interrupt"
#new lines so i can scroll down farther

















