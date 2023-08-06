#
# Copyright John Reid 2012
#

import _pyicl as P
import cStringIO, cPickle

# set up Interval test
interval = P.IntInterval(0, 10)
assert 0 in interval
assert 9 in interval
assert 10 not in interval

# write to string
f = cStringIO.StringIO()
cPickle.dump(interval, f)
f.flush()

# Read from string
in_f = cStringIO.StringIO(f.getvalue())
pickled = cPickle.load(in_f)

# check the same
assert P.IntInterval == type(pickled)
assert pickled == interval
assert 0 in pickled
assert 9 in pickled
assert 10 not in pickled



# IntervalSet test
interval_set = P.IntIntervalSet()
interval_set += P.IntInterval( 0, 10)
interval_set += P.IntInterval(20, 30)
assert 0 in interval_set
assert 9 in interval_set
assert 10 not in interval_set
assert 20 in interval_set
assert 29 in interval_set
assert 30 not in interval_set

# write to string
f = cStringIO.StringIO()
cPickle.dump(interval_set, f)
f.flush()

# Read from string
in_f = cStringIO.StringIO(f.getvalue())
pickled = cPickle.load(in_f)

# check the same
assert P.IntIntervalSet == type(pickled)
assert pickled == interval_set
assert 0 in pickled
assert 9 in pickled
assert 10 not in pickled
assert 20 in pickled
assert 29 in pickled
assert 30 not in pickled



