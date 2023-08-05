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

"""Extensions to permit creatings OOPS reports with twisted types."""

__metaclass__ = type

__all__ = [
    'failure_to_context',
    ]


def failure_to_context(report, context):
    """If a twisted_failure key is present, use it to set context['exc_info'].

    This permits using regular python hooks with a twisted failure.
    """
    failure = context.get('twisted_failure')
    if not failure:
        return
    exc_info=(failure.type, failure.value, failure.getTraceback())
    context['exc_info'] = exc_info
    del exc_info # prevent cycles
