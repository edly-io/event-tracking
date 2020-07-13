"""
Transformers for problem interaction events.
"""
from eventtracking.processors.caliper.utils.helpers import get_block_id_from_event


def problem_check(current_event, caliper_event):
    """
    The server emits problem_check events when a problem is successfully checked.

    Both browser interactions and server requests produce problem_check events,
    so your data package can also contain events with an event source of browser.

    Events emitted by the browser contains the GET parameters.

    Only events emitted by the server are useful for most purposes.
    """
    object_id = get_block_id_from_event(current_event) or current_event['referer']

    caliper_event['object'].update({
        'id': object_id,
        'type': 'Assessment',
    })

    caliper_event.update({
        'action': 'Submitted',
        'type': 'AssessmentEvent',
    })

    if current_event.get('event_source') == 'server':
        caliper_event['object']['extensions'].update(current_event['event'])
    else:
        caliper_event['object']['extensions'].update({
            'event': current_event['event']
        })

    return caliper_event


def edx_grades_problem_submitted(current_event, caliper_event):
    """
    This event is generated when learner submits a question of peer assignment.
    """
    object_id = get_block_id_from_event(current_event) or current_event['referer']

    caliper_event['object'].update({
        'id': object_id,
        'type': 'Assessment',
    })

    current_event['event'].pop('user_id')
    caliper_event['object']['extensions'].update(current_event['event'])

    caliper_event.update({
        'action': 'Submitted',
        'type': 'AssessmentEvent',
    })
    return caliper_event


def show_answer(current_event, caliper_event):
    """
    This event is generated when learner show answer button on a problem.
    """
    object_id = get_block_id_from_event(current_event) or current_event['referer']

    caliper_event['object'].update({
        'id': object_id,
        'type': 'Frame',
    })

    caliper_event['object']['extensions'].update(current_event['event'])

    caliper_event.update({
        'action': 'Viewed',
        'type': 'ViewEvent',
    })
    return caliper_event
