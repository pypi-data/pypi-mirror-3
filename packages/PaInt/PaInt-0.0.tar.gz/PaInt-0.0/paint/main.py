#!/usr/bin/env python

"""
python PAckage INTrospection
"""

import sys
import optparse
import tempfile

class InspectPackages(object):
    def __init__(self):
        pass

    def dependencies(self, *packages):
        if len(packages) > 1:
            retval = set()
            for package in packages:
                retval += self.dependencies(package)
        else:
            raise NotImplementedError

    def cleanup(self):
        pass
    __del__ = cleanup

def main(args=sys.argv[:]):

    # parse command line options
    usage = '%prog [options]'

    # description formatter
    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        def format_description(self, description):
            if description:
                return description + '\n'
            else:
                return ''

    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    options, args = parser.parse_args(args)

if __name__ == '__main__':
    main()
