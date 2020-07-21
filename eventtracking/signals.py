"""
Signal handles for the eventtracking app.
"""
from logging import getLogger

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edx_django_utils.cache import TieredCache, get_cache_key

from eventtracking.django.models import RegExFilter, FILTER_CACHE_NAMESPACE


logger = getLogger(__name__)


@receiver([post_save, post_delete], sender=RegExFilter)
def invalidate_backend_filter_cache(instance, *args, **kwargs):   # pylint: disable=unused-argument
    """
    Delete filter's cache for a backend if a backend's filter is updated, deleted
    or a new one is created.
    """
    logger.info('Filter for backend "%s" is updated. '
                'Invalidating filter cache for this backend '
                'as well as the default filter.', instance.backend_name)
    key = get_cache_key(
        namespace=FILTER_CACHE_NAMESPACE,
        backend_name=instance.backend_name
    )
    TieredCache.delete_all_tiers(key)

    # cache key if no backend is specified
    key = get_cache_key(
        namespace=FILTER_CACHE_NAMESPACE,
        backend_name=None
    )
    TieredCache.delete_all_tiers(key)


@receiver(post_save, sender=RegExFilter)
def invalidate_compiled_expressions_cache(instance, created, *args, **kwargs):   # pylint: disable=unused-argument
    """
    If a filter is updated, remove the cached compiled expressions value matching
    the filter's regular expressions
    """
    if not created:
        logger.info('Filter for backend "%s" is updated. '
                    'Invalidating compiled expressions cache for regular expressions '
                    'that match this backend\'s.',
                    instance.backend_name)
        key = get_cache_key(
            namespace=FILTER_CACHE_NAMESPACE,
            expressions=instance.regular_expressions
        )
        TieredCache.delete_all_tiers(key)
