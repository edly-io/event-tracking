"""
Transformers for problem interaction events.
"""


def problem_check(orig_event, caliper_event):
    """
    The server emits problem_check events when a problem is successfully checked.

    Both browser interactions and server requests produce problem_check events,
    so your data package can also contain events with an event source of browser.

    Events emitted by the browser contains the GET parameters.

    Only events emitted by the server are useful for most purposes.
    """

    caliper_event.update({
        'action': 'Submitted',
        'type': 'AssessmentEvent',
        'object': {
            'id': orig_event['referer'],
            'type': 'Assessment',
        }
    })
    caliper_event['actor'].update({
        'name': orig_event['username'],
        'type': 'Person'
    })
    caliper_event['extensions']['extra_fields'].update(orig_event['context'])
    caliper_event['extensions']['extra_fields']['ip'] = orig_event['ip']

    if orig_event.get('event_source') == 'server':
        caliper_event['extensions']['extra_fields'].pop('session')
        caliper_event['object']['extensions'] = orig_event['event']
    else:
        caliper_event['object'].update({
            'extensions': {
                'event': orig_event['event']
            }
        })

    return caliper_event
