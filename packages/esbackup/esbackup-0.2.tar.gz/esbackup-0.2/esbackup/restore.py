#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: restore.py 3 2011-10-31 06:44:49Z yaka $
#

import logging
import os
import subprocess
import sys
import tarfile
import time

import esbackup.config
import esbackup.gpg
import esbackup.utils

logger = logging.getLogger(__name__)

def do_restore(config):
	timestamp_prefix = time.strftime("%Y%m%d-%H%M%S-UTC", time.gmtime())

	esbackup.utils.makedirs_safe(config.restores_dir)

	errcount = 0

	if len(config.args.tasks) == 0:
		logger.critical("No backup archives specified")
		sys.exit(1)

	for encrypted_filepath in config.args.tasks:
		archive_filename = "restore-" + os.path.basename(encrypted_filepath).lstrip("backup-").rstrip(".asc")
		archive_filepath = os.path.join(config.restores_dir, archive_filename)
		target_dir = archive_filepath.rstrip(".tar.bz2")
		if target_dir == archive_filepath:
			target_dir = archive_filepath + "-extracted"
		
		esbackup.utils.makedirs_safe(target_dir)

		logger.info("Restoring from %s", encrypted_filepath)
		logger.debug("    Encrypted:    %s", encrypted_filepath)
		logger.debug("    Archive:      %s", archive_filepath)
		logger.debug("    Extracted to: %s", target_dir)

		encrypted_file = file(encrypted_filepath, "r")
		archive_file = file(archive_filepath, "w")
		esbackup.gpg.decrypt(config, encrypted_file, archive_file)
		archive_file.close()
		encrypted_file.close()

		proc = subprocess.Popen([ "tar", "-C", target_dir, "-xpf", archive_filepath])
		proc.communicate()
		if proc.returncode != 0:
			logger.error("Tar command returned %d", proc.returncode)
			errcount += 1

		os.unlink(archive_filepath)

	if errcount == 0:
		logger.info("Restore completed with %d errors.", errcount)
	else:
		logger.warn("Restore completed with %d errors.", errcount)

def main_restore():
	config = esbackup.config.load_config(mode="restore")
	do_restore(config)

if __name__ == "__main__":
	main_restore()

