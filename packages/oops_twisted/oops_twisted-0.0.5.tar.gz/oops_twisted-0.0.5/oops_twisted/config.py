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

"""OOPS config and publishing for Twisted.

This module acts as an adapter for the oops.Config module - see `pydoc
oops.Config` for the primary documentation.

The only change is that Config.publish works with deferreds.

A helper function defer_publisher is supplied which can wrap a non-deferred
publisher.
"""

from functools import partial
from twisted.internet import defer
from twisted.internet.threads import deferToThread

import oops

from createhooks import failure_to_context

__all__ = [
    'Config',
    'defer_publisher',
    ]


class Config(oops.Config):
    """Twisted version of oops.Config.

    The only difference is that the publish method, which could block now
    expects each publisher to return a deferred.

    For more information see the oops.Config documentation.
    """

    def __init__(self, *args, **kwargs):
        oops.Config.__init__(self)
        self.on_create.insert(0, failure_to_context)

    def publish(self, report):
        """Publish a report.

        The report is first synchronously run past self.filters, then fired
        asynchronously at all of self.publishers.

        See `pydoc oops.Config.publish` for more documentation.

        :return: a twisted.internet.defer.Deferred. On success this deferred
            will return the list of oops ids allocated by the publishers (a
            direct translation of the oops.Config.publish result).
        """
        for report_filter in self.filters:
            if report_filter(report):
                return defer.succeed(None)
        if not self.publishers:
            return defer.succeed([])
        d = self.publishers[0](report)
        result = []
        def stash_id(id):
            report['id'] = id
            result.append(id)
            return report
        d.addCallback(stash_id)
        for publisher in self.publishers[1:]:
            d.addCallback(publisher)
            d.addCallback(stash_id)
        def return_result(_):
            return result
        d.addCallback(return_result)
        return d


def defer_publisher(publisher):
    """Wrap publisher in deferToThread."""
    return partial(deferToThread, publisher)
