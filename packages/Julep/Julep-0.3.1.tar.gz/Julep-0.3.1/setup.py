#!/usr/bin/python

from distutils.core import setup

setup(name="Julep",
	version="0.3.1",
	description="Yet another WSGI server",
	author="Rev. Johnny Healey",
	author_email="rev.null@gmail.com",
	packages=["julep","julep.bin"],
	scripts=["julep/bin/julep-server.py"])

