/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_BASE_HPP_JORE_110217
#define PYICL_BASE_HPP_JORE_110217

#include <boost/python.hpp>
#include <boost/functional/hash.hpp>
#include <boost/test/utils/wrap_stringstream.hpp>
#include <boost/preprocessor/list/for_each.hpp>
#include <boost/icl/interval_set.hpp>
#include <boost/icl/interval_map.hpp>
#include <boost/icl/split_interval_set.hpp>
#include <boost/icl/split_interval_map.hpp>
#include <boost/icl/separate_interval_set.hpp>
#include <boost/type_traits/has_minus.hpp>

/// Make a string from the streamed arguments.
#define PYICL_MAKE_STRING( x ) ( boost::wrap_stringstream().ref() << x ).str()

/// Used to define repetitive methods.
#define PYICL_TRY_EXTRACT_AND_APPLY(R, apply, extracted_type) \
	{ \
		boost::python::extract< extracted_type > extractor( o ); \
		if( extractor.check() ) { \
			return apply( s, extractor() ); \
		} \
	} \
	/**/

/// Used to define repetitive methods.
#define PYICL_COULD_NOT_EXTRACT_THROW \
	throw std::invalid_argument( "Type error." ) \
	/**/

/// Used to define repetitive methods.
#define PYICL_DECLARE_FN_1(ret_type, fn_name, apply, subject_type, contained_types) \
	static ret_type fn_name( subject_type & s, boost::python::object o ) { \
		BOOST_PP_LIST_FOR_EACH(PYICL_TRY_EXTRACT_AND_APPLY, apply, contained_types); \
		PYICL_COULD_NOT_EXTRACT_THROW; \
	} \
	/**/




namespace pyicl {



/// If argument is a boost python object, then extract a string from it.
template< typename T >
struct extract_str_if_object_ {
	typedef T return_type;
	T operator()( T t ) { return t; }
};


/// If argument is a boost python object, then extract a string from it. Specialisation for boost::python::object.
template<>
struct extract_str_if_object_< boost::python::object > {
	typedef std::string return_type;
	std::string operator()( boost::python::object t ) {
		namespace bp = boost::python;
		return bp::extract< std::string >( bp::str( t ) )();
	}
};


/// If argument is a boost python object, then extract a string from it, otherwise return the argument unchanged.
template< typename T >
typename extract_str_if_object_< T >::return_type
extract_str_if_object( T t ) {
	return extract_str_if_object_< T >()( t );
}


/// Is x non-empty?
template< typename base_t >
bool
non_zero( base_t const & x ) {
	return ! boost::icl::is_empty( x );
}

/// As string
template< typename T >
std::string
convert_to_str( const T & t ) {
	return PYICL_MAKE_STRING( t );
}

/// Wrapper for find.
template< typename ExposedT, typename DomainT >
static
::boost::python::object
find_wrapper( const ExposedT & exposed, DomainT key ) {
	namespace icl = ::boost::icl;

	typename ExposedT::const_iterator i = exposed.find( key );
	if( exposed.end() == i ) {
		return ::boost::python::object();
	} else {
		return ::boost::python::object( *i );
	}
}



/// Exposes pair like objects (std::pair and icl::mapping_pair)
template< typename Pair >
struct pair_exposer {
};



/// Specialisation for mapping_pair
template<>
template< typename DomainT, typename CodomainT >
struct pair_exposer< ::boost::icl::mapping_pair< DomainT, CodomainT > > {
	typedef ::boost::icl::mapping_pair< DomainT, CodomainT > exposed_t; ///< Exposed type.

    /// Already exposed/registered?
    static
    bool
    already_exposed() {
        boost::python::type_info info = boost::python::type_id< exposed_t >();
        const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
        return reg != NULL;
    }


    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.key, x.data );
        }
    };


	static
	void
	expose( const char * name, const char * docstring, const char * key_name = "key", const char * data_name = "data" ) {
		namespace bp = ::boost::python;

        //if( ! already_exposed() ) {
        // expose the segment type inside the class scope
        bp::class_<
            exposed_t
        > bp_class(
            name,
            docstring,
            bp::init< DomainT, CodomainT >( bp::args( "key", "data" ), "Construct a key-data pair." )
        );
        bp_class.def_pickle( _pickle_suite() );
        bp_class.def( "__str__", convert_to_str, "String representation." );
        bp_class.def_readonly( key_name, &exposed_t::key,  "The key." );
        bp_class.def_readonly( data_name, &exposed_t::data, "The data." );
		//}
	}

	/// String representation
	static
	std::string
	convert_to_str( exposed_t const & x ) {
		return PYICL_MAKE_STRING(
			x.key
			<< "; "
			<< extract_str_if_object( x.data )
		);
	}
};




/// Specialisation for std::pair
template<>
template< typename T1, typename T2 >
struct pair_exposer< ::std::pair< T1, T2 > > {
	typedef ::std::pair< T1, T2 > exposed_t; ///< Exposed type.

    /// Already exposed/registered?
    static
    bool
    already_exposed() {
        boost::python::type_info info = boost::python::type_id< exposed_t >();
        const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
        return reg != NULL;
    }


    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.first, x.second );
        }
    };


	static
	void
	expose( const char * name, const char * docstring, const char * first_name = "first", const char * second_name = "second" ) {

        //if( ! already_exposed() ) {
        namespace bp = ::boost::python;

        // expose the segment type inside the class scope
        bp::class_<
            exposed_t
        > bp_class(
            name,
            docstring,
            bp::init< T1, T2 >( bp::args( "first", "second" ), "Construct a pair." )
        );
        bp_class.def_pickle( _pickle_suite() );
        bp_class.def( "__str__", convert_to_str, "String representation." );
        bp_class.def_readonly( first_name, &exposed_t::first );
        bp_class.def_readonly( second_name, &exposed_t::second );
	    //}
	}

	/// String representation
	static
	std::string
	convert_to_str( exposed_t const & x ) {
		return PYICL_MAKE_STRING(
			x.first
			<< "; "
			<< extract_str_if_object( x.second )
		);
	}
};


} // namespace pyicl

#endif //PYICL_BASE_HPP_JORE_110217


