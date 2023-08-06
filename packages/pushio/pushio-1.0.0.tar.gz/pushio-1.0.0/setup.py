from distutils.core import setup
setup(
	name = 'pushio',
	packages = ['pushio'],
	version = '1.0.0',
	description = 'Push IO API interface',
	author='Push IO LLC',
	author_email = "info@push.io",
	url = "http://wwww.push.io/",
	download_url = "http://cdn.push.io/download/pushio-1.0.0.tgz",
	keywords = ["pushio", "push", "notifications"],
	classifiers = [
	   	"Programming Language :: Python",
		"Programming Language :: Python :: 2",
	        "Programming Language :: Python :: 3",
        	"Development Status :: 4 - Beta",
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"Topic :: Internet :: WWW/HTTP",
		"License :: OSI Approved :: BSD License",	
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Other/Nonlisted Topic",
        ],
    long_description = """\
Push IO push notification module
--------------------------------
This library makes it easy to send push notifications via the Push IO service.

This version requires Python 2 or later.
"""
)
