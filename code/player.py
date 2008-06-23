import pygame
from pygame.locals import *
import main
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
			image = main.loadImage(name+str(i)+".png", 0, -1)
			self.frames[name].append(image)
			
	def loadImages(self):
		"""loads images"""
		self.loadAnm("run", 4)
		self.loadAnm("jumpfwd", 3)
		self.loadAnm("fallforwards", 2)
		self.loadAnm("fallback", 2)
		self.loadAnm("crouch", 2)
		self.loadAnm("roll", 4)
		self.fall = main.loadImage('fall.png', 0, -1)
		self.stand, self.rect = main.loadImage('stand.png', 1, -1)
		
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
		