#!/usr/bin/env python

from setuptools import setup

setup(
	name='yospaceCDS',
	version='1.1.0',
	description='Yospace CDS Webservice Client',
	long_description='''A simple library providing access to the yospaceCDS video transcoding and
mobile delivery services.

yospaceCDS is underpinned by a powerful and extensible storage and transcoding
system that is now available to integrate into your own video production
workflow or internet/mobile video application.  The service allows you to
upload video content of practically any format and order it to be transcoded
into a wealth of different popular formats for web and mobile consumption.
You can also order content to be forwarded to an FTP server for syndication
purposes. With this library you integrate with yospaceCDS using a simple set
of Web Services APIs to give you absolute control of your transcoding and
storage requirements.

Usage example:

import yospaceCDS

yospaceCDS.buildConnections()
mediaItemID = yospaceCDS.CreateMediaItem(
	"yospace_account",
	"yospace_secret",
	"http://server.name/video.mp4",
	12345678
)
# "yospace_account" is your login name to yospaceCDS
# "yospace_password" is your yospaceCDS password
# 12345678 is the Content Group in your yospaceCDS account


For more information, or to request a trial account, please visit our website.''',
	author='Yospace Systems',
	license='Distribute Freely',
	author_email='systems@yospace.com',
	url='http://www.yospace.com/index.php/cds_main.html',
	packages=['yospaceCDS'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: Freely Distributable",
		"Operating System :: Unix",
		"Operating System :: POSIX :: Linux",
		"Operating System :: POSIX :: SunOS/Solaris",
		"Operating System :: Microsoft",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: MacOS",
		"Programming Language :: Python",
		"Topic :: Multimedia :: Video :: Conversion",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	install_requires=[
		"suds >= 0.4",
	],
)
