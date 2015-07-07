Bbuf = (	'\x81' 			# Message Type 'B'
	+ chr(0b01010011) 	# Status 1, No lock, Same/Both, fork mode off, transmitter on
	+ chr(0b01000100) 	# Status 2, No fast speed locked, faster enabled, no low volt
	+ '\x31\x31\x31' 	# Patrol Speed, 111
	+ '\x32\x32\x32' 	# Locked Speed, 222
	+ '\x33\x33\x33' 	# Faster speed, 333
	+ '\x34\x34\x34' 	# Target speed, 444
	+ '\x0D'		# Carriage return
	)

