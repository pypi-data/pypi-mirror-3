"""
Tests for L{txzmq.connection}.
"""
from twisted.trial import unittest

class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """
    
    def make_push(self, *args, **kwargs):
        from txzmq.pushpull import ZmqPushConnection
        return ZmqPushConnection(self.factory, *args, **kwargs)

    def make_pull(self, *args, **kwargs):
        from txzmq.pushpull import ZmqPullConnection
        return ZmqPullConnection(self.factory, *args, **kwargs)
    
    def setUp(self):
        from txzmq.factory import ZmqFactory
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_send_recv(self):
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        pull = self.make_pull(callback=msg_func)
        pull.bind("inproc://#1")
        
        push = self.make_push()
        push.connect("inproc://#1")
        push.send(['abcd'])

        def check(ignore):
            expected = [['abcd']]
            self.assertEqual(result, expected)

        return _wait(0.1).addCallback(check)
    
    def test_send_to_multiple_nodes(self):
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg):
            result.append(msg)
        
        pull1 = self.make_pull(callback=msg_func)
        pull1.bind("inproc://#1")
        
        pull2 = self.make_pull(callback=msg_func)
        pull2.bind("inproc://#2")
        
        pull3 = self.make_pull(callback=msg_func)
        pull3.bind("inproc://#3")
        
        push = self.make_push()
        push.connect("inproc://#1")
        push.connect("inproc://#2")
        push.connect("inproc://#3")
        
        for i in range(1, 6+1):
            push.send(['msg%d' % i])
            
        def check(ignore):
            for i in range(1, 6+1):
                self.assertIn(['msg1'], result)

        return _wait(0.1).addCallback(check)