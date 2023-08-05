"""
MOCK
====
Mocks are what we are talking about here:
objects pre-programmed with expectations which form a
specification of the calls they are expected to receive.

Stubs
=====
Stubs provide canned answers to calls made during the test,
usually not responding at all to anything outside what's programmed in for the test.

Dummy
=====
Dummy objects are passed around but never validated.

"""
from ludibrio.mock import Mock
from ludibrio.stub import Stub
from ludibrio.dummy import Dummy
from ludibrio.spy import Spy, verify, times

from ludibrio.matcher import *
