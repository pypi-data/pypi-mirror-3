#!/usr/bin/python
# -*- coding:utf8 -*-
import os
import sys
import subprocess
import urllib2
import cookielib
import base64
import re
from urlparse import urljoin
import shelve

import ConfigParser
try:
	import json
except ImportError:
	import simplejson as json


def get_cmd_output(cmd):
	p = subprocess.Popen(cmd,
#			stdin = subprocess.PIPE,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE)
#	p.stdin.close()
	return p.communicate()[0]

#print get_cmd_output(["python", "-c", "print 32"])

