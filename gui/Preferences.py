#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class PreferencesException(Exception):
	''' Exceptiion raised when config file has wrong format '''
	def __init__(self):
		pass

class Preferences:
	'''Class saving the preferences of the local user'''
	def __init__(self, filename):
		f = open(filename)
		line = f.readline().split(':')
		if len(line) != 3 or line[0] != 'username':
			raise PreferencesException()
		
		self.username = line[1]
		#print(self.username)

P = Preferences('preferences.cfg')
