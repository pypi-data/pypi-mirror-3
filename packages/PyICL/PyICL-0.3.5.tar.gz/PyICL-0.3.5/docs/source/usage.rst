..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



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
    
   
    
