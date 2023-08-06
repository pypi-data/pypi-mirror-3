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

import imp
import socket
import os
import signal
import logging
import sys

import scoreboard

class ServerConfig(object):
	_default_options = {
		"num_servers" : 4,
		"max_connections" : 32,
		"preload_hooks" : [],
		"max_requests" : 4096,
		"max_errors" : 16,
		"max_request_time" : 30
	}

	@property
	def default_options(self):
		return self._default_options

	def verify_options(self):
		if 'app' in self.options:
			if isinstance(self.options['app'],str):
				mod_name,fun_name = self.options['app'].rsplit(".",1)
				module = __import__(mod_name,globals(),locals(),[fun_name])
				self.app = getattr(module,fun_name)
			else:
				self.app = self.options['app']
		if 'wsgi_file' in self.options:
			self.wsgi_module = imp.load_source('_wsgi_mod',
				self.options['wsgi_file'])
			self.app = self.wsgi_module.application

	def initialize_scoreboard(self,server_set):
		self.scoreboard = scoreboard.Scoreboard(self.options['num_servers'])
		server_set.scoreboards[self.name] = self.scoreboard

	def cleanup_sockets(self):
		pass

class NetworkServer(ServerConfig):
	def __init__(self,address,port,**kwargs):
		self.address = address
		self.port = port

		self.options = {}
		self.options.update(self.default_options)
		self.options.update(kwargs)

	def initialize_socket(self,server_set):
		sock = server_set.get_or_create_socket(socket.AF_INET,
			(self.address,self.port))
		sock.listen(self.options['max_connections'])
		self.socket = sock

class SocketFileServer(ServerConfig):
	def __init__(self,filename,**kwargs):
		self.filename = filename

		self.options = {}
		self.options.update(self.default_options)
		self.options.update(kwargs)

	def initialize_socket(self,server_set):
		sock = server_set.get_or_create_socket(socket.AF_UNIX,self.filename)
		sock.listen(self.options['max_connections'])
		self.socket = sock

class ConfigFileParser(object):
	def __init__(self,filename):
		imp.acquire_lock()

		try:
			config_module = imp.load_source("julep_config",filename)
		except Exception,e:
			logging.exception("Failed to load config file")
			raise

		imp.release_lock()
		
		servers = self.servers = {}

		for name in dir(config_module):
			value = getattr(config_module,name)
			if isinstance(value,ServerConfig):
				servers[name] = value

def test_config(config_file):
	try:
		config_module = ConfigFileParser(config_file)
		for name,serverconfig in config_module.servers.items():
			serverconfig.name = name
			serverconfig.verify_options()
		return True
	except:
		return False
	return False

