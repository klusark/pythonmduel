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
	pass
main = main.Main()
print time.clock()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"