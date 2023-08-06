### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU Library General Public License as published by
### the Free Software Foundation; version 2 only
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU Library General Public License for more details.
###
### You should have received a copy of the GNU Library General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
### Fork of dstat - Copyright 2004, 2005 Dag Wieers <dag@wieers.com>
### New code Copyright 2006 Monty Taylor <monty@inaugust.com>
### Changed plugin system to use pkg_resources and setuptools.

from __future__ import generators
import pkg_resources

VERSION = '0.7.1'

def inspath(path):
	if os.path.isdir(path) and path not in sys.path:
		sys.path.insert(1, path)


try:
	import sys, signal, os, re, time
	import types, signal, resource, getpass
	inspath('/usr/local/share/mtstat/')
	inspath('/usr/share/mtstat/')
	inspath(os.path.abspath(os.path.dirname(sys.argv[0])) + '/plugins/')	# binary path + /plugins/
	inspath(os.getcwd() + '/plugins/')										# current path + /plugins/
	inspath(os.getcwd())													# current path
	inspath(os.path.expanduser('~/.mtstat/'))								# home + /.mtstat/
except KeyboardInterrupt, e:
	pass

if sys.version_info < (2, 2):
	sys.exit('error: Python 2.2 or later required, try mtstat15 instead')

### Workaround for python <= 2.2.1
try:
	True, False
except NameError:
	True = 1
	False = 0

### Workaround for python < 2.3
#if 'enumerate' not in __builtins__.__dict__.keys():
if sys.version_info < (2, 3) and sys.version_info >= (2, 2):
	def enumerate(sequence):
		index = 0
		for item in sequence:
			yield index, item
			index = index + 1
elif sys.version_info < (2, 2):
	def enumerate(sequence):
		index = 0
		list = []
		for item in sequence:
			list.append((index, item))
			index = index + 1
		return list

### Workaround for python < 2.3
#if 'sum' not in __builtins__.__dict__.keys():
if sys.version_info < (2, 3):
	def sum(sequence):
		ret = 0
		for i in sequence:
			ret = ret + i
		return ret

class Options:
	def __init__(self, args):
		self.args = args
		self.count = -1
		self.cpulist = None
		self.debug = 0
		self.delay = 1
		self.disklist = None
		self.full = False
		self.integer = False
		self.intlist = None
		self.netlist = None
		self.swaplist = None
		self.nolimit = False
		self.color = True
		self.update = True
		self.header = True
		self.output = False

		### Temporary hardcoded for my own project
		self.diskset = {
			'local': ('sda', 'hd[a-d]'),
			'lores': ('sd[b-k]', 'sd[v-z]', 'sda[a-e]'),
			'hires': ('sd[l-u]', 'sda[f-o]'),
		}

		try:
			import getopt
			opts, args = getopt.getopt (args, 'acdfghilmno:pstvyC:D:I:M:N:S:V',
				['all', 'cpu', 'disk', 'help', 'int', 'ipc', 'load', 'lock', 'mem', 'net', 'page',
				'proc', 'raw', 'swap', 'sys', 'tcp', 'time', 'udp', 'unix', 'version', 'vmstat',
				'debug', 'full', 'integer', 'mods', 'modules', 'nocolor', 'noheaders', 'noupdate', 'output='])
		except getopt.error, exc:
			print 'mtstat: %s, try mtstat -h for a list of all the options' % str(exc)
			exit(1)

		self.modlist = []

		for opt, arg in opts:
			if opt in ['-c', '--cpu']:
				self.modlist.append('cpu')
			elif opt in ['-C']:
				self.cpulist = arg.split(',')
			elif opt in ['-d', '--disk']:
				self.modlist.append('disk')
			elif opt in ['-D']:
				self.disklist = arg.split(',')
			elif opt in ['--debug']:
				self.debug = self.debug + 1
			elif opt in ['-g', '--page']:
				self.modlist.append('page')
			elif opt in ['-i', '--int']:
				self.modlist.append('int')
			elif opt in ['-I']:
				self.intlist = arg.split(',')
			elif opt in ['--ipc']:
				self.modlist.append('ipc')
			elif opt in ['-l', '--load']:
				self.modlist.append('load')
			elif opt in ['--lock']:
				self.modlist.append('lock')
			elif opt in ['-m', '--mem']:
				self.modlist.append('mem')
			elif opt in ['-M', '--mods', '--modules']:
				self.modlist = self.modlist + arg.split(',')
			elif opt in ['-n', '--net']:
				self.modlist.append('net')
			elif opt in ['-N']:
				self.netlist = arg.split(',')
			elif opt in ['-p', '--proc']:
				self.modlist.append('proc')
			elif opt in ['--raw']:
				self.modlist.append('raw')
			elif opt in ['-s', '--swap']:
				self.modlist.append('swap')
			elif opt in ['-S']:
				self.swaplist = arg.split(',')
			elif opt in ['--tcp']:
				self.modlist.append('tcp')
			elif opt in ['-t', '--time']:
				self.modlist.append('time')
			elif opt in ['--udp']:
				self.modlist.append('udp')
			elif opt in ['--unix']:
				self.modlist.append('unix')
			elif opt in ['-y', '--sys']:
				self.modlist.append('sys')

			elif opt in ['-a', '--all']:
				self.modlist = self.modlist + [ 'cpu', 'disk', 'net', 'page', 'sys' ]
			elif opt in ['-v', '--vmstat']:
				self.modlist = self.modlist + [ 'proc', 'mem', 'page', 'disk', 'sys', 'cpu' ]
			elif opt in ['-f', '--full']:
				self.full = True

			elif opt in ['--integer']:
				self.integer = True
			elif opt in ['--nocolor']:
				self.color = False
				self.update = False
			elif opt in ['--noheaders']:
				self.header = False
			elif opt in ['--noupdate']:
				self.update = False
			elif opt in ['-o', '--output']:
				self.output = arg
			elif opt in ['-h', '--help']:
				self.usage()
				self.help()
				exit(0)
			elif opt in ['-V', '--version']:
				self.version()
				exit(0)

		if not self.modlist:
			self.modlist = [ 'cpu', 'disk', 'net', 'page', 'sys' ]

		try:
			if len(args) > 0: self.delay = int(args[0])
			if len(args) > 1: self.count = int(args[1])
		except:
			print 'mtstat: incorrect argument, try mtstat -h for the correct syntax'
			exit(1)

		if self.delay <= 0:
			print 'mtstat: delay must be an integer, greater than zero'
			exit(1)

	def version(self):
		print 'mtstat %s' % VERSION
		print 'Written by Dag Wieers <dag@wieers.com>'
		print 'Homepage at http://dag.wieers.com/home-made/mtstat/'
		print
		print 'Platform %s/%s' % (os.name, sys.platform)
		print 'Kernel %s' % os.uname()[2]
		print 'Python %s' % sys.version
		print
		rows, cols = gettermsize()
		print 'Terminal size: %d lines, %d columns' % (rows, cols)
		print
		print 'Processors: %d' % getcpunr()
		print 'Pagesize: %d' % resource.getpagesize()
#		print 'Clock ticks per secs: %d' % os.sysconf('SC_CLK_TCK')
		print

		global op
		op = self
		listmodules()

	def usage(self):
		print 'Usage: mtstat [-afv] [options..] [delay [count]]'

	def help(self):
		print '''Versatile tool for generating system resource statistics

mtstat options:
  -c, --cpu              enable cpu stats
     -C 0,3,total           include cpu0, cpu3 and total
  -d, --disk             enable disk stats
     -D total,hda           include hda and total
  -g, --page             enable page stats
  -i, --int              enable interrupt stats
     -I 5,eth2              include int5 and interrupt used by eth2
  -l, --load             enable load stats
  -m, --mem              enable memory stats
  -n, --net              enable network stats
     -N eth1,total          include eth1 and total
  -p, --proc             enable process stats
  -s, --swap             enable swap stats
     -S swap1,total         include swap1 and total
  -t, --time             enable time counter
  -y, --sys              enable system stats
  --ipc                  enable ipc stats
  --lock                 enable lock stats
  --raw                  enable raw stats
  --tcp                  enable tcp stats
  --udp                  enable udp stats
  --unix                 enable unix stats

  -M stat1,stat2         enable external stats
     --mods stat1,stat2

  -a, --all              equals -cdngy (default)
  -f, --full             expand -C, -D, -I, -N and -S discovery lists
  -v, --vmstat           equals -pmgdsc -D total

  --integer              show integer values
  --nocolor              disable colors (implies --noupdate)
  --noheaders            disable repetitive headers
  --noupdate             disable intermediate updates
  --output file          write CSV output to file

  delay is the delay in seconds between each update
  count is the number of updates to display before exiting
  The default delay is 1 and count is unspecified (unlimited)
'''

### START STATS DEFINITIONS ###
class mtstat:
	### Initialise default variables
	def init(self, vars=(), len=0):
		if vars:
			self.val = {}; self.cn1 = {}; self.cn2 = {}
			for name in vars:
				if len <= 1:
					self.val[name] = self.cn1[name] = self.cn2[name] = 0
				else:
					self.val[name] = self.cn1[name] = self.cn2[name] = range(len)
					for i in range(len):
						self.val[name][i] = self.cn1[name][i] = self.cn2[name][i] = 0

	def open(self, file):
		"Open stat file descriptor"
		self.file = file
		self.fd = dopen(file)

	def statwidth(self):
		"Return complete stat width"
		return len(self.vars) * self.width() + len(self.vars) - 1

	def width(self):
		"Return column width"
		if isinstance(self.name, types.StringType):
			return self.format[1]
		else:
			for name in self.cn2.keys():
				return len(self.cn2[name]) * self.format[1] + len(self.cn2[name]) - 1
			return 0

	def title(self, nr):
		if nr == 1:
			return self.title1()
		else:
			return self.title2()

	def title1(self):
		if isinstance(self.name, types.StringType):
			max = self.statwidth()
			return ansi['darkblue'] + self.name[0:max].center(max).replace(' ', '-') + ansi['default']
		ret = ''
		for i, name in enumerate(self.name):
			max = self.width()
			ret = ret + name[0:max].center(max).replace(' ', '-')
			if i + 1 != len(self.name): ret = ret + ansi['blue'] + char['dash'] + ansi['darkblue']
		return ansi['darkblue'] + ret

	def title2(self):
		if isinstance(self.name, types.StringType):
			ret = ''
			for i, nick in enumerate(self.nick):
				ret = ret + nick.center(self.format[1]).replace(' ', '_')
				if i + 1 != len(self.nick): ret = ret + char['space']
			return ansi['blue'] + ret
		else:
			ret = ''
			for i, name in enumerate(self.name):
				for j, nick in enumerate(self.nick):
					ret = ret + ansi['blue'] + nick.center(self.format[1]).replace(' ', '_')
					if j + 1 != len(self.nick): ret = ret + char['space']
				if i + 1 != len(self.name): ret = ret + ansi['gray'] + char['colon']
			return ansi['blue'] + ret

	def titlecsv(self, nr):
		if nr == 1:
			return self.titlecsv1()
		else:
			return self.titlecsv2()

	def titlecsv1(self):
		if isinstance(self.name, types.StringType):
			return '"' + self.name + '"' + ',' * (len(self.nick) - 1)
		else:
			ret = ''
			for i, name in enumerate(self.name):
				ret = ret + '"' + name + '"' + ',' * (len(self.nick) - 1)
				if i + 1 != len(self.name): ret = ret + ','
			return ret

	def titlecsv2(self):
		if isinstance(self.name, types.StringType):
			ret = ''
			for i, nick in enumerate(self.nick):
				ret = ret + '"' + nick + '"'
				if i + 1 != len(self.nick): ret = ret + ','
			return ret
		else:
			ret = ''
			for i, name in enumerate(self.name):
				for j, nick in enumerate(self.nick):
					ret = ret + '"' + nick + '"'
					if j + 1 != len(self.nick): ret = ret + ','
				if i + 1 != len(self.name): ret = ret + ','
			return ret

	def check(self):
		"Check if stat is applicable"
		if hasattr(self, 'fd') and not self.fd:
			raise Exception, 'File %s does not exist' % self.file
		if not self.vars:
			raise Exception, 'No objects found, no stats available, module disabled'
		if self.discover and self.width():
			return True
		raise Exception, 'Unknown problem, please report'

	def discover(self):
		return True

	def show(self):
		"Display stat results"
		line = ''
		for i, name in enumerate(self.vars):
			if isinstance(self.val[name], types.TupleType) or isinstance(self.val[name], types.ListType):
				line = line + cprintlist(self.val[name], self.format)
				sep = ansi['gray'] + char['colon']
			else:
				line = line + cprint(self.val[name], self.format)
				sep = char['space']
			if i + 1 != len(self.vars):
				line = line + sep
		return line

	def showend(self, totlist, vislist):
		if self is not vislist[-1]:
			return ansi['gray'] + char['pipe']
		elif totlist != vislist:
			return ansi['gray'] + char['gt']
		return ''

	def showcsv(self):
		def printcsv(var):
			if var != round(var):
				return '%.3f' % var
			return '%s' % round(var)

		line = ''
		for i, name in enumerate(self.vars):
			if isinstance(self.val[name], types.ListType) or isinstance(self.val[name], types.TupleType):
				for j, val in enumerate(self.val[name]):
					line = line + printcsv(val)
					if j + 1 != len(self.val[name]):
						line = line + ','
			else:
				line = line + printcsv(self.val[name])
			if i + 1 != len(self.vars):
				line = line + ','
		return line

	def showcsvend(self, totlist, vislist):
		if self is not vislist[-1]:
			return ','
		elif self is not totlist[-1]:
			return ','
		return ''

class mtstat_cpu(mtstat):
	def __init__(self):
		self.format = ('p', 3, 34)
		self.open('/proc/stat')
		self.nick = ( 'usr', 'sys', 'idl', 'wai', 'hiq', 'siq' )
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = self.name()
		self.init(self.vars + ['total',], 6)

	def name(self):
		ret = []
		for name in self.vars:
			if name == 'total':
				ret.append('total cpu usage')
			else:
				ret.append('cpu' + name + ' usage')
		return ret

	def discover(self, *list):
		ret = []
		if self.fd:
			self.fd.seek(0)
			for line in self.fd.readlines():
				l = line.split()
				if len(l) < 8 or l[0][0:3] != 'cpu': continue
				ret.append(l[0][3:])
			ret.sort()
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.cpulist:
			list = op.cpulist
		elif not op.full:
			list = ('total', )
		else:
			list = []
			cpu = 0
			while cpu < cpunr:
				list.append(str(cpu))
				cpu = cpu + 1
#			if len(list) > 2: list = list[0:2]
		for name in list:
			if name in self.discover + ['total']:
				ret.append(name)
		return ret

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 8: continue
			for name in self.vars:
				if l[0] == 'cpu' + name or ( l[0] == 'cpu' and name == 'total' ):
					self.cn2[name] = ( long(l[1]) + long(l[2]), long(l[3]), long(l[4]), long(l[5]), long(l[6]), long(l[7]) )
		for name in self.vars:
			for i in range(6):
				self.val[name][i] = 100.0 * (self.cn2[name][i] - self.cn1[name][i]) / (sum(self.cn2[name]) - sum(self.cn1[name]))
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_cpu24(mtstat):
	def __init__(self):
		self.format = ('p', 3, 34)
		self.open('/proc/stat')
		self.nick = ( 'usr', 'sys', 'idl')
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = self.name()
		self.init(self.vars + ['total',], 3)

	def name(self):
		ret = []
		for name in self.vars:
			if name:
				ret.append('cpu' + name)
			else:
				ret.append('cpu total')
		return ret

	def discover(self, *list):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) != 5 or l[0][0:3] != 'cpu': continue
			ret.append(l[0][3:])
		ret.sort()
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.cpulist:
			list = op.cpulist
		elif not op.full:
			list = ('total', )
		else:
			list = []
			cpu = 0
			while cpu < cpunr:
				list.append(str(cpu))
				cpu = cpu + 1
#			if len(list) > 2: list = list[0:2]
		for name in list:
			if name in self.discover + ['total']:
				ret.append(name)
		return ret

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			for name in self.vars:
				if l[0] == 'cpu' + name or ( l[0] == 'cpu' and name == 'total' ):
					self.cn2[name] = ( long(l[1]) + long(l[2]), long(l[3]), long(l[4]) )
		for name in self.vars:
			for i in range(3):
				self.val[name][i] = 100.0 * (self.cn2[name][i] - self.cn1[name][i]) / (sum(self.cn2[name]) - sum(self.cn1[name]))
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_disk(mtstat):
	def __init__(self):
		self.format = ('f', 5, 1024)
		self.open('/proc/diskstats')
		self.nick = ('read', 'writ')
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = ['dsk/'+name for name in self.vars]
		self.init(self.vars + ['total',], 2)

	def discover(self, *list):
		ret = []
		if self.fd:
			self.fd.seek(0)
			for line in self.fd.readlines():
				l = line.split()
				if len(l) < 13: continue
				if l[3:] == ['0',] * 11: continue
				name = l[2]
				ret.append(name)
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.disklist:
			list = op.disklist
		elif not op.full:
			list = ('total', )
		else:
			list = self.discover
#			if len(list) > 2: list = list[0:2]
			list.sort()
		for name in list:
			if name in self.discover + ['total'] + op.diskset.keys():
				ret.append(name)
		return ret

	def extract(self):
		for name in self.vars: self.cn2[name] = (0, 0)
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 13: continue
			if l[5] == '0' and l[9] == '0': continue
			name = l[2]
			if l[3:] == ['0',] * 11: continue
			if not re.match('(md[0-9]+|dm-[0-9]+)', name):
				self.cn2['total'] = ( self.cn2['total'][0] + long(l[5]), self.cn2['total'][1] + long(l[9]) )
			if name in self.vars and name != 'total':
				self.cn2[name] = ( self.cn2[name][0] + long(l[5]), self.cn2[name][1] + long(l[9]) )
			for set in self.vars:
				if set in op.diskset.keys():
					for disk in op.diskset[set]:
						if re.match('^'+disk+'$', name):
							self.cn2[set] = ( self.cn2[set][0] + long(l[5]), self.cn2[set][1] + long(l[9]) )
		for name in self.cn2.keys():
			self.val[name] = ( 
				(self.cn2[name][0] - self.cn1[name][0]) * 512.0 / tick,
				(self.cn2[name][1] - self.cn1[name][1]) * 512.0 / tick,
			)
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_disk24(mtstat):
	def __init__(self):
		self.format = ('f', 5, 1024)
		self.open('/proc/partitions')
		self.nick = ('read', 'writ')
		self.discover = self.discover()
		self.vars = self.vars()
		if self.fd and not self.discover:
			raise Exception, 'kernel is not compiled with CONFIG_BLK_STATS'
		self.name = ['dsk/'+sysfs_dev(name) for name in self.vars]
		self.init(self.vars + ['total',], 2)

	def discover(self, *list):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 15 or l[0] == 'major' or int(l[1]) % 16 != 0: continue
			name = l[3]
			ret.append(name)	
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.disklist:
			list = op.disklist
		elif not op.full:
			list = ('total', )
		else:
			list = self.discover
#			if len(list) > 2: list = list[0:2]
			list.sort()
		for name in list:
			if name in self.discover + ['total'] + op.diskset.keys():
				ret.append(name)
		return ret

	def extract(self):
		for name in self.vars: self.cn2[name] = (0, 0)
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 15 or l[0] == 'major' or int(l[1]) % 16 != 0: continue
			name = l[3]
			if not re.match('(md[0-9]+|dm-[0-9]+)', name):
				self.cn2['total'] = ( self.cn2['total'][0] + long(l[6]), self.cn2['total'][1] + long(l[10]) )
			if name in self.vars:
				self.cn2[name] = ( self.cn2[name][0] + long(l[6]), self.cn2[name][1] + long(l[10]) )
			for set in self.vars:
				if set in op.diskset.keys():
					for disk in op.diskset[set]:
						if re.match('^'+disk+'$', name):
							self.cn2[set] = ( self.cn2[set][0] + long(l[6]), self.cn2[set][1] + long(l[10]) )
		for name in self.cn2.keys():
			self.val[name] = ( 
				(self.cn2[name][0] - self.cn1[name][0]) * 512.0 / tick,
				(self.cn2[name][1] - self.cn1[name][1]) * 512.0 / tick,
			)
		if step == op.delay:
			self.cn1.update(self.cn2)

### FIXME: Needs rework, does anyone care ?
class mtstat_disk24old(mtstat):
	def __init__(self):
		self.format = ('f', 5, 1024)
		self.open('/proc/stat')
		self.nick = ('read', 'writ')
		self.regexp = re.compile('^\((\d+),(\d+)\):\(\d+,\d+,(\d+),\d+,(\d+)\)$')
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = ['dsk/'+name for name in self.vars]
		self.init(self.vars + ['total',], 2)

	def discover(self, *list):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split(':')
			if len(l) < 3: continue
			name = l[0]
			if name != 'disk_io': continue
			for pair in line.split()[1:]:
				m = self.regexp.match(pair)
				if not m: continue
				l = m.groups()
				if len(l) < 4: continue
				name = dev(int(l[0]), int(l[1]))
				ret.append(name)
			break
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.disklist:
			list = op.disklist
		elif not op.full:
			list = ('total', )
		else:
			list = self.discover
#			if len(list) > 2: list = list[0:2]
			list.sort()
		for name in list:
			if name in self.discover + ['total'] + op.diskset.keys():
				ret.append(name)
		return ret

	def extract(self):
		for name in self.vars: self.cn2[name] = (0, 0)
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split(':')
			if len(l) < 3: continue
			name = l[0]
			if name != 'disk_io': continue
			for pair in line.split()[1:]:
				m = self.regexp.match(pair)
				if not m: continue
				l = m.groups()
				if len(l) < 4: continue
				name = dev(int(l[0]), int(l[1]))
				if not re.match('(md[0-9]+)', name):
					self.cn2['total'] = ( self.cn2['total'][0] + long(l[2]), self.cn2['total'][1] + long(l[3]) )
				if name in self.vars and name != 'total':
					self.cn2[name] = ( self.cn2[name][0] + long(l[2]), self.cn2[name][1] + long(l[3]) )
				for set in self.vars:
					if set in op.diskset.keys():
						for disk in op.diskset[set]:
							if re.match('^'+disk+'$', name):
								self.cn2[set] = ( self.cn2[set][0] + long(l[2]), self.cn2[set][1] + long(l[3]) )
			break
		for name in self.cn2.keys():
			self.val[name] = (
				(self.cn2[name][0] - self.cn1[name][0]) * 512.0 / tick,
				(self.cn2[name][1] - self.cn1[name][1]) * 512.0 / tick,
			)
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_int(mtstat):
	def __init__(self):
		self.name = 'interrupts'
		self.format = ('d', 5, 1000)
		self.open('/proc/stat')
		self.discover = self.discover()
		self.intmap = self.intmap()
		self.vars = self.vars()
		self.nick = self.vars
		self.init(self.vars, 1)

	def intmap(self):
		ret = {}
		for line in dopen('/proc/interrupts').readlines():
			l = line.split()
			if len(l) <= cpunr: continue
			l1 = l[0].split(':')[0]
			l2 = ' '.join(l[cpunr+2:]).split(',')
			ret[l1] = l1
			for name in l2:
				ret[name.strip().lower()] = l1
		return ret

	def discover(self):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if l[0] != 'intr': continue
			for name, i in enumerate(l[2:]):
				if long(i) > 10: ret.append(str(name))
		return ret

#	def check(self):
#		if self.fd and self.vars:
#			self.fd.seek(0)
#			for line in self.fd.readlines():
#				l = line.split()
#				if l[0] != 'intr': continue
#				return True
#		return False

	def vars(self):
		ret = []
		if op.intlist:
			list = op.intlist
		else:
			list = self.discover
			for name in list:
				if name in ('0', '1', '2', '8', 'NMI', 'LOC', 'MIS', 'CPU0'):
					list.remove(name)
			if not op.full and len(list) > 3: list = list[-3:]
		for name in list:
			if name in self.discover:
				ret.append(name)
			elif name.lower() in self.intmap.keys():
				ret.append(self.intmap[name.lower()])
		return ret

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if not l or l[0] != 'intr': continue
			for name in self.vars:
				self.cn2[name] = long(l[int(name) + 2])
		for name in self.vars:
			self.val[name] = (self.cn2[name] - self.cn1[name]) * 1.0 / tick
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_int24(mtstat):
	def __init__(self):
		self.name = 'interrupts'
		self.format = ('d', 5, 1000)
		self.open('/proc/interrupts')
		self.discover = self.discover()
		self.vars = self.vars()
		self.nick = self.vars
		self.init(self.vars, 1)

	def intmap(self):
		ret = {}
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) <= cpunr: continue
			l1 = l[0].split(':')[0]
			l2 = ' '.join(l[cpunr+2:]).split(',')
			ret[l1] = l1
			for name in l2:
				ret[name.strip().lower()] = l1
		return ret

	def discover(self):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < cpunr+1: continue
			name = l[0].split(':')[0]
			if long(l[1]) > 10:
				ret.append(name)
		return ret

#	def check(self):
#		if self.fd and self.discover:
#			self.fd.seek(0)
#			for line in self.fd.readlines():
#				l = line.split()
#				if l[0] != 'intr' or len(l) > 2: continue
#				return True
#		return False

	def vars(self):
		ret = []
		if op.intlist:
			list = op.intlist
		else:
			list = self.discover
			for name in list:
				if name in ('0', '1', '2', '8', 'CPU0', 'ERR', 'LOC', 'MIS', 'NMI'):
					list.remove(name)
			if not op.full and len(list) > 3: list = list[-3:]
		for name in list:
			if name in self.discover:
				ret.append(name)
			elif name.lower() in self.intmap.keys():
				ret.append(self.intmap[name.lower()])
		return ret

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < cpunr+1: continue
			name = l[0].split(':')[0]
			if name in self.vars:
				self.cn2[name] = 0
				for i in l[1:1+cpunr]:
					self.cn2[name] = self.cn2[name] + long(i)
#			elif len(l) > 2 + cpunr:
#				for hw in self.vars:
#					for mod in l[2+cpunr:]:
#						self.cn2[mod] = long(l[1])
		for name in self.cn2.keys():
			self.val[name] = (self.cn2[name] - self.cn1[name]) * 1.0 / tick
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_ipc(mtstat):
	def __init__(self):
		self.name = 'sysv ipc'
		self.format = ('d', 3, 10)
		self.vars = ('msg', 'sem', 'shm')
		self.nick = self.vars
		self.init(self.vars, 1)

	def extract(self):
		for name in self.vars:
			self.val[name] = len(dopen('/proc/sysvipc/'+name).readlines()) - 1

class mtstat_load(mtstat):
	def __init__(self):
		self.name = 'load avg'
		self.format = ('f', 4, 10)
		self.open('/proc/loadavg')
		self.nick = ('1m', '5m', '15m')
		self.vars = ('load1', 'load5', 'load15')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 3: continue
			self.val['load1'] = float(l[0])
			self.val['load5'] = float(l[1])
			self.val['load15'] = float(l[2])

class mtstat_lock(mtstat):
	def __init__(self):
		self.name = 'file locks'
		self.format = ('f', 3, 10)
		self.open('/proc/locks')
		self.nick = ('pos', 'lck', 'rea', 'wri')
		self.vars = ('posix', 'flock', 'read', 'write')
		self.init(self.vars, 1)

	def extract(self):
		for name in self.vars: self.val[name] = 0
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 4: continue
			if l[1] == 'POSIX':
				self.val['posix'] = self.val['posix'] + 1
			elif l[1] == 'FLOCK':
				self.val['flock'] = self.val['flock'] + 1
			if l[3] == 'READ':
				self.val['read'] = self.val['read'] + 1
			elif l[3] == 'WRITE':
				self.val['write'] = self.val['write'] + 1

class mtstat_mem(mtstat):
	def __init__(self):
		self.name = 'memory usage'
		self.format = ('f', 5, 1024)
		self.open('/proc/meminfo')
		self.nick = ('used', 'buff', 'cach', 'free')
		self.vars = ('MemUsed', 'Buffers', 'Cached', 'MemFree')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 2: continue
			name = l[0].split(':')[0]
			if name in self.vars + ('MemTotal', 'SwapCached'):
				self.val[name] = long(l[1]) * 1024.0
		self.val['Cached'] = self.val['Cached'] + self.val['SwapCached']
		self.val['MemUsed'] = self.val['MemTotal'] - self.val['MemFree'] - self.val['Buffers'] - self.val['Cached']

class mtstat_net(mtstat):
	def __init__(self):
		self.format = ('f', 5, 1024)
		self.open('/proc/net/dev')
		self.nick = ('recv', 'send')
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = ['net/'+name for name in self.vars]
		self.init(self.vars + ['total',], 2)

	def discover(self, *list):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.replace(':', ' ').split()
			if len(l) < 17: continue
			if l[2] == '0' and l[10] == '0': continue
			name = l[0]
			if name not in ('lo', 'face'):
				ret.append(name)
		ret.sort()
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.netlist:
			list = op.netlist
		elif not op.full:
			list = ('total', )
		else:
			list = self.discover
#			if len(list) > 2: list = list[0:2]
			list.sort()
		for name in list:
			if name in self.discover + ['total', 'lo']:
				ret.append(name)
		return ret

	def extract(self):
		self.cn2['total'] = [0, 0]
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.replace(':', ' ').split()
			if len(l) < 17: continue
			if l[2] == '0' and l[10] == '0': continue
			name = l[0]
			if name in self.vars :
				self.cn2[name] = ( long(l[1]), long(l[9]) )
			if name not in ('lo','face'):
				self.cn2['total'] = ( self.cn2['total'][0] + long(l[1]), self.cn2['total'][1] + long(l[9]))
		if update:
			for name in self.cn2.keys():
				self.val[name] = ( 
					(self.cn2[name][0] - self.cn1[name][0]) * 1.0 / tick,
					(self.cn2[name][1] - self.cn1[name][1]) * 1.0 / tick,
				 )
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_page(mtstat):
	def __init__(self):
		self.name = 'paging'
		self.format = ('f', 5, 1024)
		self.open('/proc/vmstat')
		self.nick = ('in', 'out')
		self.vars = ('pswpin', 'pswpout')
		self.init(self.vars, 1)

	def extract(self):

		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 2: continue
			name = l[0]
			if name in self.vars:
				self.cn2[name] = long(l[1])
		for name in self.vars:
			self.val[name] = (self.cn2[name] - self.cn1[name]) * pagesize * 1.0 / tick
		if step == self.op.delay:
			self.cn1.update(self.cn2)

class mtstat_page24(mtstat):
	def __init__(self):
		self.name = 'paging'
		self.format = ('f', 5, 1024)
		self.open('/proc/stat')
		self.nick = ('in', 'out')
		self.vars = ('pswpin', 'pswpout')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 3: continue
			name = l[0]
			if name != 'swap': continue
			self.cn2['pswpin'] = long(l[1])
			self.cn2['pswpout'] = long(l[2])
			break
		for name in self.vars:
			self.val[name] = (self.cn2[name] - self.cn1[name]) * pagesize * 1.0 / tick
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_proc(mtstat):
	def __init__(self):
		self.name = 'procs'
		self.format = ('f', 3, 10)
		self.open('/proc/stat')
		self.nick = ('run', 'blk', 'new')
		self.vars = ('procs_running', 'procs_blocked', 'processes')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 2: continue
			name = l[0]
			if name == 'processes':
				self.val['processes'] = 0
				self.cn2[name] = long(l[1])
			elif name == 'procs_running':
				self.cn2[name] = self.cn2[name] + long(l[1]) - 1
			elif name == 'procs_blocked':
				self.cn2[name] = self.cn2[name] + long(l[1])
		self.val['processes'] = (self.cn2['processes'] - self.cn1['processes']) * 1.0 / tick
		for name in ('procs_running', 'procs_blocked'):
			self.val[name] = self.cn2[name] * 1.0 / tick
		if step == op.delay:
			self.cn1.update(self.cn2)
			for name in ('procs_running', 'procs_blocked'):
				self.cn2[name] = 0

class mtstat_raw(mtstat):
	def __init__(self):
		self.name = 'raw'
		self.format = ('f', 3, 10)
		self.open('/proc/net/raw')
		self.nick = ('soc',)
		self.vars = ('sockets',)
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		self.val['sockets'] = len(self.fd.readlines()) - 1

class mtstat_swap(mtstat):
	def __init__(self):
		self.name = 'swap'
		self.format = ('f', 5, 1024)
		self.open('/proc/swaps')
		self.nick = ('used', 'free')
		self.discover = self.discover()
		self.vars = self.vars()
		self.name = ['swp/'+improve(name) for name in self.vars]
		self.init(self.vars + ['total',], 2)

	def discover(self, *list):
		ret = []
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 5: continue
			if l[0] == 'Filename': continue
#			ret.append(improve(l[0]))
			ret.append(l[0])
		ret.sort()
		for item in list: ret.append(item)
		return ret

	def vars(self):
		ret = []
		if op.swaplist:
			list = op.swaplist
		elif not op.full:
			list = ('total', )
		else:
			list = self.discover
#			if len(list) > 2: list = list[0:2]
		list.sort()
		for name in list:
			if name in self.discover + ['total']:
				ret.append(name)
		return ret

	def extract(self):
		self.val['total'] = [0, 0]
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 5 or l[0] == 'Filename': continue
			name = l[0]
			self.val[name] = ( long(l[3]) * 1024.0, (long(l[2]) - long(l[3])) * 1024.0 )
			self.val['total'] = ( self.val['total'][0] + self.val[name][0], self.val['total'][1] + self.val[name][1])

class mtstat_swapold(mtstat):
	def __init__(self):
		self.name = 'swap'
		self.format = ('f', 5, 1024)
		self.open('/proc/meminfo')
		self.nick = ('used', 'free')
		self.vars = ('SwapUsed', 'SwapFree')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 2: continue
			name = l[0].split(':')[0]
			if name in self.vars + ('SwapTotal',):
				self.val[name] = long(l[1]) * 1024.0
		self.val['SwapUsed'] = self.val['SwapTotal'] - self.val['SwapFree']

class mtstat_sys(mtstat):
	def __init__(self):
		self.name = 'system'
		self.format = ('d', 5, 1000)
		self.open('/proc/stat')
		self.nick = ('int', 'csw')
		self.vars = ('intr', 'ctxt')
		self.init(self.vars, 1)

	def extract(self):
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 2: continue
			name = l[0]
			if name in self.vars:
				self.cn2[name] = long(l[1])
		for name in self.vars:
			self.val[name] = (self.cn2[name] - self.cn1[name]) * 1.0 / tick
		if step == op.delay:
			self.cn1.update(self.cn2)

class mtstat_tcp(mtstat):
	def __init__(self):
		self.name = 'tcp sockets'
		self.format = ('f', 3, 100)
		self.open('/proc/net/tcp')
		self.nick = ('lis', 'act', 'syn', 'tim')
		self.vars = ('listen', 'established', 'syn_sent', 'time_wait')
		self.init(self.vars, 1)

	def extract(self):
		for name in self.vars: self.val[name] = 0
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if len(l) < 12: continue
			if l[3] == '0A': self.val['listen'] = self.val['listen'] + 1
			elif l[3] == '01': self.val['established'] = self.val['established'] + 1
			elif l[3] == '02': self.val['syn_sent'] = self.val['syn_sent'] + 1
			elif l[3] == '06': self.val['time_wait'] = self.val['time_wait'] + 1

class mtstat_time(mtstat):
	def __init__(self):
		self.name = 'time'
		self.format = ('t', 10, 0)
		if op.debug:
			self.format = ('t', 14, 0)
		self.nick = ('epoch',)
		self.vars = self.nick
		self.init(self.vars, 1)

	def extract(self):
		self.val['epoch'] = time.time()

#	def show(self):
#		return ansi['reset'] + ( '%10.2f' % self.val['epoch'] )

class mtstat_udp(mtstat):
	def __init__(self):
		self.name = 'udp'
		self.format = ('f', 3, 100)
		self.open('/proc/net/udp')
		self.nick = ('lis', 'act')
		self.vars = ('listen', 'established')
		self.init(self.vars, 1)

	def extract(self):
		for name in self.vars: self.val[name] = 0
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if l[3] == '07': self.val['listen'] = self.val['listen'] + 1
			elif l[3] == '01': self.val['established'] = self.val['established'] + 1

class mtstat_unix(mtstat):
	def __init__(self):
		self.name = 'unix sockets'
		self.format = ('d', 4, 100)
		self.open('/proc/net/unix')
		self.nick = ('dgrm', 'strm', 'lis', 'act')
		self.vars = ('datagram', 'stream', 'listen', 'established')
		self.init(self.vars, 1)

	def extract(self):
		for name in self.vars: self.val[name] = 0
		self.fd.seek(0)
		for line in self.fd.readlines():
			l = line.split()
			if l[4] == '0002':
				self.val['datagram'] = self.val['datagram'] + 1
			elif l[4] == '0001':
				self.val['stream'] = self.val['stream'] + 1
				if l[5] == '01':
					self.val['listen'] = self.val['listen'] + 1
				elif l[5] == '03':
					self.val['established'] = self.val['established'] + 1

### END STATS DEFINITIONS ###

ansi = {
	'black': '\033[0;30m',
	'darkred': '\033[0;31m',
	'darkgreen': '\033[0;32m',
	'darkyellow': '\033[0;33m',
	'darkblue': '\033[0;34m',
	'darkmagenta': '\033[0;35m',
	'darkcyan': '\033[0;36m',
	'silver': '\033[0;37m',

	'gray': '\033[1;30m',
	'red': '\033[1;31m',
	'green': '\033[1;32m',
	'yellow': '\033[1;33m',
	'blue': '\033[1;34m',
	'magenta': '\033[1;35m',
	'cyan': '\033[1;36m',
	'white': '\033[1;37m',

	'blackbg': '\033[40m',
	'redbg': '\033[41m',
	'greenbg': '\033[42m',
	'yellowbg': '\033[43m',
	'bluebg': '\033[44m',
	'magentabg': '\033[45m',
	'cyanbg': '\033[46m',
	'whitebg': '\033[47m',

	'reset': '\033[0;0m',
	'bold': '\033[1m',
	'reverse': '\033[2m',
	'underline': '\033[4m',

	'clear': '\033[2J',
#	'clearline': '\033[K',
	'clearline': '\033[2K',
#	'save': '\033[s',
#	'restore': '\033[u',
	'save': '\0337',
	'restore': '\0338',

	'up': '\033[1A',
	'down': '\033[1B',
	'right': '\033[1C',
	'left': '\033[1D',

	'default': '\033[0;0m',
}

char = {
	'pipe': '|',
	'colon': ':',
	'gt': '>',
	'space': ' ',
	'dash': '-',
}

def ticks():
	"Return the number of 'ticks' since bootup"
	try:
		for line in open('/proc/uptime', 'r', 0).readlines():
			l = line.split()
			if len(l) < 2: continue
			return float(l[0])
	except:
		for line in dopen('/proc/stat').readlines():
			l = line.split()
			if len(l) < 2: continue
			if l[0] == 'btime':
				return time.time() - long(l[1])

def improve(str):
	"Improve a device name"
	if str.startswith('/dev/mapper/'):
		str = str.split('/')[3]
	elif str.startswith('/dev/'):
		str = str.split('/')[2]
	return str

def dopen(file):
	"Open a file for reuse, if already opened, return file descriptor"
	global fds
	if not os.path.exists(file): return None
	if 'fds' not in globals().keys(): fds = {}
	if file not in fds.keys():
		fds[file] = open(file, 'r', 0)
	else:
		fds[file].seek(0)
	return fds[file]

def dclose(file):
	"Close an open file and remove file descriptor from list"
	global fds
	if not 'fds' in globals(): fds = {}
	if file in fds:
		fds[file].close()
		del(fds[file])

def dpopen(cmd):
	"Open a pipe for reuse, if already opened, return pipes"
	global pipes
	if 'pipes' not in globals().keys(): pipes = {}
	if cmd not in pipes.keys():
		pipes[cmd] = os.popen3(cmd, 't', 0)
	return pipes[cmd]

def readpipe(file, tmout = 0.001):
	"Read available data from pipe in a non-blocking fashion"
	ret = ''
	while not select.select([file.fileno()], [], [], tmout)[0]:
		pass
	while select.select([file.fileno()], [], [], tmout)[0]:
		ret = ret + file.read(1)
	return ret.split('\n')
#	return ret

def dchg(var, max, base):
	"Convert decimal to string given base and length"
	c = 0
	while True:
		ret = str(long(round(var)))
		if len(ret) <= max:
			break
		var = var / base
		c = c + 1
	else:
		c = -1
	return ret, c

def fchg(var, max, base):
	"Convert float to string given base and length"
	c = 0
	while True:
		if var == 0:
			ret = str('0')
			break
#		ret = repr(round(var))
#		ret = repr(long(round(var,max)))
		ret = str(long(round(var,max)))
		if len(ret) <= max:
			i = max - len(ret)
			while i > 0:
				ret = ('%.'+str(i)+'f') % var
				if len(ret) < max and ret != repr(round(var)):
					break
				i = i - 1
			else:
				ret = str(long(round(var)))
			break
		var = var / base
		c = c + 1
	else:
		c = -1
	return ret, c

def cprintlist(list, format):
	ret = sep = ''
	for var in list:
		ret = ret + sep + cprint(var, format)
		sep = ' '
	return ret

def cprint(var, format = ('f', 4, 1000)):
	c = -1
	type = format[0]
	max = format[1]
	mp = format[2]

	base = 1000
	if mp == 1024:
		base = 1024

	unit = False
	if mp in (1000, 1024) and max >= len(str(base)):
		unit = True
		max = max - 1

	if var < 0:
		if unit:
			return ansi['default'] + '-'.rjust(max) + ' '
		else:
			return ansi['default'] + '-'.rjust(max)

	if base == 1024:
		units = ('B', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
	else:
		units = (' ', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')

	if step != op.delay:
		colors = ('darkred', 'darkyellow', 'darkgreen', 'darkblue', 'darkmagenta', 'darkcyan', 'silver', 'red', 'green')
	else:
		colors = ('red', 'yellow', 'green', 'blue', 'magenta', 'cyan', 'white', 'darkred', 'darkgreen')

	if op.integer and type in ('d', 'p', 'f'):
		ret, c = dchg(var, max, base)
	elif type in ('d', 'p'):
		ret, c = dchg(var, max, base)
	elif type in ('f'):
		ret, c = fchg(var, max, base)
	elif type in ('t'):
		ret, c = fchg(var, max+1, base)
	else:
		ret = str(var)

	if ret == '0':
		color = 'default'
	elif type in ('d', 'p'):
		color = colors[int(var/mp)%len(colors)]
	elif type in ('f'):
		color = colors[c%len(colors)]
	else:
		color = 'default'

	if type in ('s',):
		ret = ansi['default'] + ret.ljust(max)
	else:
		ret = ansi[color] + ret.rjust(max)

	if unit:
		if c != -1 and round(var) != 0:
			ret = ret + units[c]
		else:
			ret = ret + ' '

	return ret

def showtitle(nr, totlist, vislist, midchar, endchar):
	line = ''
	for o in vislist:
		line = line + o.title(nr)
		if o is not vislist[-1]:
			line = line + midchar
		elif totlist != vislist:
			line = line + endchar
	sys.stdout.write(line + '\n')

def showcsvtitle(nr, totlist):
	line = ''
	for o in totlist:
		line = line + o.titlecsv(nr)
		if o is not totlist[-1]:
			line = line + ','
	outputfile.write(line + '\n')

def info(level, str):
	"Output info message"
#	if level <= op.verbose:
	print str

def die(ret, str):
	"Print error and exit with errorcode"
	info(0, str)
	exit(ret)

def initterm():
	"Initialise terminal"
	global termsize

	termsize = None, None

	### Unbuffered sys.stdout
	sys.stdout = os.fdopen(1, 'w', 0)

	try:
		global fcntl, struct, termios
		import fcntl, struct, termios
		termios.TIOCGWINSZ
	except:
		try:
			curses.setupterm()
			curses.tigetnum('lines'), curses.tigetnum('cols')
		except:
			pass
		else:
			termsize = None, 2
	else:
		termsize = None, 1

def gettermsize():
	"Return the dynamic terminal geometry"
	global termsize

	if not termsize[0]:
		try:
			if termsize[1] == 1:
				s = struct.pack('HHHH', 0, 0, 0, 0)
				x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
				return struct.unpack('HHHH', x)[:2]
			elif termsize[1] == 2:
				curses.setupterm()
				return curses.tigetnum('lines'), curses.tigetnum('cols')
			else:
				termsize = (int(os.environ['LINES']), int(os.environ['COLUMNS']))
		except:
			termsize = 25, 80
	return termsize

def getcpunr():
	"Return the number of CPUs in the system"
	cpunr = -1
	for line in dopen('/proc/stat').readlines():
		if line[0:3] == 'cpu':
			cpunr = cpunr + 1
	if cpunr < 0:
		raise "Problem finding number of CPUs in system."
	return cpunr

### FIXME: Add scsi support too and improve
def sysfs_dev(device):
	"Convert sysfs device names into device names"
	m = re.match('ide/host([0-9])/bus([0-9])/target([0-9])/lun([0-9])/disc', device)
	if m:
		l = m.groups()
		# ide/host0/bus0/target0/lun0/disc -> 0 -> hda
		# ide/host0/bus1/target0/lun0/disc -> 2 -> hdc
		nr = int(l[1]) * 2 + int(l[3])
		return 'hd' + chr(ord('a') + nr)
	m = re.match('placeholder', device)
	if m:
		return 'sdX'
	return device

def scsi_dev(nr):
	"Convert sequential number into scsi device names"
	if nr < 26:
		return 'sd' + chr(ord('a') + nr)
	else:
		return 'sd' + chr(ord('a') - 1 + nr / 26) + chr(ord('a') + nr % 26)

def dev(maj, min):
	"Convert major/minor pairs into device names"
	scsi = [8, 65, 66, 67, 68, 69, 70, 71, 128, 129, 130, 131, 132, 133, 134, 135]
	ide = [3, 22, 33, 34, 56, 57, 88, 89, 90, 91]
	if maj in scsi:
		nr = scsi.index(maj) * 16 + min
#		nr = scsi.index(maj) * 16 + min / 16
		return scsi_dev(nr)
	elif maj in ide:
		nr = ide.index(maj) * 2 + min / 64
		return 'hd' + chr(ord('a') + nr)

#def mountpoint(dev):
#	"Return the mountpoint of a mounted device/file"
#	for entry in dopen('/etc/mtab').readlines():
#		if entry:
#			list = entry.split()
#			if dev == list[0]:
#				return list[1]

def readfile(file):
	ret = ''
	for line in open(file,'r').readlines():
		ret = ret + line
	return ret

def signaler(signum, frame):
	signal.alarm(interval)

def exit(ret):
	sys.stdout.write(ansi['reset'])
	if 'signal' in sys.modules.keys():
		signal.signal(signal.SIGALRM, signal.SIG_DFL)
	sys.exit(ret)

def listmodules():
	import glob
	rows, cols = gettermsize()
	remod = re.compile('.+/mtstat_(.+).py$')
	for path in sys.path:
		list = []
		for file in glob.glob(path + '/mtstat_*.py'):
			list.append(remod.match(file).groups()[0])
		if not list: continue
		list.sort()
		cols2 = cols - 8
		print '%s:\n\t' % os.path.abspath(path),
		for mod in list:
			cols2 = cols2 - len(mod) - 2
			if cols2 <= 0:
				print '\n\t',
				cols2 = cols - len(mod) - 10
			print mod + ',',
		print

def main():
	global update, loop, step, pagesize, cpunr, ansi, interval, outputfile, tick, cols, op

	op = Options(sys.argv[1:])

	loop = update = 0
	step = op.delay
	tick = ticks()
	pagesize = resource.getpagesize()
	cpunr = getcpunr()
#	hz = os.sysconf('SC_CLK_TCK')
	interval = 1

	user = getpass.getuser()
	hostname = os.uname()[1].split('.')[0]

	rows, cols = gettermsize()

	### Write term-title
	term = os.getenv('TERM')
	if term and re.compile('(screen*|xterm*)').match(term):
		sys.stdout.write('\033]0;(%s@%s) %s %s\007' % (user, hostname, os.path.basename(sys.argv[0]), ' '.join(op.args)))

	### Check terminal capabilities
	if not sys.stdout.isatty():
		op.color = False
		op.nolimit = True
		op.update = False
	else:
		try:
			import curses
			curses.setupterm()
			if curses.tigetnum('colors') < 0:
				op.color = False
		except:
			op.color = False

	if op.output:
		if os.path.exists(op.output):
			outputfile = open(op.output, 'a', 0)
			outputfile.write('\n\n')
		else:
			outputfile = open(op.output, 'w', 0)
			outputfile.write('"mtstat %s CSV output"\n' % VERSION)
			outputfile.write('"Author:","Dag Wieers <dag@wieers.com>",,,,"URL:","http://dag.wieers.com/home-made/mtstat/"\n')

		outputfile.write('"Host:","%s",,,,"User:","%s"\n' % (hostname, user))
		outputfile.write('"Cmdline:","mtstat %s",,,,"Date:","%s"\n\n' % (' '.join(op.args), time.strftime('%d %b %Y %H:%M:%S %Z', time.localtime())))

	### Empty ansi database if no colors are requested
	if not op.color:
		op.update = False
		for key in ansi.keys():
			ansi[key] = ''

	if not op.update:
		interval = op.delay

	if 'list' in op.modlist or 'help' in op.modlist:
		listmodules()
		exit(0)

	### Build list of requested modules
	linewidth = 0
	oldvislist = []
	totlist = []

	
	for res in pkg_resources.iter_entry_points('mtstat.plugins'):

		if res.name in op.modlist:

			try:
				c=res.load()
			except Exception, e:
				info(1, 'Module %s failed to load. (%s)' % (res.name, e))
				#tb = sys.exc_info()[2]
				continue

			try:

				
				o = c()
				## This should be changed!!! Probably create
				## a container object that gets passed in to
				## the class creation
				o.op = op
				o.tick = tick
				o.ansi = ansi
				o.step = step

				### Remove defect stat objects and calculate line length
				if not o.check():
					raise Exception, 'Unknown problem, please report'

				linewidth = linewidth + o.statwidth() + 1
				totlist.append(o)
				#break

			except Exception, e:
				info(1, 'Module %s has problems. (%s)' % (res.name, e))
				if op.debug:
					raise
				continue

	if not totlist:
		die(8, 'None of the stats you selected are available.')

	if op.debug:
		for o in totlist:
			print 'Module', str(o.__class__).split('.')[1],
			if hasattr(o, 'file'): print 'requires', o.file,
			print

	if op.output:
		showcsvtitle(1, totlist)
		showcsvtitle(2, totlist)

	### Increase precision if we're root (does not seem to have effect)
#	if os.geteuid() == 0:
#		os.nice(-20)
#	sys.setcheckinterval(op.delay / 10000)

	### Always show header the first time
	showheader = True

	signal.signal(signal.SIGALRM, signaler)
	signal.alarm(interval)

	tt = 0

	### Let the games begin
	while update <= op.delay * op.count or op.count == -1:

		if op.debug:
			if step == 1: tt = 0
			t1 = time.time()
			curwidth = 8
		else:
			curwidth = 0

		### Trim object list to what is visible on screen
		rows, cols = gettermsize()
		vislist = []
		for o in totlist:
			newwidth = curwidth + o.statwidth() + 1
			if newwidth <= cols or ( vislist == totlist[:-1] and newwidth < cols ):
				vislist.append(o)
				curwidth = newwidth

		### Check when to display the header
		if op.header and rows >= 6:
			if oldvislist != vislist:
				showheader = True
			elif step == 1 and loop % (rows - 1) == 0:
				showheader = True

		oldvislist = vislist

		if showheader:
			if loop == 0 and totlist != vislist:
				info(1, 'Terminal width too small, trimming output.')
			showheader = False
			showtitle(1, totlist, vislist, ansi['darkblue'] + char['space'], ansi['darkblue'] + char['gt'])
			showtitle(2, totlist, vislist, ansi['gray'] + char['pipe'], ansi['darkblue'] + char['gt'])

		### Prepare the colors for intermediate updates, last step in a loop is definitive
		if step == op.delay:
			ansi['default'] = ansi['reset']
		else:
			ansi['default'] = ansi['gray']
		line = ansi['default']

		### Calculate all objects (visible, invisible)
		oline = ''
		for o in totlist:
			o.extract()
			if o in vislist:
				line = line + o.show() + o.showend(totlist, vislist)
			if op.output and step == op.delay:
				oline = oline + o.showcsv() + o.showcsvend(totlist, vislist)

		### Print stats
		sys.stdout.write(line + ansi['default'])
		if op.output and step == op.delay:
			outputfile.write(oline + '\n')

		### Print debugging output
		if op.debug:
			t2 = time.time();
			tt = tt + (t2 - t1) * 1000.0
			if loop == 0: tt = tt * step
			if op.debug == 1:
				sys.stdout.write('%6.2fms' % (tt / step))
			elif op.debug > 1:
				sys.stdout.write('%6.2f [%d:%d:%d]' % (tt / step, loop, step, update))

		### If intermediate results, update increases with 1 sec (=interval)
		update = update + interval

		if not op.update:
			sys.stdout.write('\n')

		### Do not pause when this is the final loop
		if update <= op.delay * op.count or op.count == -1:
			signal.pause()

		### The last step in a loop is to show the definitive line on its own line
		if op.update:
			if step == op.delay:
				sys.stdout.write('\n' + ansi['reset'] + ansi['clearline'] + ansi['save'])
#				import gc
#				for object in gc.get_objects():
#					if isinstance(object, mtstat):
#						print dir(object)
#						for object2 in gc.get_referents(object):
#							print object2
			else:
				sys.stdout.write(ansi['restore'])

		loop = (update + op.delay - 1) / op.delay
		step = ((update - 1) % op.delay) + 1
		tick = step

### Main entrance
def run():
	try:
		initterm()
		main()
	except KeyboardInterrupt, e:
		print
	except IOError, e:
		if e.errno != 32:				## [Errno 32] Broken pipe
			print
			print 'IOError: %s' % e
			exit(7)
	except OSError, e:
		print
		print 'OSError: %s' % e
		exit(7)
	exit(0)

#op = Options('')
#step = 1
#tick = ticks()

# vim:ts=4:sw=4
