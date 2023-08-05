"""
Tests for L{txzmq.xreq_xrep}.
"""
from twisted.trial import unittest

class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """
    
    def make_req(self, *args, **kwargs):
        from txzmq.reqrep import ZmqXREQConnection
        return ZmqXREQConnection(self.factory, *args, **kwargs)

    def make_rep(self, *args, **kwargs):
        from txzmq.reqrep import ZmqXREPConnection
        return ZmqXREPConnection(self.factory, *args, **kwargs)

    def setUp(self):
        from txzmq.factory import ZmqFactory
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_send_recv(self):
        from txzmq.test import _wait
        
        result = []
        def msg_func(msg_id, msg_parts):
            result.append(msg_parts)
        
        rep = self.make_rep(callback=msg_func)
        rep.bind('inproc://#1')
            
        req = self.make_req()
        req.connect('inproc://#1')
        req.request(['hello', 'baby'])

        def check(ignore):
            expected = [['hello', 'baby']]
            self.assertEqual(result, expected)

        return _wait(0.1).addCallback(check)

    def test_send_recv_reply(self):
        from twisted.internet import reactor
        from twisted.internet import defer
        
        def reply_func(msg_id, msg_parts):
            rep.reply(msg_id, ['reply'] + msg_parts)
        
        rep = self.make_rep(callback=reply_func)
        rep.bind('inproc://#1')
            
        req = self.make_req()
        req.connect('inproc://#1')
        
        d = req.request(['hello', 'baby'])
        
        def timeout():
            if not d.called:
                defer.timeout(d)
        call_id = reactor.callLater(0.1, timeout)
        
        def check(msg):
            expected = ['reply', 'hello', 'baby']
            self.assertEqual(msg, expected)
            if not call_id.called:
                call_id.cancel()
        d.addCallback(check)
            
        return d
    
    def test_request_with_timeout(self):
        rep = self.make_rep(callback=lambda msg_id, msg_parts: None)
        rep.bind('inproc://no-reply')
        # connect to a non-exist 
        req = self.make_req()
        req.connect('inproc://no-reply')

        from twisted.internet import task
        clock = task.Clock()
                
        d = req.request(['a', 'b', 'c'], timeout=5, call_later=clock.callLater)
        def check_timeout(failure):
            from twisted.internet.defer import TimeoutError
            self.assertEqual(failure.type, TimeoutError)
        d.addBoth(check_timeout)
        
        clock.advance(11)
        return d
    
    def test_request_with_timeout_not_trigged(self):
        from twisted.internet import reactor
        from twisted.internet import defer
        
        def reply_func(msg_id, msg_parts):
            rep.reply(msg_id, ['reply'] + msg_parts)
        
        rep = self.make_rep(callback=reply_func)
        rep.bind('inproc://#1')
            
        req = self.make_req()
        req.connect('inproc://#1')
        
        d = req.request(['hello', 'baby'], timeout=10)
        
        def timeout():
            if not d.called:
                defer.timeout(d)
        call_id = reactor.callLater(0.1, timeout)
        
        def check(msg):
            expected = ['reply', 'hello', 'baby']
            self.assertEqual(msg, expected)
            if not call_id.called:
                call_id.cancel()
        d.addCallback(check)
        return d
            
    def test_read_signal_up_when_send_bug(self):
        """Reference to https://github.com/smira/txZMQ/pull/3
        
        """
        import zmq
        import threading
        from twisted.internet import reactor
        from twisted.internet import defer
        
        rep = zmq.Context.instance().socket(zmq.REP)
        rep.bind('tcp://127.0.0.1:5555')
        def reply():
            for _ in range(2):
                msgs = rep.recv_multipart()
                rep.send_multipart(['reply'] + msgs)
        thread = threading.Thread(target=reply)
        thread.start()
            
        req = self.make_req()
        req.connect('tcp://127.0.0.1:5555')
        
        req.request(['a'])
        # wait until the request is replied
        # then FD will be notified with read signal, if we don't check
        # socket events in send() and try to read something, then
        # we have no second chance to be notified, then the reading
        # is stopped. If we do read in send, then it will make sure
        # the event is reset by reading, FD can then be notified later
        while True:
            events = req.socket.getsockopt(zmq.EVENTS)
            if (events & zmq.POLLIN) == zmq.POLLIN:
                break
        
        d = req.request(['hello', 'baby'])
        
        def timeout():
            if not d.called:
                defer.timeout(d)
        call_id = reactor.callLater(1, timeout)
        
        def check(msg):
            expected = ['reply', 'hello', 'baby']
            self.assertEqual(msg, expected)
            if not call_id.called:
                call_id.cancel()
        d.addCallback(check)
            
        return d