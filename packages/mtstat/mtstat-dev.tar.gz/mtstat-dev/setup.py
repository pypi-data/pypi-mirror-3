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


# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup (name = "mtstat",
       version = "dev",
       description = "A versatile resource statistics tool",
       author = "Monty Taylor",
       author_email = "monty@inaugust.com",
       url = "http://trac.inaugust.com/mtstat/",

       py_modules = [],
       packages = ["mtstat","mtstat.plugins"],
       entry_points = {
         'console_scripts': [
           'mtstat = mtstat.mtstat:run',
         ],
         'mtstat.plugins': [
           '%s = mtstat.plugins.mtstat_%s:mtstat_%s' % (f,f,f) for f in
           [ 'app','battery','clock','cpufreq','dbus',
             'freespace','gpfsop','gpfs','nfs3op','nfs3','nfsd3op',
             'nfsd3p','postfix','rpcd','rpc','sendmail','thermal',
             'utmp','wifi' ]
           
         ] + [ '%s = mtstat.mtstat:mtstat_%s' % (f,f) for f in 
           [ 'cpu', 'disk', 'net', 'page', 'sys','time']
         ]
       },

      )
