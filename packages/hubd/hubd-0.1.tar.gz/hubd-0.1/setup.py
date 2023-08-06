import os

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'hubd',
	version = '0.1',
	description = 'Real-time JSON MVC Framework',
	url = 'http://hubd.io/',
	author = 'Tim Behrsin',
	author_email = 'tim@behrsin.com',
	maintainer = 'Tim Behrsin',
	maintainer_email = 'tim@behrsin.com',
	keywords = [ 'Hub', 'Hubd', 'PubSub', 'Django', 'Redis', 'JSON', 'Real-Time', 'MVC' ],
	license = 'MIT',
	classifiers = [
		'Development Status :: 1 - Planning',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Communications',
		'Topic :: Database',
		'Topic :: Desktop Environment',
		'Topic :: Internet',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: System :: Clustering',
		'Topic :: System :: Distributed Computing',
		'Topic :: System :: Filesystems',
		'Topic :: System :: Operating System Kernels',
		'Topic :: System :: Software Distribution',
	]
)



