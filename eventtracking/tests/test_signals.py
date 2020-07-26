"""
Tests for signal handlers.
"""
from mock import patch
from django.test import TestCase

from edx_django_utils.cache import TieredCache

from eventtracking.django.tests.factories import RegExFilterFactory
from eventtracking.django.models import RegExFilter, _clean_expressions


class TestSignals(TestCase):
    """
    Test the signal handlers.
    """

    def setUp(self):
        super(TestSignals, self).setUp()
        TieredCache.dangerous_clear_all_tiers()

    @patch(
        'eventtracking.django.models.RegExFilter.objects.filter',
        side_effect=RegExFilter.objects.filter
    )
    def test_invalidate_backend_cache(self, mocked_filter):
        regex_filter = RegExFilterFactory(backend_name='test')

        # First time there is no cache and dB
        actual_filter = RegExFilter.get_latest_enabled_filter('test')

        self.assertEqual(regex_filter, actual_filter)
        mocked_filter.assert_called_once_with(is_enabled=True)

        mocked_filter.reset_mock()

        actual_filter = RegExFilter.get_latest_enabled_filter('test')

        # Second time, filter will be found from the cache
        self.assertEqual(regex_filter, actual_filter)
        mocked_filter.assert_not_called()

        mocked_filter.reset_mock()

        # if the filter is updated, the cache will be invalidated
        regex_filter.save()
        actual_filter = RegExFilter.get_latest_enabled_filter('test')

        # since the cache is invalidated, filter will not be found in cache
        self.assertEqual(regex_filter, actual_filter)
        mocked_filter.assert_called_once_with(is_enabled=True)

    @patch('eventtracking.django.models._clean_expressions', side_effect=_clean_expressions)
    def test_invalidate_compiled_expressions_cache(self, mocked_clean_expressions):
        test_filter = RegExFilterFactory(backend_name='test', regular_expressions='test.*')

        _ = test_filter.compiled_expressions

        # no previous cache. _clean_expressions will be called
        mocked_clean_expressions.assert_called_once_with(test_filter.regular_expressions)

        mocked_clean_expressions.reset_mock()

        _ = test_filter.compiled_expressions

        # property `compiled_expressions` was cached. _clean expressions will not be called.
        mocked_clean_expressions.assert_not_called()

        _ = RegExFilterFactory(backend_name='test2', regular_expressions='test2.*')

        _ = test_filter.compiled_expressions

        # Creating a new filter does not affect the cache. _clean expressions will not be called.
        mocked_clean_expressions.assert_not_called()

        test_filter.save()
        _ = test_filter.compiled_expressions

        # Since the filter is updated, cache is invalidated. _clean expressions will be called
        mocked_clean_expressions.assert_called_once_with(test_filter.regular_expressions)
