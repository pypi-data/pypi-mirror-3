import argparse
import logging
import os
import sys

from shrink import get_version
from shrink import utils
from shrink.parser import Parser
from shrink.parser import ParserError
from shrink.utils import JAVA_BIN
from shrink.utils import YUI_JAR

DEFAULT_CFG = 'shrink.cfg'

LOG = logging.getLogger('shrink')


def get_argument_parser():
    """Get a new ArgumentParser for current shrink parameters

    """
    usage = 'shrink [options] (section [section ..] | all)'
    desc = 'Minify css and javascript files using an external minifier'

    # initialize help text for all arguments
    help = {}
    help['cfg_file'] = 'shrink config file [default: %s]' % DEFAULT_CFG
    help['java_bin'] = 'java binary file [default: %s]' % JAVA_BIN
    help['yui_jar'] = 'yui compressor jar file [default: %s]' % YUI_JAR
    help['list_sections'] = 'list all config file sections'
    help['hash'] = 'use all files to create "shrink.sha1" hash file'
    help['debug'] = 'enable debugging messages'
    help['verbose'] = 'show yuicompressor errors'
    help['quiet'] = 'only output errors to console'
    help['version'] = 'output version information and exit'
    help['section'] = ('section name(s) to minify, or "all" '
                       'to minifiy all files')

    parser = argparse.ArgumentParser(usage=usage, description=desc)
    parser.add_argument('-f', '--cfg-file', dest='cfg_file',
                        help=help['cfg_file'])
    parser.add_argument('-j', '--java-bin', dest='java_bin',
                        help=help['java_bin'])
    parser.add_argument('-y', '--yui-jar', dest='yui_jar',
                        help=help['yui_jar'])
    parser.add_argument('-l', '--list-sections', action='store_true',
                        dest='list_sections', help=help['list_sections'])
    parser.add_argument('-a', '--hash-all', action='store_true', dest='hash',
                        help=help['hash'])
    parser.add_argument('-d', '--debug', action='store_true', dest='debug',
                        help=help['debug'])
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose', help=help['verbose'])
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help=help['quiet'])
    parser.add_argument('--version', dest='version', action='store_true',
                        help=help['version'])
    parser.add_argument('sections', nargs='*', metavar='section',
                        help=help['section'])

    return parser


def print_config_sections(parser):
    """Print all sections in a config file for a given parser

    """
    for line in parser.list_all_sections():
        print line


def run():
    """Main entry point for shrink command

    """
    # parse shrink command arguments
    arg_parser = get_argument_parser()
    args = arg_parser.parse_args()

    # init config file absolute path
    cfg_file = (args.cfg_file or DEFAULT_CFG)
    cfg_file = os.path.abspath(cfg_file)

    if args.version:
        print 'Shrink %s' % get_version()
        sys.exit()
    elif not (args.sections or args.list_sections):
        #when no section name(s) is given or no section
        #listing is being made print command help and exit
        arg_parser.print_help()
        sys.exit()

    cfg_file_exists = os.path.isfile(cfg_file)
    if args.cfg_file and not cfg_file_exists:
        # when config file argument exist but
        # file does not inform user and exit
        print (u'File %s does not exist' % cfg_file)
        sys.exit(1)

    try:
        parser = Parser(cfg_file, args)
        utils.init_logging(options=parser.args)
        # print message when using default config file
        if not args.cfg_file:
            LOG.info(u'Using config file %s', cfg_file)

        if args.list_sections:
            # list config file sections (--list-sections)
            print_config_sections(parser)
        else:
            # by default parse config file and minify
            parser.parse()
    except ParserError, err:
        LOG.error(err)
        sys.exit(1)

    sys.exit()
