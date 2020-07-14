"""
Registry to keep track of event transforems
"""
import json
import uuid
from logging import getLogger

import six
from django.contrib.auth import get_user_model

from student.models import anonymous_id_for_user    # pylint: disable=import-error

from eventtracking.processors.caliper.utils.helpers import convert_datetime


CALIPER_CONTEXT = 'http://purl.imsglobal.org/ctx/caliper/v1p1'

logger = getLogger()


class TransformerRegistry:
    """
    This class keeps tracks of event to transformer mapping.
    """

    mapping = {}

    @classmethod
    def register(cls, event_key):
        """
        Decorator to register a transformer for an event
        """
        def __inner__(transformer):
            cls.mapping[event_key] = transformer
            return transformer

        return __inner__

    @classmethod
    def get_transformer(cls, event):
        event_name = event.get('name')
        return cls.mapping[event_name](event)


class CaliperTransformer:
    """
    Base transformer class to transform common fields.

    Other transformers are inherited from this class.
    """
    transforming_fields = (
        'type',
        'object',
        'action'
    )

    def __init__(self, event):
        self.event = event.copy()

    def json_load_event(self):
        if isinstance(self.event['event'], six.string_types):
            self.event['event'] = json.loads(self.event['event'])

    def transform(self):
        transformed_event = {}
        self._base_transform(transformed_event)

        for key in self.transforming_fields:
            if hasattr(self, key):
                value = getattr(self, key)
                transformed_event[key] = value
            elif hasattr(self, 'get_{}'.format(key)):
                value = getattr(self, 'get_{}'.format(key))(self.event, transformed_event)
                transformed_event[key] = value
            else:
                raise ValueError(
                    'Cannot find value for "{}" in transforomer {} for the event "{}"'.format(
                        key, self.__class__.__name__, self.event['name']
                    )
                )

        return transformed_event

    def _base_transform(self, transformed_event):
        self._add_generic_fields(transformed_event)
        self._add_actor_info(transformed_event)
        self._add_referrer(transformed_event)

    def _add_generic_fields(self, transformed_event):
        """
        Add all of the generic fields to the transformed_event object.
        """
        transformed_event.update({
            '@context': CALIPER_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime(self.event.get('time'))
        })
        transformed_event['object'] = {
            'extensions': {
                'course_id': self.event['context'].get('course_id', '')
            }
        }

    def _add_actor_info(self, transformed_event):
        """
        Add all generic information related to `actor`.
        """
        anonymous_id = self._generate_anonymous_id()

        transformed_event['actor'] = {
            'id': anonymous_id,
            'type': 'Person'
        }

    def _generate_anonymous_id(self):
        """
        Generate anonymous user id using the username and course_id
        in the event data. If no anonymous id is generated, return "anonymous"
        """
        User = get_user_model()

        # Prefer None over empty course_id
        course_id = self.event['context'].get('course_id') or None
        username = self.event.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('User with username "%s" does not exist. '
                         'Cannot generate anonymous ID', username)

            anonymous_id = 'anonymous'
        else:
            anonymous_id = anonymous_id_for_user(user, course_id)

        return anonymous_id

    def _add_extensions(self, transformed_event):
        """
        A map of additional attributes not defined by the model MAY be
        specified for a more concise representation of the Event.
        """
        transformed_event['extensions'] = {
            'extra_fields': {
                'agent': self.event.get('agent'),
                'event_type': self.event.get('event_type'),
                'event_source': self.event.get('event_source'),
                'host': self.event.get('host'),
                'session': self.event.get('session'),
                # 'user_id': event['context'].get('user_id'),
                'accept_language': self.event.get('accept_language'),
                'page': self.event.get('page'),
            }
        }

        if 'user_id' in self.event['context']:
            del self.event['context']['user_id']

        transformed_event['extensions']['extra_fields'].update(self.event['context'])

    def _add_referrer(self, transformed_event):
        """
        Adds information of an Entity that represents the referring context.

        @param event: unprocessed event dict
        @param transformed_event: caliper event dict
        """
        transformed_event['referrer'] = {
            'id': self.event.get('referer'),
            'type': 'WebPage'
        }
