#
# Copyright John Reid 2011, 2012
#

import pkg_resources as _pkg_resources

__doc__ = _pkg_resources.resource_string(__name__, "README")
__license__ = _pkg_resources.resource_string(__name__, "LICENSE")
__release__, __svn_revision__ = _pkg_resources.resource_string(__name__, "VERSION").strip().split('-')
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    """Return the release and svn revision as a string."""
    return '%s %s' % (__release__, __svn_revision__)


class Set(set):
    """A set class that implements += and -= as the pyicl package expects.
    """
    
    def __iadd__(self, other):
        """Set union operation. Does not update self
        """
        return self | other
    
    def __iand__(self, other):
        """Set intersection operation. Does not update self
        """
        return self & other

    def __ior__(self, other):
        """Set union operation. Does not update self
        """
        return self | other
    
    def __isub__(self, other):
        """Set subtraction operation. Does not update self
        """
        return self - other

    def __ixor__(self, other):
        """Set exclusive-or operation. Does not update self
        """
        return self ^ other

    



#from functools import wraps
#def my_simple_logging_decorator(func):
#    @wraps(func)
#    def you_will_never_see_this_name(*args, **kwargs):
#        print 'calling {}'.format(func.__name__)
#        return func(*args, **kwargs)
#    return you_will_never_see_this_name
#  
#import types, inspect
#for name, fn in inspect.getmembers(Set):
#    if isinstance(fn, types.UnboundMethodType):
#        setattr(Set, name, my_simple_logging_decorator(fn))
#
#
#def __trace__(frame, event, arg):
#    print event
#    if event == "call":
#        filename = frame.f_code.co_filename
#        lineno = frame.f_lineno
#        print "%s @ %s" % (filename, lineno)
#        #print arg
#    return __trace__



#
# Load everything in extension module.
#
from _pyicl import *

