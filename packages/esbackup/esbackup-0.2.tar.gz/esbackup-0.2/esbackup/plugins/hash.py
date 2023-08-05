#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: hash.py 3 2011-10-31 06:44:49Z yaka $
#

import hashlib
import logging
import os

logger = logging.getLogger(__name__)

def _generic_hash(context, func, hash_name):
	ext = "." + hash_name.lower()

	newfiles = []
	for filepath in context._files:
		newfiles.append(filepath)
		newfiles.append(filepath + ext)

		h = func()
		in_file = file(filepath, "r")
		while True:
			buf = in_file.read(65536)
			if len(buf) == 0:
				break
			h.update(buf)
		in_file.close()

		hash_file = file(filepath + ext, "w")
		hash_file.write("%s (%s) = %s\n" % (hash_name, os.path.basename(filepath), h.hexdigest()))
		hash_file.close()

	context._files = newfiles
	return True

def do_md5_builtin(context):
	return _generic_hash(context, hashlib.md5, "MD5")

def do_sha1_builtin(context):
	return _generic_hash(context, hashlib.sha1, "SHA1")

def do_sha256_builtin(context):
	return _generic_hash(context, hashlib.sha256, "SHA256")

def do_sha512_builtin(context):
	return _generic_hash(context, hashlib.sha512, "SHA512")

def get_plugin():
	return {
		"hash.md5.builtin": do_md5_builtin,
		"hash.sha1.builtin": do_sha1_builtin,
		"hash.sha256.builtin": do_sha256_builtin,
		"hash.sha512.builtin": do_sha512_builtin,
	}
