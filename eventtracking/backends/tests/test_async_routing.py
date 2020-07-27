"""
Test the async routing backend
"""

from __future__ import absolute_import

import json
from unittest import TestCase

from mock import MagicMock, call, sentinel, patch
from eventtracking.backends.async_routing import AsyncRoutingBackend
from eventtracking.processors.exceptions import EventEmissionExit


class TestAsyncRoutingBackend(TestCase):
    """
    Test the async routing backend
    """

    def setUp(self):
        super(TestAsyncRoutingBackend, self).setUp()
        self.sample_event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'event': {
                'key': 'value'
            },
            'session': '0000'
        }

        self.mocked_backends = {
            str(i): MagicMock() for i in range(3)
        }

    @patch('eventtracking.backends.async_routing.async_send')
    def test_event_emission_exit(self, mocked_async_send):
        mocked_processor = MagicMock(side_effect=EventEmissionExit)
        backend = AsyncRoutingBackend(processors=[
            mocked_processor
        ])
        backend.send(self.sample_event)
        mocked_async_send.assert_not_called()

    @patch('eventtracking.backends.async_routing.LOG')
    @patch('eventtracking.backends.async_routing.json.dumps', side_effect=ValueError)
    @patch('eventtracking.backends.async_routing.async_send')
    def test_with_value_error_in_event_json_encoding(self, mocked_async_send, _, mocked_log):

        backend = AsyncRoutingBackend()
        backend.send(self.sample_event)

        mocked_log.exception.assert_called_once_with(
            'JSONEncodeError: Unable to encode event: {}'.format(self.sample_event),
            exc_info=True
        )
        mocked_async_send.assert_not_called()

    @patch('eventtracking.backends.async_routing.dumps')
    @patch('eventtracking.backends.async_routing.LOG')
    @patch('eventtracking.backends.async_routing.async_send.delay')
    def test_with_value_error_in_one_backend_json_encoding(
        self, mocked_async_send, mocked_log, mocked_dumps
    ):
        """
        Test the backend's send method when one of the three backends
        could not be encoded into json.
        """
        mocked_dumps.side_effect = [ValueError, '{"mocked_backend":1}', '{"mocked_backend":2}']
        json_event = json.dumps(self.sample_event)

        backend = AsyncRoutingBackend(backends=self.mocked_backends)
        backend.send(self.sample_event)

        mocked_log.exception.assert_called_once_with('JSONEncodeError: Unable to encode backend: 0')

        mocked_async_send.assert_has_calls([
            call('{"mocked_backend":1}', json_event, backend_name='1'),
            call('{"mocked_backend":2}', json_event, backend_name='2'),
        ])
