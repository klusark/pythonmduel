#/usr/bin/env python
"""
Mduel
"""

#Import Modules
import pygame, cPickle, PixelPerfect, socket, ConfigParser
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
	def __init__(self, x = 0, y = 0):
		"""Initializes Player class"""
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.frames = {}
		self.loadImages()
		self.image = self.stand
		self.rect.move_ip(x,y)
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
		self.name = "Unset"
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
		
	def loadAnm(self,name,num):
		self.frames[name]=[]
		for i in range(num):
			image = loadImage(name+str(i)+".png",0,-1)
			self.frames[name].append(image)
			
	def loadImages(self):
		"""loads images"""
		self.loadAnm("run", 4)
		self.loadAnm("fallforwards", 2)
		self.loadAnm("fallback", 2)
		self.loadAnm("crouch", 2)
		self.loadAnm("roll", 4)
		self.stand, self.rect = loadImage('stand.png', 1,-1)
		
	def setKeys(self, right = K_RIGHT, left = K_LEFT, down = K_DOWN):
		"""setKeys(right key, left key, crouch key)
		Sets the keys for the player object"""
		self.keys = {}
		self.keys["right"] = right
		self.keys["left"] = left
		self.keys["down"] = down
		
	def MoveKeyDown(self, key):
		"""Event fuction for when any keys bound to the current player object are hit"""
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
		elif self.running:
			if key == self.keys["down"]:
				self.rolling = 1
				self.current = 0
				if key == self.keys["right"]:
					self.xMove = 8
				elif key == self.keys["left"]:
					self.xMove = -8
		if not self.lastkey:
			self.lastkey = key

	def MoveKeyUp(self, key):
		"""Event fuction for when any keys bound to the current player object are let go of"""
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
				self.xMove = 0
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
		elif self.running:
			self.image = self.frames["run"][self.current]
			if self.current == len(self.frames["run"]) -1:
				self.current = 0
			else:
				self.current += 1
		else:
			self.crouchup = 0
			self.crouchdown = 0
			self.image = self.stand
		if self.dir==1:
			self.image = pygame.transform.flip(self.image, 1, 0)
		#if self.xMove > 0:
		#	self.xMove -= 1
		
		self.rect.move_ip(self.xMove,self.yMove)

	def collide(self, dir, speed):
		"""Acts on collitions"""
		if self.xMove == 0 and speed == -6 or speed == 6:
			self.fallingback = 1
			self.running = 0
			self.current = 0
			self.xMove = 6
			
		else:
			self.fallingforwards = 0
			
		#print otherdir, speed
	
class Platform(pygame.sprite.Sprite):
	"""Platform Sprite"""
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = loadImage('platform.png', 1, -1)
		self.rect.move_ip(x, y)
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()

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
		self.image, self.rect = loadImage('mallow0.png', 1, -1)
		self.rect.move_ip(x, y)
		self.anmframe = []
		for i in range(4):
			image = loadImage("mallow"+str(i)+".png",0,-1)
			self.anmframe.append(image)
		self.current = frame

	def update(self):
		if self.current == len(self.anmframe)-1:
			self.current = 0
		else:
			self.current += 1
		self.image = self.anmframe[self.current]

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
		pygame.init()
		
		self.screen = pygame.display.set_mode((640, 400))
		pygame.display.set_caption('Mduel')
		#pygame.mouse.set_visible(0)
	#Menu
		self. introimage = loadImage("intro.png",0)
		#menup2 = loadImage("menup2.png",0)
	#Create The Backgound
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((0, 0, 0))

	#Display The Background
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
		
	#Font
		pygame.font.init()
		self.font = pygame.font.Font("data/marshmallowDuel.ttf", 28)
	#Prepare Game Objects
		self.clock = pygame.time.Clock()
		self.platform = self.generateBricks()
		self.groundGroup = pygame.sprite.Group()
		self.groundGroup.add(self.platform)
		self.player1 = Player(39, 288)
		self.player1.setKeys(K_d, K_a, K_s)
		self.player2 = Player(457, 288)
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
		self.allsprites = pygame.sprite.RenderPlain((self.player1, self.player2, self.platform, self.mallows, self.mallow, self.rope))
		self.playerGroup = pygame.sprite.Group()
		self.playerGroup.add(self.player1, self.player2)
	#Odds and ends
		self.menu = 1
		self.playing = 0
		self.page = 0 #
		self.bind = 0
		self.connect = 0
		self.bound = 0
		self.connected = 0
		self.selected =  -2
		self.getnewkey = 0
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
		self.stuffs = {}
		
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
		
	def mainloop(self):
		"""The games main loop"""
		while 1:
			self.clock.tick(10)
			if self.playing:
				#Handle Input Events
				for event in pygame.event.get():
					if event.type == QUIT:
						return
					elif event.type == KEYDOWN:
						if event.key in self.player1.keys.values():
							self.player1.MoveKeyDown(event.key)
						if event.key in self.player2.keys.values():
							self.player2.MoveKeyDown(event.key)
						#if event.key == K_DOWN:
						#	player1.yMove = 5
						if event.key == K_b:
							self.bind = 1
						if event.key == K_c:
							self.connect = 1
					elif event.type == KEYUP:
						if event.key in self.player1.keys.values():
							self.player1.MoveKeyUp(event.key)
						if event.key in self.player2.keys.values():
							self.player2.MoveKeyUp(event.key)
				self.allsprites.update()
				if len(PixelPerfect.spritecollide_pp(self.player1, self.playerGroup, 0)) == 2:
					self.player1.collide(self.player2.dir, self.player2.xMove)
					self.player2.collide(self.player1.dir, self.player1.xMove)
				
				#Draw Everything
				self.screen.blit(self.background, (0, 0))
				self.allsprites.draw(self.screen)
				pygame.display.flip()
			if self.menu:
				"""Pages are 0: shows intro image 1: main menu 2: view fighters 3: set controls 9: displays who is playing when game is starting 10: get game started"""
				for event in pygame.event.get():
					if event.type == QUIT:
						return
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
							
				if self.page is 0:
					self.background.blit(self.introimage, (0, 0))
				elif self.page is 1:
					if self.selected == -1:
						self.selected = 2
					if self.selected == 3:
						self.selected = 0
					self.menucolour = (255,255,255)
					#menucolour = (176, 0, 0)
					if self.selected == 0:
						self.menucolour = (176, 0, 0)
					else:
						self.menucolour = (255,255,255)
					self.begin = self.font.render("Begin Game", 0, self.menucolour)
					self.beginpos = self.begin.get_rect(center=(self.background.get_width()/2,50))
					self.background.blit(self.begin, self.beginpos)
					
					if self.selected == 1:
						self.menucolour = (176, 0, 0)
					else:
						self.menucolour = (255,255,255)
					
					self.view = self.font.render("View Fighters", 0, self.menucolour)
					self.viewpos = self.view.get_rect(center=(self.background.get_width()/2,70))
					self.background.blit(self.view, self.viewpos)
					
					if self.selected == 2:
						self.menucolour = (176, 0, 0)
					else:
						self.menucolour = (255,255,255)
						
					self.controls = self.font.render("Set Controls", 0, self.menucolour)
					self.controlspos = self.controls.get_rect(center=(self.background.get_width()/2,90))
					self.background.blit(self.controls, self.controlspos)
					
					
					#mouse code
					if self.beginpos.collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
						self.page=9
						self.background.fill((0, 0, 0))

					if self.viewpos.collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
						self.page = 2
						self.background.fill((0, 0, 0))
					
					if self.controlspos.collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
						self.page = 3
						self.background.fill((0, 0, 0))

				elif self.page is 2:
					for i in range(len(self.players)):
						if self.players[i] == self.player1.name:
							self.colour = (176, 0, 0)
						elif self.players[i] == self.player2.name:
							self.colour = (0, 48, 192)
						else:
							self.colour = (164, 64, 164)
						self.text = self.font.render(self.players[i], 0, self.colour)
						self.background.blit(self.text, (0,160+40*i))
						
						self.text = self.font.render(self.playerinfo[i][0], 0, self.colour)
						self.background.blit(self.text, (150,160+40*i))
						
						self.text = self.font.render(self.playerinfo[i][1], 0, self.colour)
						self.background.blit(self.text, (250,160+40*i))
						
						self.text = self.font.render(self.playerinfo[i][2], 0, self.colour)
						self.background.blit(self.text, (300,160+40*i))
						
						self.text = self.font.render(self.playerinfo[i][3], 0, self.colour)
						self.background.blit(self.text, (400,160+40*i))
						
						self.text = self.font.render(self.playerinfo[i][4], 0, self.colour)
						self.background.blit(self.text, (500,160+40*i))
						
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

				elif self.page is 9:
					self.text = self.font.render(self.player1.name+" vs. "+self.player2.name, 0, (164, 64, 164))
					self.pos = self.text.get_rect(center=(self.background.get_width()/2,self.background.get_height()/2))
					self.background.blit(self.text, self.pos)
				elif self.page is 10:
					self.playing = 1
					self.menu = 0
					self.background.fill((0, 0, 0))

				self.screen.blit(self.background, (0, 0))
				pygame.display.flip()
			if self.bind:
				if not self.bound:
					self.binds()
					self.bound = 1

				self.player2 = self.depickelForRecving(self.conn.recv(512), self.player2)
				self.conn.send(self.pickelForSending(self.player1))
			if self.connect:
				if not self.connected:
					if self.connects():
						self.connected=1
					#if self.s:
						
					else:
						self.connect=0
						continue

				self.s.send(self.picelForSending(self.player2))
				self.player1 = self.depickelForRecving(self.s.recv(512), self.player1)
		
	def setNewKey(self, name, key, i, y):
		self.text = self.font.render(name+": "+pygame.key.name(self.posinfo["p"+i].keys[key]), 0, self.posinfo["colour"+i])
		self.stuffs["textpos"+i] = self.text.get_rect(x=self.posinfo["x"+i],y=y)
		self.background.blit(self.text, self.stuffs["textpos"+i])
		if self.stuffs["textpos"+i].collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
			self.text = self.font.render("Press new "+name+" key: ", 0, (255,255,255))
			self.pos = self.text.get_rect(centerx=self.background.get_width()/2,y=350)
			self.background.blit(self.text, self.pos)
			self.getnewkey = (key, i)
			
	def connects(self):
		"""Connects to the server"""
		self.HOST = '127.0.0.1'	# The remote host
		self.s = socket.socket()
		try:
			self.s.connect((self.HOST, self.PORT))
		except socket.error, msg:
			print msg[1]
			return 0
		return 1

	def binds(self):
		"""Makes the curret player wait for a connection from another player"""
		self.HOST = ''
		self.s = socket.socket()
		self.s.bind((self.HOST, self.PORT))
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

















