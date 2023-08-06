"""
settings

Settings module for cooker
"""
import os
import ConfigParser

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read('/etc/cooker/config.cfg')

TEMPLATES_DIR = os.path.expanduser(
                    CONFIG.get('main', 'templates_dir'))
LANG          = CONFIG.get('defaults', 'language')
CONTEST       = CONFIG.get('defaults', 'contest')
SITE          = CONFIG.get('defaults', 'site')
