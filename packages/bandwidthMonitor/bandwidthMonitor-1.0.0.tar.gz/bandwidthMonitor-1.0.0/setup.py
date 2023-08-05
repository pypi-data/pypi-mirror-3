from distutils.core import setup


setup(
  name 		= 'bandwidthMonitor',
  version 	= '1.0.0',
  py_modules 	= ['bandwidthMonitor'],
  author 	= 'master',
  author_email  = 'master@cardiffgiant.org',
  url 		= 'www.cardiffgiant.org',
  description	= 'A collection of methods to interface with a rrd file containing data on bandwidth usage via /proc/net/dev.'
)
