from distutils.core import setup


setup(
  name 		= 'bandwidthTracker',
  version 	= '1.0.0',
  py_modules 	= ['bandwidthTracker'],
  author 	= 'master',
  author_email  = 'master@cardiffgiant.org',
  url 		= 'www.cardiffgiant.org',
  description	= 'A class with methods to interface with a rrd file containing data on bandwidth usage via /proc/net/dev.'
)
