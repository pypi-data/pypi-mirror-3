"""
ZeroMQ PUB-SUB wrappers.
"""
import uuid

import zmq
from twisted.internet import defer

from txzmq.connection import ZmqConnection

class ZmqReqConnection(ZmqConnection):
    """
    A REQ connection.
    """

    def __init__(self, factory, socket=None):
        if socket is None:
            socket = factory.socket(zmq.DEALER)
        self._requests = {}
        self._timeout_calls = {}
        ZmqConnection.__init__(self, factory, socket, self.messageReceived)

    def _getNextId(self):
        """
        Returns an unique id.
        """
        return uuid.uuid4().hex

    def request(self, message_parts, timeout=None, call_later=None):
        """
        Send L{message} with specified L{tag}.

        @param message_parts: message data
        @type message: C{tuple}
        """
        d = defer.Deferred()
        msg_id = self._getNextId()
        self._requests[msg_id] = d
        self.send([msg_id, ''] + list(message_parts))
        
        def call_timeout():
            if not d.called:
                defer.timeout(d)
        if timeout:
            if call_later is None:
                call_later = self.factory.reactor. callLater
            self._timeout_calls[msg_id] = call_later(timeout, call_timeout)
        return d

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        msg_id, _, msg = message[0], message[1], message[2:]
        timeout_call = self._timeout_calls.pop(msg_id, None)
        if timeout_call is not None and not timeout_call.called:
            timeout_call.cancel()
        d = self._requests.pop(msg_id)
        if not d.called:
            d.callback(msg)

class ZmqRepConnection(ZmqConnection):
    """
    A REP connection.
    """

    def __init__(self, factory, callback, socket=None):
        if socket is None:
            socket = factory.socket(zmq.ROUTER)
        self.req_callback = callback
        self._routing_info = {}  # keep track of routing info
        ZmqConnection.__init__(self, factory, socket, self.messageReceived)

    def reply(self, message_id, message_parts):
        """
        Send L{message} with specified L{tag}.

        @param message_id: message uuid
        @type message_id: C{str}
        @param message: message data
        @type message: C{str}
        """
        routing_info = self._routing_info.pop(message_id)
        self.send(routing_info + [message_id, ''] + list(message_parts))

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        i = message.index('')
        assert i > 0
        (routing_info, msg_id, payload) = (
            message[:i - 1], message[i - 1], message[i + 1:])
        msg_parts = payload[0:]
        self._routing_info[msg_id] = routing_info
        self.req_callback(msg_id, msg_parts)
        
def _deprecated(deprecated, instead):
    import warnings
    msg = "Class %s was deprecated, use %s instead" % (
        deprecated.__name__, instead.__name__)
    warnings.warn(msg, DeprecationWarning)
    
class ZmqXREQConnection(ZmqReqConnection):
    def __init__(self, *args, **kwargs):
        _deprecated(self.__class__, ZmqRepConnection)
        ZmqReqConnection.__init__(self, *args, **kwargs)
    
class ZmqXREPConnection(ZmqRepConnection):
    def __init__(self, *args, **kwargs):
        _deprecated(self.__class__, ZmqRepConnection)
        ZmqRepConnection.__init__(self, *args, **kwargs)