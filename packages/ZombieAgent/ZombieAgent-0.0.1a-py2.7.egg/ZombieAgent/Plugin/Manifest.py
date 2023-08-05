from ZombieAgent.exceptions import ZombieAgentException
from ZombieAgent.Plugin.Parser import shellquote, parse_cli_params
import os
import shlex, subprocess
import logging
from jinja2 import Template
import json


class PluginManifestException(ZombieAgentException): pass
class PluginManifestParseException(ZombieAgentException): pass
class FunctionNotFound(ZombieAgentException): pass
class ExecutionError(ZombieAgentException): pass
class ParameterRequired(ZombieAgentException): pass


class PluginManifest(object):
	basedir = ''
	name = 'Unnamed Plugin'
	author = 'Unknown Author'
	copyright = ''
	license = ''
	version = 'Unknown'
	description = ''
	
	requires = []
	provides = {}
	
	def __init__(self, manifest_file):
		try:
			self.basedir = os.path.abspath(manifest_file.split('/manifest.json')[0])
			
			manifest = open(manifest_file)
			parsed = json.loads(manifest.read())
			manifest.close()
			
			for x in parsed.keys():
				setattr(self, x, parsed[x])
			
			self.logger = logging.getLogger('ZombieAgent.Plugin.%s' % self.name)
		except Exception, e:
			raise PluginManifestParseException(e)
	
	def execute(self, function, params=''):
		self.logger.debug('Executing function "%s" with parameters %s' % (function, params))
		if function not in self.provides:
			raise FunctionNotFound('Function "%s" was not found' % function)
		
		function_def = self.provides[function]
		
		params_parsed = {}
		params_cmd = []
		params_preparsed = parse_cli_params(params)
		
		for param in function_def['params']:
			pdef = function_def['params'][param]
			
			if 'required' in pdef \
				and pdef['required'] \
				and param not in params_preparsed.keys() \
				and 'default' not in pdef:
				raise ParameterRequired('Parameter "%s" is required' % param)
			
			elif 'default' in pdef \
				and param not in params_preparsed.keys():
				params_parsed[param] = pdef['default']
			
			elif param in params_preparsed.keys():
				params_parsed[param] = params_preparsed[param]
		
		_params_parsed = {}
		for param in params_parsed.keys():
			template = Template(params_parsed[param])
			_params_parsed[param] = shellquote(template.render(**params_parsed))
		
		params_parsed = _params_parsed
		del _params_parsed
		
		for param in params_parsed:
			pdef = function_def['params'][param]
			
			if 'param' in pdef:
				params_cmd.append('%s %s' % (pdef['param'], params_parsed[param]))
			else:
				params_cmd.append('--%s %s' % (param, params_parsed[param]))
		
		command = '/bin/bash -ex %s %s' % (function_def['script'], ' '.join(params_cmd))
		
		proc = subprocess.Popen(command, \
			cwd=self.basedir, \
			universal_newlines=True, \
			shell=True, \
			stdout=subprocess.PIPE, \
			stderr=subprocess.STDOUT)
		
		proc.wait()
		
		lines = proc.stdout.read().split('\n')
		
		debug = []
		output = []
		
		for line in lines:
			if line.strip() != '':
				if line.startswith('+'):
					debug.append(line.split('+', 2)[1].strip())
				else:
					output.append(line.rstrip())
		
		if proc.returncode != 0:
			raise ExecutionError('\n'.join(output))
		
		self.logger.debug('\n'.join(lines))
		
		return (output, debug)
		
	def __repr__(self):
		return '<"%s" ZombieAgent plugin>' % self.name