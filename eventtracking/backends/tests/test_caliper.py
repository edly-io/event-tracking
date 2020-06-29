"""Test the caliper backend"""

from __future__ import absolute_import

from unittest import TestCase

from mock import call, patch, sentinel

from eventtracking.backends.caliper import CaliperBackend


class TestCaliperBackend(TestCase):
    """Test cases for Caliper backend"""

    def setUp(self):
        super(TestCaliperBackend, self).setUp()
        self.sample_event = {
            'name': sentinel.name
        }
        self.backend = CaliperBackend()

    @patch('eventtracking.backends.caliper.logger')
    def test_send_method(self, mocked_logger):
        """
        TODO: Modify the test case once the logic has been implemented for the backend
        """
        self.backend.send(self.sample_event)
        mocked_logger.info.assert_has_calls([
            call('CALIPER'),
            call(self.sample_event)
        ])
