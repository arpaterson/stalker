#!/usr/bin/env python
#
# Author: Anthony Paterson arpaterson@wordpress.com Mar 2015

import sys, struct

def isodd(x): return(x%2==1) == True

NaN = float('nan')
def isnan(x): return(str(x)) == 'nan'


############################################################
# Definition of Configuration command protocol
#
# Configuration packet format
#
# Byte		Description			Value
# 1		StartID
CMD_StartID = 			0xEF
# 2		Destination ID
CMD_DestID = 			0x02
# 3		Source ID
CMD_SourceID = 			0x01
# 4		Packet Type
CMD_PacketType = 		0x00
# 5		Payload Length (LSB)
# 6		Payload Length (MSB)
# 7		Command ID
# 8		Antenna Number
CMD_AntennaNumber = 		0x00
# 9		Configuration Value
# 10		Checksum (LSB)
# 11		Checksum (MSB)
############################################################

############################################################
# Configuration Settings Table
#
# ID	Description	Default (Traffic 232)	Values
# 1	Mode				0	0 Stationary 1 Moving
# 2	Zone				2	0 Away(Sta)/Same(Mov), 
#						 1 Closing (Sta)/Opposite(Mov)
# 3	Ground speed sensitivity	--	1 min - 23 max
# 4	Opposite/Stationary sensitivity 4	0 min - 4 max
# 5	Same lane sensitivity		3	0 min- 4 max
# 6	Fine sensitivity adjust		3	0 min - 3 max
# 7	Stationary low cutoff		0	0 low (~1mph) 1 high (~12mph/19kph)
# 8	Patrol speed low cutoff		0	0 low (~1mph) 1 high (~12mph/19kph)	
# 9	?
# 10	?
# 11	?
# 12	Alarm speed threshold
# 13	faster target tracking
# 14	faster locking enable
# 15	lock option
# 16	AUX pin config
# 17	Double suppression
# 18	Cosine angle 1
# 19	Cosine angle 2
# 20	Units				0	0 MPH, 1 KPH, 2 Knots, 3 m/s, 4 feet/s
# 21	Unit resolution			0	0 ones 1 tenths
# 22	?
# 23	Leading zero character		0	0 space (ASCII 0x20), 1 zero (ASCII 0x30)
# 24	Squelch
# 25	Doppler audio volume
# 26	Audio 0 enable
# 27	Variable doppler loudness
# 28	Beep volume
# 29	Serial port baud rate		5	0 300, 
#						1 600, 
#						2 1200, 
#						3 2400, 
#						4 4800, 
#						5 9600, 
#						6 19200, 
#						7 38400
# 30	Serial port output format	3	0 None (No Serial Output)
#						1 EE
#						2 Enhanced Output
#						3 B
#						4 S
#						5 F
#						6 A
#						7 AF
#						8 D0
#						9 D1
#						10 D2
#						11 D3
#						12 D4
CMD_ID_Output_Format = 30
CMD_VAL_Output_Format_B = 3
CMD_VAL_Output_Format_S = 4
OUTPUT_FORMAT_B = 3
OUTPUT_FORMAT_S = 4
# 31	Message Period			0	0-10000 ms
# 32	?
# 33	?
# 34	?
# 35	?
# 36	?
# 37	Get Product ID		supported	1 request ascii string with product model and software version
CMD_Get_Product_ID = 37
# 38	?
# 39	?
# 40	?
# 41	?
# 42	Transmitter control		1	0 off 1 on
# 43	Strongest Lock			0	0 release, 1 lock
# 44	Fast lock			0	0 release, 1 lock
# 45	Patrol speed blank	supported	1 re-acquire patrol speed or (Traffic 232, toggle locked patrol speed on and off)
# 46	Test				1	Init internal test
# 47	Fork enable			0	0 off, 1 on (non-directional)
# 48	Max AGC gain			7	0 low - 7 high (max >= min)
# 49	Min AGC gain			0	0 low - 7 high (min <= max)
# 50	Get current AGC gain	supported
# 51	?
# 52	Auto test period		600	30 - 900 seconds (can be two byte value)
# 53	Auto test mode			0	0 always, 1 only when transmitter is on
# 54	Low sensitivity			--	0 disable 1 enabled
# 55	Target acquisition quality	--	see manual
# 56	?
# 57	?
# 58	?
# 59	?
# 60	?
# 61	?
# 62	Target loss quality		--	see manual
# 63	TX on time			--	0 - 60000 ms see manual
# 64	TX off time			--	0 - 60000 ms see manual
# 65	?
# 66	?
# 67	?
# 68	?
# 69	?
# 70	?
# 71	?
# 72	?
# 73	?
# 74	?
# 75	?
# 76	Enhanced test		supported	0 get last test result, 1 initiate test and return result
# 77	?
# 78	?
# 79	Get product type	supported	1 request 3 byte code associated with product model
# 80	?
# 81	Get software version	supported	1 request ascii string containing software version
# 82	?
# 83	?
# 84	?
# 85	Target strength sensitivity
# 86	?
# 87	Sensitivity hysteresis
# 88	Holder over delay		45	1 - 222 (Traffic and Speedometer, stationary fixed 45)
# 89	?
# 90	Format D polled modes		--
# 91	Format D direction enable	--
# 92	Format D zero report		--
# 93	Format D update on change only	--
# 94	?
# 95	?
# 96	?
# 97	?
# 98	Zeros after target loss		--
# 99	Keep TX on with target		--
# 100	Max TX on time			--
# 101	?
# 102	?
# 103	?
# 104	?
# 105	?
# 106	?
# 107	?
# 108	?
# 109	?
# 110	?
# 111	?
# 112	?
# 113	?
# 114	?
# 115	?
# 116	Speed sensor address		2	2-254 (only for RS-485 models)

############################################################

METHOD_GET = 0
METHOD_CHANGE = 1
METHOD_SET = 2


class radarcommand:
	def __init__(self):
	 # data members 
	 self.startid = NaN
	 self.destid = NaN
	 self.sourceid = NaN
	 self.packettype = NaN
	 self.payloadlength = NaN
	 self.commandid = NaN
	 self.antennanumber = NaN
	 self.configurationvalue = NaN
	 self.checksum = NaN

class radarconfig(radarcommand):
	
	def __init__(self):
	 self.command = radarcommand()
	 self.setMethod()
	 self.setCommand() #default?
	 self.setValue() #does not check for valid values	

	def setMethod(self, method = METHOD_GET):
	 self.commandmethod = method

	def setCommand(self, cmd =  CMD_Get_Product_ID):
	 if self.commandmethod == METHOD_GET:
  	  self.command.commandid = cmd
	 elif self.commandmethod == METHOD_CHANGE:
  	  self.command.commandid = cmd
	 elif self.commandmethod == METHOD_SET:
  	  self.command.commandid = cmd + 0x80 # 0x80 causes radar to use configuration value

	def setValue(self, value = 0x00):
	 if self.commandmethod == METHOD_GET:
	  if not value == 0x00:
	   sys.stderr.write("radarconfig.setvalue():\n  received value other than 0  but method is 'set'\n")
 	  self.command.configurationvalue = 0
	 elif self.commandmethod == METHOD_CHANGE:
	  if not value == 0x01:
	   sys.stderr.write("radarconfig.setvalue():\n  received value other than 1 but method is 'chnage'\n")
	  self.command.configurationvalue = 1
	 elif self.commandmethod == METHOD_SET:
	  self.command.configurationvalue = value

	def getMessage(self):

	 CMD_CommandID = self.command.commandid
	 CMD_ConfigValue = self.command.configurationvalue
	 

	 # Assemble the fixed length part of the cammand message
 	 cmdstr	= struct.pack(	'B', CMD_StartID )		#always 1 byte
	 cmdstr	+= struct.pack(	'B', CMD_DestID )		#always 1 byte
	 cmdstr	+= struct.pack(	'B', CMD_SourceID )		#always 1 byte
	 cmdstr	+= struct.pack(	'B', CMD_PacketType )		#always 1 byte


	 # Calculate and append the payload length bytes
	 if CMD_ConfigValue < 0xFF:
	  CMD_PayloadLength = 0x03
	 elif CMD_ConfigValue >= 0xFF and CMD_ConfigValue < 0xFFFF:
	  CMD_PayloadLength = 0x04
	 else:
	  sys.stderr.write("CMD_ConfigValue has unsupported length (>2)")
	  return -1
	 
	 cmdstr += struct.pack( '<H', CMD_PayloadLength )	#always 2 bytes

	 cmdstr += struct.pack( 'B', CMD_CommandID )		#always 1 byte
	 cmdstr += struct.pack( 'B', CMD_AntennaNumber )	#always 1 byte
	
	 # Append the variable length command value
	 if CMD_ConfigValue < 0xFF:
	  cmdstr += struct.pack( 'B', CMD_ConfigValue )	#case for 1 byte values
	 elif CMD_ConfigValue >= 0xFF and CMD_ConfigValue < 0xFFFF:
	  cmdstr += struct.pack( '<H', CMD_ConfigValue )#case for 2 byte values
	 else:
	  sys.stderr.write("CMD_ConfigValue has unsupported length (>2)")
	  return -1

	 # Calculate the modular checksum
	 checksum = self.getChecksum(cmdstr)

	 # Append the Checksum bytes
	 CMD_Checksum_LSB = checksum % 256
	 CMD_Checksum_MSB = checksum / 256
	 cmdstr += struct.pack( 'B', CMD_Checksum_LSB ) 	#always 1byte
	 cmdstr += struct.pack( 'B', CMD_Checksum_MSB )		#always 1byte

	 

	 return cmdstr

	
	def getChecksum(self,buf):
	 # Calculate the modular checksum of pairs of bytes in LSB,MSB order,
	 # if there is an odd number of bytes in the 
	 # message, the last msb is to be 0x00
	 buf_len = len(buf)
	 if isodd(buf_len):
	  buf += '\x00' #buf is not being passed back so this does not need ot be removed
	 
	 # TODO use bytes and byte arrays, and pack to str later. using strings causes excessive copying

	 checksum = 0
	 for i in range(1, len(buf), 2):
	  msb = buf[i]
	  lsb = buf[i-1]
	  checksum += (ord(msb)*256 + ord(lsb))

	 #truncate to low order 2 bytes
	 
	 #pass back the checksum
	 return checksum

