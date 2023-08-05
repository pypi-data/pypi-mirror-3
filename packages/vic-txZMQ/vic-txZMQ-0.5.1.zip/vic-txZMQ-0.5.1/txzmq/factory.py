"""
ZeroMQ Twisted factory which is controlling ZeroMQ context.
"""
import zmq

class ZmqFactory(object):
    """
    I control individual ZeroMQ connections.

    Factory creates and destroys ZeroMQ context.

    @cvar reactor: reference to Twisted reactor used by all the connections
    @ivar connections: set of instanciated L{ZmqConnection}s
    @type connections: C{set}
    @ivar context: ZeroMQ context
    @type context: L{Context}
    """

    def __init__(self, context=None, reactor=None, linger_period=100):
        """
        Constructor.

        Create ZeroMQ context.
        """
        self.reactor = reactor
        if self.reactor is None:
            from twisted.internet import reactor
            self.reactor = reactor
        self.context = context
        if self.context is None:
            self.context = zmq.Context.instance()
        self.linger_period = linger_period
        #: connections made with this factory
        self.connections = set()
        
    def socket(self, type):
        """Create a ZeroMQ socket, and set ZMQ_LINGER on it if 
        self.linger_period is not None 
        
        """
        s = self.context.socket(type)
        if self.linger_period is not None:
            s.setsockopt(zmq.LINGER, self.linger_period)
        return s

    def shutdown(self):
        """
        Shutdown factory.

        This is shutting down all created connections
        and terminating ZeroMQ context.
        """
        for connection in self.connections.copy():
            connection.shutdown()

        self.connections = None

        self.context.term()
        self.context = None

    def registerForShutdown(self):
        """
        Register factory to be automatically shut down
        on reactor shutdown.
        """
        self.reactor.addSystemEventTrigger('during', 'shutdown', self.shutdown)
