"""
Mduel
"""
#get load time stuff
import time
time.clock()

try:
	import psyco
	psyco.full()
except ImportError:
	print "Could not import psyco."

try:
	import pygame
except ImportError:
	exit("Could not import pygame.\nThis game requires pygame. Get it at pygame.org")

if pygame.image.get_extended() is 0:
	exit("Can not load extended images. ")
import main
main = main.Main()
print time.clock()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"