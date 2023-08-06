# setup.py for proofcheck

import os
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install_scripts import install_scripts

if os.name == 'nt':
	try:
		import win_add2path
	except ImportError:
		win_add2path = None
	try:
		import win_add2syspath
	except ImportError:
		win_add2syspath = None

scriptlist = ['audit', 'check','checkall','mathparse','padscope',
              'parse', 'renote','renum','resetdefs','resetprops']


fontlist   = ['fonts/morse10.mf', 'fonts/cmbasea.mf', 'fonts/mmx10.mf', 
              'fonts/mathexa.mf', 'fonts/bigopa.mf',  'fonts/mathsya.mf', 
              'fonts/caluapm.mf', 'fonts/symbola.mf', 'fonts/symapm.mf']

headerlist   = ['tex/common.tdf', 'tex/utility.tdf',
                'tex/common.ldf', 'tex/utility.ldf','tex/common.dfs']

libfilelist  = ['tex/rules.tex','tex/common.tex', 'tex/properties.tex'] 

#
# Places to look for TeX
#
good_guesses_posix = ['share/texmf','share/texlive','texmf','texlive']

good_guesses_windows = ['C:\\texlive\\texmf-local',]

class install_proofcheck_scripts(install_scripts):
	""" Check for write access and bail if it is not there. 
	Do the regular install scripts.  Then if this is Windows 
	add '.py' to the script names and add python to
	the path."""

	user_options = install_scripts.user_options 
	
	boolean_options= install_scripts.boolean_options

	def initialize_options(self):
		install_scripts.initialize_options(self)

	def run(self):
		# Get scripts directory 
		for x in self.user_options:
			if x[0] == "install-dir=":
				scriptsdir = getattr(self,"install_dir")
				print "scriptsdir =", scriptsdir
				parentdir = os.path.split(scriptsdir)[0]
				print "parentdir =", parentdir
				if not os.access(parentdir, os.W_OK):
					print "You need root access or just install in your own directory."
					raise SystemExit
		# Run the original install_scripts 
		install_scripts.run(self)
		# Check whether this is Windows 
		if os.name == 'nt':
			print "Adding .py to script names"
			for fil in os.listdir(os.path.join(os.sys.prefix,"Scripts")):
				if fil in scriptlist:
					without_py = os.path.join(os.sys.prefix,"Scripts",fil)
					with_py = without_py + ".py"
					if os.path.isfile(with_py):
						os.remove(with_py)
					os.rename(without_py,with_py)
			if win_add2syspath: 
				try:
					win_add2syspath.extend()
				except:
					if win_add2path:
						try:
							win_add2path.main()
						except:
							print "Add Python to your path manually"
					else:
						print "Add Python to your path manually"
			else:
				print "Add Python to your path manually"


class install_proofcheck_data(install_data):

	""" Locate TeX, put files there, and then run mktexlsr. """

	user_options = install_data.user_options 
	
	boolean_options= install_data.boolean_options

	def initialize_options(self):
		install_data.initialize_options(self)

					
	def run(self):
		for x in self.user_options:
			if x[0] == "install-dir=":
				datadir = getattr(self,"install_dir")
				print "datadir =", datadir
				if not os.access(datadir, os.W_OK):
					print "You need root access or just install in your own directory."
					raise SystemExit
				if os.name == 'nt':
						for guess in good_guesses_windows:
							texdir = os.path.join(datadir,guess)
							if os.path.isdir(texdir):
								self.install_dir = texdir
								break
						else:
							save_dir = os.getcwd()
							os.chdir("\\")	
							print "Running dir /s"
							pipe = os.popen("dir /B /s texmf-local")
							texdir = pipe.read().strip()
							os.chdir(save_dir)
							if texdir.startswith("File not found"):
								print "Can't find TeX"
								raise SystemExit
							else:	
								self.install_dir = texdir 
				elif os.name == 'posix':
						for guess in good_guesses_posix:
							texdir = os.path.join(datadir,guess)
							if os.path.isdir(texdir):
								self.install_dir = texdir
								break
						else:
							print "Running find"
							pipe = os.popen("find " + datadir + " -name texmf -print")
							texdir = pipe.read().strip()
							if texdir:
								self.install_dir = texdir 
							else:
								print "Can't find TeX"
								raise SystemExit
				else:
					print "Don't know where to look for TeX on a ", os.name
					raise SystemExit

		install_data.run(self)
			
		error = os.system(texdir + "/bin/mktexlsr")
		if error :
			error = os.system("mktexlsr")
		if error:
			print "Warning: mktexlsr not found"
		else:
			print "Done"



setup(name = "proofcheck",
		version = "1.0",
		platforms = ['linux', 'windows','mac'],
		license = "GNU General Public License",
		py_modules = ['getpath','pattern','synt','unify'],
		scripts = scriptlist,
		author = "Bob Neveln",
		author_email = "neveln@cs.widener.edu",
		data_files = [('fonts/source/public/morse', fontlist),
                  ('tex/proofcheck/include', headerlist),
                  ('tex/proofcheck/lib', libfilelist)],
		description = "Checks mathematical proofs written in TeX",
		url = "http://www.proofcheck.org/",
		cmdclass = {"install_data" : install_proofcheck_data,
                "install_scripts" : install_proofcheck_scripts},
		classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
									 'Natural Language :: English',
									 'Operating System :: Microsoft :: Windows',
		               'Operating System :: POSIX',
		               'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.3',
                   'Programming Language :: Python :: 2.4',
									 'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
									 'Topic :: Scientific/Engineering :: Mathematics'],
		#Get the long description from admin/pypipage.rst
		long_description =\
""" 
============================================================
ProofCheck:  Checking Mathematical Proofs Written in TeX
============================================================


Mathematical proofs are sequences of
steps which take expressions in a formal language which
state something already known to another formal expression
which becomes known as a result.
Each step must be justified by a rule of inference.  The notion
of proof is sharpened when the set of inference rules is 
reduced to a small number.  But the effect of such reduction
on proofs is to make them cumbersome, like the
computations of a Turing Machine.  ProofCheck uses 
a really large rule set to make possible proofs which are not
cumbersome.   The default inference rule set currently contains over 1500 rules
and is still growing.  

Either TeX or LaTeX may be used. What is
required in the way of document structure  is that:

  1. Each theorem must be labeled and 
  numbered in number-dot-number style,

  2. Each theorem and proof must be 
  expressed in a language that ProofCheck can learn to parse, and

  3. Proof steps must be numbered and annotated 
  following ProofCheck syntax.

The work cycle is as follows:

  1. Edit the document using your preferred text editor:

      emacs article.tex

  2. TeX the document:

      tex article

  3. Parse the document:

      parse.py article

  4. Check a proof of, say theorem 1.23:

      check.py article 1.23

Errors at any stage of course send you back to the text editor.
""")
