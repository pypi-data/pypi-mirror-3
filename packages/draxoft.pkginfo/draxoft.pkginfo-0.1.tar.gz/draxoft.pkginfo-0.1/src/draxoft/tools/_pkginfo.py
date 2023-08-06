#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description='Extract package metadata from FILE.')
parser.add_argument('-f', '--file',
                    metavar='FILE', type=argparse.FileType(),
                    help='the setup file to parse (defaults to ./setup.py)',
                    default='setup.py')
lk = parser.add_argument_group('key list (-l) options',
                               'Controls output when listing metadata keys.')

parser.add_argument('-l', '--list-keys', action='store_true',
                    help='list all available metadata keys and exit')
lk.add_argument('-t', '--show-types', action='store_true',
                    help='show types when listing available metadata keys')
lk.add_argument('-v', '--show-values', action='store_true',
                    help='show values when listing available metadata keys')
parser.add_argument('-V', '--version', action='version',
                    version='%(prog)s version 0.1')
parser.add_argument('formats', metavar='FORMAT', type=str,
                    nargs=argparse.REMAINDER,
                    help='output format string')

def main(args=None):
    from . import pkginfo
    args = args or parser.parse_args()
    try:
        metadata = pkginfo.parse_setup(args.file.read())
    except IOError, ex:
        parser.error(ex.args[1])
    if (args.list_keys):
        print 'Available metadata keys:'
        if args.show_types:
            fmt = ' * {key} ({type})'
        else:
            fmt = ' * {key}'
        if args.show_values:
            fmt += '\n   {value}'
        for key in sorted(metadata):
            val = metadata[key]
            args = dict(key=key, value=val, type=type(val).__name__)
            print fmt.format(**args)
        return 0
    if not args.formats:
        parser.error('too few arguments')
    for format in args.formats:
        print format.format(**metadata)
    return 0
