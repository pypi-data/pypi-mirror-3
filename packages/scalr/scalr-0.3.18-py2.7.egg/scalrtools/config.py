'''
Created on Feb 21th, 2011

@author: Dmytro Korsakov
'''
import os

from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from prettytable import PrettyTable	

class ScalrCfgError(BaseException):
	pass


class ScalrEnvError(ScalrCfgError):
	pass

	
class ConfigSection(object):
	config_name = None
	options = {}
	
	def __init__(self, **kwargs):
		for arg in kwargs:
			if hasattr(self, arg):
				setattr(self, arg, kwargs[arg])

	def write(self, base_path, section):
		config = ConfigParser()
		
		path = os.path.join(base_path, self.config_name)
		if os.path.exists(path):
			config.read(path)
		elif not os.path.exists(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
			
		if not config.has_section(section):
			config.add_section(section)
		
		for option in self.options:
			config.set(section, self.options[option], getattr(self, option))
			
		file = open(path, 'w')
		config.write(file)
		file.close()
			
	@classmethod
	def from_ini(cls, base_path, section):
		path = os.path.join(base_path, cls.config_name)
		
		if not os.path.exists(path):
			raise ScalrCfgError('%s: Config file not found.' % path)
		
		config = ConfigParser()	
		config.read(path)
		obj = cls()
		setattr(obj, 'name', section)
		
		for option in cls.options:
			try:
				setattr(obj, option, config.get(section, cls.options[option]))
			except (NoSectionError, NoOptionError), e:
				raise ScalrCfgError('%s in %s'%(e, path))
		return obj

	
class Environment(ConfigSection):
	url=None
	key_id=None
	key=None
	api_version = None	
	
	config_name = 'config.ini'
	
	options = dict(
			url = 'scalr_url',
			key_id = 'scalr_key_id',
			key = 'scalr_api_key',
			api_version = 'version')
	
	def write(self, base_path, section='api'):
		super(Environment, self).write(base_path, section)
			
	@classmethod
	def from_ini(cls, base_path, section='api'):
		return super(Environment, cls).from_ini(base_path, section)
	
	def __repr__(self):
		column_names = ('setting','value')
		table = PrettyTable(column_names)
		
		for field in column_names:
			table.set_field_align(field, 'l')		
		
		visible_length = 26

		table.add_row(('url', self.url))
		table.add_row(('access key', self.key[:visible_length]+'...' if len(self.key)>40 else self.key))
		table.add_row(('key id', self.key_id))
		table.add_row(('version', self.api_version))
		return str(table)
	

class Configuration:
	logger = None
	base_path = None
	
	environment = None
	application = None
	repository = None
	scripts = None
	
	def __init__(self, base_path=None, logger=None):
		self.base_path = base_path or os.path.expanduser("~/.scalr/")
		self.logger = logger

	def set_logger(self, logger):
		self.logger = logger
				
	def set_environment(self, key, key_id, url):
		if key and key_id and url:
			self.environment = Environment(key=key, key_id=key_id, url=url)
	
		try:
			self.environment = Environment.from_ini(self.base_path)
		except ScalrCfgError:
			raise ScalrEnvError('Environment not set.')
		
		if not self.environment or not self.environment.key or not self.environment.key_id or not self.environment.url:
			raise ScalrEnvError('Environment not set.')
