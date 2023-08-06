#!/usr/local/bin/python

__doc__='''distutils configuration file

$Id: setup.py,v 1.24 2011/10/05 23:08:48 csoftmgr Exp $'''

__version__='$Revision: 1.24 $'[11:-2]

# from distutils.core import setup
from setuptools import setup
from glob import glob
import os, sys

prefix = sys.prefix

images = glob('images/*.gif')

setup(name="Csys",
	version="1.23",
	description="Celestial's Python Utilities",
	author="Bill Campbell",
	author_email="support@celestial.com",
	packages=[
		"Csys",
		"Csys.DNS",
		"Csys.Maildir",
		"Csys.LDAP",
		"Csys.Spamassassin",
		"Csys.DateTime",
	],
	package_dir = {
		'Csys'					: '.',
		'Csys.DNS'				: './DNS',
		'Csys.Maildir'			: './Maildir',
		'Csys.LDAP'				: './LDAP',
		'Csys.Spamassassin'		: './Spamassassin',
		'Csys.DateTime'			: './DateTime',
	},
	scripts= [
		'Xelm.py',
		'Maildir/mbox2maildir.py',
		'Maildir/imap2maildir.py',
		'csgetcfg.py',
		'csmain.py',
		'csmenu.py',
		'deliver_post.py',
		'gdfspace.py',
		'getglobals.py',
		'mapnics.py',
		'csstatmap.py',
		'stripcomments.py',
		'uniqlines.py',
		'pflogsumm_cleanup.py',
		'putty2sshpub.py',
		'rpmgetopts.py',
		'undelsend.py',
		'bigtmp.py',
		'mounted.py',
		'whlserver.py',
		'csinsertcopyright.py',
		'rmopkgenv.py',
		'dnsmap.py',
		'dnsnextip.py',
		'cssecscan.py',
		'twgenconfig.py',
		'findcritical.py',
		'mkUserRsyncConfs.py',
		'tw.djbdns_files.py',
		'chkrpms.py',
		'psmailq.py',
		'backupfile.py',
		'djbdhcpgen.py',
		'chgnetworkinfo.py',
		'emailcheck.py',
		'termcapcmp.py',
		'nfpipe.py',
	],
	data_files = [
		('images', images),
	],
)
