"""
Tests for L{txzmq.connection}.
"""
from twisted.trial import unittest

class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """
    
    def make_one(self, *args, **kwargs):
        from txzmq.connection import ZmqConnection
        return ZmqConnection(self.factory, *args, **kwargs)

    def setUp(self):
        from txzmq.factory import ZmqFactory
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_interfaces(self):
        from zope.interface import verify as ziv
        from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
        from txzmq.connection import ZmqConnection
        ziv.verifyClass(IReadDescriptor, ZmqConnection)
        ziv.verifyClass(IFileDescriptor, ZmqConnection)

    def test_send_recv(self):
        import zmq
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        r = self.make_one(self.factory.context.socket(zmq.PULL), msg_func)
        r.bind("inproc://#1")
        
        s = self.make_one(self.factory.context.socket(zmq.PUSH))
        s.connect("inproc://#1")
        s.send(['abcd'])

        def check(ignore):
            expected = [['abcd']]
            self.assertEqual(result, expected)

        return _wait(0.1).addCallback(check)

    def test_send_recv_tcp(self):
        import zmq
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        r = self.make_one(self.factory.context.socket(zmq.PULL), msg_func)
        r.bind("tcp://127.0.0.1:5555")
        
        s = self.make_one(self.factory.context.socket(zmq.PUSH))
        s.connect("tcp://127.0.0.1:5555")
        
        msgs = [[str(i)] for i in xrange(100)]
        for m in msgs:
            s.send(m)

        def check(ignore):
            self.assertEqual(result, msgs)

        return _wait(0.1).addCallback(check)