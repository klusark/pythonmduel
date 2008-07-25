import image
import pygame
from pygame.locals import *
class Menu():
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
			if not self.drawMenuItem("Begin Game", 		0, 50, 9):
				return
			if not self.drawMenuItem("View Fighters", 	1, 70, 2):
				return
			if not self.drawMenuItem("Set Controls", 	2, 90, 3):
				return
			if not self.drawMenuItem("Options", 		3, 110, 4):
				return
			if not self.drawMenuItem("Exit", 			4, 130, 8):
				return
				
		elif self.page is 2:
			for i in range(len(self.playerNames)):
				if self.playerNames[i] == self.player1Name:
					self.colour = (176, 0, 0)
				elif self.playerNames[i] == self.player2Name:
					self.colour = (0, 48, 192)
				else:
					self.colour = (164, 64, 164)
				
				y=144+18*(i+1)
				
				self.drawText(self.playerNames[i], self.font2, 0, y, self.colour)
				
				self.drawText(self.playerinfo[i][0], self.font2, 150, y, self.colour)

				self.drawText(self.playerinfo[i][1], self.font2, 250, y, self.colour)

				self.drawText(self.playerinfo[i][2], self.font2, 300, y, self.colour)

				self.drawText(self.playerinfo[i][3], self.font2, 400, y, self.colour)

				self.drawText(self.playerinfo[i][4], self.font2, 500, y, self.colour)
				
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
			for i in range(1, 3):
				stri = str(i)

				self.text = self.font.render("player.Player "+str(i), 0, self.posinfo["colour"+stri])
				self.background.blit(self.text, (self.posinfo["x"+stri], 25))
				
				self.setNewKey("Right", "right", stri, 50)
				self.setNewKey("Left", "left", stri, 75)
				self.setNewKey("Crouch", "down", stri, 100)
				self.setNewKey("Jump", "up", stri, 125)
		elif self.page is 4:
			if not self.drawMenuItem("Net", 0, 50, 5):
				return
		elif self.page is 5:
			self.drawText("Port = " + str(self.port), self.font, 0, 0, (255, 255, 255))
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
		
	def __initMenu__(self):
		self.introimage = self.loadImage("intro.png", 0)
		self.numMenuItmes = 5
		self.menuItems = [""]*self.numMenuItmes
		self.selected =  -2 # so none are selected at start
		
	def drawText(self, text, font, x, y, colour):
		text = font.render(text, 0, colour)
		self.background.blit(text, (x, y))
		
	def inMenuEvents(self):
		"""handle events in the menu"""
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
			self.menucolour = (255, 255, 255)
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
		self.keyItems["textpos"+i] = self.text.get_rect(x=self.posinfo["x"+i], y=y)
		self.background.blit(self.text, self.keyItems["textpos"+i])
		if self.keyItems["textpos"+i].collidepoint(pygame.mouse.get_pos()) == 1 and pygame.mouse.get_pressed()[0]:
			self.text = self.font.render("Press new "+name+" key: ", 0, (255, 255, 255))
			self.pos = self.text.get_rect(centerx=self.background.get_width()/2, y=350)
			self.background.blit(self.text, self.pos)
			self.getnewkey = (key, i)