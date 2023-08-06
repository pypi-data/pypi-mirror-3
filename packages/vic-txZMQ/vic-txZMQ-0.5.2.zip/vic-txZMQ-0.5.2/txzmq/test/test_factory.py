"""
Tests for L{txzmq.factory}.
"""
from twisted.trial import unittest

class ZmqFactoryTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.factory.Factory}.
    """
    
    def make_one(self, *args, **kwargs):
        from txzmq.factory import ZmqFactory
        return ZmqFactory(*args, **kwargs)

    def setUp(self):
        pass

    def test_shutdown(self):
        factory = self.make_one()
        factory.shutdown()

    def test_socket_linger(self):
        """Make sure LINGER is set, also make sure that shutdown will return
        in time.
        
        """
        import zmq
        factory = self.make_one(linger_period=100)
        s = factory.socket(zmq.PUB)
        # this makes
        s.connect('tcp://127.0.0.1:1234')
        linger = s.getsockopt(zmq.LINGER)
        s.send('msg')
        s.close()
        self.assertEqual(linger, factory.linger_period)
        self.assertEqual(factory.linger_period, 100)
        
        from twisted.internet import defer
        from twisted.internet import reactor
        d = defer.Deferred()
        def shutdown():
            factory.shutdown()
            d.callback(None)
            if not call_id.called:
                call_id.cancel()
        def timeout():
            defer.timeout(d)
        call_id = reactor.callLater(1, timeout)
            
        import threading
        thread = threading.Thread(target=shutdown)
        thread.daemon = True
        thread.start()
        return d