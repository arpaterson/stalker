#!/usr/bin/env python
#
# Author: Anthony Paterson arpaterson@wordpress.com Mar 2015

import time, serial, sys, select
from radarcommon import *
from radarconfig import *
###########################################################
# Definition of output format B for Stalker Traffic Radar
#
# B format - All Speeds + Status
#
# Byte# Description             		Value
# 1     Message Type            		0x81    
# 2     Status 1                		See detail below
# 3     Status 2                		See detail below
# 4     Patrol Speed Hundreds			0-9 (ASCII)
# 5     Patrol Speed Tens			0-9 (ASCII)
# 6     Patrol Speed Ones			0-9 (ASCII)
# 7     Locked Speed Hundreds
# 8     Locked Speed Tens
# 9     Locked Speed Ones
# 10    Faster Speed Hundreds
# 11    Faster Speed Tens
# 12    Faster Speed Ones
# 13    Target Speed Hundreds
# 14    Target Speed Tens
# 15    Target Speed Ones
# 16    Carriage Return         		0x0D
#
# Status 1 Byte:
#  Bits 7:6     always = 01
#  Bit 5        lock status (0 = no speed locked, 1 = speed locked)
B_SB1_lockstatus_locked = (1<<5)
#  Bit 4        zone (0 = opposite, 1 = same/both)
B_SB1_zone_sameboth = (1<<4)
#  Bit 3        fork mode (0 = off/normal, 1 = fork mode enabled)
B_SB1_forkmode_enabled = (1<<3)
#  Bit 2        always = 0
#  Bit 1        always = 1
#  Bit 0        transmitter status (0 = off, 1 = on)
B_SB1_transmitter_on = (1<<0)
#
# Status 2 Byte:
#  Bits 7:6     always = 01
#  Bits 5:4     always = 00
#  Bit 3        fast lock status (0 = no fast speed locked, 1 = fast speed lock$
B_SB2_fastlockstatus_locked = (1<<3)
#  Bit 2        fast status (0 = faster disabled, 1 = faster enabled)
B_SB2_fastlock_enabled = (1<<2)
#  Bit 1        Low voltage (LoV) status (0 = normal, 1 = low voltage condition$
B_SB2_voltage_low = (1<<1)
#  Bit 0        always = 0
#

###########################################################
# Definition of output format B for Stalker Traffic Radar
#
# S format - Target Speeds, Status
#
# Byte# Description             		Value
# 1	Message Type				0x83
# 2	Faster Target Dir			Away = 'A', Closing = 'C'
# 3	Faster Speed Hundreds			0-9 (ASCII)
# 4	Faster Speed Tens			0-9 (ASCII)
# 5	Faster Speed Ones			0-9 (ASCII)
# 6	Faster Speed Tenths			0-9 (ASCII)
# 7	Strongest Target Dir			Away = 'C', Closing = 'C'
# 8	Strongest Speed Hundreds		0-9 (ASCII)
# 9	Strongest Speed Tens			0-9 (ASCII)
# 10	Strongest Speed Ones			0-9 (ASCII)
# 11	Strongest Speed Tenths			0-9 (ASCII)
# 12	Strongest Strength Hundreds		0-9 (ASCII)
# 13	Strongest Strength Tens			0-9 (ASCII)
# 14	Strongest Strength Ones			0-9 (ASCII)
# 15	Channel Signal Strength Ratio Hundreds 	0-9 (ASCII)
# 16	Channel Signal Strength Ratio Tens 	0-9 (ASCII)
# 17	Channel Signal Strength Ratio Ones 	0-9 (ASCII)
# 18	Status Bytes				See detail
# 19	Carriage Return				0x0D

# Status Byte:
# Bits 7:6	always 01
# Bit 5		always 0
# Bit 4		fork mode enabled = 1, disabled = 0
S_SB_forkmode_enabled = (1<<4)
# Bits 3:0	always 0

NaN = float('nan')
def isnan(x): return(str(x)) == 'nan'

MSG_B_FORMAT = 0x81
MSG_S_FORMAT = 0x83

#Flags
NOT_LOCKED = 0
LOCKED = 1

FORK_MODE_DISABLED = 0
FORK_MODE_ENABLED = 1

ZONE_OPPOSITE = 0
ZONE_SAMEBOTH = 1

TRANSMITTER_ON = 0
TRANSMITTER_OFF = 1

NOT_FASTLOCKED = 0
FASTLOCKED = 1

FASTER_DISABLED = 0
FASTER_ENABLED = 1

VOLTAGE_NORMAL = 0
VOLTAGE_LOW = 1

DIR_CLOSING = 0
DIR_AWAY = 1

class radarreport:
        def __init__(self):
        # data members other
	 self.timereceived = NaN
	 self.valid = NaN

        # data members A AF B D0 D1 D2 D3 D4 S format sentences
         self.patrolspeed = NaN
         self.lockedspeed = NaN
         self.fasterspeed = NaN
         self.targetspeed = NaN
	
	# sata members S format
	 self.strongspeed = NaN
	 self.strongspeeddir = NaN
	 self.strongstrength = NaN
	 self.channelsignalstrengthratio = NaN

	# additional data members Enhanced Output format
	 self.patrolspeeddir = NaN
	 self.lockedspeeddir = NaN
	 self.fasterspeeddir = NaN
	 self.targetspeeddir = NaN
	 self.testresult = NaN
	 #self.forkmode			#duplicated in other formats
	 self.units= NaN
	 #self.transmitterstatus	#duplicated in other formats
	 self.stronglock = NaN
	 self.fastlock = NaN
	 #self.zone			#duplicated in other formats
	 self.mode = NaN

	 
	# datamember status & config
         self.lockstatus = NaN
         self.zone = NaN
         self.forkmode = NaN
         self.transmitterstatus = NaN
         self.fastlockstatus = NaN
         self.fastlockmode = NaN
         self.voltagestatus = NaN

class radardata:
        def __init__(self):
         # inititialize all data members
         self.online = 0
         self.report = radarreport()

         #self.status = STATUS_NO_DATA

        def __repr__(self):
	 #produce a printable representation of this object
         print("radardata __repr__() called but not implemented yet\n")
	 return -1 # ?

class radar(radardata,radarcommon,radarconfig):
	def __init__(		self,
			 	port_num="/dev/ttyUSB0", 
				port_baud=9600, 
				port_bytesize=8, 
				port_parity='N', 
				port_stopbits = 1,
				verbose = 0):
	 radardata.__init__(self)
	 radarcommon.__init__(	self,
				port_num, 
				port_baud, 
				port_bytesize, 
				port_parity, 
				port_stopbits,
				verbose)
	 radarconfig.__init__(self)

	def __unpackEnhanced(self,buf):
	 #unpack an Enhanced Output format sentence
	 self.report.timereceived = self.received #NO only do this if checksum valid
	 self.report.valid=0
	 ######
	 ###### In fact check the checksum first!

	 #check it is an Enhanced Output format sentence
	 #0xEF 0xFF 0x02 0x01
	 # if not buf[0] == 0xEF and buf[1] == 0xFF and buf[2] == 0x02 and buf[3] == 0x01:
	 # sys.stderr.write("__unpackEnhanced(): Incorrect first four bytes")
	 # return -1
	 #check message is correct length (always 21 bytes)
	 if not len(buf)==21:
	  sys.stderr.write("__unpackEnhanced(): Incorrect message length")
	 

	 #unpack payload length LSB and MSB

	 #unpack command ID 0x00

	 #unpack antenna number 0x01

	 #unpack target speed lsb msb

	 #unpack faster speed lsb msb

	 #unpack locked speed lsb msb

	 #unpack patrol speed lsb msb

	 #unpack direction byte

	 #unpack status byte

	 #unpack configuration byte

	 #calculate checksum of received bytes lsb msb

	 #compare to received checksum bytes lsb msb

	 #only return 0 and make assignments if checksum valid

	 sys.stderr.write("__unpackEnhanced(): Not fully implemented yet")
	 self.report.valid = 0
	 return -1


	def __unpackS(self,buf):
	 #unpack an S format sentence
	 self.report.timereceived = self.received
	 self.report.valid = 0
	
	 #check it is an S format sentence
	 msgtype = ord(buf[0])
	 if msgtype != MSG_S_FORMAT:
	  if self.verbose > 1:
	   sys.stderr.write("__unpackS(): Message type was not S format\n")
	  return -1
	 
	 #unpack  faster target direction
	 if buf[1] != ' ':
	  if buf[1] == 'A':
	   self.report.fasterspeeddir = DIR_AWAY
	  elif buf[1] == 'C':
	   self.report.fasterspeeddir = DIR_CLOSING
	  else:
	   self.report.fasterspeeddir = NaN	   
	   sys.stderr.write("__unpackS(): Unexpected character received in fastertargetdir field")
	 else:
	  self.report.fasterspeeddir = NaN

	 #unpack  faster target speed	 
	 if buf[2:6] != '    ':
	  fasterspeed = int(buf[2:6])
	  if buf[5] != ' ':
	   fasterspeed = fasterspeed /10
	  self.report.fasterspeed = fasterspeed
	 else:
	  self.report.fasterspeed = NaN

	 #unpack  strongest target direction
	 if buf[6] != ' ':
	  if buf[6] == 'A':
	   self.report.strongspeeddir = DIR_AWAY
	  elif buf[6] == 'C':
	   self.report.strongspeeddir = DIR_CLOSING
	  else:
	   self.report.strongspeeddir = NaN	   
	   sys.stderr.write("__unpackS(): Unexpected character received in strongesttargetdir field\n")
	 else:
	  self.report.strongspeeddir = NaN

	 #unpack strongest target speed	 
	 if buf[7:11] != '    ':
	  strongspeed = int(buf[7:11])
	  if buf[10] != ' ':
	   strongspeed = strongspeed / 10	  
	  self.report.strongspeed = strongspeed
	 else:
	  self.report.strongspeed = NaN

	 #unpack strongest target strength
	 if buf[11:14] != '   ':
	  self.report.strongstrength = int(buf[11:14])
	 else:
	  self.report.strongstrength = NaN

	 #unpack  channel signal strength ratio
	 if buf[14:17] != '   ':
	  self.report.channelsignalstrengthratio = int(buf[14:17])
	 else:
	  self.report.channelsignalstrengthratio = NaN

	 #unpack  status byte
	 statusbyte = ord(buf[17])
	 if statusbyte & S_SB_forkmode_enabled:
	  self.report.forkmode = FORK_MODE_ENABLED 
	 else:
	  self.report.forkmode = FORK_MODE_DISABLED	 
	 
	 self.report.valid = 1
	 return 0


	def __unpackB(self,buf):
         # unpack a B format sentence
         # buf should contain a complete sentence to the carriage return
         # as per the Stalker Radar Speed Sensor User Manual, A-3.

	 self.report.timereceived = self.received
	 self.report.valid = 0

 	 #check it is a B format sentence
	 msgtype = ord(buf[0])
	 if msgtype != MSG_B_FORMAT:
	  if self.verbose > 1:
	   sys.stderr.write("__unpackB(): Message type was not B format\n")
	  return -1

	 #unpack status 1 byte	 
	 status1byte = ord(buf[1])
	 if self.verbose > 1:
	  sys.stderr.write("status1byte arrived at __unpackB()\n  contents: %s\n" % (status1byte))
	 if status1byte & B_SB1_lockstatus_locked:
	  self.report.lockstatus = LOCKED
	 else:
	  self.report.lockstatus = NOT_LOCKED

	 if status1byte & B_SB1_zone_sameboth:
	  self.report.zone = ZONE_SAMEBOTH
	 else:
	  self.report.zone = ZONE_OPPOSITE
	
	 if status1byte & B_SB1_forkmode_enabled:
	  self.report.forkmode = FORK_MODE_ENABLED
	 else:
	  self.report.forkmode = FORK_MODE_DISABLED

	 if status1byte & B_SB1_transmitter_on:
	  self.report.transmitterstatus = TRANSMITTER_ON
	 else:
	  self.report.transmitterstatus = TRANSMITTER_OFF

	 #unpack status 2 byte
	 status2byte = ord(buf[2])
	 if status2byte & B_SB2_fastlockstatus_locked:
	  self.report.fastlockstatus = FASTLOCKED
	 else:
	  self.report.fastlockstatus = NOT_FASTLOCKED

	 if status2byte & B_SB2_fastlock_enabled:
	  self.report.fastlockmode = FASTER_ENABLED
	 else:
	  self.report.fastlockmode = FASTER_DISABLED
	 
	 if status2byte & B_SB2_voltage_low:
	  self.report.voltagestatus = VOLTAGE_LOW
	 else:
	  self.report.voltagestatus = VOLTAGE_NORMAL

	 #speeds returned in ascii, convert to int and copy to data members.
	 if self.verbose >1 :
	  sys.stderr.write("unpacking speeds...\n  buf[3:15] contents: %s\n  type: %s\n " % (buf[3:15], type(buf[3:15])) )
	 if buf[3:6] != '   ':
	  self.report.patrolspeed = int(buf[3:6])
	 else:
	  self.report.patrolspeed = NaN
	 
	 if not buf[6:9] == '   ':
	  self.report.lockedspeed = int(buf[6:9])
	 else:
	  self.report.lockedspeed = NaN

	 if not buf[9:12] == '   ':
	  self.report.fasterspeed = int(buf[9:12])
	 else:
	  self.report.fasterspeed = NaN

	 if not buf[12:15] == '   ':
	  self.report.targetspeed = int(buf[12:15])
	 else:
	  self.report.targetspeed = NaN

	 if self.verbose > 1:
	  sys.stderr.write( "Reached end of __unpackB()")
	 self.report.valid = 1
	 return 0

	def read(self):
	 #Read and interpret data
	 status = radarcommon.read(self)
	 if status <= 0:
	  return status
	 #identify and unpack a B format sentence
	 if self.__unpackB(self.response) == 0:
	  return 0
	 #identify and unpack an S format sentence
	 elif self.__unpackS(self.response) == 0:
	  return 0
	 #identify an Enhanced Output format sentence
	 elif self.__unpackEnhanced(self.response) == 0:
	  return 0
	 else:
	  if self.verbose >1:
	   sys.stderr.write("Failed to identify self.response in radar.read()\nContents of self.response: %s" % (self.response) )
	  #some exception stuff here?
	 return 0


	def next(self):
	 if self.read() == -1:
	  raise StopIteration
	 return self.response

	def close(self):
	 radarcommon.close(self)
	
	def __del__(self):
	 self.close()
	
