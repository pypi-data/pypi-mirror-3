#
# Copyright John Reid 2011, 2012
#

"""
Python interface to the Boost Interval Container Library.
"""

#
# Load everything in extension module.
#
from _pyicl import *

import os, pkg_resources

__release__ = pkg_resources.resource_string(__name__, "VERSION").strip()
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__svn_revision__ = '$Revision: 3124 $' # auto-magically updated by subversion using keywords property
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    return '%s %s' % (__release__, __svn_revision__)

