#!/usr/bin/env python

from distutils.core import setup

setup(
	name="esbackup",
	version="0.2",
	description="Simple backup tool",
	author="Alexander Samarin",
	author_email="sasha@enikasoft.ru",
	license="BSD",
	#url="http://www.enikasoft.ru/projects/opensource/esbackup/",
	#download_url="http://www.enikasoft.ru/projects/opensource/esbackup/download/",
	classifiers=[
		"Intended Audience :: System Administrators",
		"Development Status :: 2 - Pre-Alpha",
		"License :: OSI Approved :: BSD License",
		"Operating System :: POSIX :: BSD",
		"Operating System :: POSIX :: BSD :: FreeBSD",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
	],

	#py_modules=["esbackup"]
	packages=["esbackup", "esbackup.plugins", "esbackup.contrib", "esbackup.contrib.gnupg"],
	package_data={
		"esbackup": ["sample/*"]
	},
)
