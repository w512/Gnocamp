"Campfire streaming support"
import base64

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.protocols import basic
from twisted.python.failure import DefaultException
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

from pinder.campfire import USER_AGENT
from pinder.connector import json

def _get_response(response, callback, errback):
    response.deliverBody(StreamingParser(callback, errback))
    return Deferred()

def _shutdown(reason, errback):
    d = Deferred()
    d.addErrback(errback)
    d.errback(reason)
    if reactor.running:
        reactor.stop()

class StreamingParser(basic.LineReceiver):
    delimiter = '\r'

    def __init__(self, user_callback, user_errback):
        self.user_callback = user_callback
        self.user_errback = user_errback

    def lineReceived(self, line):
        d = Deferred()
        d.addCallback(self.user_callback)
        d.addErrback(self.user_errback)
        line = line.strip()
        try:
            d.callback(json.loads(line))
        except ValueError, e:
            if self.user_errback:
                d.errback(e)

    def connectionLost(self, reason):
        if self.user_errback:
            d = Deferred()
            d.addErrback(self.user_errback)
            d.errback(DefaultException(reason.getErrorMessage()))

def start(username, password, room_id, callback, errback):
    auth_header = 'Basic ' + base64.b64encode("%s:%s" % (username, password)).strip()
    url = 'https://streaming.campfirenow.com/room/%s/live.json' % room_id
    headers = Headers({
        'User-Agent': [USER_AGENT],
        'Authorization': [auth_header]})

    # issue the request
    agent = Agent(reactor)
    d = agent.request('GET', url, headers, None)
    d.addCallback(_get_response, callback, errback)
    d.addBoth(_shutdown, errback)
    reactor.run()
