#!/usr/bin/python26 -u

# -------------------------------------------------------------------------- #
# Copyright 2011, MadeiraCloud (support@madeiracloud.com)                  	 #
# -------------------------------------------------------------------------- #

"""MadeiraCloud Agent 
"""

import os
import sys
import errno
import signal
import urllib
import logging
from optparse import Option, OptionParser

from madeiracloud import Log
from madeiracloud import Task
from madeiracloud import Health
from madeiracloud import Watcher
from madeiracloud import RTimer

__copyright__ 	= "Copyright 2011, MadeiraCloud (http://www.madeiracloud.com))"
__license__ 	= "GPL"
__version__ 	= "1.0.0"
__maintainer__ 	= "MadeiraCloud"
__author__ 		= "dev@madeiracloud.com"
__email__ 		= "support@madeiracloud.com"
__status__ 		= "Production"

# -----------------------------------------------------
#  Exception
# -----------------------------------------------------
class MadeiraAgentException(Exception):
		"""A simple exception class used for MadeiraAgent exceptions"""
		pass

# ----------------------------------------------------------------------------------------------
#	MadeiraAgent
# ----------------------------------------------------------------------------------------------
class MadeiraAgent(object):
	log_level 	= 'INFO'
	log_dir		= '/var/log/madeiracloud/'
	log_file	= log_dir + 'madeiracloud.log'
	log_rotate	= 3
	log_size	= 10000000
	pidfile 	= '/var/lock/subsys/madeiracloud'
	endpoint_task	= 'https://api.madeiracloud.com/agent/task/'
	endpoint_health	= 'https://api.madeiracloud.com/agent/health/'
	interval_task	= 6
	interval_health	= 60
	url_metadata	= 'http://169.254.169.254/latest/meta-data/'
	url_userdata	= 'http://169.254.169.254/latest/user-data/'

	def __init__(self, daemon=True, no_task=False, no_health=False):
		""" Initializes MadeiraAgent. """    
		self.__daemon = daemon
		self.__no_task= no_task
		self.__no_health = no_health
		self.__timer  = []
		self.__key 	  = None
		self.__distro = None

		# Log, Daemonize and Signal
		self._log()		
		if daemon:	self._daemonize()
		signal.signal(signal.SIGTERM, self._signal)
		signal.signal(signal.SIGINT,  self._signal)
		signal.signal(signal.SIGQUIT, self._signal)
		signal.signal(signal.SIGHUP,  self._signal)
		signal.signal(signal.SIGCHLD, self._signal)
		signal.signal(signal.SIGUSR2, self._signal)

		# Key & Distro
		#self._key()
		self._distro()

	def _log(self):
		# setup LOG
		try:
			level = logging.getLevelName(self.log_level)
			logging.getLogger().setLevel(level)
			logger = logging.getLogger()
			if self.__daemon:
				# Add the log message handler to the logger
				if not os.path.exists(MadieraAgent.log_dir):
					os.makedirs(self.log_dir, 0755)
				fh = logger.handlers.RotatingFileHandler(
					filename	= self.log_file,
					maxBytes	= self.log_size,
					backupCount	= self.log_rotate
				)
				formatter = Log.LogFormatter(console=False)
			else:
				# Set up color if we are in a tty and curses is installed
				fh = logging.StreamHandler()
				formatter = Log.LogFormatter(console=True)
			fh.setFormatter(formatter)
			logger.addHandler(fh)	
		except OSError, msg:
			raise MadeiraAgentException

	def _signal(self, sig, frame):
		if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):		# exit
			logging.info('caught signal %s' % sig)
			self.exit()
		elif sig == signal.SIGHUP:										# reload
			logging.info('caught signal %s' % sig)
			self.reload()
		elif sig == signal.SIGCHLD:										# TODO:
			pass
			logging.debug('caught signal %s' % sig)
		elif sig == signal.SIGUSR2:										# TODO:
			pass
			logging.debug('caught signal %s' % sig)
		else:
			logging.warning('caught signal %s' % sig)

	# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012 
	def _daemonize(self):
		try:
			# First fork
			try:
				pid = os.fork()
				if pid > 0: 
					# Exit first parent
					sys.exit(0) 
			except OSError, e:
				logging.error("Cannot run MadeiraAgent in daemon mode: (%d) %s\n" % (e.errno, e.strerror))
				raise MadeiraAgentException
	
			# Decouple from parent environment.
			os.chdir(".")
			os.umask(0)
			os.setsid()
	
			# Second fork
			try:
				pid = os.fork()
				if pid > 0: 
					# Exit second parent.
					sys.exit(0) 
			except OSError, e:
				logging.error("Cannot run MadeiraAgent in daemon mode: (%d) %s\n" % (e.errno, e.strerror))
				raise MadeiraAgentException
			
			# Open file descriptors and print start message
			si = file('/dev/null', 'r')
			so = file('/dev/null', 'a+')
			se = file('/dev/null', 'a+', 0)
			pid = os.getpid()
			sys.stderr.write("\nStarted MadeiraAgent with pid %i\n\n" % pid)
			sys.stderr.flush()
			if not os.path.exists(os.path.dirname(self.pidfile)):
				os.mkdir(os.path.dirname(self.pidfile))
			file(self.pidfile,'w+').write("%i\n" % pid)

			# Redirect standard file descriptors.
			os.close(sys.stdin.fileno())
			os.close(sys.stdout.fileno())
			os.close(sys.stderr.fileno())
			os.dup2(si.fileno(), sys.stdin.fileno())
			os.dup2(so.fileno(), sys.stdout.fileno())
			os.dup2(se.fileno(), sys.stderr.fileno())
		except OSError, e:
			logging.error("Cannot run MadeiraAgent as daemon: %s" % e)
			raise MadeiraAgentException

	def _key(self):
		try:
			u = urllib.urlopen(self.url_userdata)
			userdata = u.read()
			u.close()
			p = userdata.find("madeira_key=")
			if p < 0:
				raise Exception
			sekf.__key = userdata[p+12:p+20]
		except:
			logging.critical("Failed to retreive agent key from userdata")
			raise MadeiraAgentException

	def _distro(self):
		try:
			f = open('/etc/issue')
			self.__distro = f.readlines()[0].split(' ')[0].lower()
			f.close()
		except:
			logging.crital("Failed to check the distribution")
			raise MadeiraAgentException

	def run(self):
		logging.info("------------------------- Starting MadeiraAgent -------------------------")
		logging.info("Log Level: %s" % self.log_level)
		if self.__daemon:
			logging.info("Log File: %s" % self.log_file)
			logging.info("Log Size: %s" % self.log_size)
			logging.info("Log Rotate: %s" % self.log_rotate)

		try:
			logging.info("Endpoint - Task: %s" % self.endpoint_task)
			logging.info("Endpoint - Health: %s" % self.endpoint_health)
			logging.info("Interval - Task: %d seconds" % self.interval_task)			
			logging.info("Interval - Health: %d seconds" % self.interval_health)

			# task & health
			if not self.__no_task:	 self.__timer.append(RTimer.RTimer(self.interval_task, Task.run, args=[self.endpoint_task, self.__key, self.__distro]))
			if not self.__no_health: self.__timer.append(RTimer.RTimer(self.interval_health, Health.run, args=[self.endpoint_task, self.__key, self.__distro]))
			for t in self.__timer:	t.run()

			# monitor forever
			self._monitor()
		except Exception, e:
			logging.error(e)
			raise MadeiraAgentException

	def reload(self):
		# TODO
		pass

	def exit(self):
		for t in self.__timer:		t.cancel()
		logging.info("------------------------- MadeiraAgent is stopped -----------------------")
		exit()

	def _monitor(self):
		Watcher.run()

#######################  main() #########################
if __name__ == "__main__":
	# Check if a daemon is already running
	pidfile = '/var/lock/subsys/madeiracloud'
	if os.path.exists(pidfile):
		pf  = file(pidfile,'r')
		pid = int(pf.read().strip())
		pf.close()
	 
		try:
			os.kill(pid, signal.SIG_DFL)
		except OSError, (err, msg):
			if err == errno.ESRCH:
			   # Pidfile is stale. Remove it.
				os.remove(pidfile)
			else:
				msg = "Unexpected error when checking pid file '%s'.\n%s\n" %(pidfile, msg)
				sys.stderr.write(msg)
				sys.exit(1)
		else:
			msg = "MadeiraAgent is already running (pid %i)\n" % pid
			sys.stderr.write(msg)
			sys.exit(1)

	# options
	usage = "[-h] [-f] [-t] [-l]"
	optparser = OptionParser(usage=usage)
	optparser.add_option(Option("-f", "--fg", action="store_true",  dest="foreground",
										 help = "Runs in the foreground. Default is background"))
	optparser.add_option(Option("-t", "--no-task", action="store_true",  dest="no_task",
										 help = "If True, the agent will not try to retrieve any task"))
	optparser.add_option(Option("-l", "--no-health", action="store_true",  dest="no_health",
										 help = "If True, the agent will not try to report system health"))
	opt = optparser.parse_args(sys.argv)[0]

	# run
	try:
		agent = MadeiraAgent(not opt.foreground, opt.no_task, opt.no_health)
		agent.run()		
	except:
		print >> sys.stderr, "Failed to launch MadeiraAgent, please check log file"
		exit(1)

