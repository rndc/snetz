#!/usr/bin/env python
#
#  This file is part of Snetz
#  by Agus Bimantoro  <l0g.bima@gmail.com>
#  This program is published under a GPLv3 license

import os
import sys

SNETZ_PROGRAM_FILE = "/bin/snetz"
SNETZ_MANUAL_FILE = "/usr/share/man/man1/snetz.1.gz"
USER = os.geteuid()

if (USER != 0):
	print("Warning: You must be root to install this program.")
	sys.exit(1)
    
agree = raw_input("Do you want to remove Snetz [Y/n]? ")

if (agree.lower() == "y" or agree.lower() == "yes"):
	print("\nRemoving snetz:")
	print("\nChecking file...")
	if not (os.path.exists(SNETZ_PROGRAM_FILE )):
		sys.stderr.write("\nError: %s: No such file or directory.\n" % (SNETZ_PROGRAM_FILE))
		sys.exit(1)
	elif not (os.path.exists(SNETZ_MANUAL_FILE)):
		sys.stderr.write("\nError: %s: No such file or directory.\n" % (SNETZ_MANUAL_FILE))
		sys.exit(1)
	print("\nRemoving snetz program...")
	os.system("rm %s 2> /dev/null" % (SNETZ_PROGRAM_FILE))
	print("Removing manual program...")
	os.system("rm %s 2> /dev/null" % (SNETZ_MANUAL_FILE))
	print("\nAll done...")

## EOF ##
