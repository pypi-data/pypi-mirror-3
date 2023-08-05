#
# Copyright (c) 2011, Canonical Ltd
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

"""OOPS error reports for Twisted.

The oops_twisted package provides integration glue between logged twisted
errors (via the twisted.log api) and the oops error reporting system
(http://pypi.python.org/pypi/oops).

Dependencies
============

* Python 2.6+

* oops (http://pypi.python.org/pypi/oops)

* Twisted

Testing Dependencies
====================

* subunit (http://pypi.python.org/pypi/python-subunit) (optional)

* testtools (http://pypi.python.org/pypi/testtools)

Usage
=====

* Setup your configuration::

  >>> from oops_twisted import Config
  >>> config = Config()

Note that you will probably want at least one publisher, or your reports will
be silently discarded.

* When adding publishers, either wrap 'normal' OOPS publishers in deferToThread
  or similar, or use native Twisted publishers. For instance::

 >>> from functools import partial
 >>> config.publishers.append(partial(deferToThread, blocking_publisher))

 A helper 'defer_publisher' is supplied to do this for your convenience.

* create an OOPS log observer::

 >>> from oops_twisted import OOPSObserver
 >>> observer = OOPSObserver(config)

* And enable it::

 >>> observer.start()

* This is typically used to supplement regular logging, e.g. you might
  initialize normal logging to a file first::

 >>> twisted.log.startLogging(logfile)

The OOPSObserver will discard all non-error log messages, and convert error log
messages into OOPSes using the oops config.

Optionally, you can provide OOPSObserver with a second observer to delegate
too. Any event that is not converted into an OOPS is passed through unaltered.
Events that are converted to OOPSes have a new event second to the second
observer which provides the OOPS id and the failure name and value::

 >>> observer = OOPSObserver(config, twisted.log.PythonLoggingObserver().emit)

If the OOPS config has no publishers, the fallback will receive unaltered
failure events (this stops them getting lost). If there are publishers but the
OOPS is filtered, the fallback will not be invoked at all (this permits e.g.
rate limiting of failutes via filters).
"""


# same format as sys.version_info: "A tuple containing the five components of
# the version number: major, minor, micro, releaselevel, and serial. All
# values except releaselevel are integers; the release level is 'alpha',
# 'beta', 'candidate', or 'final'. The version_info value corresponding to the
# Python version 2.0 is (2, 0, 0, 'final', 0)."  Additionally we use a
# releaselevel of 'dev' for unreleased under-development code.
#
# If the releaselevel is 'alpha' then the major/minor/micro components are not
# established at this point, and setup.py will use a version of next-$(revno).
# If the releaselevel is 'final', then the tarball will be major.minor.micro.
# Otherwise it is major.minor.micro~$(revno).
__version__ = (0, 0, 3, 'beta', 0)

__all__ = [
    'Config',
    'defer_publisher',
    'OOPSObserver',
    ]

from oops_twisted.config import (
    Config,
    defer_publisher,
    )
from oops_twisted.log import OOPSObserver
