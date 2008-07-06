#/usr/bin/env python
"""
Mduel
"""
#get load time stuff
import time
time.clock()
#Import Modules
import main
try:
	import psyco
	psyco.full()
except ImportError:
	print "Could not import psyco."
try:
	import pygame
except ImportError:
	exit("Could not import pygame.\nThis game requires pygame. Get it at pygame.org")
main = main.Main()
print time.clock()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"