"""
Caliper event processing backend
"""
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class CaliperBackend:
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """

    def send(self, event):
        """
        Process the passed event.
        """
        logger.info('CALIPER')
        logger.info(event)
