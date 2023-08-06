/** Copyright John Reid 2011, 2012
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_MAP_HPP_JORE_110217
#define PYICL_INTERVAL_MAP_HPP_JORE_110217

#include <pyicl/base.h>
#include <boost/icl/interval_map.hpp>

namespace pyicl {




/**
 * Expose a interval map.
 */
template< typename IntervalMap >
struct interval_map_exposer {

	typedef IntervalMap                                  exposed_t; ///< The container type to be exposed.
	typedef typename exposed_t::domain_type              domain_t; ///< The domain type.
	typedef typename exposed_t::codomain_type            codomain_t; ///< The codomain type.
	typedef typename exposed_t::traits                   traits_t; ///< The traits type.
	typedef typename exposed_t::interval_type            interval_t; ///< Interval type.
	typedef boost::shared_ptr< exposed_t >               exposed_ptr; ///< A type for a pointer to the container.
	typedef typename exposed_t::element_type             element_t; ///< element-value pair.
	typedef typename exposed_t::segment_type             segment_t; ///< interval-value pair.
	typedef boost::python::class_<
		exposed_t,
		exposed_ptr,
		boost::noncopyable
	>                                                    bp_class_t; ///< Boost.python class type.
	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.
	typedef domain_t ( * domain_1_fn )( const exposed_t & ); ///< Function taking exposed type, returning domain type.

	/// Expose/register the interval container.
	static
	void
	expose( char const * name, char const * docstring ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;

		// Class and construct.
		bp_class_t bp_class(
			name,
			docstring,
			bp::init<>( "Contructs an empty interval map." )
		);
	    //bp_class.def( bp::init< element_t >( "Constructor for a interval set with the given element." ) );
	    bp_class.def( bp::init< segment_t >( "Constructor for a interval set with the given segment." ) );
	    bp_class.def( bp::init< exposed_t >( "Copy constructor." ) );

	    // Expose auxiliary types inside the map class.
		bp::scope _scope( bp_class );

		pair_exposer< segment_t >::expose(
			"Segment",
			"A segment in the interval map, that is an interval and an associated value.",
			"interval",
			"value"
		);

		pair_exposer< typename exposed_t::iterator::value_type >::expose(
			"ConstSegment",
			"An element in the interval map, that is a member of the domain and an associated value.",
			"interval",
			"value"
		);

		pair_exposer< element_t >::expose(
			"Element",
			"An element in the interval map, that is a member of the domain and an associated value.",
			"key",
			"value"
		);

	    // Iterator stuff
	    bp_class.def( "__iter__",                 bp::iterator< exposed_t >(), "Iterate (by-interval) over the container." );
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
	    bp_class.def( "find",                     &find_wrapper< exposed_t, domain_t >, "Find the interval for the given element." );
#endif

		// Containedness
		bp_class.add_property( "empty",           &icl::is_empty< exposed_t >, "Is the interval map empty?" );
		bp_class.def( "__nonzero__",              &non_zero< exposed_t >, "Does the interval map contain anything?" );
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "__contains__",             &contains, "Does the interval map contain the argument?" );
#endif

		// Equivalences and Orderings
		bp_class.def( "__eq__",                   bool_2_fn( icl::operator== ), "Equality." );
		bp_class.def( "__ne__",                   bool_2_fn( icl::operator!= ), "Inequality." );
		bp_class.def( "__lt__",                   bool_2_fn( icl::operator< ), "Interval less." );

		// Size
		bp_class.def( "__len__",                  &icl::length< exposed_t >, "Arithmetic size." );
		bp_class.add_property( "size",            &icl::size< exposed_t >, "Size." );
		bp_class.add_property( "cardinality",     &icl::cardinality< exposed_t >, "Cardinality of the interval: The number of elements." );
		bp_class.add_property( "iterative_size",  &icl::iterative_size< exposed_t > );
		bp_class.add_property( "interval_count",  &icl::interval_count< exposed_t > );

		// Arithmetic operations
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "add",                      add, "Add an element or an interval to the map.", bp::return_self<>() );
		bp_class.def( "__add__",                  plus, "Create a new map f by adding an element, interval or map to this one." );
		bp_class.def( "__iadd__",                 plus_equals, "Add an element, interval or map to this one.", bp::return_self<>() );
		bp_class.def( "__or__",                   plus, "Create a new map f by adding an element, interval or map to this one." );
		bp_class.def( "__ior__",                  plus_equals, "Add an element, interval or map to this one.", bp::return_self<>() );
#endif
		//operator_minus_exposer< bp_class_t, true >()( bp_class );
		operator_minus_exposer< bp_class_t, boost::has_minus< codomain_t, codomain_t, codomain_t >::value >::expose( bp_class );
		bp_class.def( "clear",                    &exposed_t::clear, "Clear this map." );

		// Intersection
		//bp_class.def( "disjoint",                 disjoint, "Is this map disjoint with the given element, interval or map?" );
		//bp_class.def( "intersects",               intersects, "Does this map intersect the given element, interval or map?" );
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "intersection",             and_, "The intersection of this map with the given element, interval or map." );
		bp_class.def( "__and__",                  and_, "The intersection of this map with the given element, interval or map." );
		bp_class.def( "__iand__",                 and_equals, "Update this map to be the intersection of itself with the given element, interval or map." );
#endif

		// Symmetric difference
#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
		bp_class.def( "flip",                     flip, "The symmetric difference of this map with the given element or interval.", bp::return_self<>() );
		bp_class.def( "__ixor__",                 xor_equals, "Update this map to be the symmetric difference of itself with the given element, interval or map.", bp::return_self<>() );
		bp_class.def( "__xor__",                  xor_, "The symmetric difference of this map with the given element, interval or map." );
#endif

		// Streaming
		//bp_class.def( "__str__",                  &::pyicl::convert_to_str< exposed_t >, "String representation." );
	}

	template< typename BPClass, bool has_minus >
	struct operator_minus_exposer {
		static void expose( BPClass & bp_class ) {
		}
	};

	template< typename BPClass >
	struct operator_minus_exposer< BPClass, true > {
		static void expose( BPClass & bp_class ) {
			namespace bp = ::boost::python;

#ifndef BOOST_ICL_USE_STATIC_BOUNDED_INTERVALS
			bp_class.def( "subtract",                 subtract, "Remove an element or an interval from the map.", bp::return_self<>() );
			bp_class.def( "__sub__",                  minus, "Create a new map f by removing an element, interval or map from this one." );
			bp_class.def( "__isub__",                 minus_equals, "Remove an element, interval or map from this one.", bp::return_self<>() );
			bp_class.def( "erase",                    subtract, "Remove an element, interval or map from this one.", bp::return_self<>() );
#endif
		}
	};

	PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))

	PYICL_DECLARE_FN_1(exposed_t &, add, ::boost::icl::add, exposed_t, (element_t, (segment_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, plus_equals, ::boost::icl::operator+=, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, plus, ::boost::icl::operator+, const exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t &, subtract, ::boost::icl::subtract, exposed_t, (element_t, (segment_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, minus_equals, ::boost::icl::operator-=, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, minus, ::boost::icl::operator-, const exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))

	PYICL_DECLARE_FN_1(bool, disjoint, ::boost::icl::disjoint, const exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))
	PYICL_DECLARE_FN_1(bool, intersects, ::boost::icl::intersects, const exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))
	PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))
	PYICL_DECLARE_FN_1(exposed_t, and_equals, ::boost::icl::operator&=, exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))

	PYICL_DECLARE_FN_1(exposed_t &, flip, ::boost::icl::flip, exposed_t, (element_t, (segment_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, xor_equals, ::boost::icl::operator^=, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, xor_, ::boost::icl::operator^, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
};






} // namespace pyicl

#endif //PYICL_INTERVAL_MAP_HPP_JORE_110217


