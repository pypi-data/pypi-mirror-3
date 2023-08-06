import os

def getpath(filename):
	if os.path.isfile(filename):
		return filename

	if os.getenv("TEXPATH"):
		another_name = os.path.join(os.getenv("TEXPATH"),filename)
		if os.path.isfile(another_name):
			return another_name

	if os.name == 'posix':
		home_dir = os.getenv("HOME")
	else:
		home_dir = "."
	config_file_name = os.path.join(home_dir, ".proofcheck")
	if os.path.isfile(config_file_name):
		config_file = open(config_file_name)
		next_line = config_file.readline().strip()
		while next_line and next_line.startswith("#"): 
			next_line = config_file.readline().strip()
		config_file.close()
		user_proofcheck_directory_name = next_line 
		if not os.path.isdir(user_proofcheck_directory_name):
			print user_proofcheck_directory_name , "not a directory!"
			raise SystemExit
		second_try_name = os.path.join(user_proofcheck_directory_name,filename)
		if os.path.isfile(second_try_name):
			return second_try_name

	pipe = os.popen("kpsewhich " + filename)
	kpathtry_name = pipe.read().strip()
	if kpathtry_name:
		return kpathtry_name


if __name__ == '__main__':
	filename = raw_input("Enter file name: ")
	print getpath(filename)
