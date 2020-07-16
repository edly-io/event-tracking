"""
Tests for celery tasks
"""
import json

import ddt
from django.test import TestCase
from mock import MagicMock, patch, sentinel

from edx_django_utils.cache import TieredCache
from json_tricks import dumps

from eventtracking.backends.routing import RoutingBackend
from eventtracking.django.tests.factories import RegExFilterFactory
from eventtracking.tasks import async_send


@ddt.ddt
class TestAsyncSend(TestCase):
    """Test async_send task"""

    def setUp(self):
        super(TestAsyncSend, self).setUp()

        self.event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'event': {
                'key': 'value'
            },
            'session': '0000'
        }

        self.backend_name = 'test'
        self.mocked_backend = MagicMock()
        self.backend = self.mocked_backend
        TieredCache.dangerous_clear_all_tiers()

    def test_with_error_in_decoding_backend(self):
        with patch('eventtracking.tasks.json.loads', side_effect=[self.event, ValueError]):
            async_send('DUMPED_BACKEND', json.dumps(self.event), self.backend_name)

        self.mocked_backend.send.assert_not_called()

    @patch('eventtracking.tasks.loads')
    @patch('eventtracking.tasks.logger')
    def test_with_no_or_disabled_filter_for_backend(self, mocked_logger, mocked_loads):
        mocked_loads.return_value = self.mocked_backend
        async_send('DUMPED_BACKEND', json.dumps(self.event), self.backend_name)

        mocked_logger.warning.assert_called_once_with(
            'Regular Expression Filter does not have any enabled configurations'
            ' for backend "%s". Allowing the event "%s" to pass through.',
            self.backend_name, str(sentinel.name)
        )
        self.mocked_backend.send.assert_called_once_with(self.event)

    @patch('eventtracking.tasks.loads')
    @patch('eventtracking.tasks.logger')
    @ddt.data(
        ('sentinel.* \n will_match', 'allowlist', True),
        ('nope \n will_not_match', 'allowlist', False),
    )
    @ddt.unpack
    def test_with_enabled_filter_for_backend(
        self, regex_string, filter_type, should_pass_test, mocked_logger, mocked_loads
    ):
        mocked_loads.return_value = self.mocked_backend

        event_name = str(sentinel.name)
        RegExFilterFactory.create(
            backend_name=self.backend_name,
            is_enabled=True,
            filter_type=filter_type,
            regular_expressions=regex_string
        )
        async_send('DUMPED_BACKEND', json.dumps(self.event), self.backend_name)

        if should_pass_test:
            mocked_logger.info.assert_called_once_with(
                'Event "%s" is allowed to be processed by backend "%s"',
                event_name, self.backend_name
            )
            self.mocked_backend.send.assert_called_once_with(self.event)

        else:
            mocked_logger.info.assert_called_once_with(
                'Event "%s" is not allowed to be processed by backend "%s"',
                event_name, self.backend_name
            )

            self.mocked_backend.send.assert_not_called()

    @patch('eventtracking.tasks.loads')
    def test_successful_sending_event_to_backend(self, mocked_load):
        mocked_load.return_value = self.mocked_backend
        async_send('mocked_backend', json.dumps(self.event), self.backend_name)
        self.mocked_backend.send.assert_called_once_with(self.event)
