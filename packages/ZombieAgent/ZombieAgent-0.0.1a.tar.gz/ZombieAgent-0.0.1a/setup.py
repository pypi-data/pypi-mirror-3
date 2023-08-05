#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

readme = open('README').read()
version = open('VERSION').read()

long_description = """
%s

----

For more information, please see the ZombieAgent website or execute ``zombie-agent --help``.
""" % (readme)

setup(
	name='ZombieAgent',
	version=version,
	description='.',
	long_description=long_description,
	author='Slava Yanson',
	author_email='slava@killerbeaver.net',
	url='http://www.killerbeaver.net',
	packages=find_packages(),
	install_requires=[
			'argparse',
			'jinja2',
			'prettytable',
			'wsgi-jsonrpc'
		],
	entry_points={
		'console_scripts': [
			'zombie-agent = ZombieAgent.main:main',
		]
	},
	classifiers=[
  		'Development Status :: 2 - Pre-Alpha',
  		'Environment :: Console',
  		'Intended Audience :: Developers',
  		'Intended Audience :: System Administrators',
  		'License :: OSI Approved :: MIT License',
  		'Operating System :: MacOS :: MacOS X',
  		'Operating System :: Unix',
  		'Operating System :: POSIX',
  		'Programming Language :: Python',
  		'Topic :: Software Development :: Libraries',
  		'Topic :: Software Development :: Libraries :: Python Modules',
  		'Topic :: System :: Clustering',
  		'Topic :: System :: Installation/Setup',
  		'Topic :: System :: Logging',
  		'Topic :: System :: Monitoring',
  		'Topic :: System :: Networking :: Monitoring',
  		'Topic :: System :: Software Distribution',
  		'Topic :: System :: Systems Administration',
	]
)