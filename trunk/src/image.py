from os import path
import pygame
from pygame.locals import *
images = {}
class loadImage():
	def loadImage(self, name, rect, colorkey = None, folder = "", force = None):
		theme = "main"
		fullname = path.join('data', theme, folder, name)
		if not force:
			if fullname in images:
				if not rect:
					return images[fullname]
				else:
					return images[fullname], images[fullname].get_rect() 
		try:
			image = pygame.image.load(fullname)
		except pygame.error, message:
			try:
				fullname = path.join('data', "main", folder, names)
				image = pygame.image.load(fullname)
			except:
				print 'Cannot load image:', names
				raise SystemExit, message
		image = image.convert()
		image = pygame.transform.scale(image, (image.get_width()*2, image.get_height()*2))
		if colorkey:
			if colorkey is -1:
				colorkey = image.get_at((0, 0))
			image.set_colorkey(colorkey, RLEACCEL)
		images[fullname] = image
		if not rect:
			return image
		else:
			return image, image.get_rect()