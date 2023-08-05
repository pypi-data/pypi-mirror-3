#!/usr/bin/env python -u

# -------------------------------------------------------------------------- #
# Copyright 2011, MadeiraCloud (support@madeiracloud.com)                  	 #
# -------------------------------------------------------------------------- #
import threading

class RTimer(object):
	def __init__(self, interval, callback, args=[], kwargs={}):
		self.__interval = interval
		self.__callback = callback
		self.__args = args
		self.__kwargs = kwargs
		self.__event = threading.Event()
		self.__timer = threading.Thread(target=self.__serve)

	def __serve(self):
		while not self.__event.is_set():
			self.__event.wait(self.__interval)
			if not self.__event.is_set():
				self.__callback(*self.__args, **self.__kwargs)

	def run(self):
		self.__timer.start()

	def cancel(self):
		self.__event.set()
		self.__timer.join()
