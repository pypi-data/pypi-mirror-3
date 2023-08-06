/** Copyright John Reid 2010, 2011
*/


#include <pyicl/interval_bounds.h>
#include <pyicl/interval.h>


/**
 * Expose interval bounds and intervals.
 */
void
expose_intervals()
{
	using namespace ::pyicl;
	namespace bp = ::boost::python;
	namespace icl = ::boost::icl;

    interval_bounds_exposer::expose( "IntervalBounds", "Types of bounds on intervals." );

	expose_interval_types< float, ICL_COMPARE_INSTANCE( std::less, float ) >( "FloatInterval", "float" );
	expose_interval_types< int  , ICL_COMPARE_INSTANCE( std::less, int   ) >( "IntInterval"  , "int"   );
}
