"""
Tests for L{txzmq.pubsub}.
"""
from twisted.trial import unittest

class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """
    
    def make_pub(self, *args, **kwargs):
        from txzmq.pubsub import ZmqPubConnection
        return ZmqPubConnection(self.factory, *args, **kwargs)

    def make_sub(self, *args, **kwargs):
        from txzmq.pubsub import ZmqSubConnection
        return ZmqSubConnection(self.factory, *args, **kwargs)

    def setUp(self):
        from txzmq.factory import ZmqFactory
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_pub_sub(self):
        import zmq
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        sub = self.make_sub(callback=msg_func)
        sub.bind('inproc://#1')
        sub.setsockopt(zmq.SUBSCRIBE, '')
        
        pub = self.make_pub()
        pub.connect('inproc://#1')
        
        pub.send(['a', 'b', 'c'])
        pub.send(['1', '2', '3'])
        
        def check(ignore):
            expected = [['a', 'b', 'c'], ['1', '2', '3']]
            self.assertEqual(result, expected)

        return _wait(0.1).addCallback(check)
    
    def test_pub_sub_with_filter(self):
        import zmq
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        sub = self.make_sub(callback=msg_func)
        sub.bind('inproc://#1')
        sub.setsockopt(zmq.SUBSCRIBE, 'a')
        
        pub = self.make_pub()
        pub.connect('inproc://#1')
        
        pub.send(['a', 'data1'])
        pub.send(['b', 'data2'])
        pub.send(['a', 'data3'])
        pub.send(['a', 'data4'])
        
        def check(ignore):
            expected = [['a', 'data1'], ['a', 'data3'], ['a', 'data4']]
            self.assertEqual(result, expected)

        return _wait(0.1).addCallback(check)