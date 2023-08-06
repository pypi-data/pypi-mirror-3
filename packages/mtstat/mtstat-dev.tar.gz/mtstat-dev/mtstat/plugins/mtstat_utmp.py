class mtstat_utmp(mtstat):
	def __init__(self):
		self.name = 'utmp'
		self.format = ('d', 3, 10)
		self.nick = ('ses', 'usr', 'adm' )
		self.vars = ('sessions', 'users', 'root')
		self.init(self.vars, 1)

	def check(self): 
		try:
			global utmp
			import utmp
			return True
		except:
			raise Exception, 'Module needs the python-utmp module.'

	def extract(self):
		for name in self.vars: self.val[name] = 0
		for u in utmp.UtmpRecord():
#			print '# type:%s pid:%s line:%s id:%s user:%s host:%s session:%s' % (i.ut_type, i.ut_pid, i.ut_line, i.ut_id, i.ut_user, i.ut_host, i.ut_session)
			if u.ut_type == utmp.USER_PROCESS:
				self.val['users'] = self.val['users'] + 1
				if u.ut_user == 'root':
					self.val['root'] = self.val['root'] + 1
			self.val['sessions'] = self.val['sessions'] + 1

# vim:ts=4:sw=4
