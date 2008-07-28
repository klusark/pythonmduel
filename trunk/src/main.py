import pygame, time, cPickle, socket, select
from ConfigParser import RawConfigParser
from random import randint
#from re import findall
from os import path
from pygame.locals import *
import sprites, player, menu, image
theme = "main"

class Main(image.loadImage, menu.Menu):
	def __init__(self):
		"""Init function for the main class. Sets up everything."""
		#Initialize Everything
		pygame.display.init()
		self.screen = pygame.display.set_mode((640, 400))
		pygame.display.set_caption('Mduel')
		#settings
		self.settings = RawConfigParser()
		self.settings.readfp(open('settings'))
		self.port = self.settings.getint('net', 'port')
		self.connectAddy = self.settings.get('net', 'connectAddy')
		
		#Create The Backgound
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()

		#Font
		pygame.font.init()
		self.font = pygame.font.Font(path.join("data", theme, "fonts", "marshmallowDuel.ttf"), 28)
		self.font2 = pygame.font.Font(path.join("data", theme, "fonts", "marshmallowDuel.ttf"), 20)

		self.clock = pygame.time.Clock()
		
		#Odds and ends
		self.menu = 1
		self.playing = 0
		self.page = 0
		self.connect = 0
		self.connected = 0
		self.getnewkey = 0
		self.keyItems = {}
		self.quit = 0
		self.id = [0]
		#players
		"""self.playerfile = open("players", "r")
		self.playerNames = []
		self.playerinfo = []
		self.playerlist = self.playerfile.readlines()
		for i in range(6):
			self.playerNames.append("".join(findall("[a-zA-Z]+", self.playerlist[i])))
			self.playerinfo.append(findall("[-0-9]+", self.playerlist[i]))"""
		self.player1Name = "jim"
		self.player2Name = "bob"


		self.sideLeft = pygame.Rect(0, -5, 0, 410)
		self.sideRight = pygame.Rect(635, -5, 0, 410)
		self.sideTop = pygame.Rect(-5, -3, 650, 0)
		self.sideBottom = pygame.Rect(-5, 340, 645, 0)
		
		self.__initMenu__()
		
	def mainloop(self):
		"""The games main loop"""
		while 1:
			if self.playing:
				self.clock.tick(60)
				self.inGameEvents()
				self.allsprites.update()
				self.colisions()
				self.screen.blit(self.background, (0, 0))
				self.allsprites.draw(self.screen)
				pygame.display.flip()
			if self.menu:
				self.clock.tick(60)
				self.inMenuEvents()
				self.drawPage()
				self.screen.blit(self.background, (0, 0))
				pygame.display.flip()
			if self.connect:
				if not self.connected:
					if self.connects():
						self.connected=1
					else:
						self.connect=0
						continue
				read, write, err = select.select([self.s], [self.s], [])
				#print read, write
				#try:
				if len(read):
					pass
				if len(write):
					packet = self.players[self.id].playerVars
					packet["type"] = 9
					self.s.send(cPickle.dumps(packet))
				#except socket.error, msg:
				#	print msg
				#	self.connect = 0
			if self.quit:
				if self.connect:
					self.s.send(cPickle.dumps({"type" : 7}))
					self.s.shutdown(2)
				return

	def __initGame__(self):
		self.platform = self.generateBricks()
		self.groundGroup = pygame.sprite.Group()
		self.groundGroup.add(self.platform)
		self.platfromRects = []
		
		for i in self.platform:
			self.platfromRects.append(i.rectTop)
			
		self.players = {}
		
		self.players[0] = player.Player(51, 288)
		self.players[0].setKeys(K_d, K_a, K_s, K_w, K_q)
		
		self.players[1] = player.Player(531, 288, 1)
		self.players[1].setKeys()
		
		self.players[0].registerVars(self.players[1], self.platfromRects, None)
		self.players[1].registerVars(self.players[0], self.platfromRects, None)
		
		self.emitterImage = self.loadImage("emitter.png", 0, -1)
		
		self.rope = self.generateRopes()

		self.mallow = []
		for i in range(22):
			self.mallow.append(sprites.Mallow(i*(15*2), 400-(15*2)))
		self.mallows = []
		frame = 0
		for i in range(20):
			if frame == 4:
				frame = 0
			self.mallows.append(sprites.MallowAnm(i*(16*2), 400-16-30, frame))
			frame +=1
		self.bubbles = []
		for i in range(3):
			self.bubbles.append(sprites.Bubble(i))
		
		
		self.playerGroup = pygame.sprite.Group()
		self.playerGroup.add(self.players[0], self.players[1])
		self.allsprites = pygame.sprite.OrderedUpdates((self.platform, self.mallows, self.mallow, self.rope, self.playerGroup, self.bubbles))
		self.players[0].name = self.player1Name
		self.players[1].name = self.player2Name
		
	def colisions(self):
		pass
		"""for bubble in self.bubbles:
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
			player = bubble.rect.collidelist([self.players[0], self.players[1]])
			if player is not -1 and bubble.image in bubble.frames["bubble"]:
				bubble.popping = 1
				self.players[player].currentWeapon = bubble.currentWeapon
				if self.players[player].currentWeapon is "gun":
					self.players[player].ammo = 4
				if player is 0:
					self.player1.currentWeapon = bubble.currentWeapon
				elif player is 1:
					self.player2.currentWeapon = bubble.currentWeapon"""
		"""if len(PixelPerfect.spritecollide_pp(self.player1, self.playerGroup, 0)) == 2:
			self.player1.collide(self.player2.dir, self.player2.xMove)
			self.player2.collide(self.player1.dir, self.player1.xMove)"""
	
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
		"""Handle events in the game"""
		for event in pygame.event.get():
			if event.type == QUIT:
				self.quit = 1
			elif event.type == KEYDOWN:
				for i in self.players:
					if event.key in self.players[i].keys.values():
					   self.players[i].keyDown(event.key)
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
				for i in self.players:
					if event.key in self.players[i].keys.values():
						self.players[i].keyUp(event.key)
			
	def connects(self):
		"""Connects to the server"""
		self.s = socket.socket()
		try:
			self.s.connect((self.connectAddy, self.port))
		except socket.error, msg:
			print msg[1]
			return 0
		self.s.send(cPickle.dumps({"type":6, "name":"joel"}))
		msg = cPickle.loads(self.s.recv(512))
		if msg["type"] == 10:
			self.id = msg["id"]
			self.players = {}
			self.players[self.id] = player.Player(51, 288)
			self.players[self.id].setKeys(K_d, K_a, K_s, K_w, K_q)
			self.playerGroup.add(self.players[self.id])
		return 1

	def pickelForSending(self, player):
		"""Gets the information in the player object ready for sending"""
		info = {}
		for value in player.playerVars:
			info[value] = player.playerVars[value]
		dump = cPickle.dumps(info)
		return compress(dump)
		
	def depickelForRecving(self, info, player):
		"""inserts information from other client"""
		try:
			info = decompress(info)
		except zlibError, msg:
			print msg
		info = cPickle.loads(info)
		for value in info:
			player.playerVars[value] = info[value]
		return player
