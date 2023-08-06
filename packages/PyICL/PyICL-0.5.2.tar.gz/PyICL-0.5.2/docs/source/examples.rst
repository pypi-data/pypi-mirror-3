..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



Examples
========

We recreate some of the `boost.icl examples`__ in python.

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples.html




Party
-----

Example party demonstrates the possibilities of an interval map. Here is the description from the `boost.icl
C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/party.html

	An interval_map maps intervals to a given content. In this case the content is a set of party guests represented by their name strings.
	
	As time goes by, groups of people join the party and leave later in the evening. So we add a time interval and a name set to the interval_map for the attendance of each group of people, that come together and leave together. On every overlap of intervals, the corresponding name sets are accumulated. At the points of overlap the intervals are split. The accumulation of content is done via an operator += that has to be implemented for the content parameter of the interval_map. Finally the interval_map contains the history of attendance and all points in time, where the group of party guests changed.
	
	Party demonstrates a principle that we call aggregate on overlap: On insertion a value associated to the interval is aggregated with those values in the interval_map that overlap with the inserted value. There are two behavioral aspects to aggregate on overlap: a decompositional behavior and an accumulative behavior.
	
	- The decompositional behavior splits up intervals on the timedimension of the interval_map so that the intervals are split whenever associated values change.
	- The accumulative behavior accumulates associated values on every overlap of an insertion for the associated values.
	
	The aggregation function is += by default. Different aggregations can be used, if desired.

First we create some sets representing people who come to the party together.
The standard python set class does not implement += (__iadd__) and -= (__isub__) as the pyicl
package expects. We will use the pyicl package's version of set, pyicl.Set that plays much nicer
with pyicl.

    >>> import pyicl
    >>> mary_harry = pyicl.Set(('Mary', 'Harry'))
    >>> diana_susan = pyicl.Set(('Diana', 'Susan'))
    >>> peter = pyicl.Set(('Peter',))
	    
A party is an interval map that maps time intervals to sets of guests. We will use integers to
represent times.

    >>> party = pyicl.IntIntervalObjectMap()
    
We add a segment for Mary and Harry's attendance

    >>> party.add(party.Segment(pyicl.IntInterval(805201930, 805202300), mary_harry))
    <pyicl...IntIntervalObjectMap object at 0x...>
    
We can also use += to add segments

    >>> party += party.Segment(pyicl.IntInterval(805202010, 805210000), diana_susan)
    >>> party += party.Segment(pyicl.IntInterval(805202215, 805210030), peter)

Now we can access the history of party guests

    >>> print 'History of party guests.'
    History of party guests.
    >>> for segment in party:
    ...     when = segment.interval
    ...     who = segment.value
    ...     print '%s: %s' % (when, ', '.join(who))
    [805201930,805202010): Mary, Harry
    [805202010,805202215): Diana, Susan, Mary, Harry
    [805202215,805202300): Diana, Harry, Mary, Peter, Susan
    [805202300,805210000): Diana, Peter, Susan
    [805210000,805210030): Peter
    