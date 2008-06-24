#/usr/bin/env python
"""
Mduel
"""
#get load time stuff
import time
time.clock()
#Import Modules
import main

main = main.Main()
try:
	main.mainloop()
except KeyboardInterrupt:
	print "Keyboard Interrupt"