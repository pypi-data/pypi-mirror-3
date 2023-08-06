/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_H_JORE_110217
#define PYICL_INTERVAL_H_JORE_110217

#include <pyicl/base.h>
#include <boost/icl/interval.hpp>

namespace boost {
namespace icl {

//
// Make intervals hashable.
//
template<
	typename DomainT,
	ICL_COMPARE Compare
>
std::size_t
hash_value(
	const typename ::boost::icl::interval< DomainT, Compare >::interval_type & x
) {
	std::size_t seed = 0;
	boost::hash_combine( seed, x.lower() );
	boost::hash_combine( seed, x.upper() );
	boost::hash_combine( seed, x.bounds() );
	return seed;
}

//
// Specialisation of interval traits of python object intervals
//
//template< ICL_COMPARE Compare >
//struct interval_traits< interval< boost::python::object, Compare > >
//{
//    typedef interval< boost::python::object, Compare >     interval_type;
//    typedef boost::python::object                          domain_type;
//    typedef boost::python::object                          difference_type;
//    //typedef typename Compare domain_compare;
//
//    static interval_type construct(const domain_type& lo, const domain_type& up)
//    { return interval_type(lo, up); }
//
//    static domain_type lower(const interval_type& inter_val){ return inter_val.first(); };
//    static domain_type upper(const interval_type& inter_val){ return inter_val.past(); };
//};

} // namespace icl
} // namespace boost



namespace pyicl {
namespace { //anonymous

/**
 * Exposes functionality depending on whether the interval is symmetric.
 */
template < bool IsAsymmetric >
struct symmetry_exposer
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;
		typedef typename Exposer::exposed_t exposed_t;
		typedef typename Exposer::bool_2_fn bool_2_fn;

	}
};

/// Enabled only if symmetric
template <>
struct symmetry_exposer< false >
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
	}
};




/**
 * Exposes functionality depending on whether the interval is continuous.
 */
template < bool IsContinuous >
struct discrete_continuous_exposer
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
	}
};

/// Enabled only if discrete
template <>
struct discrete_continuous_exposer< false >
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;
		typedef typename Exposer::exposed_t exposed_t;

		bp_class.add_property( "first",           &icl::first< exposed_t >, "First element." );
		bp_class.add_property( "last",            &icl::last< exposed_t >, "Last element." );
	}
};


/**
 * Exposer different things depending on whether is dynamic or static.
 */
template< bool IsDynamic >
struct dynamic_static_exposer {
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		typedef typename Exposer::domain_t domain_t;
	    bp_class.def( bp::init< domain_t, domain_t >( "Constructor for an interval with default bounds." ) );
	}
};

// specialization
template<>
struct dynamic_static_exposer< true > {
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		typedef typename Exposer::domain_t domain_t;
		bp_class.def( bp::init<>( "Contructs an empty interval." ) );
	    bp_class.def( bp::init< domain_t >( "Constructor for a closed singleton interval [val,val]." ) );
	    bp_class.def( bp::init< domain_t, domain_t >( "Constructor for an interval with default bounds." ) );
	    bp_class.def( bp::init< domain_t, domain_t, ::boost::icl::interval_bounds >( "Interval from lower to upper with given bounds." ) );
	    bp_class.add_property( "bounds", &Exposer::exposed_t::bounds, "The bounds." );
	}
};






} //anonymous



/**
 * Expose an interval.
 */
template< typename IntervalT >
struct interval_exposer {

	typedef interval_exposer< IntervalT >                                this_t;       ///< This type.
	typedef IntervalT                                                    exposed_t;    ///< Interval type to be exposed.
	typedef ::boost::icl::interval_traits< exposed_t >                    traits_t;     ///< Interval traits.
    typedef typename ::boost::icl::difference_type_of< traits_t >::type  difference_t; ///< Difference type.
    typedef typename ::boost::icl::domain_type_of< traits_t >::type      domain_t;     ///< Domain type.
    typedef typename ::boost::icl::size_type_of< traits_t >::type        size_t;       ///< Size type.
	typedef ::boost::python::class_< exposed_t >                          bp_class_t;   ///< Boost.python class type.

	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.


	/// To pickle intervals
	struct _pickle_suite : boost::python::pickle_suite
    {
	    static
	    boost::python::tuple
	    getinitargs( const exposed_t & x )
	    {
	        return boost::python::make_tuple( x.lower(), x.upper() );
	    }
    };

	/// Already exposed/registered?
	static
	bool
	already_exposed() {
	    boost::python::type_info info = boost::python::type_id< exposed_t >();
	    const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
	    return reg != NULL;
	}


	/// Expose/register the interval.
	static
	void
	expose( char const * name, char const * docstring ) {

        namespace bp = boost::python;
        namespace icl = boost::icl;

        // Class and constructors.
        bp_class_t bp_class(
            name,
            docstring,
            bp::no_init
        );

        // pickling
        bp_class.def_pickle( _pickle_suite() );

        // set attributes for the traits of the class
//		bp::scope( bp_class ).attr( "__dynamic_bounds__" ) = icl::has_dynamic_bounds< exposed_t >::value;
//		bp::scope( bp_class ).attr( "__continuous__" ) = icl::is_continuous< domain_t >::value;
//		bp::scope( bp_class ).attr( "__asymmetric__" ) = icl::is_asymmetric_interval< domain_t >::value;

        // Expose those methods that are dependent on traits.
        symmetry_exposer< icl::is_asymmetric_interval< exposed_t >::value >::template expose< this_t >( bp_class );
        dynamic_static_exposer< icl::has_dynamic_bounds< exposed_t >::value >::template expose< this_t >( bp_class );
        discrete_continuous_exposer< icl::is_continuous< domain_t >::value >::template expose< this_t >( bp_class );

        // make hash-able
        bp_class.def( "__hash__",                 boost::hash_value< exposed_t >, "Hash value." );

        // bounds
        bp_class.def( "lower", &exposed_t::lower, "The lower bound." );
        bp_class.def( "upper", &exposed_t::upper, "The upper bound." );

        // Containedness
        bp_class.add_property( "empty",           &icl::is_empty< exposed_t >, "Is the interval empty?" );
        bp_class.def( "__nonzero__",              &non_zero< exposed_t >, "Does the interval contain anything?" );
        bp_class.def( "__contains__",             &contains, "Does the interval contain the argument?" );

        // Miscellaneous
        bp_class.def( "distance",                 &distance, "The distance between two intervals." );
        bp_class.def( "touches",                  bool_2_fn( icl::touches< exposed_t > ), "There is no gap between the 2 intervals and they have no element in common." );
        bp_class.def( "inner_complement",         inner_complement );

        // Equivalences and Orderings
        bp_class.def( "__eq__",                   bool_2_fn( icl::operator== ), "Equality." );
        bp_class.def( "__ne__",                   bool_2_fn( icl::operator!= ), "Inequality." );
        bp_class.def( "__lt__",                   bool_2_fn( icl::operator< ), "Interval less." );
//		bool ( * ptr_lessequals )( const exposed_t &, const exposed_t & ) = &icl::operator<=;
//		bp_class.def( "__le__",                   ptr_lessequals, "Less or equals." );
//		bool ( * ptr_greater )( const exposed_t &, const exposed_t & ) = &icl::operator>;
//		bp_class.def( "__gt__",                   ptr_greater, "Greater." );
//		bool ( * ptr_greaterequals )( const exposed_t &, const exposed_t & ) = &icl::operator>=;
//		bp_class.def( "__ge__",                   ptr_greaterequals, "Greater or equals." );
        bp_class.def( "exclusive_less",           bool_2_fn( icl::exclusive_less< exposed_t > ), "Maximal element of left is less than the minimal element of right." );
        bp_class.def( "lower_less",               bool_2_fn( boost::icl::lower_less< exposed_t > ) );
        bp_class.def( "lower_equal",              bool_2_fn( boost::icl::lower_equal< exposed_t > ) );
        bp_class.def( "lower_less_equal",         bool_2_fn( boost::icl::lower_less_equal< exposed_t > ) );
        bp_class.def( "upper_less",               bool_2_fn( boost::icl::upper_less< exposed_t > ) );
        bp_class.def( "upper_equal",              bool_2_fn( boost::icl::upper_equal< exposed_t > ) );
        bp_class.def( "upper_less_equal",         bool_2_fn( boost::icl::upper_less_equal< exposed_t > ) );

        // Size
        bp_class.def( "__len__",                  &icl::length< exposed_t >, "Arithmetic size." );
        bp_class.add_property( "cardinality",     &icl::cardinality< exposed_t >, "Cardinality of the interval: The number of elements." );
        bp_class.add_property( "size",            &icl::size< exposed_t >, "Size." );

        // Range
        bp_class.add_property( "lower",           &icl::lower< exposed_t >, "Lower bound." );
        bp_class.add_property( "upper",           &icl::upper< exposed_t >, "Upper bound." );

        // Subtraction
        bp_class.def( "left_subtract",            &icl::left_subtract< exposed_t >, "Left subtract." );
        bp_class.def( "right_subtract",           &icl::right_subtract< exposed_t >, "Right subtract." );

        // Intersection
        bp_class.def( "intersection",             intersection, "Intersection." );
        bp_class.def( "__and__",                  intersection, "Intersection." );
        bp_class.def( "intersects",               bool_2_fn( icl::intersects< exposed_t > ), "Intersects." );
        bp_class.def( "disjoint",                 bool_2_fn( icl::disjoint< exposed_t > ), "Disjoint." );

        // Streaming
        bp_class.def( "__str__",                  &convert_to_str< exposed_t >, "String representation." );
	}

    PYICL_DECLARE_FN_1(difference_t, distance, ::boost::icl::distance, const exposed_t, (const exposed_t, BOOST_PP_NIL))
    PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (exposed_t, (domain_t, BOOST_PP_NIL)))
	PYICL_DECLARE_FN_1(exposed_t, intersection, ::boost::icl::operator&, const exposed_t, (exposed_t, BOOST_PP_NIL))
	PYICL_DECLARE_FN_1(exposed_t, inner_complement, ::boost::icl::inner_complement, const exposed_t, (const exposed_t &, BOOST_PP_NIL))
};







/**
 * Expose static interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_static_interval_types( const std::string & name, const std::string & typename_ ) {
	namespace icl = ::boost::icl;

	interval_exposer< icl::right_open_interval< DomainT, Compare > >::expose(
		PYICL_MAKE_STRING( name << "RightOpen" ).c_str(),
		PYICL_MAKE_STRING( "A right-open interval of " << typename_ << "s." ).c_str()
	);

	interval_exposer< icl::left_open_interval< DomainT, Compare > >::expose(
		PYICL_MAKE_STRING( name << "LeftOpen" ).c_str(),
		PYICL_MAKE_STRING( "A left-open interval of " << typename_ << "s." ).c_str()
	);

//	interval_exposer< icl::closed_interval< DomainT, Compare > >::expose(
//		PYICL_MAKE_STRING( name << "Closed" ).c_str(),
//		PYICL_MAKE_STRING( "A closed interval of " << typename_ << "s." ).c_str()
//	);
//
//	interval_exposer< icl::open_interval< DomainT, Compare > >::expose(
//		PYICL_MAKE_STRING( name << "Open" ).c_str(),
//		PYICL_MAKE_STRING( "An open interval of " << typename_ << "s." ).c_str()
//	);
}




/**
 * Expose dynamic interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_dynamic_interval_type( const std::string & name, const std::string & typename_ ) {
	namespace icl = ::boost::icl;

	interval_exposer< typename icl::interval< DomainT, Compare >::type >::expose(
		PYICL_MAKE_STRING( name ).c_str(),
		PYICL_MAKE_STRING( "A dynamically bounded interval of " << typename_ << "s." ).c_str()
	);
}

/**
 * Expose all interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_interval_types( const std::string & name, const std::string & typename_ ) {
	expose_static_interval_types< DomainT, Compare >( name, typename_ );
	expose_dynamic_interval_type< DomainT, Compare >( name, typename_ );
}



} // namespace pyicl

#endif //PYICL_INTERVAL_H_JORE_110217


