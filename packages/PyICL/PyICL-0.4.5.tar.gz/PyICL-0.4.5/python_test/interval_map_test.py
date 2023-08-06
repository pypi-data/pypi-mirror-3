#
# Copyright John Reid 2011
#

from setup_environment import init_test_env, update_path_for_tests, logging
init_test_env(__file__, level=logging.INFO)
update_path_for_tests()

import pyicl as P
#import _pyicl as P

# Segment/Element construction
P.IntIntervalObjectMap.Element(1, object())
P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object())

# Construction
P.IntIntervalObjectMap()
#P.IntIntervalObjectMap(P.IntIntervalObjectMap.Element(1, object()))
P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object()))
print P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object()))
P.IntIntervalObjectMap(P.IntIntervalObjectMap())
P.FloatIntervalSet()
P.FloatIntervalSet(.1)
interval_set = P.FloatIntervalSet(P.FloatInterval(.1, .9))
P.FloatIntervalSet(interval_set)

# Iteration
for segment in P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object())):
    print str(segment.interval), str(segment.value)
assert P.IntInterval(1, 5) == P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object())).find(2).interval

# empty-ness
assert not P.IntIntervalObjectMap()
assert P.IntIntervalObjectMap().empty
assert P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object()))
assert not P.IntIntervalObjectMap(P.IntIntervalObjectMap.Segment(P.IntInterval(1, 5), object())).empty

# containedness
o = object()
interval = P.IntInterval(1, 5)
element = P.IntIntervalObjectMap.Element(1, o)
segment = P.IntIntervalObjectMap.Segment(interval, o)
empty_map = P.IntIntervalObjectMap()
map = P.IntIntervalObjectMap(segment)
assert 1 not in empty_map
assert 1 in map
assert interval not in P.IntIntervalObjectMap()
assert interval in map
assert element not in empty_map
assert element in map
assert segment not in empty_map
assert segment in map

# Equivalences and Orderings
assert empty_map == P.IntIntervalObjectMap()
assert map == P.IntIntervalObjectMap(segment)
assert map != P.IntIntervalObjectMap()
assert empty_map != P.IntIntervalObjectMap(segment)

# Size
assert 0 == empty_map.size
assert 4 == map.size
assert 4 == map.cardinality
assert 4 == len(map)
assert 1 == map.iterative_size
assert 1 == map.interval_count

# Range
#    assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).lower
#    assert 5 == P.IntIntervalSet(P.IntInterval(1, 5)).upper
#    assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).first
#    assert 4 == P.IntIntervalSet(P.IntInterval(1, 5)).last

# Subtraction
assert P.IntInterval(1, 3) == P.IntInterval(1, 5).right_subtract(P.IntInterval(3, 5))
assert P.IntInterval(3, 5) == P.IntInterval(1, 5).left_subtract(P.IntInterval(1, 3))

# Intersection
assert P.IntInterval(1, 3) == P.IntInterval(1, 5).intersection(P.IntInterval(0, 3))
assert P.IntInterval(1, 3) == P.IntInterval(1, 5) & P.IntInterval(0, 3)
interval = P.IntInterval(1, 5)
interval &= P.IntInterval(0, 3)
assert P.IntInterval(1, 3) == interval 
assert P.IntInterval(3, 5).intersects(P.IntInterval(1, 4))
assert not P.IntInterval(3, 5).intersects(P.IntInterval(1, 3))
assert not P.IntInterval(3, 5).disjoint(P.IntInterval(1, 4))
assert P.IntInterval(3, 5).disjoint(P.IntInterval(1, 3))

assert '[1,5)' == str(P.IntInterval(1, 5))
assert '[1,5)' == str(P.FloatInterval(1, 5))


