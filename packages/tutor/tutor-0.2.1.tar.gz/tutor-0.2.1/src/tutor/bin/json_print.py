#!/usr/bin/env python
import sys
import pyson
import argparse
from fs.opener import fsopen
import tutor.version

#===============================================================================
# Main Parser
#===============================================================================
parser = argparse.ArgumentParser(
  description='Pretty print JSON files.',
  prog='json-print', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

parser.add_argument('name', help='JSON filename')
parser.add_argument('--human-friendly', '-f', '-H',
  action='store_true', help='exhibit JSON structure in a human-friendly format')


#===============================================================================
# Pretty print content of JSON file
#===============================================================================
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    try:
        with fsopen(args.name.decode('utf8')) as F:
            obj = pyson.load(F)
    except Exception as ex:
        raise SystemExit(ex)

    if args.human_friendly:
        pyson.simpleprint(obj)
    else:
        pyson.pprint(obj)

if __name__ == '__main__':
    main(['-h'])
