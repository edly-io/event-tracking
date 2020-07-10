"""Test the xapi backend"""

from __future__ import absolute_import

from unittest import TestCase

from mock import call, patch, sentinel

from eventtracking.backends.xapi import XAPIBackend


class TestXAPIBackend(TestCase):
    """Test cases for XAPI backend"""

    def setUp(self):
        super(TestXAPIBackend, self).setUp()
        self.sample_event = {
            'name': sentinel.name
        }
        self.backend = XAPIBackend()

    @patch('eventtracking.backends.xapi.logger')
    def test_send_method(self, mocked_logger):
        """
        TODO: Modify the test case once the logic has been implemented for the backend
        """
        self.backend.send(self.sample_event)
        mocked_logger.info.assert_has_calls([
            call('XAPI'),
            call(self.sample_event)
        ])
