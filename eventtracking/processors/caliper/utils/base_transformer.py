"""
Base transformer to add or transform common data values.
"""

import uuid
from eventtracking.processors.caliper.utils.helpers import convert_datetime
from student.models import anonymous_id_for_user


CALIPER_EVENT_CONTEXT = 'http://purl.imsglobal.org/ctx/caliper/v1p1'


def base_transformer(event):
    """Transforms event into caliper format
    @param event: unprocessed event dict
    """
    caliper_event = {}

    _add_generic_fields(event, caliper_event)
    _add_actor_info(event, caliper_event)
    _add_referrer(event, caliper_event)
    _add_extensions(event, caliper_event)

    return caliper_event


def _add_generic_fields(event, caliper_event):
    """
    Adds all of the generic fields to the caliper_event object.

    @param event: unprocessed event dict
    @param caliper_event: caliper event dict
    """
    caliper_event.update({
        '@context': CALIPER_EVENT_CONTEXT,
        'id': uuid.uuid4().urn,
        'eventTime': convert_datetime(event.get('time'))
    })


def _add_actor_info(event, caliper_event):
    """
    Adds all generic information related to `actor`

    @param event: unprocessed event dict
    @param caliper_event: caliper event dict
    """
    caliper_event['actor'] = {
        'id': 'anonymousID',
        'type': 'Person'
    }


def _add_extensions(event, caliper_event):
    """
    A map of additional attributes not defined by the model MAY be
    specified for a more concise representation of the Event.

    @param event: unprocessed event dict
    @param caliper_event: caliper event dict
    """
    caliper_event['extensions'] = {
        'extra_fields': {
            'agent': event.get('agent'),
            'event_type': event.get('event_type'),
            'event_source': event.get('event_source'),
            'host': event.get('host'),
            'org_id': event['context'].get('org_id'),
            'path': event['context'].get('path'),
            'session': event.get('session'),
            'user_id': event['context'].get('user_id'),
            'accept_language': event.get('accept_language'),
            'page': event.get('page'),
        }
    }


def _add_referrer(event, caliper_event):
    """
    Adds information of an Entity that represents the referring context.

    @param event: unprocessed event dict
    @param caliper_event: caliper event dict
    """
    caliper_event['referrer'] = {
        'id': event.get('referer'),
        'type': 'WebPage'
    }
