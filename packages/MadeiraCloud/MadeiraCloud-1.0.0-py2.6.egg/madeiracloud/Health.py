#!/usr/bin/env python -u
# coding: utf-8

# -------------------------------------------------------------------------- #
# Copyright 2011, MadeiraCloud (support@madeiracloud.com)                  	 #
# -------------------------------------------------------------------------- #
import logging

def _amazon(mode, ns):
	# os
	# hw
	# sw
	# load
	pass

def _redhat(mode, ns):
	pass

def _centos(mode, ns):
	pass

def _debian(mode, ns):
	pass

def _ubuntu(mode, ns):
	pass

def _suse(mode, ns):
	pass

Distro = {
	'amazon'	:	_amazon,
	'redhat'	:	_redhat,
	'centOS'	:	_centos,
	'debian'	:	_debian,
	'ubuntu'	:	_ubuntu,
	'suse'		:	_suse
}

def run(endpoint, key, distro):
	status = {}

	try:
		# states
		status = Distro[distro]()

		# report
		server = Server(endpoint)
		if not server.report(key, status):
			raise Exception
	except:
		logging.error("Failed to report system health")
