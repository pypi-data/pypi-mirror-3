"""
ZeroMQ PUB-SUB wrappers.
"""
import zmq

from txzmq.connection import ZmqConnection

class ZmqPubConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    
    def __init__(self, factory, socket=None):
        if socket is None:
            socket = factory.context.socket(zmq.PUB)
        ZmqConnection.__init__(self, factory, socket)

class ZmqSubConnection(ZmqConnection):
    """
    Subscribing to messages.
    """
    
    def __init__(self, factory, socket=None, callback=None):
        if socket is None:
            socket = factory.context.socket(zmq.SUB)
        ZmqConnection.__init__(self, factory, socket, callback)