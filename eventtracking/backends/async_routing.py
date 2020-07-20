"""Route events to processors and backends"""

from __future__ import absolute_import

import json
import logging

import six

from json_tricks import dumps

from eventtracking.backends.routing import RoutingBackend
from eventtracking.backends.logger import DateTimeJSONEncoder
from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.tasks import async_send


LOG = logging.getLogger(__name__)


class AsyncRoutingBackend(RoutingBackend):
    """
    Route events to configured backends asynchronously
    """

    def send(self, event):
        """
        Process the event using all registered processors and send it to all registered backends.
        """
        try:
            processed_event = self.process_event(event)
        except EventEmissionExit:
            return

        try:
            json_event = json.dumps(processed_event, cls=DateTimeJSONEncoder)
        except ValueError:
            LOG.exception(
                'JSONEncodeError: Unable to encode event:%s', processed_event
            )
            return

        for name, backend in six.iteritems(self.backends):
            try:
                json_backend = dumps(backend)
            except ValueError:
                LOG.exception(
                    'JSONEncodeError: Unable to encode backend: %s', name
                )
                continue

            async_send.delay(json_backend, json_event, backend_name=name)
