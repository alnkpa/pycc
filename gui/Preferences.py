# -*- coding: utf-8 -*-

class PreferencesException(Exception):
	''' Exceptiion raised when config file has wrong format '''
	def __init__(self):
		pass

class Preferences:
	'''Class saving the preferences of the local user'''
	def __init__(self, config):
		self.config = config
		self.prefs = {}

		fObj = open(self.config, 'r')
		for line in fObj:
			line = line.split(':')
			if len(line) != 3:
				raise PreferencesException()
			self.prefs[line[0]] = line[1]
		fObj.close()

	def setPreferences(self, username, textcolor):
		self.prefs['username'] = username
		self.prefs['textcolor'] = textcolor
		fObj = open(self.config, 'w')
		for key in self.prefs:
			fObj.write('{0}:{1}:\n'.format(key,self.prefs[key]))
		fObj.close
