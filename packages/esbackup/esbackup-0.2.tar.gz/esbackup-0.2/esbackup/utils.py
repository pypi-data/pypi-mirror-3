#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# $Id: utils.py 3 2011-10-31 06:44:49Z yaka $
#

import email.mime.text
import ftplib
import logging
import os
import smtplib
import subprocess
import sys

logging_format = "%(asctime)-15s %(levelname)-8s %(message)s"
logging_format_color = sys.stderr.isatty()
logging_colors = {
	logging.DEBUG:    "\033[1m",
	logging.INFO:     "\033[0m",
	logging.WARN:     "\033[0;33m",
	logging.ERROR:    "\033[0;31m",
	logging.CRITICAL: "\033[1;31m",
}

logging.basicConfig(level=logging.DEBUG, format=logging_format)

logger = logging.getLogger(__name__)

def makedirs_safe(path):
	try:
		os.makedirs(path)
	except OSError, ex:
		if ex.errno not in [17]:
			logger.critical("Unable to create directory %r: %s", path, str(ex))
			sys.exit(1)

def todo_exec_one(task, todo):
	if isinstance(todo, list):
		cmdline = " ".join([ '"%s"' % s for s in todo ])
		logger.info("    Executing external command: %s", cmdline)
		proc = subprocess.Popen(todo)
		proc.communicate()
		if proc.returncode != 0:
			logger.error("        Exit code is %d", proc.returncode)
			preexec_ok = False
			return False
	elif callable(todo):
		logger.info("    Executing function or lambda: %r", todo)
		try:
			ret = todo(task=task)
		except Exception, ex:
			logger.error("        Function or lambda raised exception: %s", str(ex))
			preexec_ok = False
			return False
		if not ret:
			logger.error("        Function or lambda returned False.")
			return False
	else:
		logger.warn("    Garbage is neither callable nor a shell comand: %r", todo)
	return True

def send_email(config, data):
	sender = config.mail_from
	recipients = config.mail_to
	if isinstance(recipients, str):
		recipients = [recipients]

	msg = email.mime.text.MIMEText(data["text"])
	msg["From"] = sender
	msg["To"] = ", ".join(recipients)
	msg["Subject"] = data["subject"]

	if config.mail_ssl == "ssl":
		smtp = smtplib.SMTP_SSL(config.mail_host, config.mail_port)
	else:
		smtp = smtplib.SMTP(config.mail_host, config.mail_port)
		if config.mail_ssl == "tls":
			smtp.starttls()
	if config.mail_auth_user is not None:
		smtp.login(config.mail_auth_user, config.mail_auth_pass)
	smtp.sendmail(sender, recipients, msg.as_string())
	smtp.quit()

