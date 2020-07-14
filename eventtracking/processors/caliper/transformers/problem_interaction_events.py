"""
Transformers for problem interaction events.
"""
from eventtracking.processors.caliper.utils.helpers import get_block_id_from_event


EVENT_ACTION_MAP = {
    'problem_check': 'Submitted',
    'edx.grades.problem.submitted': 'Submitted',
    'showanswer': 'Viewed',
    'edx.problem.hint.demandhint_displayed': 'Viewed',
    'edx.problem.completed': 'Completed'
}

OBJECT_TYPE_MAP = {
    'problem_check': 'Assessment',
    'edx.grades.problem.submitted': 'Assessment',
    'showanswer': 'Frame',
    'edx.problem.hint.demandhint_displayed': 'Frame',
    'edx.problem.completed': 'AssessmentItem'
}

EVENT_TYPE_MAP = {
    'problem_check': 'AssessmentEvent',
    'edx.grades.problem.submitted': 'AssessmentEvent',
    'showanswer': 'ViewEvent',
    'edx.problem.hint.demandhint_displayed': 'ViewEvent',
    'edx.problem.completed': 'AssessmentItemEvent'
}


def problem_transformer(current_event, caliper_event):
    """
    Transform problem interaction related events into caliper format.
    This transformer can transform the following events:
        - problem_check
        - edx.grades.problem.submitted
        - showanswer
        - edx.problem.hint.demandhint_displayed
        - edx.problem.completed

    Currently there is no "edx.problem.completed" event in open edx but
    will be added in future as per the mapping document:
    https://docs.google.com/spreadsheets/u/1/d/1z_1IGFVDF-wZToKS2EGXFR3s0NXoh6tTKhEtDkevFEM/edit?usp=sharing.
    """
    event_name = current_event['name']

    object_id = get_block_id_from_event(current_event) or current_event['referer']

    caliper_event['object'].update({
        'id': object_id,
        'type': OBJECT_TYPE_MAP[event_name],
    })

    caliper_event.update({
        'action': EVENT_ACTION_MAP[event_name],
        'type': EVENT_TYPE_MAP[event_name],
    })

    if 'user_id' in current_event['event']:
        del current_event['event']['user_id']

    if current_event.get('event_source') == 'server':
        caliper_event['object']['extensions'].update(current_event['event'])
    else:
        caliper_event['object']['extensions'].update({
            'event': current_event['event']
        })

    return caliper_event


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


def edx_problem_hint_demandhint_displayed(current_event, caliper_event):
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


def edx_problem_completed(current_event, caliper_event):
    """
    #TODO: Update the transformer and test JSON files once the event is
    implemented in the code base.

    Currently there is no such event in open edx but
    will be added in future as per the mapping document:
    https://docs.google.com/spreadsheets/u/1/d/1z_1IGFVDF-wZToKS2EGXFR3s0NXoh6tTKhEtDkevFEM/edit?usp=sharing.

    This event is generated when learner completes a problem.
    """
    object_id = get_block_id_from_event(current_event) or current_event['referer']

    caliper_event['object'].update({
        'id': object_id,
        'type': 'AssessmentItem',
    })

    current_event['event'].pop('user_id')
    caliper_event['object']['extensions'].update(current_event['event'])

    caliper_event.update({
        'action': 'Completed',
        'type': 'AssessmentItemEvent',
    })
    return caliper_event
