"""
utility methods for PaInt
"""

# TODO: in general, these should be upstreamed to
# python's standard library or equivalent methods
# from python's standard library used instead of
# having yet another utils.py file.

# Until that magical day, we'll put them here

def isURL(path_spec):
    return '://' in path_spec
