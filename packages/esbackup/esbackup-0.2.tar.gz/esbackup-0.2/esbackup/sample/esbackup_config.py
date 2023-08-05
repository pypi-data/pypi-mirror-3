#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: esbackup_config.py 3 2011-10-31 06:44:49Z yaka $

gpg_homedir    = "/var/db/esbackup/gnupg_home"
gpg_keyname    = "Akira (Automated backup only) <akira@example.org>"
gpg_passphrase = "secret-gpg"

backups_dir   = "/var/db/esbackup/backups"
restores_dir  = "/var/db/esbackup/restores"
temporary_dir = "/var/db/esbackup/tmp"

mail_host      = "mail.example.org"
mail_port      = 25
mail_ssl       = "tls"
mail_auth_user = "akira@example.org"
mail_auth_pass = "secret-smtp"
mail_from      = "akira@example.org"
mail_to        = "akira@example.org"
mail_subject_template = "[esbackup@host.example.org] Backup report"
mail_body_template = """ES backup report.

Backup done:
    %(tasks_total)d tasks processed.
    %(tasks_count)d successes.
    %(errors_count)d errors.

--
esbackup system at host.example.org.
This mail was automatically generated.
"""

ftp_host       = "backups.example.org"
ftp_username   = "autobackup"
ftp_password   = "secret-ftp"
ftp_remote_dir = "host"

default_scenario = [
	# Echo header
	("echo", ["Backup started."]),

	# Pre-exec
	#("exec", ["sh", "-c", "sleep 1; echo Ha-ha."]),

	# PostgreSQL database dump.
	#("exec", ["su", "-", "pgsql", "-c", "/../make_pgsql_backup.sh localhost pgsql mydatabase /var/db/esbackup/tmp/pgsql_backup_mydatabase"]),

	# Archive
	#("plugin", ["tar"]),
	#("plugin", ["tar.gz"]),
	("plugin", ["tar.bz2"]),
	#("plugin", ["tar.xz"]),

	# Protect
	#("plugin", ["hash.md5.builtin"]),
	#("plugin", ["hash.sha1.builtin"]),
	("plugin", ["hash.sha256.builtin"]),
	#("plugin", ["hash.sha512.builtin"]),
	#("plugin", ["gpg.sign", gpg_homedir, gpg_keyname, gpg_passphrase]),
	#("plugin", ["gpg.signencrypt", gpg_homedir, gpg_keyname, gpg_passphrase]),
	#("plugin", ["gpg.encrypt", gpg_homedir, gpg_keyname, gpg_passphrase]),

	# Upload
	("plugin", ["ftp", ftp_host, ftp_username, ftp_password, ftp_remote_dir]),

	# Post-exec
	#("exec", ["sh", "-c", "sleep 1; echo He-he."]),

	# Remove PostgreSQL database dumps
	#("exec", ["rm", "-f", "/var/db/esbackup/tmp/pgsql_backup_mydatabase.schema.dump"]),
	#("exec", ["rm", "-f", "/var/db/esbackup/tmp/pgsql_backup_mydatabase.data.dump"]),
]

tasks = {
	"etc": {
		"scenario": default_scenario,
		"files": [
			"/usr/local/etc",
			"/etc",
		],
	},
	"logs": {
		"scenario": default_scenario,
		"files": [
			"/var/log/messages",
		],
	},
}

