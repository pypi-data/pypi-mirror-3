"""
Tests for L{txzmq.factory}.
"""
from twisted.trial import unittest

class ZmqFactoryTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.factory.Factory}.
    """
    
    def make_one(self):
        from txzmq.factory import ZmqFactory
        return ZmqFactory()

    def setUp(self):
        self.factory = self.make_one()

    def test_shutdown(self):
        self.factory.shutdown()
