#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: gpg.py 3 2011-10-31 06:44:49Z yaka $
#

import logging

try:
	import GnuPGInterface
except ImportError:
	# Fallback to bundled version
	from esbackup.contrib.gnupg import GnuPGInterface

logger = logging.getLogger(__name__)

def _create_gnupg(config, homedir, keyname, passphrase, recipients=None):
	gnupg = GnuPGInterface.GnuPG()
	gnupg.options.homedir = homedir
	gnupg.options.default_key = keyname
	gnupg.options.comment = "Backup created automatically"
	gnupg.options.batch = True
	gnupg.options.meta_interactive = False
	gnupg.options.extra_args.append("--no-secmem-warning")
	if recipients is not None:
		gnupg.options.recipients = recipients
		gnupg.options.encrypt_to = recipients
	gnupg.passphrase = passphrase
	return gnupg

def _do_crypt(args, config, homedir, keyname, passphrase, in_filepath, out_filepath, recipients=None):
	try:
		in_file = file(in_filepath, "r")
	except (OSError, IOError), err:
		logger.error("    Error opening input file: %s", str(err))
		return False

	try:
		out_file = file(out_filepath, "w")
	except (OSError, IOError), err:
		logger.error("Error opening output file: %s", str(err))
		in_file.close()
		return False

	gnupg = _create_gnupg(config, homedir, keyname, passphrase, recipients=recipients)
	proc = gnupg.run(args, attach_fhs={ "stdin": in_file, "stdout": out_file })

	res = True
	try:
		proc.wait()
	except IOError, ex:
		logger.error(str(ex))
		res = False

	in_file.close()
	out_file.close()

	return res

logger = logging.getLogger(__name__)

#
# .pgp - encrypted message
# .sig - detached signature
# .asc - ASCII encoded file (exported public or private keys)
#

#
# /usr/local/etc/rc.conf:
#  * filename: rc.conf
#  * filepath: /usr/local/etc/rc.conf
#  * pathname: /usr/local/etc
#  * path:     /usr/local/etc
#

def _generic_gpg(context, homedir, keyname, passphrase, ext, args, recipients=None, replace_files=False):
	newfiles = []
	for filepath in context._files:
		if not replace_files:
			newfiles.append(filepath)
		newfiles.append(filepath + ext)

		res = _do_crypt(args, context._config, homedir, keyname, passphrase, filepath, filepath + ext, recipients=recipients)
		if not res:
			return False

	context._files = newfiles
	return True

def do_encrypt(context, homedir, keyname, passphrase):
	return _generic_gpg(context, homedir, keyname, passphrase, ".pgp", ["--encrypt"], recipients=[keyname], replace_files=True)

def do_signencrypt(context, homedir, keyname, passphrase):
	return _generic_gpg(context, homedir, keyname, passphrase, ".pgp", ["--sign", "--encrypt"], recipients=[keyname], replace_files=True)

def do_sign(context, homedir, keyname, passphrase):
	return _generic_gpg(context, homedir, keyname, passphrase, ".sig", ["--sign", "--detach-sign"], replace_files=False)

def get_plugin():
	return {
		"gpg.encrypt": do_encrypt,
		"gpg.signencrypt": do_signencrypt,
		"gpg.sign": do_sign,
	}
