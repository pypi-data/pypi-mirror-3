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



__major_version__ = 0
__minor_version__ = 3
__release_version__ = 5
__svn_revision__ = '$Revision: 3114 $' # auto-magically updated by subversion using keywords property

__version__ = '%d.%d' % (__major_version__, __minor_version__)
__release__ = '%d.%d.%d' % (__major_version__, __minor_version__, __release_version__)

def version_string():
    return '%s %s' % (__release__, __svn_revision__)

