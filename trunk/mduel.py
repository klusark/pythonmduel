#/usr/bin/env python
"""
Mduel
"""
#Import Modules
import os, pygame, socket, cPickle, PixelPerfect
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
	def __init__(self,x=0,y=0):
		"""Initializes Player class"""
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.runframe=[]
		for i in range(4):
			image = loadImage("run"+str(i)+".png",0,-1)
			self.runframe.append(image)
		self.stand, self.rect = loadImage('stand.png', 1,-1)
		self.image = self.stand
		self.rect.move_ip(x,y)
		"""Set the number of Pixels to move each time"""
		self.x_dist = 6
		self.y_dist = 6 
		"""Initialize how much we are moving"""
		self.xMove = 0
		self.yMove = 0
		self.current = 0
		self.running=0
		self.dir = 0
		self.name = "Unset"
		self.hitmask = pygame.surfarray.array_colorkey(self.image)
		self.image.unlock()
		self.image.unlock()
	def setKeys(self, right = K_RIGHT, left = K_LEFT):
		"""Sets the keys for the player object"""
		self.right = right
		self.left = left
	def MoveKeyDown(self, key):
		"""Event fuction for when any keys bound to the current player object are hit"""
		
		if key == self.right:
			self.xMove = self.x_dist
			self.dir = 0
		elif key == self.left:
			self.xMove = -self.x_dist
			self.dir = 1
		self.running = 1

	def MoveKeyUp(self, key):
		"""Event fuction for when any keys bound to the current player object are let go of"""
		self.xMove = 0
		self.running = 0
		self.current = 0
	def update(self):
		if self.running:
			if self.current == len(self.runframe)-1:
				self.current = 0
			else:
				self.current += 1
			self.image = self.runframe[self.current]

		else:
			self.image = self.stand
		if self.dir==1:
			self.image = pygame.transform.flip(self.image, 1, 0)
		#print self.rect.collidelistall()
		#if self.xMove > 0:
		#	self.xMove -= 1

		self.rect.move_ip(self.xMove,self.yMove)

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

class Selector(pygame.sprite.Sprite):
	"""The selector on menup2"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = loadImage('selector.png', 1, -1)
		self.y=94
		self.rect.move_ip(212, self.y)
		
	def move(self, key):
		"""Moves the selector and loops when at bottom or top"""
		if key == K_DOWN:
			self.rect.move_ip(0,30)
			self.y+=30
		elif key == K_UP:
			self.rect.move_ip(0,-30)
			self.y-=30
		if self.y == 64:
			self.rect.move_ip(0,210)
			self.y =274
		elif self.y == 304:
			self.rect.move_ip(0,-210)
			self.y=94
class Rope(pygame.sprite.Sprite):
	"""The rope"""
	def __init__(self,x,y,len):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = loadImage('rope.png', 1)
		self.rect.move_ip(x, y)
		self.image = pygame.transform.scale(self.image,(1,16*len))

class SendPlayer():
	def __init__(self):
		self.xMove = 0
		self.yMove = 0
		self.current = 0
		self.running = 0
		self.dir = 0
def getMenuItem(y):
	"""simple fuction to tell the item number on the main menu"""
	return (y-94)/30
def binds():
	"""Makes the curret player wait for a connection from another player"""
	HOST = ''				# Symbolic name meaning the local host
	PORT = 50007			# Arbitrary non-privileged port
	s = socket.socket()
	s.bind((HOST,PORT))
	s.listen(1)
	conn, addr = s.accept()
	print 'Connected by', addr
	return conn

def connects():
	HOST = '127.0.0.1'	# The remote host
	PORT = 50007			  # The same port as used by the server
	s = socket.socket()
	s.connect((HOST,PORT))
	return s

def pickelForSending(player):
	pickle = SendPlayer()
	pickle.xMove =  player.xMove
	pickle.yMove =  player.yMove
	pickle.current =  player.current
	pickle.running =  player.running
	pickle.dir =  player.dir
	dump = cPickle.dumps(pickle)
	return compress(dump)
	
def depickelForRecving(pickle, player):
	pickle = decompress(pickle)
	pickle = cPickle.loads(pickle)
	player.xMove = pickle.xMove
	player.yMove = pickle.yMove
	player.current = pickle.current
	player.running = pickle.running
	player.dir = pickle.dir
	return player

def generateBricks():
	"""Taken from MDuel DS and modifyed
	void gameManager::generateBricks()
	{
		u16 tileGFX = loadGFX(tileSprite.spriteData, OBJ_SIZE_16X16, 1);
		for (int i=0; i < 51; ++i)
		{
			floorTile *temp = new floorTile(this);
			temp->setPallete(tileSprite.palleteID);
			temp->giveGFX(tileGFX, OBJ_SIZE_16X16, 8, 8, 0, OFFX, OFFY);
			
			if (i<3)
				temp->setPos(i*16+24, 192-32+8);
			else if (i<6)
				temp->setPos(256-24-((i-3)*16), 192-32+8);
			else if (i>47)
				temp->setPos(256-16-8-((i-47)*16), 192-32+8+4*-32);
			else if (i>44)
				temp->setPos((i-45)*16+16+16+8, 192-32+8+4*-32);
			else {
				u8 j = i-6;
				u8 col = j%13;
				u8 row = j/13;
				if (PA_RandMax(10) < 7 || (
					(gameSprites.size()-2 > 0 && gameSprites[gameSprites.size()-2]->getx() > 0) && 
					(gameSprites.size()-3 > 0 && gameSprites[gameSprites.size()-3]->getx() < 0) ))
					temp->setPos((col+1)*16+16, 192-32+8+((row+1)*-32));
			}
			temp->makeStatic();
		}
	}"""
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

def generateRopes():
	"""Taken from MDuel DS and modifyed
	void gameManager::generateRopes()
	{
		u16 ropeHeadGFX = loadGFX(tileSprite.spriteData, OBJ_SIZE_16X16, 1);
		u16 ropeGFX = loadGFX(tileSprite.spriteData, OBJ_SIZE_16X16, 1);
		
		Rope *r1 = new Rope(this);
		r1->setPallete(tileSprite.palleteID);
		r1->giveGFX(ropeHeadGFX, OBJ_SIZE_16X16, 8, 8);
		r1->childGFX = ropeGFX;
		r1->setPos(56, 3);
		r1->setLength(9);
		r1->makeStatic();
		
		Rope *r2 = new Rope(this);
		r2->setPallete(tileSprite.palleteID);
		r2->giveGFX(ropeHeadGFX, OBJ_SIZE_16X16, 8, 8);
		r2->childGFX = ropeGFX;
		r2->setPos(256-56, 3);
		r2->setLength(9);
		r2->makeStatic();
	}"""
	rope = []
	rope.append(Rope(56*2, 3*2, 9*2))
	rope.append(Rope((256-56)*2, 3*2, 9*2))
	return rope
	
def main():
	"""Main fuction that sets up variables and contains the main loop"""
#Initialize Everything
	pygame.init()
	
	screen = pygame.display.set_mode((640, 400))
	pygame.display.set_caption('Mduel')
	#pygame.mouse.set_visible(0)
#Menu
	introimage = loadImage("intro.png",0)
	menup2 = loadImage("menup2.png",0)
#Create The Backgound
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0, 0, 0))

#Display The Background
	screen.blit(background, (0, 0))
	pygame.display.flip()
	
#Font
	pygame.font.init()
	font = pygame.font.Font("data/marshmallowDuel.ttf", 28)
	#text = font.render("Mduel", 0, (164, 64, 164))
	#textpos = text.get_rect(centerx=background.get_width()/2)
	#background.blit(text, textpos)
#Prepare Game Objects
	clock = pygame.time.Clock()
	platform = generateBricks()
	#groundGroup = pygame.sprite.Group()
	#groundGroup.add(platform)
	player1 = Player(39,288)
	player1.setKeys()
	player2 = Player(457,288)
	player2.dir = 1
	player2.setKeys(K_d,K_a)
	rope = generateRopes()
	#print platform
	mallow = []
	for i in range(22):
		mallow.append(Mallow(i*(15*2),400-(15*2)))
	#mallows = MallowAnm()
	mallows = []
	frame = 0
	for i in range(20):
		if frame == 4:
			frame = 0
		mallows.append(MallowAnm(i*(16*2),400-16-30,frame))
		frame +=1
	#platform = Platform(0,100)
	allsprites = pygame.sprite.RenderPlain((player1, player2, platform, mallows, mallow, rope))
	playerGroup = pygame.sprite.Group()
	playerGroup.add(player1,player2)

	selector = Selector()
	selectorRender = pygame.sprite.RenderUpdates(selector)
#Odds and ends
	menu = 1
	playing = 0
	page = 0 #
	bind = 0
	connect = 0
	bound = 0
	connected = 0
#players
	playerfile = open("players","r")
	players = []
	playerinfo = []
	playerlist = playerfile.readlines()
	for i in range(6):
		players.append("".join(findall("[a-zA-Z]+",playerlist[i])))
		playerinfo.append(findall("[-0-9]+",playerlist[i]))

	player1.name = players[0]
	player2.name = players[1]
#Main Game Loop
	while 1:
		clock.tick(10)
		if playing:
			#Handle Input Events
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN:
					if (event.key == player1.right
					or event.key == player1.left):
						player1.MoveKeyDown(event.key)
					if (event.key == player2.right
					or event.key == player2.left):
						player2.MoveKeyDown(event.key)
					if event.key == K_DOWN:
						player1.yMove = 5
					if event.key == K_b:
						bind = 1
					if event.key == K_c:
						connect = 1
				elif event.type == KEYUP:
					if (event.key == player1.right
					or event.key == player1.left):
						player1.MoveKeyUp(event.key)
					if (event.key == player2.right
					or event.key == player2.left):
						player2.MoveKeyUp(event.key)
			allsprites.update()
			if len(PixelPerfect.spritecollide_pp(player1,playerGroup, 0)) == 2:
				print "Colides"
			
			#Draw Everything
			screen.blit(background, (0, 0))
			allsprites.draw(screen)
			pygame.display.flip()
		if menu:
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == KEYDOWN:
					if page is 0:
						if event.key is K_SPACE:
							page+=1
							background.fill((0, 0, 0))
					if page is 1:
						if (event.key == K_DOWN
						or event.key == K_UP):
							selector.move(event.key)
						elif event.key == K_RETURN:
							if getMenuItem(selector.y) == 0:
								page=9
								background.fill((0, 0, 0))
							elif getMenuItem(selector.y) == 2:
								page = 2
								background.fill((0, 0, 0))
							elif getMenuItem(selector.y) == 6:
								return
					elif page is 9:
						if event.key == K_SPACE:
							page = 10
						
			if page is 0:
				background.blit(introimage, (0, 0))
			elif page is 1:
				pos = menup2.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
				background.blit(menup2, pos)
				selectorRender.draw(background)
				#text = font.render("Begin Match", 0, (164, 64, 164))
				#textpos = text.get_rect(centerx=background.get_width()/2)
				#background.blit(text, textpos)
			elif page is 2:
				for i in range(len(players)):
					text = font.render(players[i], 0, (164, 64, 164))
					background.blit(text, (0,160+40*i))
				for i in range(len(players)):
					text = font.render(playerinfo[0][i], 0, (164, 64, 164))
					background.blit(text, (0,160+40*i))
				text = font.render("Name", 0, (255, 255, 255))
				background.blit(text, (0,140))
				text = font.render("Rank", 0, (255, 255, 255))
				background.blit(text, (150,140))
				text = font.render("W", 0, (255, 255, 255))
				background.blit(text, (200,140))
				text = font.render("L", 0, (255, 255, 255))
				background.blit(text, (250,140))
				text = font.render("S", 0, (255, 255, 255))
				background.blit(text, (300,140))
				text = font.render("FIDS", 0, (255, 255, 255))
				background.blit(text, (350,140))
			elif page is 9:
				text = font.render(player1.name+" vs. "+player2.name, 0, (164, 64, 164))
				pos = text.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
				background.blit(text, pos)
			elif page is 10:
				playing = 1
				menu = 0
				background.fill((0, 0, 0))
			screen.blit(background, (0, 0))
			pygame.display.flip()
		if bind:
			if not bound:
				conn = binds()
				bound = 1
			player2 = depickelForRecving(conn.recv(512),player2)
			conn.send(pickelForSending(player1))
		if connect:
			if not connected:
				s = connects()
				connected=1

			s.send(pickelForSending(player2))
			player1 = depickelForRecving(s.recv(512),player1)

if __name__ == '__main__': main()
#new lines so i can scroll down farther
















