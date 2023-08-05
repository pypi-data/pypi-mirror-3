"""
Tests for L{txzmq}.
"""

def _wait(interval):
    from twisted.internet import defer, reactor
    d = defer.Deferred()
    reactor.callLater(interval, d.callback, None)
    return d
