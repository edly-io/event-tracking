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
    # 'complete_video': 'Ended',
}


def make_video_block_id(video_id, course_id, video_block_name='video+block', block_version='block-v1'):
    return '{block_version}:{course_id}+type@{video_block_name}@{video_id}'.format(
        block_version=block_version,
        course_id=course_id,
        video_block_name=video_block_name,
        video_id=video_id
    )


def _base_video_transformer(current_event, caliper_event):
    """
    Base tranformer for video related events.
    """
    event_name = current_event['name']
    event = json.loads(current_event['event'])
    current_event['event'] = event

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

    caliper_event['object'].update({
        'id': object_id,
        'type': 'VideoObject',
        'duration': duration_isoformat(timedelta(
                seconds=event.pop('duration')
        ))
    })

    caliper_event.update({
        'action': EVENTS_ACTION_MAP[event_name],
        'type': event_type,
    })

    return caliper_event


def load_stop_video(current_event, caliper_event):
    """
    This transformer is responsible for transformation of these two events:
        - load_video
        - stop_video
    """
    caliper_event = _base_video_transformer(current_event, caliper_event)

    if 'currentTime' in current_event['event']:
        # TODO: delete this or get this?
        del current_event['event']['currentTime']
    caliper_event['object']['extensions'].update(current_event['event'])
    return caliper_event


def play_pause_video(current_event, caliper_event):
    """
    This transformer is responsible for transformation of these two events:
        - play_video
        - pause_video
    """
    caliper_event = _base_video_transformer(current_event, caliper_event)

    current_time = duration_isoformat(timedelta(
        seconds=current_event['event'].pop('currentTime')
    ))

    caliper_event['target'] = {
        'id': caliper_event['object']['id'],
        'type': 'MediaLocation',
        'currentTime': current_time
    }
    caliper_event['object']['extensions'].update(current_event['event'])
    return caliper_event


def seek_video(current_event, caliper_event):
    """
    Transform "seek_video" event.
    """
    caliper_event = _base_video_transformer(current_event, caliper_event)

    new_time = duration_isoformat(timedelta(
        seconds=current_event['event'].pop('new_time')
    ))
    old_time = duration_isoformat(timedelta(
        seconds=current_event['event'].pop('old_time')
    ))
    caliper_event['object']['extensions'].update({
        'new_time': new_time,
        'old_time': old_time
    })

    caliper_event['object']['extensions'].update(current_event['event'])
    return caliper_event
