/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_SET_HPP_JORE_110217
#define PYICL_INTERVAL_SET_HPP_JORE_110217

#include <pyicl/base.h>
#include <boost/icl/interval_set.hpp>

namespace pyicl {

/**
 * Expose a interval set.
 */
template< typename IntervalSet >
struct interval_set_exposer {

	typedef IntervalSet exposed_t; ///< The type to be exposed.
	typedef typename exposed_t::domain_type domain_t; ///< The domain of the set.
	typedef typename exposed_t::interval_type interval_t; ///< The interval type of the set.
	typedef boost::shared_ptr< exposed_t >  exposed_ptr; ///< Pointer to exposed type.
	typedef boost::python::class_<
		exposed_t,
		exposed_ptr
	> bp_class_t; ///< Boost.python class type.
	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.
	typedef domain_t ( * domain_1_fn )( const exposed_t & ); ///< Function taking exposed type, returning domain type.

	/// Expose the exposed_t using boost.python.
	static
	void
	expose( char const * name, char const * docstring ) {
		namespace bp = boost::python;
		namespace icl = boost::icl;

		// Class and construct.
		bp_class_t bp_class(
			name,
			docstring,
			bp::init<>( "Contructs an empty interval set." )
		);
	    bp_class.def( bp::init< domain_t >( "Constructor for a interval set with the given element." ) );
	    bp_class.def( bp::init< interval_t >( "Constructor for a interval set with the given interval." ) );
	    bp_class.def( bp::init< exposed_t >( "Copy constructor." ) );

	    // Iterator stuff
	    bp_class.def( "__iter__",                 bp::iterator< exposed_t >(), "Iterate (by-interval) over the container." );
	    bp_class.def( "find",                     &find_wrapper< exposed_t, domain_t >, "Find the interval for the given element." );

		// Containedness
		bp_class.add_property( "empty",           &icl::is_empty< exposed_t >, "Is the interval set empty?" );
		bp_class.def( "__nonzero__",              &non_zero< exposed_t >, "Does the interval set contain anything?" );
		bp_class.def( "__contains__",             &contains, "Does the interval contain the argument?" );

		// Equivalences and Orderings
		bp_class.def( "__eq__",                   bool_2_fn( icl::operator== ), "Equality." );
		bp_class.def( "__ne__",                   bool_2_fn( icl::operator!= ), "Inequality." );
		bp_class.def( "__lt__",                   bool_2_fn( icl::operator< ), "Interval less." );
		//bp_class.def( "is_element_equal",         is_element_equal );
		//bp_class.def( "is_element_less",          is_element_less );
		//bp_class.def( "is_element_greater",       is_element_greater );

		// Size
		bp_class.def( "__len__",                  &icl::length< exposed_t >, "Arithmetic size." );
		bp_class.add_property( "size",            &icl::size< exposed_t >, "Size." );
		bp_class.add_property( "cardinality",     &icl::cardinality< exposed_t >, "Cardinality of the interval: The number of elements." );
		bp_class.add_property( "iterative_size",  &icl::iterative_size< exposed_t > );
		bp_class.add_property( "interval_count",  &icl::interval_count< exposed_t > );

		// Range
		bp_class.add_property( "lower",           domain_1_fn( icl::lower< exposed_t > ), "Lower bound." );
		bp_class.add_property( "upper",           domain_1_fn( icl::upper< exposed_t > ), "Upper bound." );

		// Arithmetic operations
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "add",                      add, "Add an element or an interval to the set.", bp::return_self<>() );
		bp_class.def( "__add__",                  plus, "Create a new set f by adding an element, interval or set to this one." );
		bp_class.def( "__or__",                   plus, "Create a new set f by adding an element, interval or set to this one." );
		bp_class.def( "__iadd__",                 plus_equals, "Add an element, interval or set to this one.", bp::return_self<>() );
		bp_class.def( "__ior__",                  plus_equals, "Add an element, interval or set to this one.", bp::return_self<>() );
		bp_class.def( "subtract",                 subtract, "Remove an element or an interval from the set.", bp::return_self<>() );
		bp_class.def( "__sub__",                  minus, "Create a new set f by removing an element, interval or set from this one." );
		bp_class.def( "__isub__",                 minus_equals, "Remove an element, interval or set from this one.", bp::return_self<>() );
#endif
//		if( ! icl::is_continuous_interval< interval_t >::value ) {
//			bp_class.def( "erase",                    subtract, "Remove an element, interval or set from this one.", bp::return_self<>() );
//		}
		bp_class.def( "clear",                    &exposed_t::clear, "Clear this set." );

		// Intersection
//		if( ! icl::is_continuous_interval< interval_t >::value ) {
//			bp_class.def( "disjoint",                 disjoint, "Is this set disjoint with the given element, interval or set?" );
//			bp_class.def( "intersects",               intersects, "Does this set intersect the given element, interval or set?" );
//		}
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "__and__",                  and_, "The intersection of this set with the given element, interval or set." );
		bp_class.def( "intersection",             and_, "The intersection of this set with the given element, interval or set." );
		bp_class.def( "__iand__",                 and_equals, "Update this set to be the intersection of itself with the given element, interval or set." );
#endif

		// Symmetric difference
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "flip",                     flip, "The symmetric difference of this set with the given element or interval.", bp::return_self<>() );
		bp_class.def( "__xor__",                  xor_, "The symmetric difference of this set with the given element, interval or set." );
		bp_class.def( "__ixor__",                 xor_equals, "Update this set to be the symmetric difference of itself with the given element, interval or set.", bp::return_self<>() );
#endif

		// Streaming
		bp_class.def( "__str__",                  &convert_to_str< exposed_t >, "String representation." );
	}

	PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))

	PYICL_DECLARE_FN_1(bool, is_element_equal, ::boost::icl::is_element_equal, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(bool, is_element_less, ::boost::icl::is_element_less, const exposed_t, (exposed_t, BOOST_PP_NIL))
	PYICL_DECLARE_FN_1(bool, is_element_greater, ::boost::icl::is_element_greater, const exposed_t, (exposed_t, BOOST_PP_NIL))

	PYICL_DECLARE_FN_1(exposed_t &, add, ::boost::icl::add, exposed_t, (domain_t, (interval_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, plus_equals, ::boost::icl::operator+=, exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, plus, ::boost::icl::operator+, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t &, subtract, ::boost::icl::subtract, exposed_t, (domain_t, (interval_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, minus_equals, ::boost::icl::operator-=, exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, minus, ::boost::icl::operator-, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))

	PYICL_DECLARE_FN_1(bool, disjoint, ::boost::icl::disjoint, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(bool, intersects, ::boost::icl::intersects, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, and_equals, ::boost::icl::operator&=, exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))

	PYICL_DECLARE_FN_1(exposed_t &, flip, ::boost::icl::flip, exposed_t, (domain_t, (interval_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, xor_equals, ::boost::icl::operator^=, exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, xor_, ::boost::icl::operator^, exposed_t, (domain_t, (interval_t, (exposed_t, BOOST_PP_NIL))))
};







} // namespace pyicl

#endif //PYICL_INTERVAL_SET_HPP_JORE_110217


