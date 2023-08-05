#!/usr/bin/env python

from optparse import OptionParser as BaseOptionParser, make_option
import os
import os.path
import sys

my_path = os.path.abspath(os.path.dirname(__file__))
sys.path = [path for path in sys.path if os.path.abspath(path) != my_path]

from stadjic.startproject import start_project


class OptionParser(BaseOptionParser):
    def parse_args(self, args, values=None):
        # Require an args parameter
        return BaseOptionParser.parse_args(self, args, values)
    
    def max_args(self, max_count, args):
        if len(args) > max_count:
            self.error('Too many arguments')


def main():
    parser = OptionParser(usage='%prog SUBCOMMAND [OPTIONS]', option_list=(
        make_option('-d', '--debug', action='store_true', default=False),
    ))
    parser.disable_interspersed_args()
    options, args = parser.parse_args(sys.argv[1:])
    
    if len(args) < 1:
        parser.error('Expected a subcommand')
    
    subcommand_name = args.pop(0)
    subcommand = globals().get('%s_cmd' % (subcommand_name,))
    if subcommand is None:
        parser.error('Unknown subcommand "%s"' % (subcommand_name,))
    
    try:
        subcommand(args)
    except BaseException, e:
        if isinstance(e, SystemExit):
            raise
        elif options.debug:
            raise
        else:
            print '!%s!' % e
            sys.exit(1)


def setup_django_env(path):
    if not os.path.isdir(path):
        raise Exception('Directory "%s" does not exist' % (path,))
    
    project_name = os.path.basename(os.path.abspath(path))
    sys.path.insert(0, os.path.join(path, '..'))
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % (project_name,)


def start_cmd(args):
    parser = OptionParser(usage='%prog start PROJECTPATH [OPTIONS]')
    options, args = parser.parse_args(args)
    parser.max_args(1, args)
    
    if len(args) < 1:
        parser.error('Expected a PROJECTPATH')
    
    start_project(args[0])


def serve_cmd(args):
    parser = OptionParser(usage='%prog serve [PATH] [OPTIONS]')
    options, args = parser.parse_args(args)
    parser.max_args(2, args)
    
    if len(args) < 1:
        path = '.'
    else:
        path = args[0]
    
    setup_django_env(path)
    
    from django.core.management import call_command
    call_command('runserver')


def build_cmd(args):
    parser = OptionParser(usage='%prog build [PATH] OUTPUTPATH [OPTIONS]')
    options, args = parser.parse_args(args)
    parser.max_args(2, args)
    
    if len(args) < 2:
        path = '.'
    else:
        path = args.pop(0)
    
    if len(args) < 1:
        parser.error('Expected an OUTPUTPATH')
    else:
        output_path = args.pop(0)
    
    setup_django_env(path)
    
    from stadjic.buildstatic import build_static
    
    build_static(output_path)


if __name__ == '__main__':
    main()
