"""
Models for filtering of events
"""
import logging
import re

from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel

from edx_django_utils.cache import TieredCache, get_cache_key


logger = logging.getLogger(__name__)


def validate_regex_list(value):
    """
    Validate every regular expression in the `value` by trying to compile it.

    Arguments:
        value (str):    A string containing `newline` seperated list of regular expressions

    Returns:
        None

    Raises:
        ValidationError:    Error message contains the list of invalid expressions.
    """
    _, invalid_expressions = _clean_expressions(value)

    if invalid_expressions:
        error_message = 'The following invalid expressions must be corrected: {}'.format(
            ', '.join(invalid_expressions)
        )
        raise ValidationError(error_message)


def _clean_expressions(expressions_string):
    """
    Compile the valid regular expressions from the provided `expressions_string`

    Compile the "whitespace-stripped" regular expression in the `expressions_string` list,
    separated by `\n`.

    Arguments:
        expressions_string (str):   `\n` separated list of regular expressions

    Returns:
        tuple   :   (compiled_expressions, invalid_expressions)
                    A tuple containing the list of compiled expressions alongwith the list of
                    invalid regular expressions.
    """
    expressions = expressions_string.split('\n')
    raw_expressions = [expression.strip() for expression in expressions]
    return _compile_and_validate_expressions(raw_expressions)


def _compile_and_validate_expressions(expressions_list):
    """
    Compile the regular expressions in `expressions_list` and invalidate the invalid ones.

    Arguments:
        expressions_list (list):   A list containing regular expression strings.

    Returns:
        tuple   :   (compiled_expressions, invalid_expressions)
                    A tuple containing the list of compiled expressions alongwith the list of
                    invalid regular expressions.
    """
    invalid_regex_expressions = []
    compiled_regex_expressions = []
    for exp in expressions_list:
        try:
            compiled = re.compile(exp)
            compiled_regex_expressions.append(compiled)
        except re.error:
            invalid_regex_expressions.append(exp)
    return compiled_regex_expressions, invalid_regex_expressions


class RegExFilter(TimeStampedModel):
    """
    A filter model to filter the events using regular expressions.
    """

    BLOCKLIST = 'blocklist'
    ALLOWLIST = 'allowlist'
    FILTER_TYPES = (
        (BLOCKLIST, 'Blocklist'),
        (ALLOWLIST, 'Allowlist'),
    )

    backend_name = models.CharField(
        max_length=50,
        verbose_name='Backend name',
        null=False,
        blank=False,
        db_index=True,
        help_text=(
            'Name of the tracking backend on which this filter should be applied.'
            '<br/>'
            'Please note that this field is <b>case sensitive.</b>'
        )
    )

    is_enabled = models.BooleanField(
        default=True,
        verbose_name='Is Enabled'
    )

    filter_type = models.CharField(
        max_length=9,
        choices=FILTER_TYPES,
        verbose_name='Filter type',
        help_text=(
            'Allowlist: Only events matching the regular expressions in the list '
            'will be allowed to passed through.'
            '<br/>'
            'Blocklist: Events matching any regular expression in the list will be '
            'blocked.')
    )

    regular_expressions = models.TextField(
        max_length=500,
        verbose_name='List of regular expressions',
        help_text=('This should be a list of regular expressions, seperated '
                   'by a newline, for the events to be filtered.'),
        validators=(validate_regex_list, )
    )

    class Meta:
        verbose_name = 'Regular Expression Filter'
        ordering = ('backend_name', 'is_enabled', '-modified')

    def __str__(self):
        return '{backend} - {type} - {is_enabled}'.format(
            backend=self.backend_name,
            type=self.filter_type,
            is_enabled='Enabled' if self.is_enabled else 'Disabled'
        )

    def __repr__(self):
        return '<{class_name}: backend_name={backend_name} type={type} is_enabled={is_enabled}>'.format(
            class_name=self.__class__.__name__,
            backend_name=self.backend_name,
            type=self.filter_type,
            is_enabled=self.is_enabled
        )

    @property
    def compiled_expressions(self):
        """
        Return a list of compiled regular expressions.

        If the cached compiled expressions are found matching the expressions string of the filter,
        return the value from the cache.
        Otherwise, compile the `\n` separated list of regular expressions in the `regular_expressions`
        and return if after storing in the cache.

        Arguments:
            None

        Returns:
            list:   list of compiled expressions
        """
        key = get_cache_key(expressions=self.regular_expressions)
        cache_response = TieredCache.get_cached_response(key)

        if cache_response.is_found:
            logger.info('Compiled expressions found in cache for filter "%s"', self)
            return cache_response.value

        logger.info('Compiled expressions not found in cache for filter "%s"', self)
        compiled_expressions, invalid_expressions = _clean_expressions(self.regular_expressions)

        if invalid_expressions:
            logger.error(
                'The following invalid expressions were found in the filter: %s',
                ', '.join(invalid_expressions)
            )

        TieredCache.set_all_tiers(key, compiled_expressions)
        logger.info('Added compiled expressions in cache for filter "%s"', self)
        return compiled_expressions

    @classmethod
    def get_latest_enabled_filter(cls, backend_name=None):
        """
        Return the last modified, enabled filter for the backend matching the `backend_name`.

        If no `backend_name` is provided, return the last modified, enabled filter
        for any backend.
        Return `None` if there is no filter matching the criteria.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.

        Returns:
            RegExFilter or None
        """
        return cls._get_cached_filter(backend_name=backend_name)

    @classmethod
    def _get_cached_filter(cls, backend_name):
        """
        Return the last modified, enabled filter for the backend matching the `backend_name`.

        First look for the filter in the cache and return its value from there if found.
        If not found in the cache, call the `_get_latest_enabled_filter` method to get the
        filter and store it in the cache before returning it.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.

        Returns:
            RegExFilter or None
        """
        filter_cache_key = get_cache_key(backend_name=backend_name)
        cache_response = TieredCache.get_cached_response(filter_cache_key)

        if cache_response.is_found:
            logger.info('Filter is found in cache for backend "%s"', backend_name)
            regex_filter = cache_response.value
        else:
            logger.info('No filter was found in cache for backend "%s"', backend_name)
            regex_filter = cls._get_latest_enabled_filter(backend_name=backend_name)

            TieredCache.set_all_tiers(filter_cache_key, regex_filter)
            logger.info('Filter has been stored in cache for backend "%s"', backend_name)

        return regex_filter

    @classmethod
    def _get_latest_enabled_filter(cls, backend_name=None):
        """
        Return the last modified, enabled filter for the backend matching the `backend_name`.

        If no `backend_name` is provided, return the last modified, enabled filter
        for any backend.
        Return `None` if there is no filter matching the criteria.

        Arguments:
            backend_name (str):    Name of the backend for which the filter is required.

        Returns:
            RegExFilter or None
        """
        queryset = cls.objects.filter(is_enabled=True)

        if backend_name:
            queryset = queryset.filter(backend_name=backend_name)

        return queryset.latest('modified') if queryset.exists() else None

    def is_string_a_match(self, string):
        """
        Match the string with the current filter's compiled regular expressions.

        Return `True`if the string is a match otherwise return `False`.

        Arguments:
            string (str):   string to be matched with regular expressions.

        Returns:
            bool
        """
        for expression in self.compiled_expressions:
            if expression.match(string):
                return True
        return False

    def string_passes_test(self, string):
        """
        Return `True` if a string passes current filter w.r.t. to the filter's type.

        A string passes the test if:
            - `string` matches any regular expression and the
              filter type is set to "allowlist"
            - `string` does not match any regular expression and
              the filter type is set to "blocklist"

        Arguments:
            string (str):   string to be matched with regular expressions.

        Returns:
            bool
        """
        is_a_match = self.is_string_a_match(string)
        if (
            (is_a_match and self.filter_type == self.ALLOWLIST) or
            (not is_a_match and self.filter_type == self.BLOCKLIST)
        ):
            return True
        return False
