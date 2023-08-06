#include <boost/icl/interval.hpp>
#include <iostream>

int main( int argc, char * argv[] ) {
	return boost::icl::has_dynamic_bounds<boost::icl::continuous_interval<float, std::less> >::value;
}

template< typename IntervalT >
void
check_equals() {
	IntervalT interval( 0, 0 );
	interval == interval;
}

template< typename IntervalT >
void
check_contains() {
	IntervalT interval;
	typedef typename IntervalT::domain_type domain_t;
	::boost::icl::contains( interval, domain_t() );
}

void h() {
	namespace icl = ::boost::icl;
	check_contains< icl::continuous_interval< float > >();
	check_contains< icl::discrete_interval< int > >();
	check_contains< icl::right_open_interval< float > >();
	check_contains< icl::left_open_interval< float > >();
	//check_contains< icl::closed_interval< float > >();
	//check_contains< icl::open_interval< float > >();
	//check_equals< icl::closed_interval< float > >();
	//check_equals< icl::open_interval< float > >();
}

int main_( int argc, char * argv[] ) {
  namespace icl = ::boost::icl;

  std::cout << "Float is continuous: " << icl::is_continuous< float >::value << "\n";

  return 0;
}

#if 0
void f() {
  namespace icl = ::boost::icl;

  icl::interval_set<int> int_set;
  icl::add( int_set, 0 );
  icl::add( int_set, icl::interval<  int>::type( 0, 1 ) );
  int_set += 0;
  int_set += icl::interval<  int>::type( 0, 1 );

  icl::subtract( int_set, 0 );
  icl::subtract( int_set, icl::interval< int >::type( 0, 1 ) );
  int_set -= 0;
  int_set -= icl::interval< int >::type( 0, 1 );

  int_set &= 0;
  int_set &= icl::interval< int >::type( 0, 1 );

  int_set ^= ( icl::interval< int >::type( 0, 1 ) );
}

void g() {
	namespace icl = ::boost::icl;
	typedef float type_;
	icl::interval_set< type_ > set;
	set.add( icl::interval< type_ >::type( 0, 2 ) );
	set.add( icl::interval< type_ >::type( 5, 7 ) );
	set.find( icl::interval< type_ >::type( 0, 9 ) );

#if 0
	icl::interval_map< float, int >().find( 0 );

	icl::interval_set< float >().find( 0 );

	icl::contains( icl::interval_set< float >(), 0 );

	icl::add( icl::interval_set< int >(), 0 );
	icl::add( icl::interval_set< int >(), icl::interval< int >::type( 0, 1 ) );
	icl::interval_set< int >() += 0;
	icl::interval_set< int >() += icl::interval< int >::type( 0, 1 );

	icl::subtract( icl::interval_set< int >(), 0 );
	icl::subtract( icl::interval_set< int >(), icl::interval< int >::type( 0, 1 ) );
	icl::interval_set< int >() -= 0;
	icl::interval_set< int >() -= icl::interval< int >::type( 0, 1 );

	icl::interval_set< int >() &= 0;
	icl::interval_set< int >() &= icl::interval< int >::type( 0, 1 );

	icl::interval_set< int >() ^= ( icl::interval< int >::type( 0, 1 ) );
#endif
}
#endif


#if 0
#include <boost/type_traits/has_operator_minus.hpp>
#include <string>

template< typename T >
T g( T x, T y ) {
	if( boost::has_operator_minus<T, T, T>::value ) {
		return x - y;
	} else {
		return T();
	}
}

template void g< std::string >( std::string, std::string );


template< typename T >
struct A {
    void register_fns() {
    	&A::subtract;
    }

    T subtract( T x, T y ) {
    	if( boost::has_operator_minus<T, T, T>::value ) {
    		return x - y;
    	} else {
    		return T();
    	}
    }
};

void test() {
	A< int >().register_fns(); // Fine
	//A< std::string >().register_fns(); // Compile error
}


#include <boost/icl/interval.hpp>
#include <boost/icl/interval_set.hpp>
#include <boost/icl/interval_map.hpp>
namespace icl = ::boost::icl;

void f() {
	icl::interval< int > int_interval;
	icl::interval_set< int > int_set;
	icl::interval_map< int, int > int_map;
	icl::interval_map< int, int >::element_type int_element;
	icl::interval_map< int, int >::segment_type int_segment;

	// AFAICT none of the following lines compiles
	icl::lower( int_interval );
	icl::upper( int_interval );
	icl::first( int_interval );
	icl::last( int_interval );
	icl::add( int_set, int_set );
	icl::add( int_map, int_map );
	icl::subtract( int_set, int_set );
	icl::subtract( int_map, int_map );
	int_set += int_interval;
	icl::disjoint( int_map, int_element );
	icl::disjoint( int_map, int_segment );
	icl::intersects( int_map, int_segment );
	icl::intersects( int_map, int_element );
}

void f() {
	icl::lower( icl::interval_set< int >() );
}

#include <boost/icl/interval_set.hpp>
void interval_set_intersects() {
	icl::intersects( icl::interval_set< int >(), 1 );
}

#include <boost/icl/continuous_interval.hpp>
#include <boost/icl/interval.hpp>
void hull_typename() {
	typedef icl::interval< float >::type interval_type;

	icl::hull( interval_type(), interval_type() );
}
#endif
