#!/usr/bin/env python
#
#  This file is part of Snetz
#  by Agus Bimantoro  <l0g.bima@gmail.com>
#  This program is published under a GPLv3 license

import os
import sys
import time

SNETZ_PROGRAM_FILE = "snetz.py"
SNETZ_MANUAL_FILE = "snetz.1.gz"
USER = os.geteuid()

if (USER != 0):
	print("Warning: You must be root to install this program.")
	sys.exit(1)

agree = raw_input("Do you want to install Snetz [Y/n]? ")

if (agree.lower() == "y" or agree.lower() == "yes"):
	print("\nInstalling snetz:")
	print("\nChecking file...")
	if not (os.path.exists(SNETZ_PROGRAM_FILE )):
		sys.stderr.write("\nError: %s: No such file or directory.\n" % (SNETZ_PROGRAM_FILE))
		sys.exit(1)
	elif not (os.path.exists(SNETZ_MANUAL_FILE)):
		sys.stderr.write("\nError: %s: No such file or directory.\n" % (SNETZ_MANUAL_FILE))
		sys.exit(1)
	print("\nCopying snetz program to '/bin'...")
	os.system("cp snetz.py /bin/snetz")
	os.system("chmod +x /bin/snetz")
	print("Copying manual program to '/usr/share/man/man1'...")
	os.system("cp snetz.1.gz /usr/share/man/man1")
	print("\nInstallation finished. Type snetz as any user to run.")

## EOF ##
