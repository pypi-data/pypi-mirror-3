#
# Copyright John Reid 2010
#


"""
pybool
======

A package to infer Boolean regulatory relationships.
"""



__version_major__  = 1
__version_minor__  = 2
__version_change__ = 0
__version_tuple__  = (__version_major__, __version_minor__, __version_change__)
__version__ = '%d.%d.%d' % __version_tuple__
__svn_revision__ = '$Revision: 2955 $' # auto-magically updated by subversion using keywords property

def version_string():
    return '%s %s' % (__version__, __svn_revision__)

