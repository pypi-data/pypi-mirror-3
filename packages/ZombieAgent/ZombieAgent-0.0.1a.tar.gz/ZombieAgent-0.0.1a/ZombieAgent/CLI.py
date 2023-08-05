import argparse
import os
from ZombieAgent import state
import ZombieAgent.Plugin
from prettytable import PrettyTable

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-q', '--quiet', action='store_true')
	parser.add_argument('--plugin-path')
	
	subparsers = parser.add_subparsers()
	
	p = subparsers.add_parser('run', help='execute a function within a plugin')
	p.add_argument('function')
	p.add_argument('params', nargs='*')
	p.set_defaults(func='run')
	
	p = subparsers.add_parser('list', help='list installed plugins')
	p.add_argument('-p', '--plugin')
	p.set_defaults(func='list')
	
	p = subparsers.add_parser('install', help='install a plugin')
	p.set_defaults(func='install')
	
	p = subparsers.add_parser('uninstall', help='uninstall a plugin')
	p.set_defaults(func='uninstall')
	
	args = parser.parse_args()
	
	if args.plugin_path != None:
		state.PLUGIN_PATH.append(os.path.realpath(args.plugin_path))
	
	if args.func == 'list':
		if args.plugin == None:
			plugins = ZombieAgent.Plugin.find()
			
			table = PrettyTable()
			table.set_field_names(['Name', 'Version', 'Author'])
			
			for plugin in plugins:
				table.add_row([plugin.name, plugin.version, plugin.author])
			
			table.printt(sortby='Name')
		else:
			plugin = ZombieAgent.Plugin.find(args.plugin)
			
			print 'Name:         %s' % plugin.name
			print 'Version:      %s' % plugin.version
			print 'Author:       %s' % plugin.author
			print 'Description:  %s' % plugin.description
			print 'Provides:'
			
			for func in plugin.provides:
				print '    %s - %s' % (func, plugin.provides[func]['description'])
	
	elif args.func == 'run':
		plugin_name, function = args.function.split('.', 2)
		plugin = ZombieAgent.Plugin.find(plugin_name)
		plugin.execute(function, args.params)