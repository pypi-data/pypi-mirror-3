.. PyICL documentation master file, created by
   sphinx-quickstart on Fri Apr 13 16:04:13 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyICL's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2



Introduction
============

The PyICL module exposes the functionality of the C++
`Boost Interval Container Library`_ to python. The author Joachim Faulhaber introduces
his C++ library thus:

    Intervals are almost ubiquitous in software development. Yet they are very easily coded into 
    user defined classes by a pair of numbers so they are only implicitly used most of the time. 
    The meaning of an interval is simple. They represent all the elements between their lower and 
    upper bound and thus a set. But unlike sets, intervals usually can not be added to a single 
    new interval. If you want to add intervals to a collection of intervals that does still 
    represent a set, you arrive at the idea of interval_sets provided by this library.

    Interval containers of the ICL have been developed initially at
    `Cortex Software GmbH <http://www.cortex-software.de/desktopdefault.aspx>`_
    to solve problems related to date and time interval computations in the context of a Hospital 
    Information System. Time intervals with associated values like amount of invoice or set 
    of therapies had to be manipulated in statistics, billing programs and therapy scheduling 
    programs. So the ICL emerged out of those industrial use cases. It extracts generic code 
    that helps to solve common problems from the date and time problem domain and can be 
    beneficial in other fields as well.

    One of the most advantageous aspects of interval containers is their very compact 
    representation of sets and maps. Working with sets and maps of elements can be very 
    inefficient, if in a given problem domain, elements are typically occurring in 
    contiguous chunks. Besides a compact representation of associative containers, 
    that can reduce the cost of space and time drastically, the ICL comes with a 
    universal mechanism of aggregation, that allows to combine associated values 
    in meaningful ways when intervals overlap on insertion.

    For a condensed introduction and overview you may want to look at the 
    `presentation material on the ICL from BoostCon2009 
    <http://www.herold-faulhaber.de/boost_icl/doc/libs/icl/doc/boostcon09/intro_to_itl.pdf>`_.


.. _Boost Interval Container Library: http://www.boost.org/libs/icl/doc/html


Installation
============



Basic Usage
===========

In this section we demonstrate basic usage of the PyICL module. We follow the examples given
in the `Boost Interval Container Library`_ documentation. First import the module:

    >>> import pyicl


.. testsetup::

   import pyicl


Intervals are half-open by default:
    
.. doctest::

    >>> interval = pyicl.IntInterval(0, 10)
    >>> print interval
    [0,10)
    >>> print 0 in interval
    True
    >>> print 10 in interval
    False





Two aspects: fundamental and segmental
--------------------------------------

Interval sets and maps can be viewed in 2 complementary ways or aspects. The first aspect treats
interval sets and maps as containers of elements and is called the **fundamental aspect**. The second
aspect treats interval sets and maps as containers of intervals (or segments) and is called the
**segmental aspect**. The fundamental aspect supports inserting elements into a set or map and testing
for their presence:

.. doctest::

    >>> myset = pyicl.IntIntervalSet()
    >>> myset += 42
    >>> print 42 in myset
    True


The segmental aspect supports efficiently iterating over a interval set or map. We would
rather not visit each element, we would rather visit whole segments at a time:

.. doctest::

	>>> news = pyicl.IntInterval(200000, 201500)
	>>> talk = pyicl.IntInterval(224530, 233050)
	>>> myTvPrograms = pyicl.IntIntervalSet()
	>>> myTvPrograms.add(news).add(talk) # doctest: +ELLIPSIS
	<_pyicl.IntIntervalSet object at 0x...>
	>>> for segment in myTvPrograms:
	...     print segment
	[200000,201500)
	[224530,233050)


We can test for an element's inclusion in an interval set just as we can in an interval:

.. doctest::

	>>> 201000 in myTvPrograms
	True
	>>> 210000 in myTvPrograms
	False
	>>> 230000 in myTvPrograms
	True



Addability and subtractability
------------------------------

For interval sets, addability is implemented as set union and subtractability is
implemented as set difference:

.. doctest::

    >>> interval1 = pyicl.IntInterval( 0, 10)
    >>> interval2 = pyicl.IntInterval( 5, 15)
    >>> interval3 = pyicl.IntInterval(20, 30)
    >>> intervalsetA = pyicl.IntIntervalSet()
    >>> intervalsetA += interval1
    >>> intervalsetA += interval3
    >>> print intervalsetA
    {[0,10)[20,30)}
    >>> intervalsetB = pyicl.IntIntervalSet()
    >>> intervalsetB += interval2
    >>> print intervalsetB
    {[5,15)}
    >>> print intervalsetA + intervalsetB
    {[0,15)[20,30)}
    >>> print intervalsetA - intervalsetB
    {[0,5)[20,30)}
    >>> print intervalsetB - intervalsetA
    {[10,15)}


For interval maps, addability and subtractability are more interesting, especially
when elements of the two maps collide:

.. doctest::

    >>> map = pyicl.IntIntervalObjectMap()
    >>> map += map.Segment(pyicl.IntInterval(0,10), 1)
    >>> map += map.Segment(pyicl.IntInterval(5,15), 2)
    >>> for segment in map:
    ...     print segment
    [0,5); 1
    [5,10); 3
    [10,15); 2
    >>> map -= map.Segment(pyicl.IntInterval(5,15), 2)
    >>> for segment in map:
    ...     print segment
    [0,10); 1
    [10,15); 0
    
   
    


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

