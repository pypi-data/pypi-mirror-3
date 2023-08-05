#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: config.py 3 2011-10-31 06:44:49Z yaka $
#

try:
	import argparse
except ImportError:
	# Python is too old
	argparse = None
	import getopt

import logging
import os
import sys

logger = logging.getLogger(__name__)

if argparse is not None:
	# New-style
	def parse_args():
		parser = argparse.ArgumentParser(description="Simple backup utility by EnikaSoft")
		parser.add_argument("tasks", metavar="task", type=str, nargs="*", help="Tasks to backup")
		parser.add_argument("-c", "--config", metavar="config_file", type=str,
			dest="config_file", default=None, help="Configuration file")
		args = parser.parse_args()
		return args
else:
	# Old-style
	class _Args(object):
		pass

	def _usage(exitcode):
		print "usage: %s [-h] [--config config_file] [task [task ...]]" % sys.argv[0]
		sys.exit(exitcode)

	def parse_args():
		args = _Args()
		args.config_file = None
		args.tasks = []

		try:
			opts, args_rem = getopt.getopt(sys.argv[1:], "c:h", ["config="])
		except getopt.GetoptError, err:
			print str(err)
			_usage(1)

		for opt, arg in opts:
			if opt == "-h":
				_usage(0)
			elif opt in ["-c", "--config"]:
				args.config_file = arg
			else:
				print "Unsupported option: (%r, %r)" % (opt, arg)
				_usage(66)
		args.tasks = args_rem
		return args


def load_config(mode=None):
	if mode is None:
		logger.critical("Unspecified mode.")
		sys.exit(1)

	args = parse_args()

	if args.config_file is None:
		if os.uname()[0] == "FreeBSD":
			args.config_file = "/usr/local/etc/esbackup_config.py"
		else:
			args.config_file = "/etc/esbackup_config.py"

	args.config_file = os.path.realpath(args.config_file)

	sys.path.insert(0, os.path.dirname(args.config_file))
	try:
		config = __import__(os.path.basename(args.config_file).rstrip(".py"))
	except ImportError, ex:
		logger.critical("Error loading cofiguration: %s", str(ex))
		sys.exit(1)
	del sys.path[0]

	config.args = args

	return config

