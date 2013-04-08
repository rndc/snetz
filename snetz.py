#!/usr/bin/env python
#
#  snetz.py 0.2 - simple bandwidth monitoring tool
#  Author by Agus Bimantoro  <l0g.bima@gmail.com> (http://rndc.or.id, http://abi71.wordpress.com) 
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

__version__ = "0.2"
__author__ = "Agus Bimantoro"
__site__ = "http://rndc.or.id/wiki"

import os
import sys
import time
import struct
import fcntl
from socket import *

SOCK = socket(AF_INET, SOCK_DGRAM)
SIOCGIFFLAGS = 0x8913
IFF_UP = 0x1 
IFF_LOOP_BACK = "lo"   
DELAY_TIME = 1
FILE_PATH = "/proc/net/dev"
UNIT_RATE = "Kb"
UNIT_RATE_ALLOWED = ["Kb","Mb","KB","MB"]
INTERFACES = ["all"]

class snetz(object):
	def __init__(self, delay, path):
		""" initialize configuration """
		self.delay = delay
		self.path = path
		
		if (self.delay < 0.500):
			sys.stderr.write("TimeError: %s: Minimal 0.500 seconds.\n" % (self.delay))
			sys.exit(1)
			
		if not (os.path.exists(self.path)):
			sys.stderr.write("PathError: %s: No such file or directory.\n" % (self.path))
			sys.exit(1)
	
	def check_if_up(self, iface):
		""" check whether the interface is up """
		ifreq = struct.pack('16sh', iface, 0)
		flags = struct.unpack('16sh', fcntl.ioctl(SOCK.fileno(), SIOCGIFFLAGS, ifreq))[1]
		
		if (iface == IFF_LOOP_BACK):
			return True
		elif (flags & IFF_UP):
			return True		
		else:
			return False
	
	def get_if_all(self):
		""" get all interfaces """
		ifaces = []
	
		for line in open(FILE_PATH):
			dev = line.split()[0].split(':')[0]
			ifaces.append(dev)
			
		ifaces.pop(0)
		ifaces.pop(0)
		
		return ifaces

	def convert_byte_to_kbits(self, new_bytes, old_bytes, diff_times):
		""" convert bytes to kilobits """
		kbits = (((new_bytes - old_bytes) * 8)/1000)/diff_times
		kbits = '%.2f' % kbits
		return float(kbits)
	
	def convert_byte_to_mbits(self, new_bytes, old_bytes, diff_times):
		""" convert bytes to megabits """
		mbits = (((new_bytes - old_bytes) * 8)/1000000)/diff_times
		mbits = '%.2f' % mbits
		return float(mbits)
		
	def convert_byte_to_kbytes(self, new_bytes, old_bytes, diff_times):
		""" convert bytes to kilobytes """
		kbytes = ((new_bytes - old_bytes)/1024)/diff_times
		kbytes = '%.2f' % kbytes
		return float(kbytes)
	
	def convert_byte_to_mbytes(self, new_bytes, old_bytes, diff_times):
		""" convert bytes to megabytes """
		mbytes = (((new_bytes - old_bytes)/1024)/1024)/diff_times
		mbytes = '%.2f' % mbytes
		return float(mbytes)

	def get_bytes(self, iface, data):
		""" get byte and packets """
		for line in open(self.path, 'r'):
			if (iface in line):
				n = line.split('%s:' % iface)[1].split()
				data[iface]['rxbn'] = float(n[0])
				data[iface]['txbn'] = float(n[8])
				break  

	def main(self):
		""" main """
		
		# initial
		interface = []
		first_run = True
		
		# check the available interfaces
		if (INTERFACES[0] != "all"):
			for line in INTERFACES:
				if (line not in self.get_if_all()):
					sys.stderr.write("ValueError: %s: No such device.\n" % (line))
					sys.exit(1)
		
		# read all interface and give zero value to data variables
		#
		# rxbn = rx bytes new
		# rxbo = rx bytes old
		#
		# txbn = tx bytes new
		# txbo = tx bytes old
		# 
		# prevtime = previous time 
		# curtime = current time
		#
		for line in open(self.path, 'r'):
			if (':' in line):
				iface = line.split(':')[0].lstrip(' ')
				if (INTERFACES[0] == "all"):
					iface = {iface: {'rxbn': 0,'rxbo': 0,'txbn': 0,'txbo': 0,'prevtime': 0.0,'curtime': 0.0}}
					interface.append(iface)
				elif (iface in INTERFACES):
					iface = {iface: {'rxbn': 0,'rxbo': 0,'txbn': 0,'txbo': 0,'prevtime': 0.0,'curtime': 0.0}}
					interface.append(iface)					
  
		while True:	
			total_all_rx = 0
			total_all_tx = 0
			total_all_rxtx = 0
			
			if not (first_run):
				time.sleep(self.delay)
			first_run = False
			os.system("clear")
			
			print("\nSNETZ - simple bandwidth monitoring tool (%s)\n" % (__site__))
			print("Refresh Time: %s  Unit Rate: %s\n" % (DELAY_TIME,UNIT_RATE))
			print("  =========================================================================")
			print("  %-15s%-17s%-17s%-18s%s" % ("Interface","RX(%s/sec)" % UNIT_RATE,"TX(%s/sec)" % UNIT_RATE,"Total(%s/sec)" % UNIT_RATE,"Status"))
			print("  =========================================================================")
			
			for data in interface:
				iface = str(data).split("'")[1]
				self.get_bytes(iface,data)
				data[iface]['curtime'] = time.time()
				diff_time = data[iface]['curtime'] - data[iface]['prevtime'] 
				
				# RX
				if (data[iface]['rxbn']  > data[iface]['rxbo']):
					if (UNIT_RATE == "Kb"):
						rx = self.convert_byte_to_kbits(data[iface]['rxbn'], data[iface]['rxbo'], diff_time)
					elif (UNIT_RATE == "Mb"):
						rx = self.convert_byte_to_mbits(data[iface]['rxbn'], data[iface]['rxbo'], diff_time)
					elif (UNIT_RATE == "KB"):
						rx = self.convert_byte_to_kbytes(data[iface]['rxbn'], data[iface]['rxbo'], diff_time)
					else:
						rx = self.convert_byte_to_mbytes(data[iface]['rxbn'], data[iface]['rxbo'], diff_time)
					data[iface]['rxbo'] = data[iface]['rxbn']
				else:
					rx = 0
			
				# TX
				if (data[iface]['txbn']  > data[iface]['txbo']):
					if (UNIT_RATE == "Kb"):
						tx = self.convert_byte_to_kbits(data[iface]['txbn'], data[iface]['txbo'], diff_time)
					elif (UNIT_RATE == "Mb"):
						tx = self.convert_byte_to_mbits(data[iface]['txbn'], data[iface]['txbo'], diff_time)
					elif (UNIT_RATE == "KB"):
						tx = self.convert_byte_to_kbytes(data[iface]['txbn'], data[iface]['txbo'], diff_time)
					else:
						tx = self.convert_byte_to_mbytes(data[iface]['txbn'], data[iface]['txbo'], diff_time)
					data[iface]['txbo'] = data[iface]['txbn']
				else:
					tx = 0
				
				# total RX+TX
				total_rxtx = rx+tx
				
				# total all	
				total_all_rx += rx
				total_all_tx += tx
				total_all_rxtx += total_rxtx
				
				data[iface]['prevtime'] = data[iface]['curtime']
				
				if self.check_if_up(iface):
					status = "Up"
				else:
					status = "Down"
			
				print("  %-15s%-17s%-17s%-18s%s" % (iface,rx,tx,total_rxtx,status))
			print("  =========================================================================")
			print("  %-15s%-17s%-17s%s" % ('Total:',total_all_rx,total_all_tx,total_all_rxtx))
			print("\n\nPress 'ctrl+c' for quit.")

def license():
	""" program license """
	print("""SNETZ License:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA. """)
	sys.exit(0)

def manual():
	""" manual or helps """
	print("SNETZ %s by %s - simple bandwidth monitoring tool (%s)\n" % (__version__, __author__,__site__))
	print("Usage: snetz <options>") 
	print("Options:") 
	print("    -h, --help                Display this help")
	print("    -t, --time <float>        Update display time/sec, defaults to 1 seconds if not specified")
	print("    -p, --path <path>         The path of  network device status information,")
	print("                              Filename defaults to '/proc/net/dev' if not specified")
	print("    -u, --unit <Kb/Mb/KB/MB>  Display output rate (Kb/Mb/KB/MB), the default units is Kbps")
	print("    -i, --interfaces <list>   Display only specified interfaces, the seperated list by comma")
	print("    -l, --license             Display software license")
	print("    -v, --version             Display version number")
	print("\nEx: snetz ")
	print("    snetz -u KB")
	print("    snetz -t 1.5 -p /proc/net/dev -u Kb")
	print("    snetz -u Mb -i eth0,eth1,eth2,eth3\n")
	print("Please report bugs to <l0g.bima@gmail.com>")
	sys.exit(0)

def version():
	""" program version """
	print("SNETZ Version: %s" % (__version__)) 
	sys.exit(0)

# getopt and sanity
if (__name__ == "__main__"):
	try:
		for arg in sys.argv:
			if (arg.lower() == "-h" or arg.lower() == "--help"):
				manual()
			if (arg.lower() == "-t" or arg.lower() == "--time"):
				DELAY_TIME = float(sys.argv[int(sys.argv[1:].index(arg))+2])   
			if (arg.lower() == "-p" or arg.lower() == "--path"):
				FILE_PATH =  str(sys.argv[int(sys.argv[1:].index(arg))+2])
			if (arg.lower() == "-u" or arg.lower() == "--unit"):
				UNIT_RATE =  str(sys.argv[int(sys.argv[1:].index(arg))+2])
			if (arg.lower() == "-i" or arg.lower() == "--interfaces"):
				ifaces =  str(sys.argv[int(sys.argv[1:].index(arg))+2])
				INTERFACES.remove("all")
				for i in ifaces.split(","):
					INTERFACES.append(i)
				del(ifaces)
			if (arg.lower() == "-l" or arg.lower() == "--license"):
				license()
			if (arg.lower() == "-v" or arg.lower() == "--version"):
				version()		
		if (UNIT_RATE not in UNIT_RATE_ALLOWED):
			sys.stderr.write("ValueError: %s: Uknown unit rate, value must be in (Kb,Mb,KB,MB).\n" % (UNIT_RATE))
			sys.exit(1)
	except ValueError:
		if (DELAY_TIME):
			sys.stderr.write("ValueError: %s: Update time must be integer.\n" % (sys.argv[int(sys.argv[1:].index(arg))+2]))
			sys.exit(1)
	except IndexError:
		manual()
	
	try:
		sntz = snetz(DELAY_TIME,FILE_PATH)
		sntz.main()
	except IndexError, err:
		print("InternalError: %s." % (err))
	except IOError:
		print("FileError: '%s' is a directory." % (FILE_PATH))
	except ValueError:
		print("FileError: %s: File doesn't contains network device status information." % (FILE_PATH))
	except KeyboardInterrupt:
		print("")
		sys.exit(0)
	except:
		if not sys.exc_info()[1]:
			print("UnexpectedError: %s" % (sys.exc_info()[1]))  

## EOF
