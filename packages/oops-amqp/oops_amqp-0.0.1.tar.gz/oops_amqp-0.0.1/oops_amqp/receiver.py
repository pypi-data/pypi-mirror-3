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

"""Receive OOPS reports over amqp and republish locally."""

__metaclass__ = type

import bson

__all__ = [
    'Receiver',
    ]

class Receiver:
    """Republish OOPS reports from AMQP to a local oops.Config.
    
    :ivar stopping: When True will cause Receiver to break out of run_forever.
    """

    def __init__(self, config, channel, queue_name):
        """Create a Receiver.

        :param config: An oops.Config to republish the OOPS reports.
        :param channel: An amqplib Channel to listen for reports on.
        :param queue_name: The queue to listen for reports on.
        """
        self.config = config
        self.channel = channel
        self.queue_name = queue_name
        self.stopping = False

    def handle_report(self, message):
        if self.stopping:
            self.channel.basic_cancel(self.consume_tag)
        try:
            report = bson.loads(message.body)
        except KeyError:
            # Garbage in the queue. Possibly this should raise an OOPS itself
            # (through a different config) or log an info level message.
            pass
        self.config.publish(report)
        # ACK last so errors here don't eat the message.
        self.channel.basic_ack(message.delivery_tag)
    
    def run_forever(self):
        self.consume_tag = self.channel.basic_consume(
            self.queue_name, callback=self.handle_report)
        self.channel.wait()
