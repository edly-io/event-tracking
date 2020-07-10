"""
Transformer for IMS Caliper.
"""
from celery.utils.log import get_task_logger

from eventtracking.processors.caliper.utils.event_mapping import EVENT_MAPPING
from eventtracking.processors.caliper.exceptions import NoTransformerImplemented
from eventtracking.processors.caliper.utils.base_transformer import base_transformer


logger = get_task_logger(__name__)


def transform_event(event):
    """
    Transform and return the event into IMS Caliper format.
    """
    event_name = event.get('name')

    event = event.copy()
    caliper_event = base_transformer(event)

    try:
        transformer_function = EVENT_MAPPING[event_name]
    except KeyError:
        logger.warning('No Caliper transformer found for event "%s"', event_name)
        raise NoTransformerImplemented

    transformed_event = transformer_function(event, caliper_event)
    return transformed_event
