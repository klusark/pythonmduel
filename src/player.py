import pygame
from pygame.locals import *
import main
class Player(pygame.sprite.Sprite):
	"""The Payer class"""
	def __init__(self, x, y, platform, dir = 0):
		"""Initializes Player class"""
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.frames = {}
		self.loadImages()
		self.rect.inflate_ip(-10, 0)
		self.image = self.stand
		self.rect.move_ip(x,y)
		self.feetRect = pygame.Rect(x+5, y+41, 38, 7)
		self.platform = platform
		self.playerVars = {}
		self.playerVars['xMove'] = 0
		self.playerVars['yMove'] = 0
		self.playerVars['current'] = 0
		self.playerVars['running'] = 0
		self.playerVars['dir'] = dir
		self.lastkey = 0
		self.crouching = 0
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
		self.currentWeapon = None
		self.name = "Unset"
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
		
	def loadAnm(self, name, num):
		"""Loads an animation baised on file name"""
		self.frames[name]=[]
		for i in range(num):
			image = main.loadImage(name+str(i)+".png", 0, -1, "player")
			self.frames[name].append(image)

	def loadImages(self):
		"""loads images"""
		self.loadAnm("run", 4)
		self.loadAnm("jumpfwd", 3)
		self.loadAnm("fallforwards", 2)
		self.loadAnm("fallback", 2)
		self.loadAnm("crouch", 2)
		self.loadAnm("roll", 4)
		self.fall = main.loadImage('fall.png', 0, -1, "player")
		self.stand, self.rect = main.loadImage('stand.png', 1, -1, "player")
		
	def setKeys(self, right = K_RIGHT, left = K_LEFT, down = K_DOWN, up = K_UP, action = K_KP0):
		"""setKeys(right key, left key, crouch key)
		Sets the keys for the player object"""
		self.keys = {}
		self.keys["right"] = right
		self.keys["left"] = left
		self.keys["down"] = down
		self.keys["up"] = up
		self.keys["action"] = action
		
	def keyDown(self, key):
		"""Event function for when any keys bound to the current player object are hit"""
		if key is self.keys['action']:
			if self.currentWeapon is "gun":
				print "gun"
		if not self.inAir:
			if not self.crouching:
				if key == self.keys["right"]:
					self.playerVars['xMove'] = 6
					self.playerVars['dir'] = 0
					self.playerVars['running'] = 1
				elif key == self.keys["left"]:
					self.playerVars['xMove'] = -6
					self.playerVars['dir'] = 1
					self.playerVars['running'] = 1
			if not self.playerVars['running']:
				if key == self.keys["down"]:
					self.crouchdown = 1
					self.crouching = 1
					self.playerVars['current'] = 0
				if key == self.keys["up"]:
					print "upjump"
			elif self.playerVars['running']:
				if key == self.keys["down"]:
					self.rolling = 1
					self.playerVars['current'] = 0
					if key == self.keys["right"]:
						self.playerVars['xMove'] = 8
					elif key == self.keys["left"]:
						self.playerVars['xMove'] = -8
				elif key == self.keys["up"]:
					if key == self.keys["right"]:
						self.playerVars['xMove'] = 10
					elif key == self.keys["left"]:
						self.playerVars['xMove'] = -10
					self.playerVars['yMove'] = -6
					self.jumpfwd = 1
					self.inAir = 1
					self.playerVars['current'] = 0

		if not self.lastkey:
			self.lastkey = key

	def keyUp(self, key):
		"""Event function for when any keys bound to the current player object are let go of"""
		if not self.noKeys:
			if key == self.lastkey:
				if key == self.keys["down"]:
					self.crouchup = 1
					self.crouchdown = 0
				self.lastkey = 0
				self.playerVars['xMove'] = 0
				self.playerVars['running'] = 0
				self.playerVars['current'] = 0

	def update(self):
		"""The update function"""
		self.animate()
		if self.playerVars['dir']==1:
			self.image = pygame.transform.flip(self.image, 1, 0)
		#if self.playerVars['yMove'] < self.maxVol:
		#	self.playerVars['yMove'] += self.gravity
		
		move = self.feetRect.move(0, self.playerVars['yMove'])
		
		if move.collidelist(self.platform) == -1:
			self.rect.move_ip(0, self.playerVars['yMove'])
			self.feetRect.move_ip(0, self.playerVars['yMove'])
		else:
			self.inAir = 0
			for i in range(self.gravity+1, 0, -1):
				move = self.feetRect.move(0, i)
				
				if move.collidelist(self.platform) == -1:
					self.rect.move_ip(0, i)
					self.feetRect.move_ip(0, i)
		self.rect.move_ip(self.playerVars['xMove'],0)
		self.feetRect.move_ip(self.playerVars['xMove'],0)
	def animate(self):
		"""does all the animations"""
		if self.fallingforwards:
			if self.playerVars['current'] == len(self.frames["fallforwards"]) -1:
				self.playerVars['current'] = 0
				self.fallingforwards = 0
				self.playerVars['xMove'] = 0
			else:
				self.playerVars['current'] += 1
			self.image = self.frames["fallforwards"][self.playerVars['current']]
		elif self.fallingback:
			if self.playerVars['current'] == len(self.frames["fallback"]) -1:
				self.playerVars['current'] = 0
				self.fallingback = 0
				self.noKeys = 0
			else:
				self.playerVars['current'] += 1
			self.image = self.frames["fallback"][self.playerVars['current']]
		elif self.crouching:
			self.image = self.frames["crouch"][self.playerVars['current']]
			if self.playerVars['current'] == len(self.frames["crouch"]) -1:
				self.playerVars['current'] = len(self.frames["crouch"]) -1
			elif self.crouchdown:
				self.playerVars['current'] += 1
			if self.crouchup:
				self.crouchup = 0
				self.playerVars['current'] -= 1
				self.crouching = 0
		elif self.rolling:
			self.image = self.frames["roll"][self.playerVars['current']]
			if self.playerVars['current'] == len(self.frames["roll"]) -1:
				self.rolling = 0
				self.crouching = 1
				self.playerVars['current'] = 0
				self.crouchdown = 1
				self.playerVars['xMove'] = 0
				self.lastkey=self.keys["down"]
			else:
				self.playerVars['current'] += 1
		elif self.jumpfwd:
			self.image = self.frames["jumpfwd"][self.playerVars['current']]
			if self.playerVars['current'] == len(self.frames["jumpfwd"]) -1:
				self.jumpfwd = 0
				self.playerVars['current'] = 0
			else:
				self.playerVars['current'] += 1
		elif self.playerVars['running']:
			self.image = self.frames["run"][self.playerVars['current']]
			if self.playerVars['current'] == len(self.frames["run"]) -1:
				self.playerVars['current'] = 0
			else:
				self.playerVars['current'] += 1
		elif self.inAir:
			self.image = self.fall
		else:
			self.crouchup = 0
			self.crouchdown = 0
			self.image = self.stand
	def collide(self, dir, speed):
		"""Acts on collitions"""
		"""#if self.playerVars['xMove'] == -6 or self.playerVars['xMove'] == 6 and speed == -6 or speed == 6:
			if self.playerVars['xMove'] == -6:
				self.playerVars['xMove'] = 6
			else:
				self.playerVars['xMove'] = -6
			self.fallingback = 1
			self.playerVars['running'] = 0
			self.playerVars['current'] = 0
			self.noKeys = 1
			#self.playerVars['xMove'] = 6
		else:
			self.fallingforwards = 0"""
		return
