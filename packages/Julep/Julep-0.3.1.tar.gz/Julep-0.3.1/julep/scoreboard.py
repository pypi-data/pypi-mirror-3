#
#   Copyright 2009 Rev. Johnny Healey
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import struct
import tempfile
import mmap
import fcntl

# struct description:
# i - pid
# b - status
# q - timestamp for start of last request
# i - total number of requests
# i - number of errors

scoreboard_struct = struct.Struct("ibqii")
blank_buf = "\0"*scoreboard_struct.size

class Status(object):
	DEAD = 0
	DYING = 1
	WAITING = 2
	PROCESSING = 3

class Scoreboard(object):
	def __init__(self,max_children):
		self.max_children = max_children

		self.tempfile = tempfile.TemporaryFile()
		self.structures = []
		self.free_structures = []
		self.total_size = scoreboard_struct.size*max_children

		for c in range(self.max_children):
			self.tempfile.write(blank_buf)
		self.tempfile.flush()

		self.map = mmap.mmap(self.tempfile.fileno(),self.total_size)

		for i in range(0,self.total_size,scoreboard_struct.size):
			sb_struct = ChildStructure(self,i)
			self.free_structures.append(sb_struct)
			self.structures.append(sb_struct)

	def get_all_data(self):

		fcntl.lockf(self.tempfile.fileno(),fcntl.LOCK_SH)
		buf = self.map.seek(0)
		buf = self.map.read(self.total_size)
		fcntl.lockf(self.tempfile.fileno(),fcntl.LOCK_UN)

		data = []
		for i in range(0,self.total_size,scoreboard_struct.size):
			data.append(ReadOnlyChildStructure(
				*scoreboard_struct.unpack_from(buf,i)))

		return data

	def free_dead_structures(self):
		for i,d in enumerate(self.get_all_data()):
			if d.status == Status.DEAD:
				sb_struct = self.structures[i]
				if sb_struct in self.free_structures:
					continue
				sb_struct.reset()
				sb_struct.flush()
				self.free_structures.append(sb_struct)

class ChildStructure(object):
	def __init__(self,scoreboard,index):
		self._scoreboard = scoreboard
		self._index = index
		
		self.reset()

	def reset(self):
		self.pid = 0
		self.status = 0
		self.timestamp = 0
		self.requests = 0
		self.errors = 0

	def update(self,pid=None,status=None,timestamp=None,
		requests=None,errors=None):

		if pid:
			self.pid = pid

		if status is not None:
			self.status = status
		
		if timestamp:
			self.timestamp = timestamp

		if requests:
			self.requests = requests

		if errors:
			self.errors = errors

	def flush(self):
		fcntl.lockf(self._scoreboard.tempfile.fileno(),fcntl.LOCK_EX,
			scoreboard_struct.size, self._index, 0)
		scoreboard_struct.pack_into(self._scoreboard.map,self._index,
			self.pid,self.status,self.timestamp,self.requests,self.errors)
		fcntl.lockf(self._scoreboard.tempfile.fileno(),fcntl.LOCK_UN,
			scoreboard_struct.size, self._index, 0)

class ReadOnlyChildStructure(object):
	def __init__(self,pid,status,timestamp,requests,errors):
		self.pid = pid
		self.status = status
		self.timestamp = timestamp
		self.requests = requests
		self.errors = errors

class ScoreboardWSGIApplication(object):
	def __init__(self,servers):
		self.servers = servers

	def __call__(self,environ,start_response):
		from StringIO import StringIO
		stdout = StringIO()

		print >>stdout,"""
<html>
<head><title>Server Statistics</title></head>
<body><h1>Server Statistics</h1><hr />"""

		for s in self.servers:
			print >>stdout, "<h2>%s</h2><table>\n"%s.name
			print >>stdout, """<tr>
<th>PID</th><th>Status</th><th>Last Request Started</th>
<th>Total Requests Served</th><th>Total Errors Served</th>
</tr>\n"""
			for sb_child_struct in s.scoreboard.get_all_data():
				print >>stdout, """<tr>
<td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td>
				</tr>""" %(sb_child_struct.pid,sb_child_struct.status,
					sb_child_struct.timestamp, sb_child_struct.requests,
					sb_child_struct.errors)
			print >>stdout, "</table><hr />\n"

		print >>stdout,"</body></html>"

		start_response("200 OK", [('Content-Type','text/html')])
		return [stdout.getvalue()]

