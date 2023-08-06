"""
settings

Settings module for cooker
"""
import os
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.readfp(open('/etc/cooker/config.cfg'))
CONFIG.read(os.path.expanduser('~/.cooker.cfg'))

TEMPLATES   = os.path.expanduser(CONFIG.get('main', 'templates'))
VERBOSE     = CONFIG.getboolean('main', 'verbose')

LANG        = CONFIG.get('defaults', 'language')
DIRECTORY   = os.path.expanduser(CONFIG.get('defaults', 'directory'))
CONTEST     = CONFIG.get('defaults', 'contest')
SITE        = CONFIG.get('defaults', 'site')
