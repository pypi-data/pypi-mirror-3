#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: backup.py 3 2011-10-31 06:44:49Z yaka $
#

import logging
import os
import subprocess
import sys
import tarfile
import time

import esbackup.config
import esbackup.plugins
import esbackup.utils

logger = logging.getLogger(__name__)

class BackupContext(object):
	def __init__(self, config, plugins, task_name, task_desc):
		"""Initializer.

		  * task_name (str)  -- Task name
		  * task_desc (dict) -- Task description dictionary from configuration file
		"""

		self._config = config
		self._plugins = plugins
		self._task_name = task_name
		self._task_desc = task_desc
		self._timestamp_str = time.strftime("%Y%m%d-%H%M%S-UTC", time.gmtime())
		self._files = task_desc["files"]

	def play(self):
		scenario = self._task_desc.get("scenario", None)
		if scenario is None:
			logger.warn("Scenario is not defined for task %s", self._task_name)
			return False

		failure = False
		for tup in scenario:
			action = None
			args = []
			plugin_kwargs = {}
			if len(tup) >= 1:
				action = tup[0]
			if len(tup) >= 2:
				args = tup[1]
			if len(tup) >= 3:
				plugin_kwargs = tup[2]

			if action == "exec":
				if not esbackup.utils.todo_exec_one(self._task_desc, args):
					logger.error("    Execution failed.")
					logger.error("Scenario terminated abnormally.")
					failure = True
					break
			elif action == "echo":
				logger.info("    %s", " ".join(args))
			elif action == "plugin":
				plugin_name = args[0]
				plugin_args = args[1:]
				plugin_func = self._plugins.get(plugin_name, None)
				if plugin_func is None:
					logger.error("    Plugin %s not found.", plugin_name)
					logger.error("Scenario terminated abnormally.")
					failure = True
					break
				logger.info("    Run plugin %s: %s", plugin_name, plugin_func)

				self._dumpfiles("Input files")
				res = plugin_func(self, *plugin_args, **plugin_kwargs)
				if not res:
					logger.error("    Plugin execution failed.")
					logger.error("Scenario terminated abnormally.")
					failure = True
					break
				self._dumpfiles("Output files")
			else:
				logger.error("    Scenario action is unknown: %s.", action)
				logger.error("Scenario is bad.")
				failure = True
				break

		return not failure

	def _dumpfiles(self, header):
		logger.debug("        %s:", header)
		for filename in self._files:
			logger.debug("            %s", filename)

def do_backup(config):
	plugins_dir = esbackup.plugins.__path__[0]
	plugins_names = [
		fname[:-3]
		for fname in os.listdir(plugins_dir)
		if fname.endswith(".py")
		if not fname.startswith("_")
	]
	logger.debug("Plugins: %s", ", ".join(plugins_names))
	plugins_modules = __import__("esbackup.plugins", globals(), locals(), plugins_names, -1)
	plugins = {}
	for mod_name in plugins_names:
		mod = getattr(plugins_modules, mod_name)
		gpf = getattr(mod, "get_plugin", None)
		if gpf is None:
			logger.warn("    Plugin %s have no \"get_plugin\" function. Module skipped.")
		plugins.update(gpf())

	for name, mod in plugins.items():
		logger.debug("    Loaded plugin %s: %r", name, mod)

	#timestamp_prefix = time.strftime("%Y%m%d-%H%M%S-UTC", time.gmtime())
	#logger.debug("Backup timestamp is %s", timestamp_prefix)

	esbackup.utils.makedirs_safe(config.backups_dir)
	esbackup.utils.makedirs_safe(config.temporary_dir)

	errcount = 0
	tasks_count = 0

	tasks_list = config.args.tasks
	if len(tasks_list) == 0:
		tasks_list = None
		tasks_total = len(config.tasks)
	else:
		tasks_total = len(tasks_list)

	for task_name, task in config.tasks.items():
		if (tasks_list is not None) and (task_name not in tasks_list):
			continue

		ctx = BackupContext(config, plugins, task_name, task)
		if ctx.play():
			tasks_count += 1
		else:
			errcount += 1


	if errcount == 0:
		logger.info("Backup completed with %d errors.", errcount)
	else:
		logger.warn("Backup completed with %d errors.", errcount)

	email_data = {
		"errors_count": errcount,
		"tasks_count": tasks_count,
		"tasks_total": tasks_total,
	}

	try:
		esbackup.utils.send_email(config, {
			"subject": config.mail_subject_template % email_data,
			"text": config.mail_body_template % email_data,
		})
	except Exception, ex:
		logger.error("Email sending failed: %s", repr(ex))
		raise

def main_backup():
	config = esbackup.config.load_config(mode="backup")
	do_backup(config)

if __name__ == "__main__":
	main_backup()

