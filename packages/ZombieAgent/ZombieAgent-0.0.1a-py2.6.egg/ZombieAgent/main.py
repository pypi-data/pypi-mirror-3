#!/usr/bin/env python

import ZombieAgent.CLI
import sys
import logging

def main():
	logging.basicConfig(level=logging.DEBUG)
	log = logging.getLogger('ZombieAgent')
	
	try:
		ZombieAgent.CLI.parse()
		return 0
	except Exception, e:
		log.exception('')
		return 1

if __name__ == '__main__':
	sys.exit(main())