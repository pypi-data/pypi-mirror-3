"""
Tests for L{txzmq.connection}.
"""
from twisted.trial import unittest

class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """
    
    def make_one(self, *args, **kwargs):
        from txzmq.pair import ZmqPairConnection
        return ZmqPairConnection(self.factory, *args, **kwargs)
    
    def setUp(self):
        from txzmq.factory import ZmqFactory
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_send_recv(self):
        from txzmq.test import _wait
        
        a_result = []
        def a_msg_func(msg):
            a_result.append(msg)
        
        b_result = []
        def b_msg_func(msg):
            b_result.append(msg)
            
        a = self.make_one(callback=a_msg_func)
        a.bind("inproc://#1")
        
        b = self.make_one(callback=b_msg_func)
        b.connect("inproc://#1")
        b.send(['b2a'])
        
        def check(ignore):
            expected = [['a2b']]
            self.assertEqual(b_result, expected)

        def check_and_send(ignore):
            expected = [['b2a']]
            self.assertEqual(a_result, expected)
            a.send(['a2b'])
            return _wait(0.1).addCallback(check)

        return _wait(0.1).addCallback(check_and_send)
    
    def test_send_lot(self):
        from txzmq.test import _wait
        
        a_result = []
        def a_msg_func(msg):
            a_result.append(msg)
        
        b_result = []
        def b_msg_func(msg):
            b_result.append(msg)
            
        a = self.make_one(callback=a_msg_func)
        a.bind("inproc://#1")
        
        b = self.make_one(callback=b_msg_func)
        b.connect("inproc://#1")
        
        a2b_msgs = [['a2b %d' % i] for i in range(100)]
        for m in a2b_msgs:
            a.send(m)
        b2a_msgs = [['b2a %d' % i] for i in range(100)]
        for m in b2a_msgs:
            b.send(m)
        
        def check(ignore):
            self.assertEqual(a_result, b2a_msgs)
            self.assertEqual(b_result, a2b_msgs)

        return _wait(0.1).addCallback(check)