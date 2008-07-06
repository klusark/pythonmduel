import pygame, time, PixelPerfect, cPickle, socket, select
from ConfigParser import RawConfigParser
from random import randint
from re import findall
from os import path
from pygame.locals import *
from zlib import compress, decompress
from zlib import error as zlibError
import sprites, player
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

class Main():
	def __init__(self):
		"""Init function for the main class. Sets up everything."""
	#Initialize Everything
		pygame.display.init()
		self.screen = pygame.display.set_mode((640, 400))
		pygame.display.set_caption('Mduel')
	#Menu
		self. introimage = loadImage("intro.png",0)
	#Create The Backgound
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()

	#Font
		pygame.font.init()
		self.font = pygame.font.Font("data/marshmallowDuel.ttf", 28)
		self.font2 = pygame.font.Font("data/marshmallowDuel.ttf", 20)
	#Prepare Game Objects
		self.clock = pygame.time.Clock()
		
	#Odds and ends
		self.menu = 1
		self.playing = 0
		self.page = 0
		self.bind = 0
		self.connect = 0
		self.bound = 0
		self.connected = 0
		self.getnewkey = 0
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
		self.player1Name = self.players[0]
		self.player2Name = self.players[1]
	#settings
		self.settings = RawConfigParser()
		self.settings.readfp(open('settings'))
		self.port = self.settings.getint('net','port')

		self.sideLeft = pygame.Rect(0, -5, 0, 410)
		self.sideRight = pygame.Rect(635, -5, 0, 410)
		self.sideTop = pygame.Rect(-5, -3, 650, 0)
		self.sideBottom = pygame.Rect(-5, 340, 645, 0)
		
	#menu stuffs
		self.__initMenu__()
		
	def mainloop(self):
		"""The games main loop"""
		while 1:
			if self.playing:
				self.clock.tick(10)
				self.inGameEvents()
				self.allsprites.update()
				self.colisions()
				self.screen.blit(self.background, (0, 0))
				self.allsprites.draw(self.screen)
				pygame.display.flip()
			if self.menu:
				self.clock.tick(100)
				self.inMenuEvents()
				self.drawPage()
				self.screen.blit(self.background, (0, 0))
				pygame.display.flip()
			if self.bind:
				if not self.bound:
					self.binds()
					self.bound = 1
				read, write, err = select.select([self.conn], [self.conn], [])
				try:
					if len(read):
						self.player2 = self.depickelForRecving(self.conn.recv(512), self.player2)
					if len(write):
						self.conn.send(self.pickelForSending(self.player1))
				except socket.error, msg:
					print msg
					self.bind = 0
			if self.connect:
				if not self.connected:
					if self.connects():
						self.connected=1
					else:
						self.connect=0
						continue
				read, write, err = select.select([self.s], [self.s], [])
				try:
					if len(read):
						self.player1 = self.depickelForRecving(self.s.recv(512), self.player1)
					if len(write):
						self.s.send(self.pickelForSending(self.player2))
				except socket.error, msg:
					print msg
					self.connect = 0
			if self.quit:
				return
	def __initGame__(self):
		self.platform = self.generateBricks()
		self.groundGroup = pygame.sprite.Group()
		self.groundGroup.add(self.platform)
		self.platfromRects = []
		for i in self.platform:
			self.platfromRects.append(i.rectTop)
		
		self.player1 = player.Player(51, 288, self.platfromRects)
		self.player1.setKeys(K_d, K_a, K_s, K_w)
		self.player2 = player.Player(531, 288, self.platfromRects, 1)
		self.player2.setKeys()
		
		self.rope = self.generateRopes()

		self.mallow = []
		for i in range(22):
			self.mallow.append(sprites.Mallow(i*(15*2),400-(15*2)))
		#mallows = MallowAnm()
		self.mallows = []
		frame = 0
		for i in range(20):
			if frame == 4:
				frame = 0
			self.mallows.append(sprites.MallowAnm(i*(16*2),400-16-30,frame))
			frame +=1
		self.bubbles = []
		for i in range(3):
			self.bubbles.append(sprites.Bubble(i))
		
		self.allsprites = pygame.sprite.OrderedUpdates((self.platform, self.mallows, self.mallow, self.rope, self.player1, self.player2, self.bubbles))
		self.playerGroup = pygame.sprite.Group()
		self.playerGroup.add(self.player1, self.player2)
		self.player1.name = self.player1Name
		self.player2.name = self.player2Name
		
	def __initMenu__(self):
		self.numMenuItmes = 5
		self.menuItems = [""]*self.numMenuItmes
		self.selected =  -2 # so none are selected at start
		
	def colisions(self):
		for bubble in self.bubbles:
			side = bubble.rect.collidelist([self.sideLeft, self.sideRight, self.sideBottom, self.sideTop])
			if side is not -1:
				if side is 0:
					bubble.xMove = -bubble.xMove
				elif side is 1:
					bubble.xMove = -bubble.xMove
				elif side is 2:
					bubble.yMove = -bubble.yMove
				elif side is 3:
					bubble.yMove = -bubble.yMove
			player = bubble.rect.collidelist([self.player1, self.player2])
			if player is not -1 and bubble.image in bubble.frames["bubble"]:
				print "powerup"
		#if len(PixelPerfect.spritecollide_pp(self.player1, self.playerGroup, 0)) == 2:
		#	self.player1.collide(self.player2.dir, self.player2.xMove)
		#	self.player2.collide(self.player1.dir, self.player1.xMove)
		#Draw Everything
	def drawPage(self):
		"""
		Pages are 
		0: shows intro image 
		1: main menu 
		2: view fighters 
		3: set controls 
		4: options
		5: Net options
		8: quits the game 
		9: displays who is playing when game is starting 
		10: starts game
		"""
		if self.page is 0:
			self.background.blit(self.introimage, (0, 0))
			
		elif self.page is 1:
			if self.selected == -1:
				self.selected = self.numMenuItmes-1
			if self.selected == self.numMenuItmes:
				self.selected = 0
			if not self.drawMenuItem("Begin Game",		0, 50, 9):
				return
			if not self.drawMenuItem("View Fighters",	1, 70, 2):
				return
			if not self.drawMenuItem("Set Controls",	2, 90, 3):
				return
			if not self.drawMenuItem("Options",			3, 110, 4):
				return
			if not self.drawMenuItem("Exit",			4, 130, 8):
				return
				
		elif self.page is 2:
			for i in range(len(self.players)):
				if self.players[i] == self.player1Name:
					self.colour = (176, 0, 0)
				elif self.players[i] == self.player2Name:
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
				
			self.drawText("Name", self.font, 0, 140, (255, 255, 255))
			self.drawText("Rank", self.font, 150, 140, (255, 255, 255))
			self.drawText("W", self.font, 250, 140, (255, 255, 255))
			self.drawText("L", self.font, 300, 140, (255, 255, 255))
			self.drawText("S", self.font, 400, 140, (255, 255, 255))
			self.drawText("FIDS", self.font, 500, 140, (255, 255, 255))

			
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

				self.text = self.font.render("player.Player "+str(i), 0, self.posinfo["colour"+stri])
				self.background.blit(self.text, (self.posinfo["x"+stri],25))
				
				self.setNewKey("Right", "right", stri, 50)
				self.setNewKey("Left", "left", stri, 75)
				self.setNewKey("Crouch", "down", stri, 100)
				self.setNewKey("Jump", "up", stri, 125)
		elif self.page is 4:
			if not self.drawMenuItem("Net",	0, 50, 5):
				return
		elif self.page is 5:
			pass
		elif self.page is 8:
			self.quit = 1
		elif self.page is 9:
			self.text = self.font.render(self.player1Name + " vs. " + self.player2Name, 0, (164, 64, 164))
			self.pos = self.text.get_rect(center = (self.background.get_width()/2, self.background.get_height()/2))
			self.background.blit(self.text, self.pos)
			
		elif self.page is 10:
			self.playing = 1
			self.menu = 0
			self.background.fill((0, 0, 0))
			self.__initGame__()
			
	def drawText(self, text, font, x, y, colour):
		text = font.render(text, 0, colour)
		self.background.blit(text, (x, y))
		
	def generateBricks(self):
		"""platform generator"""
		platform = []
		for i in range(4): # bottom left platforms
			platform.append(sprites.Platform((i*16+24)*2, (168)*2))
		for i in range(4): # bottom right platforms
			platform.append(sprites.Platform((304-24-(i*16))*2, (168)*2))
		for i in range(4): # top left
			platform.append(sprites.Platform(97+i*32, 81))
		for i in range(4): # top right
			platform.append(sprites.Platform(417+i*32, 81))
		"""for i in range(50):
			if (i>48):
				platform.append(sprites.Platform((256-16-8-((i-47)*16))*2, (168+4*-32)*2))
			elif (i>44):
				platform.append(sprites.Platform(((i-45)*16+40)*2, (168+4*-32)*2))
			else:
				j = i-6;
				col = j%13;
				row = j/13;
				if (randint(0,10) < 7):
					platform.append(sprites.Platform(((col+1)*16+16)*2, (192-32+8+((row+1)*-32))*2))"""
		return platform

	def generateRopes(self):
		"""Rope generator"""
		rope = []
		rope.append(sprites.Rope(159, 39, 6))
		rope.append(sprites.Rope(479, 39, 6))
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
				if event.key == K_ESCAPE:
					self.playing = 0
					self.menu = 1
					self.page = 1
					self.background.fill((0, 0, 0))
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
							self.selected = self.numMenuItmes-1
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
						elif self.selected == 3:
							self.page = 4
							self.background.fill((0, 0, 0))
						elif self.selected == 4:
							self.quit = 1
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
		for value in player.playerVars:
			info[value] = player.playerVars[value]
		dump = cPickle.dumps(info)
		return compress(dump)
		
	def depickelForRecving(self, info, player):
		"""inserts infermation from other client"""
		try:
			info = decompress(info)
		except zlibError, msg:
			print msg
		info = cPickle.loads(info)
		for value in info:
			player.playerVars[value] = info[value]
		return player