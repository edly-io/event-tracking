"""
Tests for django models
"""
import re

import ddt
from mock import call, patch, sentinel
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from edx_django_utils.cache import TieredCache

from eventtracking.django.tests.factories import RegExFilterFactory
from eventtracking.django.models import validate_regex_list, RegExFilter, _clean_expressions


@ddt.ddt
class TestRegExFilter(TestCase):
    """Test RegExFilter model"""

    def setUp(self):
        super(TestRegExFilter, self).setUp()

        TieredCache.dangerous_clear_all_tiers()

    def test_get_latest_filter(self):
        # With no existing filters, it should return None
        self.assertIsNone(RegExFilter.get_latest_enabled_filter())

        first_enabled = []
        first_disabled = []
        second_enabled = []
        second_disabled = []

        for _ in range(5):
            first_enabled.append(RegExFilterFactory.create(is_enabled=True, backend_name='first'))
            first_disabled.append(RegExFilterFactory.create(is_enabled=False, backend_name='first'))
            second_enabled.append(RegExFilterFactory.create(is_enabled=True, backend_name='second'))
            second_disabled.append(RegExFilterFactory.create(is_enabled=False, backend_name='second'))

        # test with no backend name
        self.assertEqual(second_enabled[4], RegExFilter.get_latest_enabled_filter())

        # test with backend name
        self.assertEqual(first_enabled[4], RegExFilter.get_latest_enabled_filter('first'))

        # test enabling a filter
        first_disabled[2].is_enabled = True
        first_disabled[2].save()

        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter())
        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter('first'))
        self.assertEqual(second_enabled[4], RegExFilter.get_latest_enabled_filter('second'))

        # test modifying an enabled filter
        second_enabled[1].save()

        self.assertEqual(second_enabled[1], RegExFilter.get_latest_enabled_filter())
        self.assertEqual(first_disabled[2], RegExFilter.get_latest_enabled_filter('first'))
        self.assertEqual(second_enabled[1], RegExFilter.get_latest_enabled_filter('second'))

    def test_validator(self):
        valid_expressions = ['abc', '.?[1-10]*']
        invalid_expressions = ['***', '*?*']
        expressions_string = ' \n '.join(valid_expressions+invalid_expressions)

        expected_error_message = 'The following invalid expressions must be corrected: {}'.format(
            ', '.join(invalid_expressions)
        )

        with self.assertRaisesMessage(ValidationError, expected_error_message):
            validate_regex_list(expressions_string)

    @patch('eventtracking.django.models.logger')
    def test_with_invalid_regular_expressions(self, mocked_logger):
        invalid_regular_exressions = ['***', '*?*']
        valid_regular_expressions = ['abc', '.?[1-10]*']

        expressions_string = ' \n '.join(invalid_regular_exressions + valid_regular_expressions)
        regex_filter = RegExFilterFactory(
            regular_expressions=expressions_string
        )

        compiled_regular_expressions = regex_filter.compiled_expressions
        self.assertEqual(compiled_regular_expressions, [
            re.compile(ex) for ex in valid_regular_expressions
        ])
        mocked_logger.error.assert_called_once_with(
            'The following invalid expressions were found in the filter: %s',
            ', '.join(invalid_regular_exressions)
        )

    @patch('eventtracking.django.models._clean_expressions', side_effect=_clean_expressions)
    def test_compiled_expressions_caching(self, mocked_clean_expressions):
        expressions_string = 'test \n test2'
        regex_filter = RegExFilterFactory(
            regular_expressions=expressions_string
        )

        # cache will be set the first time and `_clean_expressions` will be called
        _ = regex_filter.compiled_expressions
        mocked_clean_expressions.assert_called_once()

        mocked_clean_expressions.reset_mock()

        # cache will found this time and `_clean_expressions` will not be called
        _ = regex_filter.compiled_expressions
        mocked_clean_expressions.assert_not_called()

    @patch('eventtracking.django.models.RegExFilter.objects.filter',
           side_effect=RegExFilter.objects.filter)
    @patch('eventtracking.django.models.logger')
    def test_latest_filter_caching(self, mocked_logger, mocked_objects_filter):
        expressions_string = 'test \n test2'

        first_regex_filter = RegExFilterFactory(
            regular_expressions=expressions_string,
            is_enabled=True,
            backend_name='first'
        )

        regex_filter = RegExFilter.get_latest_enabled_filter(backend_name='first')

        mocked_objects_filter.assert_called_once_with(is_enabled=True)
        self.assertIn(
            call('No filter was found in cache for backend "%s"', 'first'),
            mocked_logger.info.mock_calls
        )

        self.assertIn(
            call('Filter has been stored in cache for backend "%s"', 'first'),
            mocked_logger.info.mock_calls
        )

        mocked_logger.reset_mock()
        mocked_objects_filter.reset_mock()

        regex_filter = RegExFilter.get_latest_enabled_filter(backend_name='first')
        mocked_objects_filter.assert_not_called()
        mocked_logger.info.assert_called_once_with('Filter is found in cache for backend "%s"', 'first')

        self.assertEqual(regex_filter, first_regex_filter)

    @ddt.data(
        ('allowlist', 'sentinel.* \n not_matching \n .*', True),
        ('allowlist', 'not_matching \n ** \n !@#$!@', False),
        ('allowlist', '', True),
        ('allowlist', None, None),
        ('blocklist', 'sentinel.* \n not_matching \n .*', False),
        ('blocklist', 'not_matching \n ** \n !@#$!@', True),
        ('blocklist', '', False),
        ('blocklist', None, None),
    )
    @ddt.unpack
    def test_string_passes_test(self, filter_type, regex, should_pass_test):
        def create_filter():
            return RegExFilterFactory.create(
                is_enabled=True,
                filter_type=filter_type,
                regular_expressions=regex
            )

        event_name = str(sentinel.name)

        if regex is None:
            with self.assertRaises(IntegrityError):
                create_filter()

        else:
            reg_filter = create_filter()
            actual_test_result = reg_filter.string_passes_test(event_name)
            self.assertEqual(actual_test_result, should_pass_test)
