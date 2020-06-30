import logging
from celery.utils.log import get_task_logger

from eventtracking.backends.routing import RoutingBackend

LOGGER = get_task_logger(__name__)


class XApiBackend(RoutingBackend):
    """
    Backend to transform events into xAPI compliant format
    and then route those events to configured endpoints.
    """

    def send(self, event):
        LOGGER.info('XAPI')
        LOGGER.info(event)
