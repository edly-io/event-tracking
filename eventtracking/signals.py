"""
Signal handles for the eventtracking app.
"""
from logging import getLogger

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edx_django_utils.cache import TieredCache, get_cache_key

from eventtracking.django.models import RegExFilter


logger = getLogger(__name__)


def _remove_from_cache(**kwargs):
    """
    Remove a value from the cache.

    Key for cache is generated using the provided `kwargs`.
    """
    key = get_cache_key(**kwargs)
    TieredCache.delete_all_tiers(key)


@receiver([post_save, post_delete], sender=RegExFilter)
def invalidate_backend_filter_cache(instance, *args, **kwargs):   # pylint: disable=unused-argument
    """
    Delete the value for a filter from cache.

    Delete the filter's cache for a backend if that backend's filter is updated, deleted
    or a new one is created.

    Arguments:
        instance (RegExFilter):     `RegExFilter` instance being updated, created or deleted.
        args     (list):             list of remaining positional arguments
        kwargs   (dict):             list of positional arguments
    """
    logger.info('Filter for backend "{}" is updated. '
                'Invalidating filter cache for this backend '
                'as well as the default filter.'.format(instance.backend_name))
    _remove_from_cache(backend_name=instance.backend_name)

    # cache key if no backend is specified
    _remove_from_cache(backend_name=None)


@receiver(post_save, sender=RegExFilter)
def invalidate_compiled_expressions_cache(instance, created, *args, **kwargs):   # pylint: disable=unused-argument
    """
    Delete the value for a filter's compiled expressions from cache.

    If a filter is updated, remove the cached compiled expressions value matching
    the filter's regular expressions.

    Arguments:
        instance (RegExFilter):     `RegExFilter` instance being updated or created.
        args     (list):             list of remaining positional arguments
        kwargs   (dict):             list of positional arguments
    """
    if not created:
        logger.info('Filter for backend "{}" is updated. '
                    'Invalidating compiled expressions cache for regular expressions '
                    'that match this backend\'s.'.format(instance.backend_name))

        _remove_from_cache(expressions=instance.regular_expressions)
