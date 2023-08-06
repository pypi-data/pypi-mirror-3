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

import socket
import select
import os
import signal
import time
import logging
import sys
import gc
import re

from wsgiref.simple_server import WSGIRequestHandler

import scoreboard

class JulepSocketServer(object):
	memory_re = re.compile("^VmSize:\s+(\d+) kB")

	def __init__(self,sock,handler=WSGIRequestHandler,children=4,
		scoreboard=None,preload_hooks=[],app=None,old_pid=None,options={}):

		self.socket = sock
		self.handler = handler
		self.max_children = children
		self.alive = True
		self.preload_hooks = preload_hooks
		self.app = app
		self.old_pid = old_pid
		self.options = options
		self.kill_rotation = 0

		# die gracefully on sigint
		signal.signal(signal.SIGINT,self.die_gracefully)
		signal.signal(signal.SIGTERM,self.die_ungracefully)
		signal.signal(signal.SIGUSR1,self.graceful_all_children)

		if scoreboard:
			self.scoreboard = scoreboard
		else:
			self.scoreboard = scoreboard.Scoreboard(self.max_children)

	def configure_logs(self):
		self.logger = logging.getLogger()

		if 'access_log' in self.options:
			try:
				sys.stderr = open(self.options['access_log'],"a",0)
			except Exception, e:
				logging.exception("Failed to open access log")
				raise
		if 'error_log' in self.options:
			try:
				self.logger = logging.getLogger("julep.socket")
				self.logger.addHandler(logging.FileHandler(
					self.options['error_log']))
				self.logger.setLevel(logging.DEBUG)
			except Exception, e:
				logging.exception("Failed to open error log")
				raise

	def serve_forever(self):
		self.configure_logs()

		for preload_hook in self.preload_hooks:
			try:
				preload_hook(self)
			except Exception,e:
				self.logger.exception("Preload Hook Failed")
				raise
			
		self.replenish_children()

		if self.old_pid:
			self.logger.info("Killing Old PID: %d"%self.old_pid)
			try:
				os.kill(self.old_pid,signal.SIGINT)
			except Exception,e:
				self.logger.exception("Error killing Old PID: %d"%self.old_pid)

		try:
			while self.alive:
				try:
					self.kill_bad_children()
					self.collect_zombies()
					self.scoreboard.free_dead_structures()
					self.replenish_children()
				except Exception,e:
					self.logger.exception("Error in master_server")
				time.sleep(1)

			self.kill_all_children()
		finally:
			self.socket.close()
			self.exit(0)

	def replenish_children(self):
		while self.scoreboard.free_structures:
			self.spawn_child()

	def die_gracefully(self,*args):
		self.logger.info("Die Gracefully")
		self.alive = False

	def die_ungracefully(self,*args):
		self.logger.info("Die Ungracefully")
		self.socket.close()
		self.exit(1)

	def graceful_all_children(self,*args):
		self.logger.info("Gracefulling all children")

		for i in range(self.max_children):
			try:
				sb_struct = self.scoreboard.get_all_data()[i]
				if sb_struct.status != scoreboard.Status.DEAD:
					#kill the child
					os.kill(sb_struct.pid,signal.SIGINT)

					# wait for the child to die
					pid,status = os.waitpid(sb_struct.pid,0)

					sb_struct = self.scoreboard.structures[i]
					sb_struct.reset()
					sb_struct.flush()
				
					#respawn a replacement child
					self.replenish_children()
			except Exception:
				self.logger.exception("Failed to graceful child")

	def exit(self,status):
		
		sys.exit(status)

	def spawn_child(self):
		sb_struct = self.scoreboard.free_structures.pop()
		sb_struct.update(status=scoreboard.Status.WAITING)
		sb_struct.flush()
		pid = os.fork()
		if pid == 0:
			try:
				child = JulepChildSocketServer(self.socket,os.getpid(),
					sb_struct,self.handler,self.app,self.logger)
				child.serve_forever()
			except Exception, e:
				self.logger.exception("Failed to spawn child process")
				sys.exit(1)

	def has_valid_option(self,name,validator=lambda x:x>0):
		if name in self.options:
			if validator(self.options[name]):
				return True
		return False

	def get_app(self):
		return self.app

	def kill_bad_children(self):
		killed = 0

		# the kill_rotation rotates elements in the list to eliminate the bias
		# towards killing the first element
		sb = self.scoreboard.get_all_data()
		sb = sb[self.kill_rotation:]+sb[:self.kill_rotation]
		self.kill_rotation = (self.kill_rotation + 1) % self.max_children

		for sb_struct in sb:
			if killed > 0: # replace with max_killed option
				break

			if sb_struct.pid == 0:
				continue
			if self.has_valid_option('max_requests'):
				if sb_struct.requests > self.options['max_requests']:
					self.logger.info("Killing %d due to old age"%sb_struct.pid)
					os.kill(sb_struct.pid,signal.SIGINT)
					killed += 1
			if self.has_valid_option('max_errors'):
				if sb_struct.errors > self.options['max_errors']:
					self.logger.warning("Killing %d due to large number of errors"%
						sb_struct.pid)
					os.kill(sb_struct.pid,signal.SIGINT)
					killed += 1
			if self.has_valid_option('max_request_time'):
				if sb_struct.status == scoreboard.Status.PROCESSING:
					request_time = time.time() - sb_struct.timestamp
					if request_time > self.options['max_request_time']:
						self.logger.warning(
							"Killing %d due to long running request"%
							sb_struct.pid)
						os.kill(sb_struct.pid,signal.SIGTERM)
						killed += 1
			if self.has_valid_option('max_memory'):
				status_file = "/proc/%d/status"%sb_struct.pid
				for line in open(status_file,"r"):
					m = self.memory_re.match(line)
					if m:
						kb = int(m.groups()[0])
						if kb > self.options['max_memory']:
							self.logger.warning(
								"Killing %d due to high memory usage"%
								sb_struct.pid)
							os.kill(sb_struct.pid,signal.SIGINT)
							killed += 1
		return killed

	def collect_zombies(self):
		for i,d in enumerate(self.scoreboard.get_all_data()):
			try:
				pid,status = os.waitpid(d.pid,os.WNOHANG)
				if pid == 0:
					continue
				if status != 0:
					self.logger.warning("Process %d exited with status %d"%
						(pid,status))
			except OSError:
				self.logger.warning("Process %d has been waited on"%d.pid)
			sb_struct = self.scoreboard.structures[i]
			sb_struct.reset()
			sb_struct.flush()

	def kill_all_children(self):
		for sb_struct in self.scoreboard.get_all_data():
			if sb_struct.status != scoreboard.Status.DEAD:
				os.kill(sb_struct.pid,signal.SIGINT)

class JulepChildSocketServer(object):
	def __init__(self,sock,pid,sb_struct,handler,app,logger):
		self.socket = sock
		self.pid = pid
		self.sb_struct = sb_struct
		self.handler = handler
		self.app = app
		self.alive = True
		self.logger = logger
	
		self.total_requests = 0
		self.total_errors = 0

		self.base_environ = {
			'SERVER_NAME' : socket.gethostname(),
			'GATEWAY_INTERFACE' : 'CGI/1.1'
		}

		signal.signal(signal.SIGINT,self.die_gracefully)
		signal.signal(signal.SIGTERM,self.die_ungracefully)
		signal.signal(signal.SIGUSR1,self.die_gracefully)

	def prepare_to_serve(self):
		gc.collect()
		gc.disable()

		self.sb_struct.update(pid = self.pid)
		self.sb_struct.flush()

		self.logger.info("Spawned Child Process: %d"%self.pid)

		read_fd,write_fd = os.pipe()
		self.read_pipe = os.fdopen(read_fd,"r")
		self.write_pipe = os.fdopen(write_fd,"w")

		self.sockets = [self.socket,self.read_pipe]

	def serve_forever(self):

		self.prepare_to_serve()
		
		try:
			while self.alive:
				self.sb_struct.update(status = scoreboard.Status.WAITING,
					requests=self.total_requests,errors=self.total_errors)
				self.sb_struct.flush()
				try:
					available = select.select(self.sockets,[],[])
				except Exception,e:
					if e[0] == 4:
						self.logger.warning("select interrupted for process %d."
							% self.pid)
						continue
					self.logger.error(
						"select failed for process %d.  Shutting down"
						% self.pid)
					break
				for a in available[0]:
					try:
						sock,addr = a.accept()
						
						# this is probably not the best way to handle this,
						# but the python http handler doesn't like the
						# empty addresses used by unix domain sockets.
						if not addr:
							addr = ("unix",0)

					except Exception,e:
						if e[0] == 4:
							self.logger.warning("accept interrupted for process %d."
								% self.pid)
							continue
						self.logger.exception("Error Accepting Socket")
					self.sb_struct.update(status = scoreboard.Status.PROCESSING,
						timestamp = int(time.time()))
					self.sb_struct.flush()
					self.handle_request(sock,addr)
		finally:
			self.exit(0)

	def handle_request(self,req,client):
		try:
			self.total_requests += 1
			handler = self.handler(req,client,self)
		except Exception,e:
			self.total_errors += 1
			self.logger.exception("Error Handling Request: %s,%s"%(req,client))
		try:
			req.close()
		except Exception,e:
			self.logger.exception("Error Closing Socket")

	def get_app(self):
		return self.app

	def exit(self,status):
		self.logger.info("Process %d is shutting down."%self.pid)
		self.sb_struct.update(status = scoreboard.Status.DYING)
		self.sb_struct.flush()

		self.write_pipe.close()
		
		sys.exit(status)

	def die_gracefully(self,*args):
		self.alive = False
		self.write_pipe.write(" ")

	def die_ungracefully(self,*args):
		self.exit(1)

def create_inet_server(address,port,app,children=4,max_connections=32):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind((address,port))
	s.listen(max_connections)

	server = JulepSocketServer(s,children=children,app=app)
	return server

def create_unix_server(fname,app,children=4,max_connections=32):
	s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
	s.bind(fname)
	s.listen(max_connections)

	server = JulepSocketServer(s,children=children,app=app)
	return server

if __name__ == '__main__':
	from wsgiref import simple_server
	httpd = create_inet_server('',8666,simple_server.demo_app)
	print "Serving on port 8666..."
	httpd.serve_forever()

