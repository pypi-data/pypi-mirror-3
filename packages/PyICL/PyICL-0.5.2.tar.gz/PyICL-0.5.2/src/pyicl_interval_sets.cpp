/** Copyright John Reid 2010, 2011
*/


#include <pyicl/interval_set.h>


/**
 * Expose interval sets.
 */
void
expose_interval_sets()
{
	using namespace ::pyicl;
	namespace bp = ::boost::python;
	namespace icl = ::boost::icl;

	interval_set_exposer< icl::interval_set< int > >::expose( "IntIntervalSet", "A interval set with integer domain." );
	interval_set_exposer< icl::interval_set< float > >::expose( "FloatIntervalSet", "A interval set with floating point domain." );
	interval_set_exposer< icl::split_interval_set< int > >::expose( "IntSplitIntervalSet", "A splitting interval set with integer domain." );
	interval_set_exposer< icl::separate_interval_set< int > >::expose( "IntSeparateIntervalSet", "A separating interval set with integer domain." );
}
