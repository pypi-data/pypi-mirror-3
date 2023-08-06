#!/usr/bin/env python

"""
python PAckage INTrospection
"""

import commandparser
import package
import sys

def main(args=sys.argv[1:]):

    parser = commandparser.CommandParser(package.Package)
    parser.invoke(args)

if __name__ == '__main__':
    main()
