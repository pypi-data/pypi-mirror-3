#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: ftp.py 3 2011-10-31 06:44:49Z yaka $
#

import ftplib
import logging
import os

logger = logging.getLogger(__name__)

def do_ftp(context, hostname, username, password, remote_path):
	for filepath in context._files:
		filename_local = os.path.basename(filepath)

		remote_filepath = remote_path + "/" + filename_local

		file_local = file(filepath, "r")

		ftp = ftplib.FTP(hostname, username, password)
		ftp.storbinary("STOR %s" % remote_filepath, file_local)
		ftp.quit()

		file_local.close()

	return True

def get_plugin():
	return {
		"ftp": do_ftp,
	}
