"""
Caliper event processing backend
"""
from celery.utils.log import get_task_logger

from eventtracking.processors.caliper.transformer import transform_event
from eventtracking.processors.caliper.exceptions import NoTransformerImplemented

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
        event_name = event.get('name')
        logger.info('Going to transform event "%s" into Caliper format', event_name)

        try:
            transformed_event = transform_event(event)
        except NoTransformerImplemented:
            logger.error('Could not transform %s event to Caliper', event.get('name'))
            return

        except Exception as ex:
            logger.error(
                'There was an error while trying to transform event "%s" into'
                ' Caliper format. Error: %s', event_name, str(ex))

        logger.info('Successfully transformed event "%s" into Caliper format', event_name)
        logger.info(transform_event)
