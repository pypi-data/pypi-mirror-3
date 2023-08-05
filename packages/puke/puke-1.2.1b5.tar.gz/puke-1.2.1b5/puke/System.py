import re, platform
from puke.Tools import *
from distutils import version


_PLATFORM = platform.system()
MACOS = "Darwin"
LINUX = "Linux"
WINDOWS = "Windows"

re_v = re.compile('((\d+)\.(\d+)(\.(\d+))?([ab](\d+))?)')
re_c = re.compile('(==|<=|>=|<|>)(.*)')

def check_package(name, compVersion = None, platform = "all"):

	if platform.lower() == "linux" and _PLATFORM != LINUX:
		return True
	
	if "mac" in platform.lower() and _PLATFORM != MACOS:
		return True

	check = sh("which %s" % name, header = None, output = False)
	check = check.strip()
	
	if not check:
		
		if _PLATFORM == MACOS:

			check = sh("brew info %s | grep -i -E \"(not installed|error)\"" % name, header=None, output=False)
			check = check.lower().strip()

			if "not installed" in check or 'error' in check:
				console.error('%s is M.I.A' % name)
				console.log(' => "brew install %s"' % name)
				console.error('')
				console.fail('%s not installed' % name)
		else:
			check = sh("aptitude show %s | grep -i -E \"(unable to locate|error)\"" % name, header=None, output=False)
			check = check.lower().strip()
			
			if "unable to locate" in check or 'error' in check:
				console.error('%s is M.I.A' % name)
				console.log(' => "aptitude install %s"' % name)
				console.error('')
				console.fail('%s not installed' % name)
		
		
	

	pVersion = get_package_version(name)

	goodVersion = True

	if compVersion:
		(op, wishVersion) = re_c.match(compVersion).groups()

		if op == "==":
			goodVersion = (version.StrictVersion(pVersion) == version.StrictVersion(wishVersion))
		elif op == "<=":
			goodVersion = (version.StrictVersion(pVersion) <= version.StrictVersion(wishVersion))
		elif op == ">=":
			goodVersion = (version.StrictVersion(pVersion) >= version.StrictVersion(wishVersion))
		elif op == "<":
			goodVersion = (version.StrictVersion(pVersion) < version.StrictVersion(wishVersion))
		elif op == ">":
			goodVersion = (version.StrictVersion(pVersion) > version.StrictVersion(wishVersion))
		else:
			console.fail('bad comp %s' % op)

	if goodVersion == True:
		console.confirm('%s : OK (%s)' % (name,pVersion))
	else:
		console.error('%s : OK (%s not %s)' % (name,pVersion, compVersion))
		resp = prompt('* Continue anyway ? [Y/N default=Y]')
		if resp.lower().strip() == "n":
			console.error('')
			console.fail('Failed on version comp %s ' % name)
		else:
			console.confirm('%s : OK (%s)' % (name,pVersion))

	return True


def get_package_version(name, index = 0):
	check = ['--version', '-v', 'hard']

	if check[index] == 'hard':
		if _PLATFORM == MACOS:
			version = sh('brew info %s | head -n 1' % (name), header = None, output = False)
		else:
			version = sh('aptitude show %s | grep -i "version:"' % (name), header = None, output = False)
	else:
		version = sh('%s %s' % (name,check[index]), header = None, output = False)

	version = re_v.findall(version)
	if version:
		return version[0][0]
	elif len(check) <= index + 1:
		return "0.0"
	else:
		return get_package_version(name, index+1)
