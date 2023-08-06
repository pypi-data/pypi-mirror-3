"""
ZeroMQ connection.
"""
import logging
from collections import deque

from zmq.core import constants, error
from zope.interface import implements
from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor

class ZmqConnection(object):
    """
    Connection through ZeroMQ, wraps up ZeroMQ socket.

    @ivar factory: ZeroMQ Twisted factory reference
    @type factory: L{ZmqFactory}
    @ivar socket: ZeroMQ Socket
    @type socket: L{Socket}
    @ivar fd: file descriptor of zmq mailbox
    @type fd: C{int}
    @ivar queue: output message queue
    @type queue: C{deque}
    """
    implements(IReadDescriptor, IFileDescriptor)

    def __init__(self, factory, socket, callback=None, logger=None):
        """
        Constructor.

        @param factory: ZeroMQ Twisted factory
        @type factory: L{ZmqFactory}
        @param socket: ZeroMQ socket
        @type socket: L{Socket}
        @param callback: Function to be called when message received
        @type callback: L{Function}
        """
        self.logger = logger or logging.getLogger(__name__)
        self.factory = factory
        self.socket = socket
        self.callback = callback
        
        self.queue = deque()
        self.recv_parts = []
        
        self.fd = self.socket.getsockopt(constants.FD)
        self.factory.connections.add(self)
        self.factory.reactor.addReader(self)
        
    def setsockopt(self, option, optval):
        """Shortcut for self.socket.setsockopt
        
        """
        return self.socket.setsockopt(option, optval)
        
    def setsockopt_unicode(self, option, optval, encoding='utf-8'):
        """Shortcut for self.socket.setsockopt_unicode
        
        """
        return self.socket.setsockopt_unicode(option, optval, encoding)
    
    def getsockopt(self, option):
        """Shortcut for self.socket.getsockopt
        
        """
        return self.socket.getsockopt(option)
    
    def getsockopt_unicode(self, option, encoding='utf-8'):
        """Shortcut for self.socket.getsockopt
        
        """
        return self.socket.getsockopt_unicode(option, encoding)
    
    def connect(self, addr):
        """Shortcut for self.socket.connect
        
        """
        return self.socket.connect(addr)
    
    def bind(self, addr):
        """Shortcut for self.socket.bind
        
        """
        return self.socket.bind(addr)
    
    def bind_to_random_port(
        self, 
        addr, 
        min_port=49152, 
        max_port=65536, 
        max_tries=100
    ):
        """Shortcut for self.socket.bind
        
        """
        return self.socket.bind_to_random_port(addr, min_port, max_port, 
                                               max_tries)
    
    def shutdown(self):
        """
        Shutdown connection and socket.
        """
        self.factory.reactor.removeReader(self)
        self.factory.connections.discard(self)

        self.socket.close()
        self.socket = None
        
        self.factory = None

    def fileno(self):
        """
        Part of L{IFileDescriptor}.

        @return: The platform-specified representation of a file descriptor
                 number.
        """
        return self.fd

    def connectionLost(self, reason):
        """
        Called when the connection was lost.

        Part of L{IFileDescriptor}.

        This is called when the connection on a selectable object has been
        lost.  It will be called whether the connection was closed explicitly,
        an exception occurred in an event handler, or the other end of the
        connection closed it first.

        @param reason: A failure instance indicating the reason why the
                       connection was lost.  L{error.ConnectionLost} and
                       L{error.ConnectionDone} are of special note, but the
                       failure may be of other classes as well.
        """
        self.logger.error('Connection to ZeroMQ lost for reason %r', reason)
        if self.factory:
            self.factory.reactor.removeReader(self)

    def _readMultipart(self):
        """
        Read multipart in non-blocking manner, returns with ready message
        or raising exception (in case of no more messages available).
        """
        while True:
            self.recv_parts.append(self.socket.recv(constants.NOBLOCK))
            if not self.socket.getsockopt(constants.RCVMORE):
                result, self.recv_parts = self.recv_parts, []

                return result

    def doRead(self):
        """
        Some data is available for reading on your descriptor.

        ZeroMQ is signalling that we should process some events.

        Part of L{IReadDescriptor}.
        """
        if self.socket is None:
            self.logger.warn('Already closed, ignore doRead call')
            return
        events = self.socket.getsockopt(constants.EVENTS)
        if (events & constants.POLLIN) == constants.POLLIN:
            while True:
                if self.factory is None:  # disconnected
                    return
                try:
                    message = self._readMultipart()
                except error.ZMQError as e:
                    if e.errno == constants.EAGAIN:
                        break

                    raise e
                if self.callback:
                    try:
                        self.callback(message)
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception, e:
                        self.logger.error('Failed to call msg_func')
                        self.logger.exception(e)
                else:
                    self.logger.warn('msg_func is not set, ignore message %r', 
                                     message)
        if (events & constants.POLLOUT) == constants.POLLOUT:
            self._startWriting()

    def _startWriting(self):
        """
        Start delivering messages from the queue.
        """
        while self.queue:
            try:
                self.socket.send(
                    self.queue[0][1], constants.NOBLOCK | self.queue[0][0])
            except error.ZMQError as e:
                if e.errno == constants.EAGAIN:
                    break
                self.queue.popleft()
                raise e
            self.queue.popleft()

    def logPrefix(self):
        """
        Part of L{ILoggingContext}.

        @return: Prefix used during log formatting to indicate context.
        @rtype: C{str}
        """
        return 'ZMQ'

    def send(self, message):
        """
        Send message via ZeroMQ.

        @param message: message data
        """
        if not hasattr(message, '__iter__'):
            self.queue.append((0, message))
        else:
            self.queue.extend([(constants.SNDMORE, m) for m in message[:-1]])
            self.queue.append((0, message[-1]))

        # this is crazy hack: if we make such call, zeromq happily signals
        # available events on other connections
        self.socket.getsockopt(constants.EVENTS)

        self._startWriting()
        # Notice: sometimes, send operation is completed and data is available
        # for reading before we goes into select, namely, reactor
        # in this case, select can't catch a read event from fd
        # to solve the problem, we should check is there data to read here
        # it will clean the POLLIN event of the socket, it makes
        # the fd will be notified if there is event later
        self.factory.reactor.callFromThread(self.doRead)
