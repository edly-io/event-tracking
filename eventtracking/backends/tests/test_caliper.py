"""Test the caliper backend"""

from __future__ import absolute_import

import json
from unittest import TestCase

from mock import ANY, MagicMock, call, patch, sentinel

from eventtracking.backends.caliper import CaliperBackend


class TestCaliperBackend(TestCase):
    """Test cases for Caliper backend"""

    def setUp(self):
        super(TestCaliperBackend, self).setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.backend = CaliperBackend()

    @patch('eventtracking.backends.caliper.logger')
    def test_send_method_with_no_transformer_implemented(self, mocked_logger):
        self.backend.send(self.sample_event)
        mocked_logger.error.assert_called_once_with(
            'Could not transform %s event to Caliper',
            self.sample_event.get('name')
        )

    @patch('eventtracking.backends.caliper.TransformerRegistry.get_transformer', side_effect=ValueError)
    @patch('eventtracking.backends.caliper.logger')
    def test_send_method_with_unknown_exception(self, mocked_logger, _):
        with self.assertRaises(ValueError):
            self.backend.send(self.sample_event)

        mocked_logger.exception.assert_called_once_with(
            'There was an error while trying to transform event "%s" into'
            ' Caliper format. Error: %s', self.sample_event['name'], ANY
        )

    @patch('eventtracking.backends.caliper.TransformerRegistry.get_transformer')
    @patch('eventtracking.backends.caliper.logger')
    def test_send_method_with_successfull_transformation(self, mocked_logger, mocked_get_transformer):
        transformed_event = {
            'transformed_key': 'transformed_value'
        }
        mocked_transformer = MagicMock()
        mocked_transformer.transform.return_value = transformed_event
        mocked_get_transformer.return_value = mocked_transformer

        self.backend.send(self.sample_event)

        self.assertIn(call(json.dumps(transformed_event)), mocked_logger.mock_calls)
