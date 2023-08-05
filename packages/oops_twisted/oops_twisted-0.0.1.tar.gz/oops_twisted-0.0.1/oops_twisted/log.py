# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Affero General Public License version 3 (see the file LICENSE).

"""twisted.log observer to create OOPSes for failures."""

__metaclass__ = type

import datetime

from pytz import utc
from twisted.python.log import textFromEventDict


__all__ = [
    'OOPSObserver',
    ]


class OOPSObserver:
    """Convert twisted log events to OOPSes if they are failures."""

    def __init__(self, config, fallback=None):
        """"Create an OOPSObserver.

        :param config: An oops_twisted.Config.
        :param fallback: If supplied, a LogObserver to pass non-failure log
            events to, and to inform (as non-failures) when an OOPS has
            occurred.
        """
        self.config = config
        self.fallback = fallback

    def emit(self, eventDict):
        """Handle a twisted log entry.
        
        :return: For testing convenience returns the oops report and a deferred
            which fires after all publication and fallback forwarding has
            occured, though the twisted logging protocol does not need (or
            examine) the return value.
        """
        if not eventDict.get('isError'):
            if self.fallback:
                self.fallback(eventDict)
            return None, None
        context = {}
        if 'failure' in eventDict:
            failure = eventDict['failure']
            exc_info=(failure.type, failure.value, failure.getTraceback())
            context['exc_info'] = exc_info
            del exc_info # prevent cycles
        report = self.config.create(context)
        report['time'] = datetime.datetime.fromtimestamp(
            eventDict['time'], utc)
        report['tb_text'] = textFromEventDict(eventDict)
        d = self.config.publish(report)
        if self.fallback:
            d.addCallback(self._fallback_report, report, dict(eventDict))
        return report, d

    def _fallback_report(self, ids, report, event):
        event['isError'] = False
        event.pop('failure', None)
        event['message'] = "Logged OOPS id %s: %s: %s" % (
            report['id'], report['type'], report['value']) 
        self.fallback(event)
