"""
functions for python package indices
"""

import os
import pkginfo

def pypi_path(path):
    """
    returns subpath 2-tuple appropriate for pypi path structure:
    http://k0s.org/portfolio/pypi.html
    """
    sdist = pkginfo.sdist.SDist(path)

    # determine the extension (XXX hacky)
    extensions = ('.tar.gz', '.zip', '.tar.bz2')
    for ext in extensions:
        if sdist.filename.endswith(ext):
            break
    else:
        raise Exception("Extension %s not found: %s" % (extensions, sdist.filename))

    # get the filename destination
    filename = '%s-%s%s' % (sdist.name, sdist.version, ext)
    return sdist.name, filename
