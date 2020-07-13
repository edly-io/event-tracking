"""
Transformers for navigation related events.
"""
import json

import six


def edx_ui_lms_sequence_selection(current_event, caliper_event):
    """
    These events are generated when the user navigates through
    the units in a course.

    This transformer supports these events:
        - edx.ui.lms.sequence.next_selected
        - edx.ui.lms.sequence.previous_selected
        - edx.ui.lms.sequence.tab_selected
    """
    if isinstance(current_event['event'], six.string_types):
        event = json.loads(current_event['event'])
    else:
        event = current_event['event']

    object_id = event.pop('target_url') if current_event['name'] == 'edx.ui.lms.link_clicked' else event.pop('id')

    caliper_event['object'].update({
        'id': object_id,  # TODO: should simply use this value or make a URL?
        'type': 'WebPage',
        'extensions': event
    })

    caliper_event.update({
        'action': 'NavigatedTo',
        'type': 'NavigationEvent',
    })

    return caliper_event
