### mtstat clock plugin
### Displays human readable clock
###
### Authority: dag@wieers.com

import time
from mtstat.mtstat import mtstat

class mtstat_clock(mtstat):
	def __init__(self):
		self.name = 'clock'
		self.format = ('s', 14, 0)
		self.nick = ('date/time',)
		self.vars = self.nick

	def extract(self):
		pass

	def show(self):
		return time.strftime('%d-%m %H:%M:%S', time.gmtime())

# vim:ts=4:sw=4
