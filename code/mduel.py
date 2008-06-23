#/usr/bin/env python
"""
Mduel
"""
import time
time.clock()
#Import Modules
#import pygame, cPickle, socket, math, select

import main, player, sprites


#from random import randint

#from pygame.locals import *

	
main = main.Main()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"