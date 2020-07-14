"""
Transformers for navigation related events.
"""
import json

import six

from eventtracking.transformers.caliper.base_transformer import CaliperTransformer
from eventtracking.transformers.caliper.registry import TransformerRegistry


@TransformerRegistry.register('edx.ui.lms.sequence.next_selected')
@TransformerRegistry.register('edx.ui.lms.sequence.previous_selected')
@TransformerRegistry.register('edx.ui.lms.sequence.tab_selected')
@TransformerRegistry.register('edx.ui.lms.link_clicked')
class NavigationEventsTransformers(CaliperTransformer):
    """
    These events are generated when the user navigates through
    the units in a course.

    This transformer supports these events:
        - edx.ui.lms.sequence.next_selected
        - edx.ui.lms.sequence.previous_selected
        - edx.ui.lms.sequence.tab_selected
    """
    action = 'NavigatedTo'
    type = 'NavigationEvent'

    def get_object(self, current_event, caliper_event):
        """
        Return transformed object for caliper event.
        """
        if isinstance(current_event['event'], six.string_types):
            event = json.loads(current_event['event'])
        else:
            event = current_event['event']

        object_id = event.pop('target_url') if current_event['name'] == 'edx.ui.lms.link_clicked' else event.pop('id')

        caliper_object = caliper_event['object']
        caliper_object.update({
            'id': object_id,
            'type': 'WebPage',
            'extensions': event
        })

        return caliper_object
