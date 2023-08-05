import os

PLUGIN_PATH = [
	os.path.realpath('.'),
	os.path.realpath('plugins'),
	os.path.realpath('../plugins'),
	'/etc/ZombieAgent/plugins',
	'/opt/ZombieAgent/plugins'
]