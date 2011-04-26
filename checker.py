#!/usr/bin/env python
# coding=utf-8

# Copyright (c) 2011 Viktor Stískala. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY VIKTOR STÍSKALA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__    = "Viktor Stískala, viktor@stiskala.cz"
__copyright__ = "(c) 2011 Viktor Stískala"
__license__   = "New BSD License"

import urllib2
import sys
from urlparse import urlparse
import re

redirect_handler = urllib2.HTTPRedirectHandler()
class Redirection(Exception):
	pass

class CustomHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		m = re.search(r"^Location:\s?(.+)$", str(headers), re.IGNORECASE | re.MULTILINE)
		url = m.group(1)
		raise Redirection(url)

	http_error_301 = http_error_303 = http_error_307 = http_error_302

def test_url(url, ip = None, prev_url = None):
	o = urlparse(url)
	if ip == None:
		req = urllib2.Request(url)
	else:
		request_url = "http://" + ip + o.path
		req = urllib2.Request(request_url, None, {'host': o.netloc})

	opener = urllib2.build_opener(CustomHTTPRedirectHandler)
	try:
		response = opener.open(req)
		return (response.getcode(), prev_url if prev_url != None else url, ip)
	except Redirection, r: # allow redirection only to www version
		p = urlparse(str(r))
		m = re.match(r'www\.(.+)', p.netloc)
		if (m and m.group(1) == o.netloc):
			return test_url(str(r), ip, url)
		else:
			return ('30x', prev_url if prev_url != None else url, ip)
	except urllib2.HTTPError, e:
		return (e.getcode(), prev_url if prev_url != None else url, ip)

	return ('???', prev_url if prev_url != None else url, ip)

if len(sys.argv) != 2:
	sys.stderr.write("Usage: " + sys.argv[0] + " file\n")
	sys.exit(1)

filename = sys.argv[1]
try:
	fh = open(filename, 'r')
except IOError:
	sys.stderr.write("Cannot open specified file\n")
	sys.exit(1)

comment = re.compile(r'^#.*')
whitespace = re.compile(r'\s+')
urlip = re.compile('^(?P<url>https?://.+?)\t?(?P<ip>[\d\.]+)*$')
line = 0
try:
	for url in fh:
		line += 1

		# skip comments and empty lines
		if comment.match(url) or whitespace.match(url):
			continue

		m = urlip.match(url)
		if not m:
			sys.stderr.write("Syntax error on line " + str(line) + "\n")
			continue

		result = test_url(m.group('url'), m.group('ip'))

		if(str(result[0]) != '200'):
			print str(result[0]) + "\t" + result[1]
except KeyboardInterrupt:
	sys.stderr.write('Terminated\n')
	sys.exit(1)

