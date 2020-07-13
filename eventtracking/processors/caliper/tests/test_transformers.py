"""
Test the transformers for all of the currently supported events
"""
import json
import os

import ddt
from mock import MagicMock, patch

from django.test import TestCase

from eventtracking.processors.caliper.transformer import transform_event


TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

EVENT_FIXTURE_FILENAMES = [
    event_file_name for event_file_name in os.listdir(
        '{}/fixtures/current/'.format(TEST_DIR_PATH)
    ) if event_file_name.endswith(".json")
]


@ddt.ddt
class TestTransformers(TestCase):
    """
    Test that supported events are transformed correctly.
    """
    # no limit to diff in the output of tests
    maxDiff = None

    @patch('eventtracking.processors.caliper.utils.base_transformer.get_user_model')
    @ddt.data(*EVENT_FIXTURE_FILENAMES)
    def test_event_transformer(self, event_filename, _):
        input_event_file_path = '{test_dir}/fixtures/current/{event_filename}'.format(
            test_dir=TEST_DIR_PATH, event_filename=event_filename
        )

        expected_event_file_path = '{test_dir}/fixtures/expected/{event_filename}'.format(
            test_dir=TEST_DIR_PATH, event_filename=event_filename
        )

        with open(input_event_file_path) as current, open(expected_event_file_path) as expected:
            original_event = json.loads(current.read())
            expected_event = json.loads(expected.read())

            actual_transformed_event = transform_event(original_event)

            # id is a randomly generated UUID therefore not comparing that
            self.assertIn('id', actual_transformed_event)
            expected_event.pop('id')
            actual_transformed_event.pop('id')

            self.assertDictEqual(expected_event, actual_transformed_event)
