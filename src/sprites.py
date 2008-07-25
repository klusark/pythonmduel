import pygame
from pygame.locals import *
from random import randint
import image
class Platform(pygame.sprite.Sprite, image.loadImage):
	"""Platform Sprite"""
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = self.loadImage('platform.png', 1, -1)
		self.rect.move_ip(x, y)
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
		self.rectTop = pygame.Rect(x, y, 14, 1)

class Mallow(pygame.sprite.Sprite, image.loadImage):
	"""Mallow Sprite"""
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = self.loadImage('mallow.png', 1)
		self.rect.move_ip(x, y)

class MallowAnm(pygame.sprite.Sprite, image.loadImage):
	"""Mallow animation Sprite"""
	def __init__(self, x, y, frame):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.rect = pygame.Rect(0, 0, 16, 8)
		self.rect.move_ip(x, y)
		self.frames = {}
		self.loadAnm("mallow", 4)
		self.current = frame

	def loadAnm(self, name, num):
		self.frames[name]=[]
		for i in range(num):
			image = self.loadImage(name+str(i)+".png", 0, -1)
			self.frames[name].append(image)

	def update(self):
		if self.current == len(self.frames["mallow"])-1:
			self.current = 0
		else:
			self.current += 1
		self.image = self.frames["mallow"][self.current]

class Bubble(pygame.sprite.Sprite, image.loadImage):
	"""bubble Sprite. also used for startpoof"""
	def __init__(self, num):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.rect = pygame.Rect(0, 0, 16, 16)
		self.frames = {}
		self.loadAnm("bubble", 3)
		self.loadAnm("bubblepop", 2)
		self.loadAnm("startpoof", 3)
		self.loadAnm("bubblestart", 3)
		self.current = 0
		self.blank = self.loadImage('blank.png', 0, -1, "", 1)
		#load weapon images
		self.weapons = {}
		self.weapons["gun"] = self.loadImage('gun.png', 0, -1)
		self.weapons["hook"] = self.loadImage('hook.png', 0, -1)
		self.weapons["x"] = self.loadImage('x.png', 0, -1)
		self.weapons["parachute"] = self.loadImage('parachute.png', 0, -1)
		self.weapons["nuke"] = self.loadImage('nuke.png', 0, -1)
		self.weapons["boot"] = self.loadImage('boot.png', 0, -1)
		self.weapons["death"] = self.loadImage('death.png', 0, -1)
		self.weapons["invis"] = self.loadImage('invis.png', 0, -1)
		self.weapons["10000v"] = self.loadImage('10000v.png', 0, -1)
		self.weapons["mine"] = self.loadImage('mine.png', 0, -1)
		self.weapons["tele"] = self.blank
		self.powerup = randint(0, 9)
		self.currentWeapon = self.weapons.keys()[self.powerup]
		#print self.weapons.keys()[self.powerup]
		self.xMove = randint(1, 5)
		self.yMove = randint(1, 5)
		self.locs = [(30, 200), (320, 30), (609, 200)]
		self.poofing = 0
		self.popping = 0
		self.bubblestarting = 0
		self.image = None
		self.hide = 0
		self.wait = 0.0
		if num is 0:
			self.rect.move_ip(51, 288)
			self.poofing = 1
		elif num is 1:
			self.rect.move_ip(531, 288)
			self.poofing = 1
		#self.rect.move_ip(self.locs[randint(0,2)])
	
	def loadAnm(self, name, num):
		self.frames[name]=[]
		for i in range(num):
			image = self.loadImage(name+str(i)+".png", 0, -1, "",1)
			self.frames[name].append(image)

	def update(self):
		if self.poofing:
			if self.current == len(self.frames["startpoof"]):
				self.current = 0
				self.poofing = 0
				self.image = self.blank
				self.getNewSpawn()
				self.hide = 1
				
			else:
				self.image = self.frames["startpoof"][self.current]
				self.current += 1
		elif self.popping:
			if self.current == len(self.frames["bubblepop"]):
				self.current = 0
				self.popping = 0
				self.image = self.blank
				self.getNewSpawn()
				self.hide = 1
			else:
				self.image = self.frames["bubblepop"][self.current]
				self.current += 1
		elif self.bubblestarting:
			if self.current == len(self.frames["bubblestart"]):
				self.bubblestarting = 0
				self.current = 0
			else:
				self.image = self.frames["bubblestart"][self.current]
				self.current += 1
		elif self.hide:
			#self.image = self.blank
			pass
		
		else:
			if self.current == len(self.frames["bubble"])-1:
				self.current = 0
			else:
				self.current += 1
			self.image = self.frames["bubble"][self.current]
			self.image.blit(self.weapons[self.currentWeapon], (0, 0))
			
			self.rect.move_ip(self.xMove, self.yMove)
		
		if self.wait:
			self.wait -= 0.1
			if  self.wait <= 0.1:
				self.wait = 0
				self.hide = 0
				self.current = 0
				self.bubblestarting = 1
	
	def getNewSpawn(self):
		self.rect[0] = 0
		self.rect[1] = 0
		self.rect.move_ip(self.locs[randint(0, 2)])
		self.wait = randint(1, 10)
		self.powerup = randint(0, 9)
		self.currentWeapon = self.weapons.keys()[self.powerup]
		

class Rope(pygame.sprite.Sprite, image.loadImage):
	"""The rope"""
	def __init__(self, x, y, len):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = self.loadImage('rope.png', 1)
		self.rect.move_ip(x, y)
		self.image = pygame.transform.scale(self.image, (2, 50 * len))
