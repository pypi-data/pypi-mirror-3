#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: tar.py 3 2011-10-31 06:44:49Z yaka $
#

import logging
import os
import subprocess

logger = logging.getLogger(__name__)

def _generic_tar(context, flags, ext, *args):
	files_list = [ f.lstrip("/") for f in context._files ]

	archive_filename = "backup-%s-%s%s" % (context._timestamp_str, context._task_name, ext)
	archive_filepath = os.path.join(context._config.temporary_dir, archive_filename)

	proc = subprocess.Popen(["tar"] + flags + ["-C", "/", "-c", "-p", "-f", archive_filepath] + files_list)
	proc.communicate()
	if proc.returncode != 0:
		logger.error("        Tar command returned %d", proc.returncode)
		return False

	context._files = [archive_filepath]
	return True

def do_tar(context):
	return _generic_tar(context, [], ".tar.bz2")

def do_tar_gz(context):
	return _generic_tar(context, ["-z"], ".tar.gz")

def do_tar_bz2(context):
	return _generic_tar(context, ["-j"], ".tar.bz2")

def do_tar_xz(context):
	return _generic_tar(context, ["-J"], ".tar.xz")

def get_plugin():
	return {
		"tar": do_tar,
		"tar.gz": do_tar_gz,
		"tar.bz2": do_tar_bz2,
		"tar.xz": do_tar_xz,
	}
