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
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Utility functions for oops_amqp."""

import errno
import socket

__all__ = [
    'close_ignoring_EPIPE',
    'is_amqplib_ioerror',
    'is_amqplib_connection_error',
    ]


def close_ignoring_EPIPE(closable):
    try:
        return closable.close()
    except socket.error, e:
        if e.errno != errno.EPIPE:
            raise


def is_amqplib_ioerror(e):
    """Returns True if e is an amqplib internal exception."""
    # Raised by amqplib rather than socket.error on ssl issues and short reads.
    return type(e) is IOError and e.args == ('Socket error',)


def is_amqplib_connection_error(e):
    """Return True if e was (probably) raised due to a connection issue."""
    return isinstance(e, socket.error) or is_amqplib_ioerror(e)
