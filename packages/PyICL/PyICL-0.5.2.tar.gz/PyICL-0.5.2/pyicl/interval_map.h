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
 * Class that implements += as a max operation
 */
template< typename Value >
struct maximiser
: boost::addable< maximiser< Value > >
, boost::equality_comparable< maximiser< Value > >
, boost::equality_comparable< maximiser< Value >, Value >
, boost::less_than_comparable< maximiser< Value > >
, boost::less_than_comparable< maximiser< Value >, Value >
{
public:
    typedef Value value_t;
    typedef maximiser< value_t > self_t;

    maximiser() : _value( Value() ) {}
    maximiser( value_t value ) : _value( value ) {}

    value_t value() const { return _value; }

    self_t & operator +=( const self_t & right ) {
        _value = std::max( _value, right._value );
        return *this;
    }

    bool operator==( const self_t & right ) const {
        return _value == right._value;
    }

    bool operator<( const self_t & right ) const {
        return _value < right._value;
    }

    int compare( const self_t & right ) const {
        return _value - right._value;
    }

    //operator value_t() const { return _value; }

    friend
    std::ostream &
    operator<<( std::ostream & os, const self_t & m ) {
        return os << m.value();
    }


protected:
    Value _value;
};



template< typename Value >
std::size_t
hash_value( maximiser< Value > const & m )
{
    boost::hash< int > hasher;
    return hasher( m.value );
}


/**
 * Struct we specialise to define type names.
 */
template< typename T >
struct type_name_selector {
    static const char * name() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct type_name_selector must be specialised for this type." );
        return 0;
    }
    static const char * lower() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct type_name_selector must be specialised for this type." );
        return 0;
    }
};

/// Specialisation
template<>
struct type_name_selector< int > {
    static const char * name() { return "Int"; }
    static const char * lower() { return "int"; }
};


/// Specialisation
template<>
struct type_name_selector< float > {
    static const char * name() { return "Float"; }
    static const char * lower() { return "float"; }
};


/// Specialisation
template<>
struct type_name_selector< maximiser< float > > {
    static const char * name() { return "FloatMax"; }
    static const char * lower() { return "floatmax"; }
};


/// Specialisation
template<>
struct type_name_selector< std::string > {
    static const char * name() { return "String"; }
    static const char * lower() { return "string"; }
};


/// Specialisation
template<>
struct type_name_selector< ::boost::python::object > {
    static const char * name() { return "Object"; }
    static const char * lower() { return "object"; }
};




/**
 * Helper struct to make operators visible for boost.python.
 */
template< typename T >
struct less_than_comparable
{
    static bool lt( const T & x, const T & y ) { return x < y; }
    static bool le( const T & x, const T & y ) { return x <= y; }
    static bool gt( const T & x, const T & y ) { return x > y; }
    static bool ge( const T & x, const T & y ) { return x >= y; }
};



/**
 * Helper struct to make operators visible for boost.python.
 */
template< typename T >
struct equality_comparable
{
    static bool eq( const T & x, const T & y ) { return x == y; }
    static bool ne( const T & x, const T & y ) { return x != y; }
};



/**
 * Expose a maximiser.
 */
template< typename Maximiser >
struct maximiser_exposer {

    typedef Maximiser exposed_t;
    typedef typename exposed_t::value_t value_t;

    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.value() );
        }
    };

    /// Expose/register the interval container.
    static
    void
    expose() {
        namespace bp = ::boost::python;
        namespace icl = ::boost::icl;

        bp::class_< exposed_t > bp_class(
            PYICL_MAKE_STRING( type_name_selector< value_t >::name() << "Max" ).c_str(),
            "Holds a value where += operation is implemented as maximisation.",
            bp::init< value_t >( "Contructs a maximiser." )
        );

        // pickling
        bp_class.def_pickle( _pickle_suite() );

        bp_class.add_property( "value", &exposed_t::value, "The value of the maximiser." );
        bp_class.def( "__iadd__", &exposed_t::operator+=, "+= operator implemented as maximisation.", bp::return_internal_reference<>() );
        bp_class.def( "__str__", &::pyicl::convert_to_str< exposed_t >, "String representation." );
        bp_class.def( "__cmp__", &exposed_t::compare );
        bp_class.def( "__lt__", &less_than_comparable< exposed_t >::lt );
        bp_class.def( "__le__", &less_than_comparable< exposed_t >::le );
        bp_class.def( "__gt__", &less_than_comparable< exposed_t >::gt );
        bp_class.def( "__ge__", &less_than_comparable< exposed_t >::ge );
        bp_class.def( "__eq__", &equality_comparable< exposed_t >::eq );
        bp_class.def( "__ne__", &equality_comparable< exposed_t >::ne );

        bp::implicitly_convertible< typename exposed_t::value_t, exposed_t >();
    }

};





/**
 * Expose an interval map.
 */
template< typename IntervalMap >
struct interval_map_exposer {

	typedef IntervalMap                                      exposed_t; ///< The container type to be exposed.
	typedef typename exposed_t::domain_type                  domain_t; ///< The domain type.
	typedef typename exposed_t::codomain_type                codomain_t; ///< The codomain type.
	typedef typename exposed_t::traits                       traits_t; ///< The traits type.
	typedef typename exposed_t::interval_type                interval_t; ///< Interval type.
	typedef boost::shared_ptr< exposed_t >                    exposed_ptr; ///< A type for a pointer to the container.
	typedef typename exposed_t::element_type                 element_t; ///< element-value pair.
	typedef typename exposed_t::segment_type                 segment_t; ///< interval-value pair.
	typedef typename ::boost::icl::interval_set< domain_t >  set_t; ///< An equivalent set type.
	typedef boost::python::class_<
		exposed_t,
		exposed_ptr
	>                                                    bp_class_t; ///< Boost.python class type.
	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.
	typedef domain_t ( * domain_1_fn )( const exposed_t & ); ///< Function taking exposed type, returning domain type.


    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple();
        }

        static
        boost::python::tuple
        getstate( const exposed_t & x )
        {
            boost::python::list l;
            for( typename exposed_t::const_iterator it = x.begin(); it != x.end(); ++it ) {
                //...so this iterates over intervals
                l.append( *it );
            }
            return boost::python::tuple( l );
        }

        static
        void
        setstate( exposed_t & x, boost::python::tuple state )
        {
            for( unsigned i = 0; boost::python::len( state ) != i; ++i ) {
                typename exposed_t::const_iterator::value_type segment = boost::python::extract< typename exposed_t::const_iterator::value_type >( state[ i ] );
                x.add( segment );
            }
        }
    };


    /// Expose/register the interval container.
	static
	void
	expose() {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;

		bp::scope enclosing_scope; // overall scope

		// define the segment type if needed
        const std::string segment_class_name = PYICL_MAKE_STRING(
            "_Segment"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), segment_class_name.c_str() ) ) {
            pair_exposer< segment_t >::expose(
                segment_class_name.c_str(),
                "A segment in an interval map, that is an interval and an associated value.",
                "interval",
                "value"
            );
        }

        // define the const segment type if needed
        const std::string const_segment_class_name = PYICL_MAKE_STRING(
            "_ConstSegment"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), const_segment_class_name.c_str() ) ) {
            pair_exposer< typename exposed_t::iterator::value_type >::expose(
                const_segment_class_name.c_str(),
                "A const segment in an interval map, that is an interval and an associated value.",
                "interval",
                "value"
            );
        }

        // define the element type if needed
		const std::string element_class_name = PYICL_MAKE_STRING(
            "_Pair"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), element_class_name.c_str() ) ) {
            pair_exposer< element_t >::expose(
                element_class_name.c_str(),
                PYICL_MAKE_STRING(
                    "A pair of a "
                        << type_name_selector< domain_t >::lower()
                        << " and a "
                        << type_name_selector< codomain_t >::lower() << "."
                ).c_str(),
                "key",
                "value"
            );
        }

		// Class and construct.
		bp_class_t bp_class(

		    // the class name
            PYICL_MAKE_STRING(
                type_name_selector< domain_t >::name()
                    << "Interval"
                    << type_name_selector< codomain_t >::name()
                    << "Map"
            ).c_str(),

            // the docstring
			PYICL_MAKE_STRING(
			    "A (joining) map from "
			        << type_name_selector< domain_t >::lower()
			        << " intervals to "
			        << type_name_selector< codomain_t >::lower() << "s."
			).c_str(),

			// the constructor
			bp::init<>( "Contructs an empty interval map." )
		);
	    //bp_class.def( bp::init< element_t >( "Constructor for a interval set with the given element." ) );
	    bp_class.def( bp::init< segment_t >( "Constructor for a interval set with the given segment." ) );
	    bp_class.def( bp::init< exposed_t >( "Copy constructor." ) );

        // pickling
        bp_class.def_pickle( _pickle_suite() );

	    // Expose auxiliary types inside the map class.
		bp::scope _scope( bp_class );
        bp_class.attr( "Segment" ) = enclosing_scope.attr( segment_class_name.c_str() );
        bp_class.attr( "ConstSegment" ) = enclosing_scope.attr( const_segment_class_name.c_str() );
        bp_class.attr( "Element" ) = enclosing_scope.attr( element_class_name.c_str() );

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
	PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (domain_t, (interval_t, (element_t, (set_t, (segment_t, (exposed_t, BOOST_PP_NIL)))))))
	PYICL_DECLARE_FN_1(exposed_t, and_equals, ::boost::icl::operator&=, exposed_t, (domain_t, (interval_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))))

	PYICL_DECLARE_FN_1(exposed_t &, flip, ::boost::icl::flip, exposed_t, (element_t, (segment_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t &, xor_equals, ::boost::icl::operator^=, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
	PYICL_DECLARE_FN_1(exposed_t, xor_, ::boost::icl::operator^, exposed_t, (element_t, (segment_t, (exposed_t, BOOST_PP_NIL))))
};






} // namespace pyicl


#endif //PYICL_INTERVAL_MAP_HPP_JORE_110217


