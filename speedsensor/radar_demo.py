#! /usr/bin/python
# Author: Anthony Paterson arpaterson@wordpress.com Mar 2015

# A demo program for reading and display value from the 
# Stalker Traffic Sensor radar unit.
#
# Initiates a seperate thread to process sentences from the radar
# see radarb1.py for further details

import time, threading, os
import radar
import io

radarObj = None #global variable

class radarPoller(threading.Thread):
        def __init__(self):
         threading.Thread.__init__(self)
         global radarObj #bring it in scope
         radarObj = radar.radar("/dev/ttyUSB0",9600,8,'N',1,0) #that last argument enable verbose mode
	 print("radarObj created")
         self.curent_value = None
         self.running = True
	
        def run(self):
         global radarObj
	 #Send config string:
	 radarObj.setMethod(2) #set  method set)
	 radarObj.setCommand(30) #set output format
	 radarObj.setValue(4) #s format
	 radarObj.send(radarObj.getMessage())
	 #Start dealing with data
         while self.running:
          radarObj.next()




#demo program
if __name__=="__main__":
        rp = radarPoller()
        try:
	 unitname = os.uname()[1]
	 starttime = time.strftime("%Y%m%d-%H%M%S")
	 filename = unitname + '_' + starttime + '_log_radar.csv'
	 fid = io.open(filename,'w')
	 fid.write(u'utc, valid, patrol speed, locked speed, faster speed,target speed, strong speed, strong direction, strong strength, ch sig str ratio, patrol dir, locked dir, faster dir, target dir, test result, units, strong lock, fast lock, mode, lock status, zone, forkmode, tx status, fastlock status, fast lock mode, voltage status\r\n')
         rp.start()
         while True:
#          os.system('clear')

	  print( '_____________________________________')
	  print( 'time received: %s'	% ( radarObj.report.timereceived ) )
          print( 'valid: %s'	% ( radarObj.report.valid ) )

          print( 'patrol speed: %s '	% ( radarObj.report.patrolspeed ) )
          print( 'locked speed: %s '	% ( radarObj.report.lockedspeed ) )
          print( 'faster speed: %s '	% ( radarObj.report.fasterspeed ) )
          print( 'target speed: %s '	% ( radarObj.report.targetspeed ) )

          print( 'strong speed: %s '	% ( radarObj.report.strongspeed ) )
          print( 'strong direction: %s '% ( radarObj.report.strongspeeddir ) )
          print( 'strong strength: %s '	% ( radarObj.report.strongstrength ) )
          print( 'channel signal strength ratio: %s '% ( radarObj.report.channelsignalstrengthratio ) )

          print( 'patrol direction: %s '% ( radarObj.report.patrolspeeddir ) )
          print( 'locked direction: %s '% ( radarObj.report.lockedspeeddir ) )
          print( 'faster direction: %s '% ( radarObj.report.fasterspeeddir ) )
          print( 'target direction: %s '% ( radarObj.report.targetspeeddir ) )

          print( 'test result: %s '	% ( radarObj.report.testresult ) )

          print( 'units: %s '		% ( radarObj.report.units ) )

          print( 'strong lock: %s '	% ( radarObj.report.stronglock ) )
          print( 'fast lock: %s '	% ( radarObj.report.fastlock ) )

          print( 'mode: %s '		% ( radarObj.report.mode ) )

          print( 'lock status: %s'	% ( radarObj.report.lockstatus  ) )
          print( 'zone: %s'		% ( radarObj.report.zone ) )
          print( 'forkmode: %s'		% ( radarObj.report.forkmode ) )
          print( 'tx status: %s'	% ( radarObj.report.transmitterstatus ) )

          print( 'fast lock status: %s'	% ( radarObj.report.fastlockstatus ) )
          print( 'fast lock mode: %s'	% ( radarObj.report.fastlockmode ) )
          print( 'voltage status: %s'	% ( radarObj.report.voltagestatus ) )


	  fid.write(u'{:f}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},\r\n'.format( 	
							radarObj.report.timereceived,
							radarObj.report.valid,

							radarObj.report.patrolspeed,  
							radarObj.report.lockedspeed, 
							radarObj.report.fasterspeed, 
							radarObj.report.targetspeed,

							radarObj.report.strongspeed,
							radarObj.report.strongspeeddir,
							radarObj.report.strongstrength,
							radarObj.report.channelsignalstrengthratio,

							radarObj.report.patrolspeeddir,
							radarObj.report.lockedspeeddir,
							radarObj.report.fasterspeeddir,
							radarObj.report.targetspeeddir,

							radarObj.report.testresult,

							radarObj.report.units,

							radarObj.report.stronglock,
							radarObj.report.fastlock,

							radarObj.report.mode,

							radarObj.report.lockstatus,
							radarObj.report.zone,
							radarObj.report.forkmode,
							radarObj.report.transmitterstatus,

							radarObj.report.fastlockstatus,
							radarObj.report.fastlockmode,
							radarObj.report.voltagestatus,

							  ) )

          time.sleep(1)

        except (KeyboardInterrupt, SystemExit):
         print "\nKilling Thread..."
         rp.running = False
         rp.join()
        print "Done.\nExiting."

