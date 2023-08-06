..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



Interval Types
==============



Intervals
---------


Intervals are right-open by default
    
    >>> from pyicl import Interval
    >>> interval = Interval(0, 10)
    >>> print interval
    [0,10)
    >>> 0 in interval
    True
    >>> 10 in interval
    False


This is shown by square and round brackets in the string representation

    >>> from pyicl import IntervalBounds
    >>> print Interval(0, 3)
    [0,3)
    >>> print Interval(0, 3, IntervalBounds.left_open())
    (0,3]
    >>> print Interval(0, 3, IntervalBounds.closed())
    [0,3]
    >>> print Interval(0, 3, IntervalBounds.open())
    (0,3)
    
    
The bounds can be accessed as lower and upper

    >>> Interval(0, 3).lower
    0
    >>> Interval(0, 3).upper
    3


Integer intervals also have first and last properties. This is only possible as integer is a discrete
data type. For continuous data types, open intervals would not have a first or a last member.

    >>> from pyicl import IntInterval
    >>> IntInterval(0, 3).first
    0
    >>> IntInterval(0, 3).last
    2


Intervals are false if empty

    >>> bool(Interval())
    False
    >>> Interval().empty
    True
    >>> bool(Interval(1, 10))
    True


Element and interval membership is straightforward

    >>> 1 in Interval(0, 2)
    True
    >>> 3 in Interval(0, 2)
    False
    >>> Interval(0, 2) in Interval(0, 2)
    True
    >>> Interval(0, 3) in Interval(0, 2)
    False


Equivalence works as expected

    >>> Interval(0, 2) == Interval(0, 2)
    True
    >>> Interval(0, 3) != Interval(0, 2)
    True


Ordering works thus

    >>> Interval(1, 3) < Interval(5, 6)
    True
    >>> Interval(5, 6) > Interval(1, 3)
    True
    >>> Interval(1, 3) < Interval(1, 5)
    True
    >>> Interval(1, 5) > Interval(1, 3)
    True
    >>> Interval(1, 3) <= Interval(5, 6)
    True
    >>> Interval(5, 6) >= Interval(1, 3)
    True
    >>> Interval(1, 3) <= Interval(1, 5)
    True
    >>> Interval(1, 5) >= Interval(1, 3)
    True
    >>> Interval(1, 3) > Interval(5, 6)
    False
    >>> Interval(5, 6) < Interval(1, 3)
    False
    >>> Interval(1, 3) > Interval(1, 5)
    False
    >>> Interval(1, 5) < Interval(1, 3)
    False


There are also tests for exclusive ordering

    >>> IntInterval(1, 3).exclusive_less(IntInterval(1, 5))
    False
    >>> IntInterval(1, 5).exclusive_less(IntInterval(5, 7))
    True
    >>> IntInterval(1, 5).lower_less(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).lower_less(IntInterval(1, 7))
    False
    >>> IntInterval(1, 5).lower_equal(IntInterval(1, 7))
    True
    >>> IntInterval(1, 5).lower_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).lower_less_equal(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).lower_less_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).upper_less(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).upper_less(IntInterval(1, 5))
    False
    >>> IntInterval(1, 5).upper_equal(IntInterval(1, 5))
    True
    >>> IntInterval(1, 5).upper_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).upper_less_equal(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).upper_less_equal(IntInterval(0, 3))
    False


Size comes in different forms. Discrete data types have a cardinality property

    >>> from pyicl import FloatInterval
    >>> IntInterval(1, 5).size
    4
    >>> IntInterval(1, 5).cardinality
    4
    >>> len(Interval(1, 5))
    4
    >>> len(FloatInterval(1, 5))
    4


Intervals can be subtracted from the left or the right

    >>> print Interval(1, 5).right_subtract(Interval(3, 5))
    [1,3)
    >>> print Interval(1, 5).left_subtract(Interval(1, 3))
    [3,5)


Intervals can be intersected and tested for intersections and disjointedness

    >>> print Interval(1, 5).intersection(Interval(0, 3))
    [1,3)
    >>> Interval(1, 3) == Interval(1, 5) & Interval(0, 3)
    True
    >>> interval = Interval(1, 5)
    >>> interval &= Interval(0, 3)
    >>> Interval(1, 3) == interval 
    True
    >>> Interval(3, 5).intersects(Interval(1, 4))
    True
    >>> Interval(3, 5).intersects(Interval(1, 3))
    False
    >>> Interval(3, 5).disjoint(Interval(1, 4))
    False
    >>> Interval(3, 5).disjoint(Interval(1, 3))
    True

    
Intervals can be tested whether they touch one another. "Touches" is not a reflexive operation.

    >>> Interval(0, 3).touches(Interval(3, 5))
    True
    >>> Interval(0, 3).touches(Interval(4, 5))
    False
    >>> Interval(0, 3).touches(Interval(2, 5))
    False
    >>> Interval(3, 5).touches(Interval(0, 3))
    False
    