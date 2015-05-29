#!/usr/bin/env python
#
# Author: Anthony Paterson arpaterson@wordpress.com Mar 2015

import time, serial, sys, select, threading, Queue


class radarcommon:
	#isolate dealing with the serial port from dealing with the data
	#this can be its own thread. see com_monitor example for ideas
	
	def __init__(	self,
			port_num = "/dev/ttyUSB0", 
			port_baud = 9600, 
			port_bytesize = 8, 
			port_parity = 'N', 
			port_stopbits = 1,
			verbose = 0):
	 self.serial_port = None
	 self.serial_arg = dict( port = port_num,
				 baudrate = port_baud,
				 bytesize = port_bytesize,
				 parity = port_parity,
				 stopbits = port_stopbits)
	 self.linebuffer = ''
	 self.verbose = verbose
	 self.connect()

	def connect(self):
	 try:
	  if self.serial_port:
	   self.serial_port.close()
	  self.serial_port = serial.Serial(**self.serial_arg)
	 except serial.SerialException, e:
	  print "serialException in radarcommon.connect()"

	def __del__(self):
	 self.close()

	def close(self):
	 self.serial_port.close()
	
	def waiting(self):
	 #return true if data is ready for the client
	 if self.linebuffer:
	  return True
	 #some exceptions stuff here? in gpsd this is where select is use (with sock)
	 return False
	
	def read(self):
	 #Wait for and read data being streamed by the radar unit.
	 if self.verbose > 1:
	  sys.stderr.write("radar: reading from serial port... \n")
	 
	 #Look for 0x0d terminated strings
	 eol = self.linebuffer.find('\x0D')
	 if eol == -1: # no end of line found in buffer, so get more data
	  frag = self.serial_port.read(1)
	  frag += self.serial_port.read(self.serial_port.inWaiting())
	  self.linebuffer += frag
	  if self.verbose >1 :
	   sys.stderr.write("radar.read(): read complete.\n")
	  if not self.linebuffer:
	   if self.verbose > 1:
	    sys.stderr.write("radar.read(): returning -1\n")
	   #read failed
	   return -1
	  eol = self.linebuffer.find('\x0D')
	  if eol == -1:
	   if self.verbose > 1:
	    sys.stderr.write("radar.read(): returning 0\n")
	   #read succeeded but only got a fragment
	   return 0
	 else:
	  if self.verbose > 1:
	   sys.stderr.write("radar: fetching from buffer.\n")
	 #We got a line
	 eol += 1
	 self.response = self.linebuffer[:eol] 
	 self.linebuffer = self.linebuffer[eol:]

	 # if port timesout?
	 if not self.response:
	  return -1
	 if self.verbose > 0:
	  sys.stderr.write("radar: data is %s\n" % (self.response))
	  sys.stderr.write("radar: length is %d\n" % (len(self.response)))
	 
	 self.received = time.time()

	 #We got a 0x0D (carriage return) terminated line
	 return len(self.response)

	
	def data(self):
	#Return the data buffer
	 return self.response
	
	def send(self, data):
	#Ship commands to serial port 
	 if self.verbose > 0:
	  sys.stderr.write("gpscommon.send(): Writing to serial port\n")
	  sys.stderr.write("  data is %s\n" % (data))
	 self.serial_port.write(data)
