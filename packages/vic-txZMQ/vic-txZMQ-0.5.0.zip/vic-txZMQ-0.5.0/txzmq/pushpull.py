"""
ZeroMQ PUSH-PULL wrappers.
"""
import zmq

from txzmq.connection import ZmqConnection

class ZmqPushConnection(ZmqConnection):
    """Push message to downstream
    
    """
    
    def __init__(self, factory, socket=None):
        if socket is None:
            socket = factory.context.socket(zmq.PUSH)
        ZmqConnection.__init__(self, factory, socket)

class ZmqPullConnection(ZmqConnection):
    """Pull messages from upstream
    
    """
    
    def __init__(self, factory, socket=None, callback=None):
        if socket is None:
            socket = factory.context.socket(zmq.PULL)
        ZmqConnection.__init__(self, factory, socket, callback)