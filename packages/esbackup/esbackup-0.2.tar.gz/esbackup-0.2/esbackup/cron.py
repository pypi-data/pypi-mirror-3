#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: cron.py 3 2011-10-31 06:44:49Z yaka $
#

import logging
import sys

import esbackup.backup
import esbackup.config
import esbackup.utils

logger = logging.getLogger(__name__)

def main_cron():
	logger.debug("Called by cron, argv=%r", sys.argv)
	config = esbackup.config.load_config(mode="cron")
	logger.debug("Config loaded, %d tasks found", len(config.tasks))
	esbackup.backup.do_backup(config)

if __name__ == "__main__":
	main_cron()
