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
import os
import signal
import time
import logging
import sys

import config
import server

class JulepMasterServer(object):
	def __init__(self):
		self.alive = True
		self.server_set = None
		self.work_queue = []

		signal.signal(signal.SIGINT,self.die_gracefully)
		signal.signal(signal.SIGUSR1,self.graceful_restart)
	
	def serve_forever(self):
		while self.alive:
			while self.work_queue:
				self.work_queue.pop()()
			time.sleep(1)

		logging.info("Shutting Down Master Server")
		self.shut_down()
	
	def shut_down(self):
		if self.server_set:
			try:
				self.server_set.kill_all_children()
			except Exception,e:
				logging.exception("Error Killing Children")
			try:
				self.server_set.close_all_sockets()
			except Exception,e:
				logging.exception("Error Closing Sockets")

	def load_config(self,config_filename=None):
		if config_filename:
			self.config_filename = config_filename
		else:
			config_filename = self.config_filename

		config_module = config.ConfigFileParser(config_filename)

		for name,serverconfig in config_module.servers.items():
			serverconfig.name = name
		# testing the server config loads modules
		# this has been moved to a different process to prevent the modules
		# from being cached
		pid = os.fork()
		if pid == 0:
			for name,serverconfig in config_module.servers.items():
				try:
					serverconfig.verify_options()
				except Exception,e:
					logging.exception("Error With Server Configuration")
					sys.exit(1)
			sys.exit(0)
		else:
			child_pid,status = os.waitpid(pid,0)
			if status != 0:
				raise Exception("Configuration Error: check the logfile for details")

		if getattr(config_module,'SERVER_LOG',None):
			logging.basicConfig(**config_module.SERVER_LOG)
		self.server_set = ServerSet(config_module,self.server_set)

	def die_gracefully(self,*args):
		self.alive = False

	def daemonize(self,pidfile):

		if os.path.exists(pidfile):
			raise Exception("PID file exists")

		self.server_set.prepare_sockets()

		# silence stdout/stderr and close stdin
		sys.stdout = open("/dev/null","w")
		sys.stderr = open("/dev/null","w")
		sys.stdin.close()

		# daemonize
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
		os.setsid()
		
		self.pidfile = open(pidfile,"w")
		self.pidfile.write("%d\n"%os.getpid())
		self.pidfile.close()

		self.server_set.spawn_workers()
		self.serve_forever()

		os.unlink(pidfile)

	def graceful_restart(self,*args):
		try:
			self.work_queue.append(self.do_graceful)
		except Exception:
			logging.exception("Graceful_Restart Failed")

	def do_graceful(self):
		logging.info("Gracefully Restarting")

		try:
			self.load_config()
			self.server_set.prepare_sockets()
			self.server_set.spawn_workers()
			self.server_set.cleanup_old_servers()
		except Exception:
			logging.exception("Graceful Restart Failed")

class ServerSet(object):
	def __init__(self,config,old_set=None):
		self.config = config

		self.sockets = {}
		self.servers = {}
		self.scoreboards = {}

		self.old_set = old_set

	def spawn_worker_server(self,config,old_pid=None):
		pid = os.fork()

		if pid == 0:
			
			config.verify_options()

			# close all sockets used by other JulepSocketServers
			for sock in self.sockets.values():
				try:
					if sock != config.socket:
						sock.close()
				except Exception,e:
					logging.exception("Could not close unused socket")

			try:
				# spawn the new socket server
				julep_server = server.JulepSocketServer(
					config.socket,
					children = config.options['num_servers'],
					scoreboard = config.scoreboard,
					preload_hooks = config.options['preload_hooks'],
					app = config.app,
					old_pid = old_pid,
					options = config.options
				)
				julep_server.serve_forever()
			except Exception,e:
				logging.exception("Failed to start server")
				sys.exit(1)
		else:
			return pid

	def spawn_workers(self):
		# spawn the servers
		for name,serverconfig in self.config.servers.items():
			old_pid = None
			if self.old_set:
				if name in self.old_set.servers:
					old_pid = self.old_set.servers[name]
			self.servers[name] = self.spawn_worker_server(serverconfig,old_pid)

	def prepare_sockets(self):
		# prepare the servers for spawning
		for name,serverconfig in self.config.servers.items():
			serverconfig.initialize_socket(self)
			serverconfig.initialize_scoreboard(self)

	def get_or_create_socket(self,type,address):
		sock_key = (type,address)
		sock = None

		# see if the old set used this socket
		if self.old_set:
			if sock_key in self.old_set.sockets:
				sock = self.old_set.sockets[sock_key]

		# if the old set didn't use it, create a new socket
		if not sock:
			sock = self.create_socket(type,address)
		
		self.sockets[sock_key] = sock

		return sock

	def create_socket(self,type,address):
		sock = socket.socket(type,socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(address)
		return sock

	def kill_all_children(self):
		for name,pid in self.servers.items():
			logging.debug("Killing %s(%d)"%(name,pid))
			os.kill(pid,signal.SIGINT)

		self.wait_for_children_to_die()

	def wait_for_children_to_die(self):
		for name in self.servers:
			tup = os.wait()
			logging.debug("process %d exited with status %d"%tup)

	def close_all_sockets(self):
		for key,sock in self.sockets.items():
			try:
				sock.close()
				if key[0] == socket.AF_UNIX:
					os.unlink(key[1])
			except Exception, e:
				logging.exception("Failed to close socket")

	def cleanup_old_servers(self):
		if not self.old_set:
			return

		# close the sockets that will no longer be used
		for sock_key,sock in self.old_set.sockets.items():
			if sock_key not in self.sockets:
				try:
					sock.close()
					if sock_key[0] == socket.AF_UNIX:
						os.unlink(sock_key[1])
					logging.info("Closing old socket %s"%str(sock_key))
				except Exception:
					logging.exception("Error closing old socket")

		for name,pid in self.old_set.servers.items():
			if name not in self.servers:
				try:
					os.kill(pid,signal.SIGINT)
				except Exception:
					logging.exception("Error killing process: %d"%pid)

		self.old_set.wait_for_children_to_die()

		self.old_set = None

