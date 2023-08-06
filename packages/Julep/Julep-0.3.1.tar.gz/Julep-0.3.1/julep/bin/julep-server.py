#!/usr/bin/python
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

from julep import master
from julep import config

import optparse
import sys

def main(config_file,pid_file):
	master_server = master.JulepMasterServer()
	master_server.load_config(config_file)
	master_server.daemonize(pid_file)

def testconfig(config_file):
	config.test_config(config_file)


if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option("-c","--config",dest="config_file",
		help="the location of the configuration file",
		metavar="FILE",default="/etc/julep/config.py")

	parser.add_option("-p","--pid-file",dest="pid_file",
		help="the location of the pid file created by the daemon",
		metavar="FILE",default="/var/run/julep.pid")
	
	parser.add_option("-t","--test-config",dest="test_config",
		help="test the validity of the configuration file then exit.",
		action="store_true",default=False)

	options,args = parser.parse_args()

	if options.test_config:
		if config.test_config(options.config_file):
			sys.exit(0)
		else:
			sys.exit(1)

	main(options.config_file,options.pid_file)

