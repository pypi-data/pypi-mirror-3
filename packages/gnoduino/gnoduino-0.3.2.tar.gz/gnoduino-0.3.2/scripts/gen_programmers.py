#!/usr/bin/python
#
# gnoduino - Python Arduino IDE implementation
# Copyright (C) 2010  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import ConfigParser

conf = ConfigParser.RawConfigParser()
f = 'hardware/arduino/programmers.txt'
res = []
tmp = []
try:
	for i in file(f):
		if i != "\n" and i != "#":
			for j in i.splitlines():
				if j[0] != "#":
					tmp.append(j)
					res.append(j.split('.', 1)[0])
except:
	raise SystemExit("Cannot find %s. Forgot to update hardware module ? Exiting" % f)

w = file("PROGRAMMERS", "w+")
cnt = []
for z in tmp:
	cnt = z.split('.', 1)[1]
	if cnt.split("=")[0] == 'name':
		w.write("\n")
		w.write("["+cnt.split("=")[1]+"]\n")
		w.write("name = "+z.split('.', 1)[0]+"\n")
	cnt = cnt.split(".")
	if cnt[0].split("=")[0] == 'communication':
		w.write(cnt[0].replace("=", " = ")+"\n")
	if cnt[0].split("=")[0] == 'protocol':
		w.write(cnt[0].replace("=", " = ")+"\n")
	if cnt[0].split("=")[0] == 'speed':
		w.write(cnt[0].replace("=", " = ")+"\n")
	if cnt[0].split("=")[0] == 'force':
		w.write(cnt[0].replace("=", " = ")+"\n")
	if cnt[0].split("=")[0] == 'delay':
		w.write(cnt[0].replace("=", " = ")+"\n")
w.close()
