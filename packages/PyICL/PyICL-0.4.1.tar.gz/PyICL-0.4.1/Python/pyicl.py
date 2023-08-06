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

import os

_version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')
__release__ = open(_version_filename).read().strip()
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__svn_revision__ = '$Revision: 3123 $' # auto-magically updated by subversion using keywords property
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    return '%s %s' % (__release__, __svn_revision__)

