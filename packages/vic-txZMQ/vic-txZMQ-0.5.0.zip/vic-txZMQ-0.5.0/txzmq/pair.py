"""
ZeroMQ PAIR wrappers.
"""
import zmq

from txzmq.connection import ZmqConnection

class ZmqPairConnection(ZmqConnection):
    """Pair connection
    
    """
    
    def __init__(self, factory, socket=None, callback=None):
        if socket is None:
            socket = factory.context.socket(zmq.PAIR)
        ZmqConnection.__init__(self, factory, socket, callback)