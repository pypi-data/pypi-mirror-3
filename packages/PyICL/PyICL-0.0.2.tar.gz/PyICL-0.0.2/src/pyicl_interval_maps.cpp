/** Copyright John Reid 2010, 2011, 2012
*/


#include <pyicl/interval_map.h>



/**
 * Expose interval maps.
 */
void
expose_interval_maps()
{
	using namespace ::pyicl;
	namespace bp = ::boost::python;
	namespace icl = ::boost::icl;

	interval_map_exposer< icl::interval_map< int, bp::object > >::expose( "IntIntervalObjectMap", "A (joining) map from int intervals to objects." );
	interval_map_exposer< icl::interval_map< int, int > >::expose( "IntIntervalIntMap", "A (joining) map from int intervals to integers." );
	interval_map_exposer< icl::interval_map< int, std::string > >::expose( "IntIntervalStringMap", "A (joining) map from int intervals to strings." );
	interval_map_exposer< icl::interval_map< float, bp::object > >::expose( "FloatIntervalObjectMap", "A (joining) map from float intervals to objects." );
	interval_map_exposer< icl::interval_map< float, int > >::expose( "FloatIntervalIntMap", "A (joining) map from float intervals to integers." );
	interval_map_exposer< icl::interval_map< float, std::string > >::expose( "FloatIntervalStringMap", "A (joining) map from float intervals to strings." );

	interval_map_exposer< icl::split_interval_map< int, bp::object > >::expose( "IntSplitIntervalObjectMap", "A (splitting) map from int intervals to objects." );
	interval_map_exposer< icl::split_interval_map< int, int > >::expose( "IntSplitIntervalIntMap", "A (splitting) map from int intervals to integers." );
	interval_map_exposer< icl::split_interval_map< int, std::string > >::expose( "IntSplitIntervalStringMap", "A (splitting) map from int intervals to strings." );
	interval_map_exposer< icl::split_interval_map< float, bp::object > >::expose( "FloatSplitIntervalObjectMap", "A (splitting) map from float intervals to objects." );
	interval_map_exposer< icl::split_interval_map< float, int > >::expose( "FloatSplitIntervalIntMap", "A (splitting) map from float intervals to integers." );
	interval_map_exposer< icl::split_interval_map< float, std::string > >::expose( "FloatSplitIntervalStringMap", "A (splitting) map from float intervals to strings." );
}
