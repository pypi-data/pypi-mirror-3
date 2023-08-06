#!/usr/bin/env python
# encoding: utf-8

""" CLI tool entry point.
"""

from __future__ import print_function

import json
import sys

import json_tools
from print_style import colorize


def usage():
    _CMDS = {'print': 'Pretty-print a JSON file',
             'diff': 'Diff between two JSON documents',
             'patch': 'Patch a JSON document',
            }
    print("Usage:", sys.argv[0], " <cmd> [options]")
    print("\nAvailable commands:")
    for cmd, info in _CMDS.items():
        print("  ", colorize(cmd, bold=True), "\t", info)


def pretty_print():
    try:
        with open(sys.argv[2]) as f:
            data = json.load(f)
    except IOError:
        print('File not found', file=sys.stderr)
        exit(-1)
    json_tools.print_json(data, '--pretty' in sys.argv)


def diff():
    try:
        with open(sys.argv[2]) as f:
            local = json.load(f)
    except IOError:
        print('Local not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to file not specified', file=sys.stderr)
        exit(-1)

    try:
        with open(sys.argv[3]) as f:
            other = json.load(f)
    except IOError:
        print('Other not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to other file not specified', file=sys.stderr)
        exit(-1)

    res = json_tools.diff(local, other)
    json_tools.print_json(res, '--pretty' in sys.argv)


def patch():
    try:
        with open(sys.argv[2]) as f:
            data = json.load(f)
    except IOError:
        print('Local not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to file not specified', file=sys.stderr)
        exit(-1)

    try:
        with open(sys.argv[3]) as f:
            patch = json.load(f)
    except IOError:
        print('Other not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to other file not specified', file=sys.stderr)
        exit(-1)

    res = json_tools.patch(data, patch)
    json_tools.print_json(res, '--pretty' in sys.argv)


COMMANDS = {
    'print': pretty_print,
    'diff': diff,
    'patch': patch
}


def main():
    if len(sys.argv) < 3:
        usage()
        exit(-1)
    else:
        try:
            COMMANDS[sys.argv[1]]()
        except KeyError:
            print('Bad command:', sys.argv[1], file=sys.stderr)


if __name__ == '__main__':
    main()
