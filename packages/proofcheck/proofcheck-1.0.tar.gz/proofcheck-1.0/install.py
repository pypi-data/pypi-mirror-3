import os,sys

#if os.name == 'nt':
#	import ctypes

#if os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin() != 1:
#	print "You must be the Administrator to run this!"
#	raw_input("OK?")
				
if os.name == 'posix' and os.geteuid() > 0:
	print "You must be superuser to run this."
else:
	os.system(sys.executable + " setup.py install")
 
