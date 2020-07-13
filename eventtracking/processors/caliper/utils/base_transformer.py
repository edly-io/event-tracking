"""
Base transformer to add or transform common data values.
"""

import uuid
from logging import getLogger

from django.contrib.auth import get_user_model

from student.models import anonymous_id_for_user

from eventtracking.processors.caliper.utils.helpers import convert_datetime


CALIPER_EVENT_CONTEXT = 'http://purl.imsglobal.org/ctx/caliper/v1p1'

logger = getLogger()


def base_transformer(event):
    """Transforms event into caliper format
    """
    caliper_event = {}

    _add_generic_fields(event, caliper_event)
    _add_actor_info(event, caliper_event)
    _add_referrer(event, caliper_event)
    # _add_extensions(event, caliper_event)

    return caliper_event


def _add_generic_fields(event, caliper_event):
    """
    Add all of the generic fields to the caliper_event object.
    """
    caliper_event.update({
        '@context': CALIPER_EVENT_CONTEXT,
        'id': uuid.uuid4().urn,
        'eventTime': convert_datetime(event.get('time'))
    })
    caliper_event['object'] = {
        'extensions': {
            'course_id': event['context'].get('course_id', '')
        }
    }


def _add_actor_info(event, caliper_event):
    """
    Adds all generic information related to `actor`
    """
    anonymous_id = _generate_anonymous_id(event)

    caliper_event['actor'] = {
        'id': anonymous_id,
        'type': 'Person'
    }


def _generate_anonymous_id(event):
    """
    Generate anonymous user id for using the username and course_id
    in the event data. If no anonymous id is generated, return "anonymous"
    """
    User = get_user_model()

    # Prefer None over empty course_id
    course_id = event['context'].get('course_id') or None
    username = event.get('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.error('User with username "%s" does not exist. '
                     'Cannot generate anonymous ID', username)

        anonymous_id = 'anonymous'
    else:
        anonymous_id = anonymous_id_for_user(user, course_id)

    return anonymous_id


def _add_extensions(event, caliper_event):
    """
    A map of additional attributes not defined by the model MAY be
    specified for a more concise representation of the Event.
    """
    caliper_event['extensions'] = {
        'extra_fields': {
            'agent': event.get('agent'),
            'event_type': event.get('event_type'),
            'event_source': event.get('event_source'),
            'host': event.get('host'),
            'session': event.get('session'),
            # 'user_id': event['context'].get('user_id'),
            'accept_language': event.get('accept_language'),
            'page': event.get('page'),
        }
    }

    event['context'].pop('user_id') if 'user_id' in event['context'] else None

    caliper_event['extensions']['extra_fields'].update(event['context'])


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
