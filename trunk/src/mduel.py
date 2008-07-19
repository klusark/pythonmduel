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
	print "Could not import psyco.\nPsyco is not required but it will speed up mduel."

try:
	import pygame
except ImportError:
	exit("Could not import pygame.\nThis game requires pygame. Get it at pygame.org")
	
if not pygame.font:
	exit("Can not load fonts.")
if not pygame.image or not pygame.image.get_extended():
	exit("Can not load extended images.")
import main
main = main.Main()
print time.clock()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"