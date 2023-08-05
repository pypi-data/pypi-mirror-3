# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).
  
"""Extended WSGI support for Twisted."""

from oops_wsgi.middleware import generator_tracker
from twisted.internet.defer import Deferred
from twisted.web.iweb import IBodyProducer
from zope.interface import implements


__all__ = [
    'body_producer_tracker',
    ]

def body_producer_tracker(on_first_bytes, on_finish, on_error, app_body):
    """A wrapper for IBodyProducer that calls the OOPS hooks as needed.

    :seealso: generator_tracker which defines the contract for this factory
    function.

    :param on_first_bytes: Called as on_first_bytes() when the first bytes from
        the app body are available but before they are delivered.
    :param on_finish: Called as on_finish() when the app body is fully
        consumed.
    :param on_error: Called as on_error(sys.exc_info()) if a handleable error
        has occured while consuming the generator. Errors like GeneratorExit
        are not handleable. The return value from this is written to the
        consumer.
    :param app_body: The iterable body for the WSGI app. This may be a simple
        list or a generator or an IBodyProducer. If it is not an IBodyProducer
        then oops_wsgi.middleware.generator_tracker will be used.
    """
    if not IBodyProducer.providedBy(app_body):
        return generator_tracker(
            on_first_bytes, on_finish, on_error, app_body)
    return ProducerWrapper(on_first_bytes, on_finish, on_error, app_body)


class ProducerWrapper:
    """Wrap an IBodyProducer and call callbacks at key points.

    :seealso: body_producer_tracker - the main user of ProducerWrapper.
    """

    implements(IBodyProducer)

    def __init__(self, on_first_bytes, on_finish, on_error, app_body):
        self.on_first_bytes = on_first_bytes
        self.on_finish = on_finish
        self.on_error = on_error
        self.app_body = app_body
        # deferred returned from startProducing. If None the producer has
        # finished its work (or never been started).
        self.result = None
        # We wrap the consumer as well so that we can track the first write.
        self.consumer = None
        # Error page from OOPS
        self.error_data = None

    @property
    def length(self):
        if self.error_data is not None:
            return len(self.error_data)
        return self.app_body.length

    def startProducing(self, consumer):
        self.consumer = consumer
        self.written = False
        # Track production state
        self.paused = False
        # Error page from OOPS
        self.error_data = None
        # The deferred we return. Because we eat errors when an OOPS error page
        # is generated, we cannot return the underlying producers deferred.
        result = Deferred()
        self.result = result
        # Tell the wrapped producer to write to us.
        wrapped_result = self.app_body.startProducing(self)
        # We need a callback at the end to fire on_finish.
        wrapped_result.addCallback(self.wrapped_finished)
        # If an exception happens, we want to fire on_error.
        wrapped_result.addErrback(self.wrapped_failure)
        return result

    def stopProducing(self):
        # The deferred from startProducing must not fire.
        self.result = None
        self.app_body.stopProducing()

    def pauseProducing(self):
        self.paused = True
        self.app_body.pauseProducing()

    def resumeProducing(self):
        if self.error_data is not None:
            self.consumer.write(self.error_data)
            result = self.result
            self.result = None
            result.callback(None)
        else:
            self.app_body.resumeProducing()

    def write(self, data):
        if not self.written:
            self.written = True
            self.on_first_bytes()
        self.consumer.write(data)

    def wrapped_finished(self, ignored):
        result = self.result
        self.result = None
        try:
            self.on_finish()
        except:
            result.errback()
        else:
            result.callback(None)

    def wrapped_failure(self, failure):
        try:
            exc_info = (
                failure.type, failure.value, failure.getTracebackObject())
            self.error_data = self.on_error(exc_info)
        except:
            result = self.result
            self.result = None
            result.errback()
        else:
            if not self.paused:
                self.consumer.write(self.error_data)
                result = self.result
                self.result = None
                result.callback(None)
            # Received an error from the producer while it was paused, and OOPS
            # generated an error page. This will be buffered until we are unpaused.
