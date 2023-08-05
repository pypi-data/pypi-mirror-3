#!/usr/bin/env python -u

# -------------------------------------------------------------------------- #
# Copyright 2011, MadeiraCloud (support@madeiracloud.com)                  	 #
# -------------------------------------------------------------------------- #
import logging
from xml.dom import minidom

import script

Script = {
	'/etc/hosts'	:	script._etc_hosts
}

# E_OK, (timestamp, [{k:[]}])
def run(endpoint, key, distro):
	res = {}

	try:
		# get
		server = Server(endpoint)
		(err, data) = server.get(key)
		if err:		raise Exception("Failed to get new task")
		tasks = data[1]
		if not taks:
			logging.info("No pending task")
			raise Exception

		# execute
		for t in tasks:
			if not Script.has_key(t['code'][0]):
				logging.error("Invalid script code: %s" % t['code'][0])
				raise Exception
	
			res[t['id'][0]] = Script[t['code'][0]].do(t['params'], distro)
			if res[t['id'][0]] is not None:
				logging.info("Successfully executed script %s with parameters %s" % (task['code'][0], task['params'][0]))

		# TODO: report
	except:
		logging.error("Error during executing pending task")
