#!/usr/bin/python
"""
    test_iters.py                    Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

NRG 12/01/10
"""

import sys
import unittest
## import os
## sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import iters

if sys.version_info[:2] < (2, 4):
    sys.exit("This test requires Python 2.4+ generator expressions")

print iters.all
print iters.any

def expensive(truth, history=[]):
    print "Expensive test returning %s" % truth
    history.append(truth)
    return truth

class TestIters(unittest.TestCase):
    def setUp(self):
        self.seq = (True, True, False, True, True)

    def testall(self):
        print "all(%s):" % (self.seq,)
        # The cool thing about any() and all() is that if you use a generator
        # (in this case a generator expression), you get "short-circuit
        # evaluation" for a dynamic sequence of tests. You only pay for the
        # tests up until the first one at which the outcome can be determined.
        history = []
        result = iters.all(expensive(t, history) for t in self.seq)
        print "all() returns %s" % result
        self.assert_(not result)
        # Convert both to tuples to blur the difference between containers:
        # we just want to know whether the individual elements are equal.
        # (If either could be a tuple or a list, converting to tuple is
        # slightly cheaper: tuple() of a tuple returns the tuple unchanged,
        # whereas list() of a list returns a new copy of the list.)
        self.assertEqual(tuple(history), tuple(self.seq[:3]))
        self.assert_(not history[-1])

    def testany(self):
        seq = [(not t) for t in self.seq]
        print "any(%s):" % (seq,)
        history = []
        result = iters.any(expensive(t, history) for t in seq)
        print "any() returns %s" % result
        self.assert_(result)
        self.assertEqual(tuple(history), tuple(seq[:3]))
        self.assert_(history[-1])

if __name__ == "__main__":
    unittest.main()
