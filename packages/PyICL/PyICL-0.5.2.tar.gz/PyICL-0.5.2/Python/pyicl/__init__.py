#
# Copyright John Reid 2011, 2012
#

import pkg_resources

__doc__ = pkg_resources.resource_string(__name__, "README")
__license__ = pkg_resources.resource_string(__name__, "LICENSE")
__release__, __svn_revision__ = pkg_resources.resource_string(__name__, "VERSION").strip().split('-')
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    """Return the release and svn revision as a string."""
    return '%s %s' % (__release__, __svn_revision__)


class Set(set):
    """A set class that implements += and -= as the pyicl package expects.
    """
    
    def __iadd__(self, other):
        """+=
        """
        return self | other
    
    def __isub__(self, other):
        """-=
        """
        return self - other

#
# Load everything in extension module.
#
from _pyicl import *

