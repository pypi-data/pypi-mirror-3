#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from urllib2 import urlopen
from urlparse import urlparse

from copy import copy
from optparse import Option, OptionValueError

from htmlgrab import get_version

parser = None

def check_bool(option, opt, value):
    try:
        return bool(value)
    except ValueError:
        raise OptionValueError(
            "option %s: invalid bool value: %r" % (opt, value))


class BoolOption(Option):
    TYPES = Option.TYPES + ("bool",)
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["bool"] = check_bool


def get_parser():

	DESCRIPTION = 'A simple command line script to generate static web pages'
	ARGS = [
		{ 'param': '-u', 'type': str, 'default': None, 'dest': 'url', 'required': True, 'help': 'page url', },
		{ 'param': '-d', 'type': str, 'default': None, 'dest': 'destination', 'required': True, 'help': 'destionation root folder for your html', },
		{ 'param': '-i', 'type': bool, 'default': False, 'dest': 'index', 'required': False, 'help': 'save index.html into a directory based on page slug', },
		{ 'param': '-o', 'type': str, 'default': None, 'dest': 'omit', 'required': False, 'help': 'omits a string from slug', },
	]

	if sys.version_info >= (2, 7, 0):
		import argparse

		parser = argparse.ArgumentParser(description=DESCRIPTION)
		for arg in ARGS:
			parser.add_argument(arg.get('param'), type=arg.get('type'), default=arg.get('default'), dest=arg.get('dest'), help=arg.get('help'))
		parser.add_argument('--version', action='version', version='%s %s' % ('htmlgrab', get_version()))
	else:
		from optparse import OptionParser

		parser = OptionParser(option_class=BoolOption, description=DESCRIPTION, usage="%prog [-h] [-u URL] [-d DESTINATION] [-i INDEX] [-o OMIT] [--version]", version='%s %s' % ('htmlgrab', get_version()))
		for arg in ARGS:
			parser.add_option(arg.get('param'), type=arg.get('type'), default=arg.get('default'), dest=arg.get('dest'), help=arg.get('help'))

	return parser

def get_options(parser):
	if sys.version_info >= (2, 7, 0):
		return parser.parse_args()
	else:
		(options, args) = parser.parse_args()
		return options


def htmlgrab():

	parser = get_parser()
	params = get_options(parser)

	if not params.url or not params.destination:
		parser.print_help()
		exit()

	content = urlopen(params.url).read()

	if params.omit:
		params.url = params.url.replace(params.omit, '')

	parsed_url = urlparse(params.url).path
	if parsed_url.endswith('/'):
		parsed_url = parsed_url[:-1]

	url_path = parsed_url.split('/')[1:]

	path = os.path.realpath(params.destination)

	if params.index == True:
		file_name = 'index'
	elif url_path.__len__() == 0:
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