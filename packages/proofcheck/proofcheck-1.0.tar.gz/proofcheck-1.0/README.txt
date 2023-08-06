#
# ProofCheck README file
#

This package assumes that some version of TeX, e.g. Texlive, is
installed on your system.  TeX can be downloaded from:

	www.tug.org 

Some version of Python 2 is absolutely required.  
Python can be downloaded from:

	www.python.org


POSIX (Linux, Unix, MacOS) Installation:

	To install the package either become superuser and from the directory
	in which this README file is located run:

		python install.py

	or

		python setup.py install

	or use sudo to execute as superuser:

		sudo python setup.py install

	This will attempt to locate your TeX directory, e.g. /usr/share/texmf,
	and under that it will install tex/proofcheck/lib and 
	tex/proofcheck/include directories.

	If the install script cannot find the TeX directory but
	you know where it is, say /opt/texmf
	try running: 

		python setup.py install --install-data /opt/texmf

	or:

		sudo python setup.py install --install-data /opt/texmf

	To test the install run:

		python test.py

	without being superuser.  Although you should get a warning
	about missing dfs files, all proofs should check, all 
	1 + 9 + 1 of them.

WINDOWS installation:

	Make sure you have administrator privileges. Then
	double click on the install.py file and then log out.  
	As a part of the install, Python is put on your the 
	system path.  But this does not take effect until the 
	next time you log in.
	
	If the install script cannot find the TeX directory but
	you know where it is, say C:\texlive, open up a DOS
	window with a command prompt and 
	try running: 

		\python27\python setup.py install --install-data C:\texlive

	To put python on the path you can use the menus. See;

		http://www.katsbits.com/tutorials/blender/
		setting-up-windows-python-path-system-variable.php

	If you cannot get Administrator privileges, then you 
	can unpack the distribution manually.  Just copy the files
	into the directory where you keep your TeX files.

	To test the install double click on the file

		test.py
	
	Although you should get a warning about missing dfs files, 
	all proofs should check, all 1 + 9 + 1 of them.
		
