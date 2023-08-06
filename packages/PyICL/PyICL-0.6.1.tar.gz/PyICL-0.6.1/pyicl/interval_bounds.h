/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_BOUNDS_H_JORE_110217
#define PYICL_INTERVAL_BOUNDS_H_JORE_110217

#include <pyicl/base.h>
#include <boost/icl/interval_bounds.hpp>

//
// Make intervals hashable.
//
namespace boost {
namespace icl {

inline
std::size_t
hash_value(
	const ::boost::icl::interval_bounds & x
) {
	return ::boost::hash_value( x.bits() );
}

} // namespace icl
} // namespace boost


namespace pyicl {

struct interval_bounds_exposer {

	/// Expose/register interval bounds.
	static
	void
	expose( char const * name, char const * docstring ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;

		bp::class_< icl::interval_bounds > _class(
			name,
			docstring,
			bp::init<>( "Default constructor." )
		);
		_class.def( "all", &icl::interval_bounds::all );
		_class.def( "left", &icl::interval_bounds::left );
		_class.def( "right", &icl::interval_bounds::right );
		_class.def( "reverse_left", &icl::interval_bounds::reverse_left );
		_class.def( "reverse_right", &icl::interval_bounds::reverse_right );
		_class.def( "bits", &icl::interval_bounds::bits );
		_class.def( "open", &icl::interval_bounds::open ).staticmethod( "open" );
		_class.def( "right_open", &icl::interval_bounds::right_open ).staticmethod( "right_open" );
		_class.def( "left_open", &icl::interval_bounds::left_open ).staticmethod( "left_open" );
		_class.def( "closed", &icl::interval_bounds::closed ).staticmethod( "closed" );
	}
};

} // namespace pyicl

#endif //PYICL_INTERVAL_BOUNDS_H_JORE_110217


