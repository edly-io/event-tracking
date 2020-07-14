"""
Transformers for video interaction events.
"""
import json
from datetime import timedelta

from isodate import duration_isoformat

EVENTS_ACTION_MAP = {
    'load_video': 'Retrieved',
    'play_video': 'Started',
    'stop_video': 'Ended',
    'pause_video': 'Paused',
    'seek_video': 'JumpedTo',
    'complete_video': 'Ended',
}


def make_video_block_id(video_id, course_id, video_block_name='video+block', block_version='block-v1'):
    return '{block_version}:{course_id}+type@{video_block_name}@{video_id}'.format(
        block_version=block_version,
        course_id=course_id,
        video_block_name=video_block_name,
        video_id=video_id
    )


def video_transformer(current_event, caliper_event):
    """
    This transformer supports transformation of these events:

        - load_video
        - play_video
        - pause_video
        - stop_video
        - complete_video (proposed)
            This event does not exist currently but is expected to be added in the future.
            # FIXME: Do we need this? stop_video serves the same purpose

    """
    event_name = current_event['name']
    event = json.loads(current_event['event'])

    if event_name == 'load_video':
        event_type = 'Event'
    elif event_name in (
        'play_video',
        'stop_video',
        'pause_video',
        'seek_video',
        'complete_video'
    ):
        event_type = 'MediaEvent'

    course_id = current_event['context']['course_id']
    video_id = event['id']

    object_id = make_video_block_id(course_id=course_id, video_id=video_id)

    current_time = duration_isoformat(timedelta(
        seconds=event.pop('currentTime')
    )) if 'currentTime' in event else None

    if event_name in (
        'play_video',
        'pause_video'
    ):
        caliper_event['target'] = {
            'id': object_id,
            'type': 'MediaLocation',
            'currentTime': current_time
        }

    caliper_event['object'].update({
        'id': object_id,
        'type': 'VideoObject',
        'duration': duration_isoformat(timedelta(
                seconds=event.pop('duration')
        ))
    })

    if event_name == 'seek_video':
        new_time = duration_isoformat(timedelta(
            seconds=event.pop('new_time')
        ))
        old_time = duration_isoformat(timedelta(
            seconds=event.pop('old_time')
        ))
        caliper_event['object']['extensions'].update({
            'new_time': new_time,
            'old_time': old_time
        })

    caliper_event['object']['extensions'].update(event)

    caliper_event.update({
        'action': EVENTS_ACTION_MAP[event_name],
        'type': event_type,
    })

    return caliper_event
