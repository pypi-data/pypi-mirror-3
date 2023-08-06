#!/usr/bin/env python
from __future__ import print_function
import argparse
import ast
import operator
import pprint
import sys
import traceback
import xmlrpclib


def literal_or_string(s):
    try:
        return ast.literal_eval(s)
    except:
        return s


def main():
    parser = argparse.ArgumentParser(
        description="XML-RPC Fiddler",
        fromfile_prefix_chars='@',
        epilog="""Arguments may also be read from a file, specified with
               @filename."""
    )
    parser.add_argument('url', help="base URL of the XML-RPC interface")
    parser.add_argument('method', help="method name")
    parser.add_argument(
        'params', metavar='parameter', nargs='*',
        help="parameter, will be interpreted as Python literal if possible")
    parser.add_argument(
        '-p', '--print', action='store_true',
        help="just print, don't pretty-print")
    parser.add_argument(
        '--traceback', action='store_true',
        help="print tracebacks for exceptions"
    )
    args = parser.parse_args()

    try:
        proxy = xmlrpclib.ServerProxy(args.url)
        arguments = [literal_or_string(param) for param in args.params]
        result = operator.attrgetter(args.method)(proxy)(*arguments)
    except xmlrpclib.Fault as fault:
        print("Fault {0.faultCode:d}: {0.faultString:s}".format(fault),
              file=sys.stderr)
        return fault.faultCode
    except KeyboardInterrupt:
        print("-- interrupted --", file=sys.stderr)
        return 1
    except Exception as exc:
        if args.traceback:
            traceback.print_exc()
        else:
            print(*traceback.format_exception_only(type(exc), exc),
                  sep="", end="", file=sys.stderr)
        return 1
    else:
        if args.print:
            print(result)
        else:
            pprint.pprint(result)
        return 0

if __name__ == '__main__':
    sys.exit(main())
