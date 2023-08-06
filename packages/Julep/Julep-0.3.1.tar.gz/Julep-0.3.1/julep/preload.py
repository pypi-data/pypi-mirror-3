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

import logging
import os
import re

svn_re = re.compile('.svn')

def preload_django(julep_server):
	print "preload_django"

	import django
	from django.conf import settings
	from django.template import loader

	julep_server.get_app().load_middleware()	

	for app in settings.INSTALLED_APPS:
		appmod = __import__(app,fromlist=[''])

		# load sub modules
		for submod in ['admin','models','urls','views']:
			mod = "%s.%s"%(app,submod)
			try:
				__import__(mod,fromlist=[''])
			except ImportError, e:
				logging.debug("Failed to load module: %s"%mod)
	
		# load templates
		base = "%s/%s/" % (appmod.__path__[0],'templates')
		try:
			for dir_path,dirnames,filenames in os.walk(base):
				if svn_re.search(dir_path):
					continue
				for f in filenames:
					try:
						template = (dir_path+"/"+f)[len(base):]
						logging.debug("Loading Template %s"%template)
						loader.get_template(template)
					except Exception,e:
						logging.exception("Could not load template %s"%template)
		except Exception,e:
			logging.exception("Walk Failed for %s"%base)

def preload_psyco(julep_server):
	try:
		import psyco

		psyco.cannotcompile(julep_server.spawn_child)
		psyco.full()
	except:
		logging.exception("Error while Psyco compiling")

