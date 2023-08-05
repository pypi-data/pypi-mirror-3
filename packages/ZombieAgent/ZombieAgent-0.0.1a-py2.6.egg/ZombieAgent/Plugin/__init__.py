from ZombieAgent import state
from ZombieAgent.exceptions import ZombieAgentException
from Manifest import PluginManifest
import os

class PluginNotFound(ZombieAgentException): pass

def find(name=None):
	plugins = []
	manifests = []
	
	for path in state.PLUGIN_PATH:
		try:
			for f in os.listdir(path):
				file_name = os.path.realpath('%s/%s/manifest.json' % (path, f))
				if os.path.isfile(file_name):
					manifests.append(file_name)
		except OSError: pass
	
	for manifest in manifests:
		try:
			plugins.append(PluginManifest(manifest))
		except: pass
	
	if name == None:
		return plugins
	else:
		for plugin in plugins:
			if plugin.name == name:
				return plugin
		
		raise PluginNotFound('Plugin "%s" was not found' % name)