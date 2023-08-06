/** Copyright John Reid 2010, 2011
*/


#include <pyicl/pyicl.h>
#include <iostream>

void expose_intervals();
void expose_interval_sets();
void expose_interval_maps();

BOOST_PYTHON_MODULE( _pyicl )
{
	namespace bp = ::boost::python;

#ifndef NDEBUG
	bp::scope().attr( "__debug__" ) = 1;
	std::cout << "WARNING: Debug version of _pyicl module loaded. If you did not intend this then check your configuration!" << std::endl;
#else //_DEBUG
	bp::scope().attr( "__debug__" ) = 0;
#endif //_DEBUG


	expose_intervals();
	expose_interval_sets();
	expose_interval_maps();
}
