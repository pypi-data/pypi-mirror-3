#!/home/jirka/.pythonbrew/pythons/Python-2.7.2/bin/python

"""
Main module of Claun system. It can be run directly from the command line and accepts one parameter which is the path to a configuration file.
>>> ./run.py config.yaml

If you prefer a different python version, you can use it like this.
>>> python2.6 run.py config.yaml

However the system was developed with Python 2.7.2 released on June 11th 2011. It is highly probable that the system will work with at least Python 2.6.

You may try to run the system in Python 3 environment, however some 3rd party libraries (web.py) are not ready for this release. Claun is highly dependant on
the web.py library.

I tried to write the code as compatible as possible but due to the backwards incompatible changes it may not work properly.
Codebase was not tested against Python 3.x.
"""

import sys
from claun import Claun

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("USAGE: ./run.py configfile.yaml")
		sys.exit(2)
	Claun(sys.argv[1])
