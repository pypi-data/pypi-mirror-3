### mtstat battery plugin
### Displays battery information from ACPI
###
### Authority: dag@wieers.com

import string, os
from mtstat.mtstat import mtstat, dopen, dclose

class mtstat_battery(mtstat):
	def __init__(self):
		self.name = 'battery'
		self.format = ('f', 4, 34)
		self.vars = []
		for battery in os.listdir('/proc/acpi/battery/'):
			for line in dopen('/proc/acpi/battery/'+battery+'/state').readlines():
				l = string.split(line)
				if len(l) < 2: continue
				if l[0] == 'present:' and l[1] == 'yes':
					self.vars.append(battery)
#		self.nick = [string.lower(name) for name in self.vars]
		self.nick = []
		for name in self.vars:
			self.nick.append(string.lower(name))
		self.init(self.vars, 1)

	def extract(self):
		for battery in self.vars:
			for line in dopen('/proc/acpi/battery/'+battery+'/info').readlines():
				l = string.split(line)
				if len(l) < 4: continue
				if l[0] == 'last':
					full = int(l[3])
					break
			for line in dopen('/proc/acpi/battery/'+battery+'/state').readlines():
				l = string.split(line)
				if len(l) < 3: continue
				if l[0] == 'remaining':
					current = int(l[2])
					break
			if current:
				self.val[battery] = current * 100.0 / full
			else:
				self.val[battery] = -1

# vim:ts=4:sw=4
