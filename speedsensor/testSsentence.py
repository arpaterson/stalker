Sbuf = (	'\x83' 			# Message Type 'S'
	+ 'C'			#fasterspeeddir closing
	+ ' 40 '		#fasterspeed 40kph (ones not enabled)
	+ 'C'			#strongspeeddir closing
	+ ' 45 '		#strongspeed
	+ ' 20'			#strongspeed strength
	+ ' 10'			#ch sig strength ratio
	+ '@'			#status 01000000 fork mode disabled
	)

Sstr1 = '▒C    C 43   1  1@'
Sstr2 = '▒C    C 10   9 20@'

