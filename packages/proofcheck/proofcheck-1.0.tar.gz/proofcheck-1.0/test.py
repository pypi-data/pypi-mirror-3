import os

os.chdir("tex")

if "rules.tex" in os.popen("kpsewhich rules.tex").read():
	pass
#	os.remove("rules.tex")
else:
	print "rules.tex not installed in TeX directory"
	raise SystemExit
if "properties.tex" in os.popen("kpsewhich properties.tex").read():
	pass
#	os.remove("properties.tex")
else:
	print "properties.tex not installed in TeX directory"
	raise SystemExit
if "common.tex" in os.popen("kpsewhich common.tex").read():
	pass
#	os.remove("common.tex")
else:
	print "common.tex not installed in TeX directory"
	raise SystemExit
if os.name == 'nt':
	os.system("parse.py geom")
	os.system("parse.py indnum")
	os.system("parse.py divides")
	os.system("checkall.py geom")
	os.system("checkall.py indnum")
	os.system("checkall.py divides")
else:
	os.system("parse geom")
	os.system("parse indnum")
	os.system("parse divides")
	os.system("checkall geom")
	os.system("checkall indnum")
	os.system("checkall divides")
