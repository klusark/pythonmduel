from distutils.core import setup
from sys import argv
from shutil import copytree
try:
	import py2exe
except ImportError:
	exit("Could not import py2exe.")
argv[1:] = ["py2exe", "-O2"] + argv[1:]
setup(windows=['start.py'])
copytree("data", "dist/data")