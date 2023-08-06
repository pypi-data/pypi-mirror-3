#!/usr/bin/env python
"""Build a web site from a set of reStructuredText source files.

This module merely contains the ``main()`` function.

$Id: sohobuild.py 54 2008-02-17 13:23:24Z damien.baty $
"""

import sys
import os.path
import logging
from optparse import OptionParser
from ConfigParser import SafeConfigParser, NoOptionError

try:
    import pygments
    HAS_PYGMENTS = True
    del pygments ## This is only a test, we do not need anything.
except ImportError:
    HAS_PYGMENTS = False

import soho.config
from soho.config import *
from soho.builder import Builder, registerPygmentsDirective


__version__ = '0.7'


def main():
    """Read options from the command-line or a configuration file and
    build the site.

    Precedence:

    1. Command-line options.
    2. Options defined in the configuration file.
    3. Default values.
    """
    ## Set up optparse
    parser = OptionParser(usage='%prog [options]',
                          version='%%prog %s' % __version__)
    ao = parser.add_option
    ao('-c',
       metavar="CONFIG-FILE",
       help='Use CONFIG-FILE. '\
            'Default value is "%s".' % DEFAULT_CONFIG_FILE,
       default=None,
       dest='config_file')
    ao('-i',
       metavar='SOURCE-DIRECTORY',
       help='Read files from SOURCE-DIRECTORY. '\
            'Default value is "%s".' % DEFAULT_IN_DIR,
       default=None,
       dest='in_dir')
    ao('-o',
       metavar='OUTPUT-DIRECTORY',
       help='Write files in OUTPUT-DIRECTORY. '\
            'Default value is "%s".' % DEFAULT_OUT_DIR,
       default=None,
       dest='out_dir')
    ao('-t',
       metavar='TEMPLATE-FILE',
       help='Use FILE as the template. '\
            'Default value is "%s".' % DEFAULT_TEMPLATE,
       default=None,
       dest='template')
    ao('--bindings',
       metavar='BINDINGS-FILE',
       help='Use FILE as the bindings module.',
       default=None,
       dest='bindings')
    ao('--filters',
       metavar='FILTERS-FILE',
       help='Use FILE as the filters module.',
       default=None,
       dest='filters')
    ao('-l',
       metavar='LOG-FILE',
       help='Log in LOG-FILE. Default behaviour is to log to the '\
            'standard output.',
       default=None,
       dest='logfile')
    ao('-f', '--force',
       help='Force all files to be processed, even if source files '\
            'are older than generated files.',
       dest='force',
       action='store_true')
    ao('-d', '--dry-run', '--do-nothing',
       help='Dry run: do not create or copy any files or directories.',
       dest='do_nothing',
       action='store_true')

    (options, args) = parser.parse_args()

    ## Get settings from the configuration file
    settings = {}
    if options.config_file is not None:
        exitIfFileNotExists(options.config_file)
        settings = getSettingsFromConfigFile(options.config_file)
    elif os.path.exists(DEFAULT_CONFIG_FILE):
        settings = getSettingsFromConfigFile(DEFAULT_CONFIG_FILE)

    (options, args) = parser.parse_args()
    options = options.__dict__

    ## Add default values for options that cannot be changed from the
    ## command-line.
    options['ignore_files'] = None
    options['ignore_directories'] = None

    ## Complete and override settings read in the configuration file
    ## by the ones provided by the user via the command-line.
    for option, value in options.items():
        if value is not None:
            ## Use value provided via the command-line
            settings[option] = value
        elif not settings.get(option):
            ## Use default value for this missing option
            settings[option] = getattr(soho.config,
                                       'DEFAULT_' + option.upper())

    ## Set main logger settings
    log_settings = {'level': LOGGING_LEVEL,
                    'format': LOGGING_FORMAT,
                    'datefmt': LOGGING_DATE_FORMAT}
    if settings.get('logfile') is not None:
        log_settings['filename'] = settings['logfile']
    logging.basicConfig(**log_settings)

    ## We do not need the configuration file and the logfile anymore
    del settings['config_file']
    del settings['logfile']

    ## Check files and directory existence
    for filename in (settings['in_dir'], settings['template'],
                     settings['bindings'], settings['filters']):
        if filename is not None:
            exitIfFileNotExists(filename)
    if not os.path.isdir(settings['in_dir']):
        logging.error('Given input directory ("%s") is not '\
                      'a directory.', settings['in_dir'])
        logging.error('Process has been aborted.')
        sys.exit(1)

    if HAS_PYGMENTS:
        registerPygmentsDirective()

    builder = Builder(**settings)
    builder.build()


def exitIfFileNotExists(filename):
    if not os.path.exists(filename):
        logging.error('Could not find file or directory: "%s".',
                      filename)
        logging.error('Process has been aborted.')
        sys.exit(1)


def getSettingsFromConfigFile(config_file):
    """Return settings as a mapping."""
    config = SafeConfigParser()
    config.read(config_file)
    settings = {}
    for option, value in config.items('main'):
        if option in BOOLEAN_SETTINGS:
            if value.lower() in ('0', 'false'):
                value = False
            elif value.lower() in ('1', 'true'):
                value = True
        elif option in REGEXP_SETTINGS:
            value = re.compile(value)
        elif option in PATH_SETTINGS:
            value = os.path.expanduser(value)
        settings[option] = value

    return settings


if __name__ == '__main__':
    main()
