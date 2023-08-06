#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
from urllib2 import urlopen
from urlparse import urlparse

def main(params):

	content = urlopen(params.url).read()

	if params.omit:
		params.url = params.url = params.url.replace(params.omit, '')

	parsed_url = urlparse(params.url).path
	if parsed_url.endswith('/'):
		parsed_url = parsed_url[:-1]

	url_path = parsed_url.split('/')[1:]

	path = os.path.realpath(params.destination)

	if params.index:
		file_name = 'index'
	else:
		file_name = url_path.pop()

	path = '%s/%s' % (path, '/'.join(url_path))

	if not os.path.exists(path):
		os.makedirs(path)

	file_path = '%s/%s.html' % (path, file_name)

	document = open('%s/%s.html' % (path, file_name), 'w')
	document.write(content)
	document.close()

	print True


parser = argparse.ArgumentParser(description='A simple command line script to generate static web pages')
parser.add_argument('-u', type=str, default=None, dest='url', required=True, help='page url')
parser.add_argument('-d', type=str, default=None, dest='destination', required=True, help='destionation root folder for your html')
parser.add_argument('-i', type=bool, default=False, dest='index', help='save index.html into a directory based on page slug')
parser.add_argument('-o', type=str, dest='omit', help='omits a string from slug')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()

if __name__ == '__main__':
	main(args)
