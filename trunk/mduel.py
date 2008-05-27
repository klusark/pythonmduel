#/usr/bin/env python
"""
Mduel
"""
#Import Modules
import os, pygame
from pygame.locals import *
#function to create our resources
def load_image(name, rect, colorkey=None):
	fullname = os.path.join('data', name)
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
	"""Player"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.runframe=[]
		for i in range(4):
			image = load_image("run"+str(i)+".png",0,-1)
			self.runframe.append(image)
		self.stand, self.rect = load_image('stand.png', 1,-1)
		self.image = self.stand
		"""Set the number of Pixels to move each time"""
		self.x_dist = 3
		self.y_dist = 3 
		"""Initialize how much we are moving"""
		self.xMove = 0
		self.yMove = 0
		self.current = 0
		self.running=0
		self.dir = 0
	def setKeys(self, right = K_RIGHT, left = K_LEFT):
		"""Sets the keys for the player object"""
		self.right = right
		self.left = left
	def MoveKeyDown(self, key):
		self.running = 1
		if key == self.right:
			self.xMove += self.x_dist
			self.dir = 0
		elif key == self.left:
			self.xMove += -self.x_dist
			self.dir = 1

	def MoveKeyUp(self, key):
		if key == self.right:
			self.xMove += -self.x_dist
		elif key == self.left:
			self.xMove += self.x_dist
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
		self.rect.move_ip(self.xMove,self.yMove)

class Platform(pygame.sprite.Sprite):
	"""Platform Sprite"""
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('platform.png', 1, -1)
		self.rect.move_ip(x, y)

class Selector(pygame.sprite.Sprite):
	"""The selector on menup2"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('selector.png', 1, -1)
		#size = 

		self.y=94
		self.rect.move_ip(212, self.y)
		
	def move(self, key):
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

def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
#Initialize Everything
	pygame.init()
	
	screen = pygame.display.set_mode((640, 400))
	pygame.display.set_caption('Mduel')
	#pygame.mouse.set_visible(0)
#Menu
	introimage = load_image("intro.png",0)
	menup2 = load_image("menup2.png",0)
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
	player1 = Player()
	player1.setKeys()
	player2 = Player()
	player2.setKeys(K_d,K_a)
	platform = []
	for i in range(5):
		platform.append(Platform(i*32,100))
	#platform = Platform(0,100)
	allsprites = pygame.sprite.RenderPlain((player1,player2,platform))
	selector = Selector()
	selectorRender = pygame.sprite.RenderUpdates(selector)
#Odds and ends
	menu = 1
	playing = 0
	page = 0
#Main Game Loop
	while 1:
		clock.tick(10)
		if playing:
			#Handle Input Events
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == KEYDOWN:
					if (event.key == player1.right
					or event.key == player1.left):
						player1.MoveKeyDown(event.key)
						player1.running = 1
					if (event.key == player2.right
					or event.key == player2.left):
						player2.MoveKeyDown(event.key)
				elif event.type == KEYUP:
					if (event.key == player1.right
					or event.key == player1.left):
						player1.MoveKeyUp(event.key)
					if (event.key == player2.right
					or event.key == player2.left):
						player2.MoveKeyUp(event.key)
			allsprites.update()
			#Draw Everything
			screen.blit(background, (0, 0))
			allsprites.draw(screen)
			pygame.display.flip()
		elif menu:
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
							if selector.y == 94:
								page=10
						
			if page is 0:
				background.blit(introimage, (0, 0))
			elif page is 1:
				pos = menup2.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
				background.blit(menup2, pos)
				selectorRender.draw(background)
				#text = font.render("Begin Match", 0, (164, 64, 164))
				#textpos = text.get_rect(centerx=background.get_width()/2)
				#background.blit(text, textpos)
			elif page is 10:
				playing = 1
				menu = 0
				background.fill((0, 0, 0))
			screen.blit(background, (0, 0))
			
			pygame.display.flip()
if __name__ == '__main__': main()

















