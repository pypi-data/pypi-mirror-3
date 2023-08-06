"""Default settings of Soho.

$Id: config.py 49 2007-10-29 13:16:25Z damien.baty $
"""

import re
import logging


## Docutils-related settings
SOURCE_SUFFIXES = ('.txt', '.rst')
ENCODING = 'utf-8'
DOCUTILS_SETTINGS = {'strip_comments': True,
                     'output_encoding': ENCODING,
                     'initial_header_level': 2}

## Logging settings
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

## Soho default settings
DEFAULT_CONFIG_FILE = 'soho.conf'
DEFAULT_IN_DIR = 'src'
DEFAULT_OUT_DIR = 'www'
DEFAULT_TEMPLATE = 'main_template.pt'
DEFAULT_BINDINGS = None
DEFAULT_FILTERS = None
DEFAULT_LOGFILE = None
DEFAULT_FORCE = False
DEFAULT_DO_NOTHING = False
DEFAULT_IGNORE_DIRECTORIES = re.compile('.*\.svn.*')
DEFAULT_IGNORE_FILES =  re.compile('(\.DS_Store)|(.*~$)')

BOOLEAN_SETTINGS = ('do_nothing', 'force')
REGEXP_SETTINGS = ('ignore_directories', 'ignore_files')
PATH_SETTINGS = ('in_dir', 'out_dir', 'template',
                 'bindings', 'filters', 'logfile')
