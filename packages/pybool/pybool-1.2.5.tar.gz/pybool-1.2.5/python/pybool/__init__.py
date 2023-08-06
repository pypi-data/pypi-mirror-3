#
# Copyright John Reid 2010, 2011, 2012
#


import pkg_resources

__doc__ = pkg_resources.resource_string(__name__, "README")
__license__ = pkg_resources.resource_string(__name__, "LICENSE")
__release__ = pkg_resources.resource_string(__name__, "VERSION").strip()
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__svn_revision__ = '$Revision: 3132 $' # auto-magically updated by subversion using keywords property
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    """Return the release and svn revision as a string."""
    return '%s %s' % (__release__, __svn_revision__)

