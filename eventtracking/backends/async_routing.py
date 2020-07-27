"""
Route events to processors and backends
"""

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
    Route events to configured backends asynchronously.

    After processing the event through the configured processors, each of the backends
    is then JSON serialized and then is passed along with the processed event to
    the celery task `async_send` where the backend will be deserialized for sending
    the processed event.
    """

    def send(self, event):
        """
        Process the event using all registered processors and send it to all registered backends.

        Arguments:
            event (dict):   Analytics event dictionary

        Returns:
            None
        """
        try:
            processed_event = self.process_event(event)
            LOG.info('Event {} is processed successfully'.format(event['name']))

            json_event = json.dumps(processed_event, cls=DateTimeJSONEncoder)

        except EventEmissionExit:
            LOG.error('Event {} could not be processed'.format(event['name']))
            return

        except (ValueError, TypeError):
            LOG.exception(
                'JSONEncodeError: Unable to encode event: {}'.format(processed_event),
                exc_info=True
            )
            return

        for name, backend in six.iteritems(self.backends):
            try:
                json_backend = dumps(backend)
            except ValueError:
                LOG.exception(
                    'JSONEncodeError: Unable to encode backend: {}'.format(name)
                )
                continue

            async_send.delay(json_backend, json_event, backend_name=name)
