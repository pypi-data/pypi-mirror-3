#!/usr/bin/python26

# -------------------------------------------------------------------------- #
# Copyright 2011, MadeiraCloud (support@madeiracloud.com)                  	 #
# -------------------------------------------------------------------------- #
import time
import signal
import asyncore
import threading
import pyinotify

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_MODIFY(self, event):
		print "Creating:", event.pathname

	def process_IN_DELETE(self, event):
		print "Removing:", event.pathname

def run():
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_DELETE | pyinotify.IN_MODIFY  # watched events

	notifier = pyinotify.AsyncNotifier(wm, EventHandler())
	wm.add_watch('/etc/host.conf', mask, rec=True)
	wm.add_watch('/etc/nssolve.conf', mask, rec=True)
	#wm.add_watch('/etc/resolv.conf', mask, rec=True)

	asyncore.loop()
