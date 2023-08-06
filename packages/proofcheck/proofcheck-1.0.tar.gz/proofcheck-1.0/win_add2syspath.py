#
# Thanks to Anthon Van der Neut for this "recipe"
#
import sys, os
import _winreg

def extend():
	"""
	extend() adds pypath and the Scripts under it to the PATH environment 
	variable as defined in the registry.  Already opened DOS-Command 
	prompts are not updated.
	"""
	pypath = os.path.split(os.sys.executable)[0]

	hKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
 				"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
				0, _winreg.KEY_READ|_winreg.KEY_SET_VALUE)

	value,typ = _winreg.QueryValueEx(hKey, "PATH")
	vals = value.split(';')
	if pypath in vals:
		print pypath, "already in the path."
		return
	scriptspath = os.path.join(pypath,"Scripts")
	vals.append(pypath)
	vals.append(scriptspath)
	print "Adding to PATH:", pypath
	_winreg.SetValueEx(hKey,"PATH",0,typ,';'.join(vals))
	_winreg.FlushKey(hKey)


if __name__ == '__main__':
	extend()
