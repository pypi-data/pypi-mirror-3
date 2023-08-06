########################################
# pattern.py
#

from re import compile 

#s = '\A\s*\\\\(chapter|(sub)*section)\W.*'
#latex_major_unit = compile(s)

s = "\\\\mathchardef\\\\([A-Z,a-z]*)=\"([A-F,\d]*)"
chardef = compile(s)
			
s = '\A\s*\\\\chap\W+(\d+)\..*'
chapthead = compile(s)

s = '\A\s*\\\\section\W.*'
latex_section = compile(s) 

s = '\A\s*\\\\chapter\W.*'
latex_chapter = compile(s) 

latex_unit_prefix = '\A\s*\\\\'
latex_unit_suffix = '\W.*'

# The alternate spellings of 'prop' have been removed
s = '\A\\\\(prop)\W+(\d+)\.(\d+)\s*\$(.*)'
thmnum = compile(s)

inputfile = compile('\s*\\\\input\s+((.+)\.([lt]df))')

#directive = compile('\s*%([:_A-Za-z]+)\s+((\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*(\S*)\s*)')
directive = compile('\s*%([:_A-Za-z]+)\s+((\S*)\s*(.*?))\s*\Z')

s = '\A\s*\\\\line([a-z])\s*\$(.*)'
line = compile(s)

s ='\A[^\$\%]*\\\\By(\W.*)'
by = compile(s)

s ='\A[^\$\%]*\\\\Bye(\W.*)'
bye = compile(s)

# Thanks to Karl Berry for enabling this:
s = '\A[^\%]*\\\\note\W+(\d+)\s+([^\$]*\$)(.*)'
note = compile(s)

s = '(?<!\\\\)(?P<TeXcomment>%)|(\\\\noparse)'
Noparse = compile(s)

s = '(?<!\\\\)(%)'
TeXcomment = compile(s)

s = '(?<!\\\\)(\$+)'
TeXdollar = compile(s)

s = '\A([a-z]*)(\d*(\.\d+)+)(.*)'
ref=compile(s)

s = '\A([a-z]+)(\d+(\.\d+)+)(.*)'
outfileref = compile(s)

s = '(\A|.*\D)\.(\d+)(.*)'
inref = compile(s)

ndotref = compile("(\d+)((\.\d+)+)")

exref = compile("(\A|[^a-z])((\d+)((\.\d+)+))")

s = '\A\$([^\$]*)\$(.*)'
TeXmath = compile(s)

s = '\A[^\$]*\\\\noparse.*'
noparse = compile(s)

s = 'z_\{(\d+)\}'
bvar = compile(s)

s = '\A\\\[qw]\^\{(\d+)\}_\{(\d+)\}'
newschem = compile(s)

s = "(\s*)(\d+|\
[\.<>;/:\[\]\(\+\)=$%\-\*\,]|\
\\\[\{\._\}]|\
([A-Za-z]|\{[^\{]*\}|\\\[A-Za-z]+)\
(?:\\\p+(?![A-Za-z]))?(?:[\^_](?:\{[^\{]*\}|.))*)(\s*)"
s = "(\s*)(\d+|\
[\.<>;/:\[\]\(\+\)=$%\-\*\,]|\
\\\[\{\._\}]|\
([A-Za-z]|\{[^\{]*\}|\\\[A-Za-z]+)\
(?:\\\p+(?![A-Za-z]))?(?:[\^_](?:\{[^\{]*\}|\\\\[A-Za-z]+|[^\\\\]))*)(\s*)"
token = compile(s) 
# token = pattern.token.match.group(2) 


s = "\A([^\d\s\.\$]*)(.*)"
puncts = compile(s)

s = "\A(\d+)(.*)"
nums = compile(s)

s = "\A[^\$]*\$(.*)"
dollar = compile(s)

s = "\A([^,\)\(]*)([,\)\(]+.*)"
findsingle = compile(s)

skipstring = "mskip 5mu plus 5mu"

s = '(?<!\\\\)\\\\((mskip 5mu plus 5mu)|([A-Za-z]+))'
alphacontrolseq_or_skip = compile(s)


if __name__ == '__main__':
	repeat = "yes"
	while repeat:
		repeat = raw_input("Enter possible directive: ")
		s = directive.match(repeat)
		if s:
			print s.group(2)

	print "yes"
